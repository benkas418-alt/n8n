"""Pre-match features computed only from information known before each match.

Input: one row per match with columns
    match_id, kickoff_date, season, home_team_id, away_team_id,
    home_goals, away_goals (NaN if not played),
    home_shots, away_shots, home_sot, away_sot (NaN if missing),
    odds_h, odds_d, odds_a (pre-match 1X2 prices, NaN if missing).
Output: the same rows with feature columns added.

Matches are processed in date order. All matches of one day get features from
the state at the end of the previous day; the state is then updated with that
day's results. A match never sees a result from its own day or later.
"""

from collections import deque
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from footintel.features import elo as elo_mod

FORM_FEATURES = [
    "form5_ppg", "form10_ppg", "gf5", "ga5", "venue5_ppg",
    "shots5_for", "shots5_against", "sot5_for", "sot5_against", "rest_days", "n_prior",
]
MARKET_FEATURES = ["mkt_p_home", "mkt_p_draw", "mkt_p_away", "mkt_overround"]
ELO_FEATURES = ["elo_home", "elo_away", "elo_diff"]


def side_features(prefix: str) -> list[str]:
    return [f"{name}_{prefix}" for name in FORM_FEATURES]


ALL_FEATURES = ELO_FEATURES + side_features("h") + side_features("a") + MARKET_FEATURES

REST_CAP_DAYS = 30


@dataclass
class TeamState:
    elo: float
    season: int | None = None
    last_date: pd.Timestamp | None = None
    n: int = 0
    # (points, goals_for, goals_against, shots_for, shots_against, sot_for, sot_against)
    recent: deque = field(default_factory=lambda: deque(maxlen=10))
    home_points: deque = field(default_factory=lambda: deque(maxlen=5))
    away_points: deque = field(default_factory=lambda: deque(maxlen=5))


def _mean(values) -> float:
    vals = [v for v in values if v is not None and not np.isnan(v)]
    return float(np.mean(vals)) if vals else np.nan


def _side(state: TeamState | None, is_home: bool, on: pd.Timestamp) -> dict[str, float]:
    if state is None or state.n == 0:
        out = {name: np.nan for name in FORM_FEATURES}
        out["n_prior"] = 0.0
        return out
    recent = list(state.recent)
    last5 = recent[-5:]
    venue = state.home_points if is_home else state.away_points
    rest = (on - state.last_date).days if state.last_date is not None else np.nan
    return {
        "form5_ppg": _mean(r[0] for r in last5),
        "form10_ppg": _mean(r[0] for r in recent),
        "gf5": _mean(r[1] for r in last5),
        "ga5": _mean(r[2] for r in last5),
        "venue5_ppg": _mean(venue) if venue else np.nan,
        "shots5_for": _mean(r[3] for r in last5),
        "shots5_against": _mean(r[4] for r in last5),
        "sot5_for": _mean(r[5] for r in last5),
        "sot5_against": _mean(r[6] for r in last5),
        "rest_days": float(min(rest, REST_CAP_DAYS)) if not np.isnan(rest) else np.nan,
        "n_prior": float(state.n),
    }


def market_probabilities(odds_h, odds_d, odds_a) -> dict[str, float]:
    """Proportional removal of the bookmaker margin. Raw 1/odds sum is the overround."""
    if any(o is None or np.isnan(o) or o <= 1.0 for o in (odds_h, odds_d, odds_a)):
        return {k: np.nan for k in MARKET_FEATURES}
    inv = np.array([1 / odds_h, 1 / odds_d, 1 / odds_a])
    total = inv.sum()
    p = inv / total
    return {"mkt_p_home": p[0], "mkt_p_draw": p[1], "mkt_p_away": p[2], "mkt_overround": total}


def build_features(matches: pd.DataFrame, params: elo_mod.EloParams | None = None) -> pd.DataFrame:
    params = params or elo_mod.EloParams()
    df = matches.copy()
    df["kickoff_date"] = pd.to_datetime(df["kickoff_date"])
    df = df.sort_values(["kickoff_date", "match_id"]).reset_index(drop=True)
    first_season = int(df["season"].min()) if len(df) else 0

    teams: dict[int, TeamState] = {}
    feature_rows: list[dict] = []

    def state_for(team_id: int, season: int) -> TeamState:
        st = teams.get(team_id)
        if st is None:
            start = params.initial if season == first_season else params.newcomer
            st = teams[team_id] = TeamState(elo=start, season=season)
        elif st.season != season:
            st.elo = params.initial + params.season_carry * (st.elo - params.initial)
            st.season = season
        return st

    for day, group in df.groupby("kickoff_date", sort=True):
        # 1) Features for every match of the day, from yesterday's state.
        for row in group.itertuples(index=False):
            season = int(row.season)
            h = state_for(int(row.home_team_id), season)
            a = state_for(int(row.away_team_id), season)
            feats = {"match_id": row.match_id, "elo_home": h.elo, "elo_away": a.elo,
                     "elo_diff": h.elo - a.elo}
            for k, v in _side(h, True, day).items():
                feats[f"{k}_h"] = v
            for k, v in _side(a, False, day).items():
                feats[f"{k}_a"] = v
            feats.update(market_probabilities(row.odds_h, row.odds_d, row.odds_a))
            feature_rows.append(feats)

        # 2) Update the state with the day's results.
        for row in group.itertuples(index=False):
            if np.isnan(row.home_goals) or np.isnan(row.away_goals):
                continue
            hg, ag = int(row.home_goals), int(row.away_goals)
            h, a = teams[int(row.home_team_id)], teams[int(row.away_team_id)]
            h.elo, a.elo = elo_mod.update(h.elo, a.elo, hg, ag, params)
            hp = 3 if hg > ag else 1 if hg == ag else 0
            ap = 3 if ag > hg else 1 if hg == ag else 0
            h.recent.append((hp, hg, ag, row.home_shots, row.away_shots, row.home_sot, row.away_sot))
            a.recent.append((ap, ag, hg, row.away_shots, row.home_shots, row.away_sot, row.home_sot))
            h.home_points.append(hp)
            a.away_points.append(ap)
            for st in (h, a):
                st.n += 1
                st.last_date = day

    feats = pd.DataFrame(feature_rows)
    return df.merge(feats, on="match_id", how="left")


def result_label(home_goals: float, away_goals: float) -> str | None:
    if np.isnan(home_goals) or np.isnan(away_goals):
        return None
    return "H" if home_goals > away_goals else "D" if home_goals == away_goals else "A"
