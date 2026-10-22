"""Command-line entry point: `footintel --help`."""

import argparse
import json
import logging
import subprocess
import sys
from datetime import UTC, date, datetime
from pathlib import Path

from sqlalchemy import select

from footintel.config import get_settings
from footintel.db.session import get_engine, session_scope
from footintel.logging_setup import configure_logging

log = logging.getLogger("footintel")


def _print(obj) -> None:
    print(json.dumps(obj, indent=2, default=str, ensure_ascii=False))


def _features(engine):
    from footintel.features.builder import build_features
    from footintel.features.dataset import load_matches

    return build_features(load_matches(engine))


def cmd_db(args, settings, engine):
    if args.action == "upgrade":
        subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], check=True)
    elif args.action == "seed":
        from footintel.catalog import seed_catalog

        with session_scope(engine) as s:
            _print(seed_catalog(s))
    elif args.action == "backup":
        out = Path(settings.data_dir) / "backups"
        out.mkdir(parents=True, exist_ok=True)
        target = out / f"footintel_{datetime.now(UTC):%Y%m%d_%H%M%S}.dump"
        url = engine.url.set(drivername="postgresql").render_as_string(hide_password=False)
        subprocess.run(["pg_dump", "--format=custom", f"--file={target}", url], check=True)
        print(f"Backup written to {target}")


def cmd_ingest(args, settings, engine):
    from footintel.ingestion import tasks

    if args.what == "history":
        st = tasks.import_history(engine, settings, args.first, args.last, args.competition)
    elif args.what == "context":
        st = tasks.import_context_leagues(engine, settings, args.first, args.last)
    elif args.what == "european":
        st = tasks.import_european(engine, settings, max(args.first, 2011), args.last)
    elif args.what == "openligadb":
        st = tasks.import_openligadb(engine, settings, [args.last] if args.last else None)
    elif args.what == "fixtures":
        st = tasks.sync_fixtures(engine, settings)
    elif args.what == "results":
        st = tasks.sync_results(engine, settings)
    else:
        st = tasks.check_data_quality(engine)
    _print({"inserted": st.inserted, "updated": st.updated, "unchanged": st.skipped,
            "issues": len(st.issues)})


def cmd_backtest(args, settings, engine):
    from footintel.evaluation.backtest import run_backtest

    feats = _features(engine)
    last = int(feats.loc[feats["home_goals"].notna(), "season"].max())
    # The current season is incomplete: test on the last N complete seasons.
    seasons = list(range(last - args.seasons, last))
    res = run_backtest(engine, feats, args.models, seasons, settings.promotion.bootstrap_samples)
    out = Path(settings.reports_dir)
    out.mkdir(parents=True, exist_ok=True)
    res.summary.to_csv(out / f"backtest_{res.run_id}_summary.csv", index=False)
    res.comparisons.to_csv(out / f"backtest_{res.run_id}_comparisons.csv", index=False)
    print(f"Backtest run {res.run_id} on seasons {seasons}")
    print(res.summary[res.summary["segment"] == "all"].round(4).to_string(index=False))
    print(res.comparisons.round(4).to_string(index=False))


def cmd_models(args, settings, engine):
    from footintel.db.models import ModelVersion
    from footintel.models import registry

    if args.action == "list":
        with session_scope(engine) as s:
            rows = s.scalars(select(ModelVersion).order_by(ModelVersion.id)).all()
            _print([{"id": m.id, "name": m.name, "version": m.version, "status": m.status,
                     "trained_until": m.trained_until, "n_train": m.n_train,
                     "decision": m.decision_note} for m in rows])
    elif args.action == "train":
        vid = registry.train_version(engine, settings, _features(engine), args.name)
        print(f"Candidate version id {vid}")
    elif args.action == "promote":
        feats = _features(engine)
        last = int(feats.loc[feats["home_goals"].notna(), "season"].max())
        seasons = list(range(last - args.seasons, last))
        d = registry.promote(engine, feats, args.version_id, seasons, settings.promotion)
        _print({"promoted": d.promoted, "reason": d.reason, "comparison": d.comparison})
    elif args.action == "rollback":
        mv = registry.rollback(engine)
        print(f"Active again: {mv.name} v{mv.version}")


def cmd_predict(args, settings, engine):
    from footintel.predictions.service import predict_upcoming

    _print(predict_upcoming(engine, settings, args.horizon).__dict__)


def cmd_user_predict(args, settings, engine):
    from footintel.predictions.service import submit_user_prediction

    hg = ag = None
    if args.score:
        hg, ag = (int(x) for x in args.score.split("-"))
    yes_no = {"yes": True, "no": False, None: None}
    pid = submit_user_prediction(engine, args.match_id, args.pick, args.confidence,
                                 home_goals=hg, away_goals=ag, over_2_5=yes_no[args.over25],
                                 btts=yes_no[args.btts], reasoning=args.reason)
    print(f"User prediction {pid} saved at {datetime.now(UTC):%Y-%m-%d %H:%M} UTC")


