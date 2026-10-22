"""Ingestion tasks. Each one runs alone, is locked, logged and safe to re-run."""

import logging
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import Engine, func, select

from footintel.catalog import COMPETITIONS, FD_NEW, FOOTBALL_DATA, OPENFOOTBALL, get_source
from footintel.config import Settings
from footintel.connectors.base import season_start_for
from footintel.connectors.football_data_uk import NEW_TO_COMPETITION, FootballDataUK
from footintel.connectors.openfootball import FILE_TO_COMPETITION, OpenFootball
from footintel.connectors.http import SourceUnavailable
from footintel.db.models import Match, MatchOutcome, OddsSnapshot, TeamMatchStatistics
from footintel.db.session import session_scope
from footintel.ingestion.store import MatchStore
from footintel.ingestion.teams import apply_manual_aliases, backfill_team_countries
from footintel.jobs import RunStats, tracked_run

log = logging.getLogger(__name__)

FD_DIVS = {c.code: c.source_codes[FOOTBALL_DATA] for c in COMPETITIONS
           if FOOTBALL_DATA in c.source_codes and not c.source_codes[FOOTBALL_DATA].startswith(FD_NEW)}
TARGET_LEAGUES = [c.code for c in COMPETITIONS if c.code in FD_DIVS and c.is_target]
CONTEXT_LEAGUES = [c.code for c in COMPETITIONS
                   if FOOTBALL_DATA in c.source_codes and not c.is_target]


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
    comps = competitions or TARGET_LEAGUES
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


def import_context_leagues(engine: Engine, settings: Settings, first_season: int,
                           last_season: int | None = None,
                           connector: FootballDataUK | None = None) -> RunStats:
    """Leagues used only to rate clubs met in European cups (France, Portugal...)."""
    current = season_start_for(date.today())
    last_season = current if last_season is None else last_season
    connector = connector or FootballDataUK(settings)
    with tracked_run(engine, "import_context_leagues", source_id=_source_id(engine, FOOTBALL_DATA),
                     params={"first_season": first_season, "last_season": last_season}) as stats:
        jobs: list[tuple[str, object]] = []
        for comp in CONTEXT_LEAGUES:
            div = next(c.source_codes[FOOTBALL_DATA] for c in COMPETITIONS if c.code == comp)
            if div.startswith(FD_NEW):
                country = div.removeprefix(FD_NEW)
                jobs.append((comp, lambda country=country: [
                    r for r in connector.fetch_country(country, first_season)
                    if r.season_start_year <= last_season]))
            else:
                for y in range(first_season, last_season + 1):
                    jobs.append((f"{comp} {y}", lambda y=y, div=div: connector.fetch_season(
                        y, div, current_season=y >= current)))
        for label, fetch in jobs:
            try:
                records = fetch()
            except (SourceUnavailable, ValueError) as exc:
                stats.issue("error", "download_failed", f"{label}: {exc}")
                continue
            with session_scope(engine) as s:
                store = MatchStore(s, FOOTBALL_DATA)
                for rec in records:
                    store.upsert(rec, stats)
            log.info("%s: %d rows", label, len(records))
        with session_scope(engine) as s:
            backfill_team_countries(s)
    return stats


def import_european(engine: Engine, settings: Settings, first_season: int = 2011,
                    last_season: int | None = None,
                    connector: OpenFootball | None = None) -> RunStats:
    """UEFA results from openfootball. A missing season file is reported, not invented."""
    current = season_start_for(date.today())
    last_season = current if last_season is None else last_season
    connector = connector or OpenFootball(settings)
    source_id = _source_id(engine, OPENFOOTBALL)
    with tracked_run(engine, "import_european", source_id=source_id,
                     params={"first_season": first_season, "last_season": last_season}) as stats:
        with session_scope(engine) as s:
            backfill_team_countries(s)
            merged = apply_manual_aliases(s, source_id, OPENFOOTBALL)
            if merged:
                stats.issue("info", "aliases_merged", f"{merged} team(s) merged from manual aliases")
        for y in range(first_season, last_season + 1):
            for filename, comp in FILE_TO_COMPETITION.items():
                try:
                    records = connector.fetch(y, filename, current_season=y >= current - 1)
                except SourceUnavailable:
                    stats.issue("info", "season_not_published", f"{comp} {y}: no file at the source")
                    continue
                with session_scope(engine) as s:
                    store = MatchStore(s, OPENFOOTBALL)
                    for rec in records:
                        store.upsert(rec, stats)
                log.info("%s %d: %d rows", comp, y, len(records))
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

            # Only seasons whose source normally publishes statistics (more than half of
            # the matches have them). Sources without statistics are not an anomaly.
            covered = (
                select(Match.season_id)
                .outerjoin(TeamMatchStatistics, TeamMatchStatistics.match_id == Match.id)
                .group_by(Match.season_id)
                .having(func.count(TeamMatchStatistics.id) > func.count(func.distinct(Match.id)))
            )
            no_stats = s.execute(
                select(Match.id)
                .join(MatchOutcome, MatchOutcome.match_id == Match.id)
                .outerjoin(TeamMatchStatistics, TeamMatchStatistics.match_id == Match.id)
                .where(Match.season_id.in_(covered))
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
