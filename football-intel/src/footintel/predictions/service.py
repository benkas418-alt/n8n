"""Produce and store pre-match predictions, and record user predictions."""

import logging
import math
from dataclasses import dataclass
from datetime import UTC, datetime, time, timedelta

import pandas as pd
from sqlalchemy import Engine, select

from footintel.config import Settings
from footintel.db.models import (
    Match,
    ModelVersion,
    Prediction,
    SidePrediction,
    UserPrediction,
)
from footintel.db.session import session_scope
from footintel.features.builder import ALL_FEATURES, build_features
from footintel.features.dataset import load_matches
from footintel.models.base import GOAL_COLS, PROB_COLS
from footintel.models.registry import load_model, train_version
from footintel.models.zoo import SIDE_MODELS

log = logging.getLogger(__name__)


class PredictionRefused(Exception):
    pass


def as_utc(value: datetime) -> datetime:
    """Some drivers return naive datetimes; all stored times are UTC."""
    return value if value.tzinfo else value.replace(tzinfo=UTC)


def kickoff_deadline(kickoff_utc: datetime | None, kickoff_date) -> datetime:
    """Latest moment a prediction counts as pre-match.

    Without a kick-off time we use midnight UTC of the match day, which is earlier
    than any real kick-off, so a prediction can never be after the start."""
    if kickoff_utc is not None:
        return as_utc(kickoff_utc)
    return datetime.combine(pd.Timestamp(kickoff_date).date(), time(0, 0), tzinfo=UTC)


def _clean(value):
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    if hasattr(value, "item"):
        value = value.item()
        return None if isinstance(value, float) and math.isnan(value) else value
    return value


def data_quality(row: pd.Series, model_features: list[str], settings: Settings) -> dict:
    warnings = []
    n_h, n_a = int(row["n_prior_h"]), int(row["n_prior_a"])
    if min(n_h, n_a) < settings.min_prior_matches:
        warnings.append(f"insufficient_history: {n_h} / {n_a} prior matches "
                        f"(minimum {settings.min_prior_matches})")
    odds_ok = not pd.isna(row["mkt_p_home"])
    if not odds_ok:
        warnings.append("no_pre_match_odds")
    missing_used = [f for f in model_features if f in row and pd.isna(row[f])]
    if missing_used:
        warnings.append(f"missing_features: {', '.join(missing_used)}")
    if pd.isna(row.get("kickoff_utc")):
        warnings.append("kickoff_time_unknown")
    uses_market = any(f.startswith("mkt_") for f in model_features)
    sufficient = min(n_h, n_a) >= settings.min_prior_matches and (odds_ok or not uses_market)
    return {"n_prior_home": n_h, "n_prior_away": n_a, "odds_available": odds_ok,
            "missing_features": missing_used, "warnings": warnings, "sufficient": sufficient}


def _upcoming(feats: pd.DataFrame, now: datetime, horizon_days: int) -> pd.DataFrame:
    feats = feats.copy()
    feats["deadline"] = [kickoff_deadline(None if pd.isna(k) else k.to_pydatetime(), d)
                         for k, d in zip(feats["kickoff_utc"], feats["kickoff_date"], strict=True)]
    # Context leagues are never predicted: they only rate clubs met in European cups.
    return feats[(feats["status"] == "scheduled") & feats["is_target"].fillna(True).astype(bool)
                 & (feats["deadline"] > now)
                 & (feats["deadline"] <= now + timedelta(days=horizon_days))]


@dataclass
class PredictSummary:
    created: int = 0
    unchanged: int = 0
    refused: int = 0
    model: str | None = None


# Same window as the start page list, so every listed match has probabilities and fair odds.
# Each morning recomputes them with the latest results and odds (D63).
PREDICT_DAYS = 21


def predict_upcoming(engine: Engine, settings: Settings, horizon_days: int = PREDICT_DAYS,
                     now: datetime | None = None) -> PredictSummary:
    now = now or datetime.now(UTC)
    summary = PredictSummary()
    with session_scope(engine) as s:
        mv = s.scalars(select(ModelVersion).where(ModelVersion.status == "active")).first()
    if mv is None:
        log.warning("No active model: no prediction produced. Run `footintel models train`.")
        return summary
    summary.model = f"{mv.name} v{mv.version}"
    model = load_model(mv)

    upcoming = _upcoming(build_features(load_matches(engine, as_of=now)), now, horizon_days)
    if upcoming.empty:
        log.info("No upcoming match within %d days", horizon_days)
        return summary

    probs = model.predict(upcoming)
    with session_scope(engine) as s:
        for idx, row in upcoming.iterrows():
            p = probs.loc[idx]
            snapshot = {f: _clean(row[f]) for f in ALL_FEATURES}
            snapshot["odds_1x2"] = [_clean(row["odds_h"]), _clean(row["odds_d"]), _clean(row["odds_a"])]
            latest = s.scalars(select(Prediction)
                               .where(Prediction.match_id == int(row["match_id"]),
                                      Prediction.model_version_id == mv.id)
                               .order_by(Prediction.predicted_at.desc())).first()
            if latest is not None and latest.feature_snapshot == snapshot:
                summary.unchanged += 1
                continue
            quality = data_quality(row, model.features, settings)
            values = {c: _clean(p[c]) if c in p else None for c in PROB_COLS + GOAL_COLS}
            if any(values[c] is None for c in PROB_COLS):
                summary.refused += 1
                log.warning("Match %s: model returned no 1X2 probability", row["match_id"])
                continue
            s.add(Prediction(match_id=int(row["match_id"]), model_version_id=mv.id,
                             predicted_at=now, feature_snapshot=snapshot, data_quality=quality,
                             sufficient_data=quality["sufficient"], **values))
            summary.created += 1
    log.info("Predictions: %d new, %d unchanged, %d refused (%s)", summary.created,
             summary.unchanged, summary.refused, summary.model)
    return summary


