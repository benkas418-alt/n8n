"""Integration tests on a real PostgreSQL test database, with SYNTHETIC data only."""

from datetime import UTC, date, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from footintel.config import PromotionCriteria
from footintel.connectors.base import MatchRecord, OddsRecord, OutcomeRecord
from footintel.db.models import (
    CollectionRun,
    Match,
    MatchOutcome,
    ModelVersion,
    OddsSnapshot,
    Prediction,
    PredictionEvaluation,
)
from footintel.db.session import session_scope
from footintel.features.builder import build_features
from footintel.features.dataset import load_matches
from footintel.ingestion import tasks
from footintel.jobs import JobAlreadyRunning, acquire_lock, release_lock
from footintel.models import registry
from footintel.postmatch.evaluate import evaluate_finished
from footintel.predictions.service import (
    PredictionRefused,
    predict_upcoming,
    submit_user_prediction,
)
from footintel.reports.daily import postmatch_report, prematch_report

from .conftest import FakeConnector, synthetic_season_records

LOW_BAR = PromotionCriteria(min_test_matches=20, min_logloss_improvement=-1.0,
                            require_ci_below_zero=False, bootstrap_samples=100)


def _count(engine, model) -> int:
    with session_scope(engine) as s:
        return s.scalar(select(func.count()).select_from(model))


def test_history_import_is_idempotent(db, settings):
    conn = FakeConnector({2020: synthetic_season_records(2020), 2021: synthetic_season_records(2021)})
    first = tasks.import_history(db, settings, 2020, 2021, ["ENG-PL"], connector=conn)
    second = tasks.import_history(db, settings, 2020, 2021, ["ENG-PL"], connector=conn)
    assert first.inserted == 112 and second.inserted == 0 and second.skipped == 112
    assert _count(db, Match) == 112 and _count(db, MatchOutcome) == 112
    assert _count(db, OddsSnapshot) == 112 * 3
    with session_scope(db) as s:
        runs = s.scalars(select(CollectionRun).order_by(CollectionRun.id)).all()
        assert [r.status for r in runs] == ["success", "success"]


def test_uncovered_competition_is_reported_not_faked(db, settings):
    st = tasks.import_history(db, settings, 2020, 2020, ["UEFA-CL"], connector=FakeConnector({}))
    assert st.inserted == 0 and any(code == "not_covered" for _, code, *_ in st.issues)


def test_rescheduled_fixture_updates_the_same_match(db, settings):
    rec = MatchRecord("football_data_uk", "E0|2030|Synthetic FC 0|Synthetic FC 1", "ENG-PL", 2030,
                      date(2030, 9, 1), None, "Synthetic FC 0", "Synthetic FC 1", "scheduled")
    tasks.sync_fixtures(db, settings, connector=FakeConnector({}, [rec]))
    rec.kickoff_date = date(2030, 9, 8)
    st = tasks.sync_fixtures(db, settings, connector=FakeConnector({}, [rec]))
    assert st.updated == 1 and _count(db, Match) == 1
    with session_scope(db) as s:
        assert s.scalars(select(Match)).one().kickoff_date == date(2030, 9, 8)


def test_job_lock_blocks_a_second_instance(db):
    owner = acquire_lock(db, "demo_job", timedelta(minutes=5))
    with pytest.raises(JobAlreadyRunning):
        acquire_lock(db, "demo_job", timedelta(minutes=5))
    release_lock(db, "demo_job", owner, "success")
    owner2 = acquire_lock(db, "demo_job", timedelta(minutes=5))
    release_lock(db, "demo_job", owner2, "success")
    # An expired lock (crashed process) can be taken over.
    acquire_lock(db, "stale_job", timedelta(seconds=-1))
    release_lock(db, "stale_job", acquire_lock(db, "stale_job", timedelta(minutes=1)), "success")


def _load_synthetic_history(db, settings, seasons=(2018, 2019, 2020, 2021, 2022)):
    conn = FakeConnector({y: synthetic_season_records(y, n_teams=10) for y in seasons})
    tasks.import_history(db, settings, min(seasons), max(seasons), ["ENG-PL"], connector=conn)