def cmd_evaluate(args, settings, engine):
    from footintel.postmatch.evaluate import evaluate_finished

    _print(evaluate_finished(engine).__dict__)


def cmd_report(args, settings, engine):
    from footintel.reports.daily import postmatch_report, prematch_report

    if args.kind == "fiche":
        from footintel.reports.fiche import match_sheet_markdown

        print(match_sheet_markdown(engine, args.match_id))
        return
    if args.kind == "prematch":
        rep = prematch_report(engine, settings, args.horizon)
    else:
        rep = postmatch_report(engine, settings, date.fromisoformat(args.start),
                               date.fromisoformat(args.end))
    print(rep.markdown)
    _print({k: str(v) for k, v in rep.paths.items()})


def cmd_upcoming(args, settings, engine):
    from sqlalchemy import text

    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT m.id, m.kickoff_date, m.kickoff_utc, c.code, th.name, ta.name
            FROM matches m JOIN competitions c ON c.id = m.competition_id
            JOIN teams th ON th.id = m.home_team_id JOIN teams ta ON ta.id = m.away_team_id
            WHERE m.status = 'scheduled' AND m.kickoff_date >= CURRENT_DATE
            ORDER BY m.kickoff_date, m.kickoff_utc LIMIT 100""")).all()
    _print([dict(zip(["match_id", "date", "kickoff_utc", "competition", "home", "away"], r,
                     strict=True)) for r in rows])


def cmd_status(args, settings, engine):
    from sqlalchemy import text

    with engine.connect() as conn:
        runs = conn.execute(text("""
            SELECT DISTINCT ON (job_name) job_name, status, started_at, rows_inserted,
                   rows_updated, error FROM collection_runs
            ORDER BY job_name, started_at DESC""")).mappings().all()
        counts = conn.execute(text("""
            SELECT (SELECT count(*) FROM matches) AS matches,
                   (SELECT count(*) FROM match_outcomes) AS results,
                   (SELECT count(*) FROM predictions) AS predictions,
                   (SELECT count(*) FROM user_predictions) AS user_predictions""")).mappings().one()
        active = conn.execute(text(
            "SELECT name, version, promoted_at FROM model_versions WHERE status='active'"
        )).mappings().all()
    _print({"api_football": "enabled" if settings.api_football_enabled
            else "disabled (no API_FOOTBALL_KEY): degraded mode on football-data.co.uk",
            "counts": dict(counts), "active_models": [dict(a) for a in active],
            "last_runs": [dict(r) for r in runs]})


def cmd_run(args, settings, engine):
    from footintel import pipeline

    _print(getattr(pipeline, args.cycle)(engine, settings))


def cmd_analyze(args, settings, engine):
    from footintel.analysis.ablation import compare_levels, run_ablation, store_ablation
    from footintel.analysis.competitions import run_analysis
    from footintel.reports.competitions import competition_report

    feats = _features(engine)
    last = int(feats.loc[feats["home_goals"].notna(), "season"].max()) - 1  # last complete
    res = run_analysis(engine, feats, args.split_season, last)
    comparisons = None
    if not args.skip_levels:
        comparisons = compare_levels(run_ablation(feats, list(range(last - 4, last + 1))))
        store_ablation(engine, comparisons)
    rep = competition_report(engine, settings, res["run_id"], comparisons)
    print(f"Analysis run {res['run_id']}: {len(res['tests'])} tests")
    print(res["tests"]["status"].value_counts().to_string())
    _print({k: str(v) for k, v in rep.paths.items()})


def cmd_trends(args, settings, engine):
    from footintel.reports.trends import trends_report

    if args.action == "run":
        from footintel.analysis.trend_engine import run_trends

        res = run_trends(engine, _features(engine))
        print(f"Trend run {res['run_id']}: {len(res['rows'])} rows")
        print(res["rows"].groupby(["population_type", "status"]).size().to_string())
    elif args.action == "evaluate":
        from footintel.analysis.trend_ablation import (compare_variants, run_trend_ablation,
                                                       store_trend_ablation)

        feats = _features(engine)
        last = int(feats.loc[feats["home_goals"].notna(), "season"].max()) - 1
        cmp = compare_variants(run_trend_ablation(feats, list(range(last - 4, last + 1))))
        print(f"Stored as run {store_trend_ablation(engine, cmp)}")
        print(cmp[cmp["verdict"] != "no demonstrated effect"].round(4).to_string(index=False))
    else:
        rep = trends_report(engine, settings, on=date.fromisoformat(args.date) if args.date else None,
                            competition=args.competition, team=args.team, category=args.category)
        print(rep.markdown)
        _print({k: str(v) for k, v in rep.paths.items()})


def cmd_hybrid(args, settings, engine):
    from footintel.analysis.hybrid import run_hybrid

    _print(run_hybrid(engine, args.user, settings.promotion))


def cmd_scheduler(args, settings, engine):
    from footintel.scheduler import run_scheduler

    run_scheduler(settings)


def cmd_serve(args, settings, engine):
    import uvicorn

    uvicorn.run("footintel.api.app:app", host=args.host, port=args.port)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="footintel", description="Football intelligence platform")
    p.add_argument("--log-level", default="INFO")
    sub = p.add_subparsers(dest="command", required=True)

    db = sub.add_parser("db", help="database: upgrade | seed | backup")
    db.add_argument("action", choices=["upgrade", "seed", "backup"])
    db.set_defaults(fn=cmd_db)

    ing = sub.add_parser("ingest", help="collect data")
    ing.add_argument("what", choices=["history", "context", "european", "openligadb", "fixtures",
                                      "results", "quality"])
    ing.add_argument("--first", type=int, default=2005, help="first season start year")
    ing.add_argument("--last", type=int, default=None, help="last season start year")
    ing.add_argument("--competition", action="append", help="e.g. ENG-PL (repeatable)")
    ing.set_defaults(fn=cmd_ingest)

    bt = sub.add_parser("backtest", help="chronological walk-forward backtest")
    bt.add_argument("--models", nargs="+", default=[
        "naive_frequency", "elo_poisson", "market_implied", "logreg_core", "logreg_market"])
    bt.add_argument("--seasons", type=int, default=5, help="number of complete test seasons")
    bt.set_defaults(fn=cmd_backtest)

    md = sub.add_parser("models", help="model registry")
    md_sub = md.add_subparsers(dest="action", required=True)
    md_sub.add_parser("list")
    tr = md_sub.add_parser("train")
    tr.add_argument("name")
    pr = md_sub.add_parser("promote")
    pr.add_argument("version_id", type=int)
    pr.add_argument("--seasons", type=int, default=3)
    md_sub.add_parser("rollback")
    md.set_defaults(fn=cmd_models)

    pd_ = sub.add_parser("predict", help="predict upcoming matches with the active model")
    pd_.add_argument("--horizon", type=int, default=7, help="days ahead")
    pd_.set_defaults(fn=cmd_predict)

    up = sub.add_parser("user-predict", help="save my own prediction (before kick-off)")
    up.add_argument("match_id", type=int)
    up.add_argument("pick", choices=["H", "D", "A", "h", "d", "a"])
    up.add_argument("confidence", type=int, choices=range(1, 6))
    up.add_argument("--score", help="e.g. 2-1")
    up.add_argument("--over25", choices=["yes", "no"])
    up.add_argument("--btts", choices=["yes", "no"])
    up.add_argument("--reason")
    up.set_defaults(fn=cmd_user_predict)

    sub.add_parser("evaluate", help="score predictions of finished matches").set_defaults(
        fn=cmd_evaluate)

    rp = sub.add_parser("report", help="generate a report")
    rp.add_argument("kind", choices=["prematch", "postmatch", "fiche"])
    rp.add_argument("--match-id", type=int, help="match for the pre-match sheet")
    rp.add_argument("--horizon", type=int, default=7)
    rp.add_argument("--start", default=str(date.today()))
    rp.add_argument("--end", default=str(date.today()))
    rp.set_defaults(fn=cmd_report)

    sub.add_parser("upcoming", help="list scheduled matches").set_defaults(fn=cmd_upcoming)
    sub.add_parser("status", help="sources, runs and active model").set_defaults(fn=cmd_status)

    rn = sub.add_parser("run", help="run one cycle now")
    rn.add_argument("cycle", choices=["morning", "evening", "nightly", "weekly"])
    rn.set_defaults(fn=cmd_run)

    an = sub.add_parser("analyze", help="competition trends and value of each analysis level")
    an.add_argument("--split-season", type=int, default=2021,
                    help="effects are estimated before this season and checked from it on")
    an.add_argument("--skip-levels", action="store_true", help="skip the level study (faster)")
    an.set_defaults(fn=cmd_analyze)

    tr_ = sub.add_parser("trends", help="trend engine: run | evaluate | report")
    tr_.add_argument("action", choices=["run", "evaluate", "report"])
    tr_.add_argument("--date", help="report as of this date (YYYY-MM-DD)")
    tr_.add_argument("--competition", help="e.g. ENG-PL")
    tr_.add_argument("--team", help="team name as in the database, e.g. 'Man City'")
    tr_.add_argument("--category", choices=["score", "team", "competition", "tactical"])
    tr_.set_defaults(fn=cmd_trends)

    hy = sub.add_parser("hybrid", help="evaluate the human + model hybrid (needs 200 picks)")
    hy.add_argument("--user", default="me")
    hy.set_defaults(fn=cmd_hybrid)

    sub.add_parser("scheduler", help="start the scheduler").set_defaults(fn=cmd_scheduler)

    sv = sub.add_parser("serve", help="start the HTTP API")
    sv.add_argument("--host", default="127.0.0.1")
    sv.add_argument("--port", type=int, default=8000)
    sv.set_defaults(fn=cmd_serve)
    return p


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    configure_logging(args.log_level)
    settings = get_settings()
    args.fn(args, settings, get_engine())


if __name__ == "__main__":
    main()