# A side model is refitted once a week with the latest results, like the active one.
SIDE_REFIT_DAYS = 7


def _side_version(engine: Engine, settings: Settings, name: str, feats: pd.DataFrame,
                  now: datetime) -> ModelVersion:
    """The current version of side model `name`, refitted when missing or a week old.
    Status "side": never "active", "candidate" or "retired", so promotion and rollback
    can never turn it into the model of the tickets."""
    with session_scope(engine) as s:
        mv = s.scalars(select(ModelVersion).where(ModelVersion.name == name, ModelVersion.status == "side")
                       .order_by(ModelVersion.version.desc())).first()
        if mv is not None and as_utc(mv.created_at) > now - timedelta(days=SIDE_REFIT_DAYS):
            s.expunge(mv)
            return mv
    new_id = train_version(engine, settings, feats, name)
    with session_scope(engine) as s:
        for old in s.scalars(select(ModelVersion).where(ModelVersion.name == name,
                                                         ModelVersion.status == "side")):
            old.status = "side_retired"
        mv = s.get(ModelVersion, new_id)
        mv.status, mv.decision_note = "side", "D105: shown next to the active model, never used for tickets"
        s.flush()
        s.expunge(mv)
        return mv


def predict_side(engine: Engine, settings: Settings, horizon_days: int = PREDICT_DAYS,
                 now: datetime | None = None) -> dict:
    """1X2 of each side model (D105) for the same matches as the active model."""
    now = now or datetime.now(UTC)
    feats = build_features(load_matches(engine, as_of=now))
    upcoming = _upcoming(feats, now, horizon_days)
    out: dict = {}
    for name in SIDE_MODELS:
        mv = _side_version(engine, settings, name, feats, now)
        if upcoming.empty:
            out[name] = {"version": mv.version, "created": 0, "unchanged": 0}
            continue
        probs = load_model(mv).predict(upcoming)
        created = unchanged = 0
        with session_scope(engine) as s:
            for idx, row in upcoming.iterrows():
                p = probs.loc[idx]
                if any(pd.isna(p[c]) for c in PROB_COLS):
                    continue
                snapshot = {f: _clean(row[f]) for f in mv.features or []}
                latest = s.scalars(select(SidePrediction)
                                   .where(SidePrediction.match_id == int(row["match_id"]),
                                          SidePrediction.model_version_id == mv.id)
                                   .order_by(SidePrediction.predicted_at.desc())).first()
                if latest is not None and latest.feature_snapshot == snapshot:
                    unchanged += 1
                    continue
                s.add(SidePrediction(match_id=int(row["match_id"]), model_version_id=mv.id, predicted_at=now,
                                     feature_snapshot=snapshot, **{c: float(p[c]) for c in PROB_COLS}))
                created += 1
        out[name] = {"version": mv.version, "created": created, "unchanged": unchanged}
        log.info("Side model %s v%d: %d new, %d unchanged", name, mv.version, created, unchanged)
    return out


def submit_user_prediction(engine: Engine, match_id: int, pick: str, confidence: int, *,
                           home_goals: int | None = None, away_goals: int | None = None,
                           over_2_5: bool | None = None, btts: bool | None = None,
                           reasoning: str | None = None, user_label: str = "me",
                           now: datetime | None = None) -> int:
    """Insert a user prediction. Refused once the match has started."""
    now = now or datetime.now(UTC)
    pick = pick.upper()
    if pick not in ("H", "D", "A"):
        raise PredictionRefused("pick must be H, D or A")
    if not 1 <= confidence <= 5:
        raise PredictionRefused("confidence must be between 1 and 5")
    if (home_goals is None) != (away_goals is None):
        raise PredictionRefused("give both goal numbers or none")
    if home_goals is not None:
        implied = "H" if home_goals > away_goals else "A" if home_goals < away_goals else "D"
        if implied != pick:
            raise PredictionRefused(f"score {home_goals}-{away_goals} contradicts pick {pick}")
    with session_scope(engine) as s:
        match = s.get(Match, match_id)
        if match is None:
            raise PredictionRefused(f"match {match_id} does not exist")
        if match.status != "scheduled" or now >= kickoff_deadline(match.kickoff_utc,
                                                                  match.kickoff_date):
            raise PredictionRefused("the match has started or finished: predictions are frozen")
        up = UserPrediction(match_id=match_id, user_label=user_label, pick=pick,
                            confidence=confidence, home_goals=home_goals, away_goals=away_goals,
                            over_2_5=over_2_5, btts=btts, reasoning=reasoning, submitted_at=now)
        s.add(up)
        s.flush()
        return up.id
