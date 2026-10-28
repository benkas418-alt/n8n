"""Ingestion tasks. Each one runs alone, is locked, logged and safe to re-run."""

import logging
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import Engine, func, select

from footintel.catalog import (COMPETITIONS, FD_NEW, FOOTBALL_DATA, FOOTBALL_DATA_ORG,
                               FOOTBALL_DATA_ORG_COMPETITIONS, OPENFOOTBALL, OPENLIGADB,
                               ODDS_API_SPORTS, OPENLIGADB_LEAGUES, THE_ODDS_API, get_source)
from footintel.config import Settings
from footintel.connectors.base import season_start_for
from footintel.connectors.football_data_uk import NEW_TO_COMPETITION, FootballDataUK
from footintel.connectors.openfootball import FILE_TO_COMPETITION, OpenFootball
from footintel.connectors.football_data_org import UEFA_TZ, FootballDataOrg
from footintel.connectors.openligadb import OpenLigaDB
from footintel.connectors.the_odds_api import TheOddsApi
from footintel.connectors.http import SourceUnavailable
from footintel.db.models import Competition, Match, MatchOutcome, OddsSnapshot, Team, TeamMatchStatistics
from footintel.db.session import session_scope
from footintel.ingestion.store import MatchStore, remove_stale_matches
from footintel.ingestion import teams as teams_mod
from footintel.ingestion.teams import apply_manual_aliases, backfill_team_countries, similarity
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
                    # Only when the file was read completely: never on an empty answer.
                    if records:
                        remove_stale_matches(s, source_id, f"{filename}|{y}|",
                                             {r.external_id for r in records}, stats)
                log.info("%s %d: %d rows", comp, y, len(records))
    return stats


def import_openligadb(engine: Engine, settings: Settings, seasons: list[int] | None = None,
                      connector: OpenLigaDB | None = None, jitter_seconds: float = 0.0) -> RunStats:
    """Current-season UEFA cups and DFB-Pokal from OpenLigaDB (fixtures and results).

    Fair use (openligadb.de/nutzungsbedingungen): one full request per league, twice a
    day, started at a random second, with backoff on 429 and 5xx (HttpClient)."""
    if jitter_seconds:
        import random
        import time

        time.sleep(random.uniform(0, jitter_seconds))
    current = season_start_for(date.today())
    seasons = seasons or [current]
    connector = connector or OpenLigaDB(settings)
    source_id = _source_id(engine, OPENLIGADB)
    with tracked_run(engine, "import_openligadb", source_id=source_id,
                     params={"seasons": seasons}) as stats:
        with session_scope(engine) as s:
            merged = apply_manual_aliases(s, source_id, OPENLIGADB)
            if merged:
                stats.issue("info", "aliases_merged", f"{merged} team(s) merged from manual aliases")
        for y in seasons:
            leagues = OPENLIGADB_LEAGUES.get(y)
            if not leagues:
                stats.issue("warning", "league_not_mapped",
                            f"OpenLigaDB {y}: no league shortcut chosen (catalog.OPENLIGADB_LEAGUES)")
                continue
            for comp, shortcut in leagues.items():
                try:
                    records = connector.fetch(comp, y)
                except SourceUnavailable as exc:
                    stats.issue("warning", "source_unavailable", f"{comp} {y}: {exc}")
                    continue
                with session_scope(engine) as s:
                    store = MatchStore(s, OPENLIGADB)
                    for rec in records:
                        store.upsert(rec, stats)
                    if records:
                        remove_stale_matches(s, source_id, f"{shortcut}|{y}|",
                                             {r.external_id for r in records}, stats)
                log.info("OpenLigaDB %s %d: %d rows", comp, y, len(records))
    return stats


def check_football_data_org(engine: Engine, settings: Settings, seasons: list[int] | None = None,
                            connector: FootballDataOrg | None = None) -> RunStats:
    """Check and complete Champions League matches with football-data.org.

    Runs after the OpenLigaDB import: it only attaches to matches that exist, fills
    results that were missing or rejected, and logs every score disagreement."""
    current = season_start_for(date.today())
    seasons = seasons or [current]
    source_id = _source_id(engine, FOOTBALL_DATA_ORG)
    with tracked_run(engine, "check_football_data_org", source_id=source_id,
                     params={"seasons": seasons}) as stats:
        if connector is None and not settings.football_data_org_enabled:
            stats.issue("info", "source_disabled", "FOOTBALL_DATA_ORG_KEY is not set: check skipped")
            return stats
        connector = connector or FootballDataOrg(settings)
        for y in seasons:
            for comp in FOOTBALL_DATA_ORG_COMPETITIONS:
                try:
                    records = connector.fetch(comp, y)
                except SourceUnavailable as exc:
                    stats.issue("warning", "source_unavailable", f"{comp} {y}: {exc}")
                    continue
                with session_scope(engine) as s:
                    store = MatchStore(s, FOOTBALL_DATA_ORG)
                    for rec in records:
                        store.upsert(rec, stats)
                log.info("football-data.org %s %d: %d rows", comp, y, len(records))
    return stats