def test_end_to_end_prediction_loop(db, settings):
    """Acceptance path: import -> features -> train -> promote -> predict -> user pick
    -> result -> evaluation -> report -> second version -> rollback."""
    _load_synthetic_history(db, settings)
    feats = build_features(load_matches(db))
    v1 = registry.train_version(db, settings, feats, "logreg_market_goals")
    decision = registry.promote(db, feats, v1, [2021, 2022], LOW_BAR)
    assert decision.promoted, decision.reason

    now = datetime.now(UTC).replace(microsecond=0)
    kickoff = now + timedelta(days=2)
    fixture = MatchRecord(
        "football_data_uk", "E0|2023|Synthetic FC 1|Synthetic FC 2", "ENG-PL", 2023,
        kickoff.date(), kickoff, "Synthetic FC 1", "Synthetic FC 2", "scheduled",
        odds=[OddsRecord("market_avg", "1X2", s, p, "fixtures@test", now - timedelta(hours=1))
              for s, p in zip("HDA", (2.1, 3.4, 3.6), strict=True)])
    tasks.sync_fixtures(db, settings, connector=FakeConnector({}, [fixture]))

    first = predict_upcoming(db, settings, now=now)
    again = predict_upcoming(db, settings, now=now + timedelta(minutes=5))
    assert first.created == 1 and again.unchanged == 1
    with session_scope(db) as s:
        pred = s.scalars(select(Prediction)).one()
        assert abs(pred.p_home + pred.p_draw + pred.p_away - 1) < 1e-9
        assert pred.p_over_2_5 is not None and pred.feature_snapshot["odds_1x2"] == [2.1, 3.4, 3.6]
        assert pred.sufficient_data is True and pred.predicted_at < kickoff
        match_id = pred.match_id

    up_id = submit_user_prediction(db, match_id, "H", 4, home_goals=2, away_goals=1,
                                   over_2_5=True, btts=True, reasoning="test", now=now)
    assert up_id > 0
    with pytest.raises(PredictionRefused):
        submit_user_prediction(db, match_id, "A", 3, now=kickoff + timedelta(minutes=1))
    with pytest.raises(PredictionRefused):
        submit_user_prediction(db, match_id, "A", 3, home_goals=2, away_goals=0, now=now)

    # Out-of-distribution inputs (synthetic odds have a near-constant margin) must not
    # produce near-certain probabilities.
    assert max(pred.p_home, pred.p_draw, pred.p_away) < 0.95
    pre = prematch_report(db, settings, today=now.date()).markdown
    assert "| Synthetic FC 1 – Synthetic FC 2 |" in pre

    # The match is played: the result arrives with the next results sync.
    fixture.status, fixture.outcome = "finished", OutcomeRecord(2, 1, "H")
    tasks.sync_fixtures(db, settings, connector=FakeConnector({}, [fixture]))
    ev = evaluate_finished(db)
    assert ev.model_rows == 3 and ev.market_rows == 1 and ev.user_rows == 3
    assert evaluate_finished(db).model_rows == 0  # idempotent
    with session_scope(db) as s:
        row = s.scalars(select(PredictionEvaluation).where(
            PredictionEvaluation.predictor_kind == "model",
            PredictionEvaluation.market == "1X2")).one()
        assert row.log_loss > 0 and row.probability_of_outcome == pytest.approx(pred.p_home)

    report = postmatch_report(db, settings, kickoff.date() - timedelta(days=1), kickoff.date())
    assert "Synthetic FC 1" in report.markdown and report.paths["html"].exists()
    assert "trop petit pour conclure" in report.markdown

    # A second version that passes the bar replaces v1, and rollback restores v1.
    v2 = registry.train_version(db, settings, feats, "logreg_core_goals")
    registry.promote(db, feats, v2, [2021, 2022],
                     PromotionCriteria(min_test_matches=20, min_logloss_improvement=-1.0,
                                       require_ci_below_zero=False, bootstrap_samples=50))
    restored = registry.rollback(db)
    assert restored.id == v1
    with session_scope(db) as s:
        statuses = dict(s.execute(select(ModelVersion.id, ModelVersion.status)).all())
    assert statuses == {v1: "active", v2: "retired"}


def test_strict_criteria_reject_and_keep_the_active_model(db, settings):
    _load_synthetic_history(db, settings)
    feats = build_features(load_matches(db))
    v1 = registry.train_version(db, settings, feats, "logreg_market_goals")
    registry.promote(db, feats, v1, [2021, 2022], LOW_BAR)
    v2 = registry.train_version(db, settings, feats, "elo_poisson")
    # 180 test matches are below this predefined minimum, whatever the gain.
    strict = PromotionCriteria(min_test_matches=1000, min_logloss_improvement=0.002,
                               require_ci_below_zero=True, bootstrap_samples=100)
    decision = registry.promote(db, feats, v2, [2021, 2022], strict)
    assert not decision.promoted and "test matches" in decision.reason
    with session_scope(db) as s:
        assert s.get(ModelVersion, v1).status == "active"
        assert s.get(ModelVersion, v2).status == "rejected"


