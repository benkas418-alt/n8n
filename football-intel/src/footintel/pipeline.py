"""Daily and weekly cycles. Each step is independent: one failure does not stop the others."""

import logging
from datetime import date, timedelta

from sqlalchemy import Engine

from footintel.config import Settings
from footintel.connectors.base import season_start_for
from footintel.features.builder import build_features
from footintel.features.dataset import load_matches
from footintel.ingestion import tasks
from footintel.jobs import JobAlreadyRunning, acquire_lock, release_lock
from footintel.models import registry
from footintel.postmatch.evaluate import evaluate_finished
from footintel.predictions.service import predict_upcoming
from footintel.reports.daily import postmatch_report, prematch_report

log = logging.getLogger(__name__)

DEFAULT_DEPLOY_MODEL = "logreg_market_goals"


def _step(name: str, fn, results: dict) -> None:
    try:
        results[name] = fn()
        log.info("Step %s: ok", name)
    except JobAlreadyRunning as exc:
        results[name] = f"skipped: {exc}"
        log.warning("Step %s skipped: %s", name, exc)
    except Exception as exc:  # noqa: BLE001 - a failed step is logged and reported
        results[name] = f"failed: {exc}"
        log.exception("Step %s failed", name)


def morning(engine: Engine, settings: Settings) -> dict:
    """Fixtures and odds, then predictions and the pre-match report."""
    results: dict = {}
    _step("sync_fixtures", lambda: tasks.sync_fixtures(engine, settings), results)
    _step("predict", lambda: predict_upcoming(engine, settings), results)
    _step("prematch_report", lambda: prematch_report(engine, settings).paths, results)
    return results


def evening(engine: Engine, settings: Settings) -> dict:
    """Results and statistics, evaluation and the post-match report.

    Results files are re-downloaded at every run, so late statistics are picked up."""
    results: dict = {}
    _step("sync_results", lambda: tasks.sync_results(engine, settings), results)
    _step("evaluate", lambda: evaluate_finished(engine), results)
    yesterday = date.today() - timedelta(days=1)
    _step("postmatch_report",
          lambda: postmatch_report(engine, settings, yesterday - timedelta(days=6), date.today()).paths,
          results)
    return results


def nightly(engine: Engine, settings: Settings) -> dict:
    results: dict = {}
    _step("check_data_quality", lambda: tasks.check_data_quality(engine), results)
    return results


def weekly(engine: Engine, settings: Settings, model_name: str = DEFAULT_DEPLOY_MODEL,
           n_test_seasons: int = 3) -> dict:
    """Retrain a candidate and promote it only if it passes the promotion criteria."""
    results: dict = {}
    owner = acquire_lock(engine, "weekly_retrain", timedelta(hours=6))
    status = "success"
    try:
        feats = build_features(load_matches(engine))
        current = season_start_for(date.today())
        test_seasons = list(range(current - n_test_seasons, current))
        version_id = registry.train_version(engine, settings, feats, model_name)
        decision = registry.promote(engine, feats, version_id, test_seasons, settings.promotion)
        results["retrain"] = {"version_id": version_id, "promoted": decision.promoted,
                              "reason": decision.reason}
    except Exception:
        status = "failed"
        raise
    finally:
        release_lock(engine, "weekly_retrain", owner, status)
    return results