def _odds_api_team(session, name: str, aliases: dict[str, str], cache: dict) -> int | None:
    if name not in cache:
        cache[name] = session.scalar(select(Team.id).where(Team.name == aliases.get(name, "")))
    return cache[name]


def _closest_team(session, competition_id: int, name: str) -> str:
    """Closest team name among this season's teams of the competition, for alias review."""
    since = date.today() - timedelta(days=400)
    ids = session.scalars(select(Match.home_team_id).where(
        Match.competition_id == competition_id, Match.kickoff_date >= since).union(
        select(Match.away_team_id).where(Match.competition_id == competition_id,
                                         Match.kickoff_date >= since))).all()
    names = session.scalars(select(Team.name).where(Team.id.in_(ids))).all()
    best = max(names, key=lambda n: similarity(name, n), default=None)
    return f", closest {best!r} at {similarity(name, best):.2f}" if best else ""


def sync_odds_api(engine: Engine, settings: Settings, connector: TheOddsApi | None = None) -> RunStats:
    """1X2 prices of upcoming cup matches from The Odds API.

    Attach only: it never creates a team or a match and never changes a match. Team names
    go through aliases checked by a human. The prices are kept under each bookmaker's own
    name, so the active model does not read them (see docs/DECISIONS.md D49)."""
    source_id = _source_id(engine, THE_ODDS_API)
    with tracked_run(engine, "sync_odds_api", source_id=source_id) as stats:
        if connector is None and not settings.odds_api_enabled:
            stats.issue("info", "source_disabled", "ODDS_API_KEY is not set: odds skipped")
            return stats
        connector = connector or TheOddsApi(settings)
        try:
            active = connector.active_sports()
        except SourceUnavailable as exc:
            stats.issue("warning", "source_unavailable", str(exc))
            return stats
        aliases = {a: t for (src, a), t in teams_mod.load_manual_aliases().items() if src == THE_ODDS_API}
        for comp, sport in ODDS_API_SPORTS.items():
            if sport not in active:
                stats.issue("info", "not_in_season", f"{sport}: not active, no credit spent")
                continue
            if connector.remaining is not None and connector.remaining < settings.odds_api_reserve:
                stats.issue("warning", "quota_low",
                            f"{connector.remaining} credits left (reserve {settings.odds_api_reserve}): stopped")
                break
            try:
                events = connector.odds(sport)
            except SourceUnavailable as exc:
                stats.issue("warning", "source_unavailable", f"{sport}: {exc}")
                continue
            with session_scope(engine) as s:
                competition = s.scalar(select(Competition).where(Competition.code == comp))
                cache: dict = {}
                for ev in events:
                    ids = [_odds_api_team(s, n, aliases, cache) for n in (ev.home_team, ev.away_team)]
                    for n, team_id in zip((ev.home_team, ev.away_team), ids):
                        if team_id is None:
                            stats.issue("warning", "unmapped_team", f"{comp} {n!r}: no manual alias"
                                        + _closest_team(s, competition.id, n))
                    if None in ids or not ev.odds:
                        stats.skipped += 1
                        continue
                    day = ev.commence_utc.astimezone(UEFA_TZ).date()
                    match_id = s.scalar(select(Match.id).where(
                        Match.competition_id == competition.id, Match.home_team_id == ids[0],
                        Match.away_team_id == ids[1], Match.status == "scheduled",
                        Match.kickoff_date.between(day - timedelta(days=2), day + timedelta(days=2))))
                    if match_id is None:
                        stats.issue("info", "match_not_found",
                                    f"{comp} {ev.home_team} - {ev.away_team} {day}: no scheduled match")
                        stats.skipped += 1
                        continue
                    seen = set(s.execute(select(OddsSnapshot.bookmaker, OddsSnapshot.selection).where(
                        OddsSnapshot.match_id == match_id, OddsSnapshot.source_id == source_id,
                        OddsSnapshot.snapshot_label == ev.odds[0].snapshot_label)).all())
                    new = [o for o in ev.odds if (o.bookmaker, o.selection) not in seen]
                    s.add_all(OddsSnapshot(match_id=match_id, source_id=source_id, bookmaker=o.bookmaker,
                                           market=o.market, selection=o.selection, price=o.price,
                                           snapshot_label=o.snapshot_label, captured_at=o.captured_at)
                              for o in new)
                    if new:
                        stats.inserted += 1
                    else:
                        stats.skipped += 1
            log.info("the-odds-api %s: %d events, %s credits left", sport, len(events), connector.remaining)
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

            ht_over_ft = s.execute(
                select(MatchOutcome.match_id).where(
                    (MatchOutcome.ht_home_goals > MatchOutcome.home_goals)
                    | (MatchOutcome.ht_away_goals > MatchOutcome.away_goals))
            ).scalars().all()
            for match_id in ht_over_ft:
                stats.issue("error", "ht_exceeds_ft",
                            f"match {match_id}: half-time score above the 90-minute score", match_id)

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
