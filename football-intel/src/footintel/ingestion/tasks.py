"""Ingestion tasks. Each one runs alone, is locked, logged and safe to re-run."""

import logging
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import Engine, func, select

from footintel.catalog import COMPETITIONS, FOOTBALL_DATA, get_source
from footintel.config import Settings
from footintel.connectors.base import season_start_for
from footintel.connectors.football_data_uk import FootballDataUK
from footintel.connectors.http import SourceUnavailable
from footintel.db.models import Match, MatchOutcome, OddsSnapshot, TeamMatchStatistics
from footintel.db.session import session_scope
from footintel.ingestion.store import MatchStore
from footintel.jobs import RunStats, tracked_run

log = logging.getLogger(__name__)

FD_DIVS = {c.code: c.source_codes[FOOTBALL_DATA] for c in COMPETITIONS
           if FOOTBALL_DATA in c.source_codes}


def _source_id(engine: Engine, code: str) -> int:
    with session_scope(engine) as s:
        return get_source(s, code).id


def import_history(
    engine: Engine,
    settings: Settings,
    first_season: int,
    last_season: int | None = None,
    competitions: list[str] | None = None,
    connector: FootballDataUK | None = None,
) -> RunStats:
    """Import football-data.co.uk season files. A failed file is logged, others continue."""
    current = season_start_for(date.today())
    last_season = current if last_season is None else last_season
    comps = competitions or list(FD_DIVS)
    connector = connector or FootballDataUK(settings)
    params = {"first_season": first_season, "last_season": last_season, "competitions": comps}
    with tracked_run(engine, "import_history", source_id=_source_id(engine, FOOTBALL_DATA),
                     params=params) as stats:
        for start_year in range(first_season, last_season + 1):
            for comp in comps:
                div = FD_DIVS.get(comp)
                if div is None:
                    stats.issue("info", "not_covered", f"{comp} is not covered by football-data.co.uk")
                    continue
                try:
                    records = connector.fetch_season(start_year, div,
                                                     current_season=start_year >= current)
                except (SourceUnavailable, ValueError) as exc:
                    stats.issue("error", "download_failed", f"{comp} {start_year}: {exc}")
                    continue
                # One transaction per file: a bad file never leaves half-written rows.
                with session_scope(engine) as s:
                    store = MatchStore(s, FOOTBALL_DATA)
                    for rec in records:
                        store.upsert(rec, stats)
                log.info("%s %d: %d rows", comp, start_year, len(records))
    return stats


def sync_fixtures(engine: Engine, settings: Settings,
                  connector: FootballDataUK | None = None) -> RunStats:
    """Fetch upcoming matches and their current odds."""
    connector = connector or FootballDataUK(settings)
    with tracked_run(engine, "sync_fixtures", source_id=_source_id(engine, FOOTBALL_DATA)) as stats:
        records = connector.fetch_fixtures()
        with session_scope(engine) as s:
            store = MatchStore(s, FOOTBALL_DATA)
            for rec in records:
                store.upsert(rec, stats)
        if not records:
            stats.issue("info", "no_fixtures", "fixtures.csv has no match for tracked leagues")
    return stats


def sync_results(engine: Engine, settings: Settings,
                 connector: FootballDataUK | None = None) -> RunStats:
    """Refresh the current season files to pick up final results and statistics."""
    current = season_start_for(date.today())
    return import_history(engine, settings, current, current, connector=connector)


def check_data_quality(engine: Engine) -> RunStats:
    """Find missing results, missing statistics and impossible states."""
    today = date.today()
    with tracked_run(engine, "check_data_quality") as stats:
        with session_scope(engine) as s:
            overdue = s.execute(
                select(Match.id, Match.kickoff_date)
                .outerjoin(MatchOutcome, MatchOutcome.match_id == Match.id)
                .where(MatchOutcome.id.is_(None), Match.kickoff_date < today - timedelta(days=2))
            ).all()
            for match_id, d in overdue:
                stats.issue("warning", "missing_result",
                            f"match {match_id} on {d} has no result after 2 days", match_id)

            no_stats = s.execute(
                select(Match.id)
                .join(MatchOutcome, MatchOutcome.match_id == Match.id)
                .outerjoin(TeamMatchStatistics, TeamMatchStatistics.match_id == Match.id)
                .group_by(Match.id)
                .having(func.count(TeamMatchStatistics.id) < 2)
            ).scalars().all()
            for match_id in no_stats:
                stats.issue("info", "missing_team_stats", f"match {match_id} lacks team statistics",
                            match_id)

            future_results = s.execute(
                select(Match.id)
                .join(MatchOutcome, MatchOutcome.match_id == Match.id)
                .where(Match.kickoff_date > today)
            ).scalars().all()
            for match_id in future_results:
                stats.issue("error", "result_before_kickoff",
                            f"match {match_id} has a result but kicks off in the future", match_id)

            # An overround below 1 means the 1X2 prices are inconsistent.
            rows = s.execute(
                select(OddsSnapshot.match_id, OddsSnapshot.snapshot_label,
                       func.sum(1.0 / OddsSnapshot.price), func.count())
                .where(OddsSnapshot.market == "1X2", OddsSnapshot.bookmaker == "market_avg")
                .group_by(OddsSnapshot.match_id, OddsSnapshot.snapshot_label)
            ).all()
            for match_id, label, inv_sum, n in rows:
                if n == 3 and not (0.98 <= inv_sum <= 1.30):
                    stats.issue("warning", "odd_overround",
                                f"match {match_id} {label}: sum(1/odds)={inv_sum:.3f}", match_id)
        log.info("Quality check at %s", datetime.now(UTC).isoformat(timespec="seconds"))
    return stats