def test_no_active_model_means_no_prediction(db, settings):
    _load_synthetic_history(db, settings, seasons=(2020, 2021))
    assert predict_upcoming(db, settings).created == 0


def test_artifact_tampering_is_detected(db, settings):
    _load_synthetic_history(db, settings, seasons=(2020, 2021, 2022))
    feats = build_features(load_matches(db))
    vid = registry.train_version(db, settings, feats, "elo_poisson")
    with session_scope(db) as s:
        mv = s.get(ModelVersion, vid)
    with open(mv.artifact_path, "ab") as f:
        f.write(b"tampered")
    with pytest.raises(RuntimeError, match="checksum"):
        registry.load_model(mv)


def test_api_write_needs_the_admin_token(db, settings, monkeypatch):
    from footintel import config
    from footintel.api import app as api_module
    from footintel.db import session as session_module

    monkeypatch.setattr(config, "get_settings", lambda: settings)
    monkeypatch.setattr(api_module, "get_settings", lambda: settings)
    monkeypatch.setattr(api_module, "get_engine", lambda: db)
    monkeypatch.setattr(session_module, "get_engine", lambda url=None: db)
    client = TestClient(api_module.app)
    assert client.get("/health").status_code == 200
    body = {"match_id": 999, "pick": "H", "confidence": 3}
    assert client.post("/api/user-predictions", json=body).status_code == 401
    r = client.post("/api/user-predictions", json=body,
                    headers={"Authorization": "Bearer test-token"})
    assert r.status_code == 409 and "does not exist" in r.json()["detail"]
    assert client.get("/api/status").json()["api_football_configured"] is False


class FakeOpenFootball:
    def __init__(self, files: dict[tuple[int, str], str]):
        self.files = files

    def fetch(self, start_year, filename, *, current_season):
        from footintel.connectors.http import SourceUnavailable
        from footintel.connectors.openfootball import parse_txt

        if (start_year, filename) not in self.files:
            raise SourceUnavailable("404")
        return parse_txt(self.files[(start_year, filename)], filename, start_year)


def test_european_import_maps_names_and_merges_manual_aliases(db, settings, monkeypatch, tmp_path):
    from footintel.db.models import Team
    from footintel.ingestion import teams as teams_mod

    # Domestic history gives the canonical names "Synthetic FC 0" ... "Synthetic FC 9".
    _load_synthetic_history(db, settings, seasons=(2020,))
    txt = """= UEFA Champions League 2020/21

▪ League, Matchday 1
  Tue Sep 15 2020
    21:00  Synthetic FC 1 (ENG)    v Synthetic Rovers (ENG)   2-0 (1-0)
"""
    conn = FakeOpenFootball({(2020, "cl.txt"): txt})
    alias_file = tmp_path / "aliases.csv"
    alias_file.write_text("source,alias,team\n", encoding="utf-8")
    monkeypatch.setattr(teams_mod, "ALIAS_FILE", alias_file)
    monkeypatch.setattr(teams_mod.load_manual_aliases, "__defaults__", (alias_file,))

    st = tasks.import_european(db, settings, 2020, 2020, connector=conn)
    assert st.inserted == 1
    assert any(code == "unmapped_team" for _, code, *_ in st.issues)
    assert any(code == "season_not_published" for _, code, *_ in st.issues)
    with session_scope(db) as s:
        assert s.scalars(select(Team).where(Team.name == "Synthetic Rovers (ENG)")).one()

    # A human adds the alias: the next run merges the placeholder into the real team.
    alias_file.write_text("source,alias,team\nopenfootball,Synthetic Rovers (ENG),Synthetic FC 7\n",
                          encoding="utf-8")
    st2 = tasks.import_european(db, settings, 2020, 2020, connector=conn)
    assert st2.inserted == 0
    with session_scope(db) as s:
        assert s.scalars(select(Team).where(Team.name == "Synthetic Rovers (ENG)")).first() is None
        m = s.scalars(select(Match).where(Match.competition.has(code="UEFA-CL"))).one()
        assert m.away_team.name == "Synthetic FC 7" and m.home_team.name == "Synthetic FC 1"


def test_prematch_sheet_lists_missing_data_instead_of_inventing_it(db, settings):
    from footintel.reports.fiche import match_sheet_markdown

    _load_synthetic_history(db, settings, seasons=(2020,))
    with session_scope(db) as s:
        match_id = s.scalars(select(Match.id).order_by(Match.kickoff_date.desc())).first()
    md = match_sheet_markdown(db, match_id)
    assert "Non disponible" in md and "formations" in md and "xG" in md
    assert "pressing haut" not in md.lower()
