"""Write normalized MatchRecords to the database. Idempotent by (source, external_id)."""

from sqlalchemy import select
from sqlalchemy.orm import Session

import re

from footintel.catalog import COUNTRY_BY_CODE, OPENFOOTBALL, get_source
from footintel.connectors.base import MatchRecord, season_label
from footintel.db.models import (
    Competition,
    Match,
    MatchExternalRef,
    MatchOutcome,
    OddsSnapshot,
    Season,
    Team,
    TeamAlias,
    TeamMatchStatistics,
)
from footintel.ingestion.teams import TeamResolver
from footintel.jobs import RunStats

_STAT_FIELDS = ("shots", "shots_on_target", "corners", "fouls", "yellow_cards", "red_cards", "xg")


class MatchStore:
    """Holds lookup caches for one ingestion batch inside one session."""

    def __init__(self, session: Session, source_code: str):
        self.s = session
        self.source = get_source(session, source_code)
        # Names from openfootball must be mapped onto the football-data.co.uk teams.
        self.resolver = TeamResolver(session, source_code) if source_code == OPENFOOTBALL else None
        self._competitions = {c.code: c for c in session.scalars(select(Competition))}
        self._seasons = {(x.competition_id, x.label): x for x in session.scalars(select(Season))}
        self._aliases = {
            a.alias: a.team_id
            for a in session.scalars(select(TeamAlias).where(TeamAlias.source_id == self.source.id))
        }
        self._refs = dict(
            session.execute(
                select(MatchExternalRef.external_id, MatchExternalRef.match_id).where(
                    MatchExternalRef.source_id == self.source.id
                )
            ).all()
        )

    def _team_id(self, name: str, rec: MatchRecord, competition: Competition,
                 stats: RunStats) -> int:
        if name in self._aliases:
            return self._aliases[name]
        canonical, country = name, competition.country
        if self.resolver is not None:
            m = re.search(r"\(([A-Z]{3})\)$", name)
            country = COUNTRY_BY_CODE.get(m[1]) if m else None
            res = self.resolver.resolve(name, rec.season_start_year)
            if res.team_name:
                canonical = res.team_name
            else:
                stats.issue("info", "unmapped_team",
                            f"{name} ({rec.season_start_year}): no safe match"
                            + (f", closest {res.runner_up!r} at {res.score:.2f}" if res.runner_up else ""))
        team = self.s.scalar(select(Team).where(Team.name == canonical))
        if team is None:
            team = Team(name=canonical, country=country)
            self.s.add(team)
            self.s.flush()
        elif team.country is None and country:
            team.country = country
        self.s.add(TeamAlias(team_id=team.id, source_id=self.source.id, alias=name))
        self._aliases[name] = team.id
        return team.id

    def _season(self, competition: Competition, start_year: int) -> Season:
        key = (competition.id, season_label(start_year))
        if key not in self._seasons:
            season = Season(competition_id=competition.id, label=key[1], start_year=start_year)
            self.s.add(season)
            self.s.flush()
            self._seasons[key] = season
        return self._seasons[key]

    def upsert(self, rec: MatchRecord, stats: RunStats) -> int:
        competition = self._competitions[rec.competition_code]
        season = self._season(competition, rec.season_start_year)
        home_id = self._team_id(rec.home_team, rec, competition, stats)
        away_id = self._team_id(rec.away_team, rec, competition, stats)
        if home_id == away_id:
            stats.issue("error", "same_team", f"{rec.external_id}: both names map to one team")
            stats.skipped += 1
            return -1

        match_id = self._refs.get(rec.external_id)
        is_new = match_id is None
        changed = False
        if is_new:
            match = Match(
                competition_id=competition.id,
                season_id=season.id,
                home_team_id=home_id,
                away_team_id=away_id,
                kickoff_date=rec.kickoff_date,
                kickoff_utc=rec.kickoff_utc,
                status=rec.status,
                round=rec.round,
                neutral_venue=rec.neutral,
            )
            self.s.add(match)
            self.s.flush()
            match_id = match.id
            self.s.add(
                MatchExternalRef(match_id=match_id, source_id=self.source.id,
                                 external_id=rec.external_id)
            )
            self._refs[rec.external_id] = match_id
        else:
            match = self.s.get(Match, match_id)
            if match.kickoff_date != rec.kickoff_date or (
                rec.kickoff_utc is not None and match.kickoff_utc != rec.kickoff_utc
            ):
                match.kickoff_date = rec.kickoff_date
                match.kickoff_utc = rec.kickoff_utc or match.kickoff_utc
                changed = True
            if match.status != rec.status and rec.status in ("finished", "cancelled"):
                match.status = rec.status
                changed = True

        for code, message in rec.issues:
            stats.issue("warning", code, f"{rec.external_id}: {message}", match_id)

        if rec.outcome is not None:
            changed |= self._upsert_outcome(match_id, rec, is_new, stats)
            for team_id, is_home, st in ((home_id, True, rec.home_stats),
                                         (away_id, False, rec.away_stats)):
                if st is not None:
                    changed |= self._upsert_stats(match_id, team_id, is_home, st, is_new)
        changed |= self._upsert_odds(match_id, rec, is_new)

        if is_new:
            stats.inserted += 1
        elif changed:
            stats.updated += 1
        else:
            stats.skipped += 1
        return match_id

    def _upsert_outcome(self, match_id: int, rec: MatchRecord, is_new: bool, stats: RunStats) -> bool:
        o = rec.outcome
        existing = None if is_new else self.s.scalar(
            select(MatchOutcome).where(MatchOutcome.match_id == match_id)
        )
        values = dict(home_goals=o.home_goals, away_goals=o.away_goals, result=o.result,
                      ht_home_goals=o.ht_home_goals, ht_away_goals=o.ht_away_goals,
                      aet_home_goals=o.aet_home_goals, aet_away_goals=o.aet_away_goals,
                      pen_home=o.pen_home, pen_away=o.pen_away, is_final=o.is_final)
        if existing is None:
            self.s.add(MatchOutcome(match_id=match_id, source_id=self.source.id, **values))
            return True
        if (existing.home_goals, existing.away_goals) != (o.home_goals, o.away_goals):
            stats.issue("warning", "outcome_changed",
                        f"{rec.external_id}: {existing.home_goals}-{existing.away_goals} -> "
                        f"{o.home_goals}-{o.away_goals}", match_id)
        diff = any(getattr(existing, k) != v for k, v in values.items())
        for k, v in values.items():
            setattr(existing, k, v)
        return diff

    def _upsert_stats(self, match_id, team_id, is_home, st, is_new) -> bool:
        existing = None if is_new else self.s.scalar(
            select(TeamMatchStatistics).where(
                TeamMatchStatistics.match_id == match_id,
                TeamMatchStatistics.team_id == team_id,
                TeamMatchStatistics.source_id == self.source.id,
            )
        )
        values = {f: getattr(st, f) for f in _STAT_FIELDS}
        if existing is None:
            self.s.add(TeamMatchStatistics(match_id=match_id, team_id=team_id,
                                           source_id=self.source.id, is_home=is_home, **values))
            return True
        diff = any(getattr(existing, k) != v for k, v in values.items())
        for k, v in values.items():
            setattr(existing, k, v)
        return diff

    def _upsert_odds(self, match_id: int, rec: MatchRecord, is_new: bool) -> bool:
        existing = {}
        if not is_new:
            for o in self.s.scalars(select(OddsSnapshot).where(
                OddsSnapshot.match_id == match_id, OddsSnapshot.source_id == self.source.id
            )):
                existing[(o.bookmaker, o.market, o.selection, o.snapshot_label)] = o
        changed = False
        for odd in rec.odds:
            key = (odd.bookmaker, odd.market, odd.selection, odd.snapshot_label)
            row = existing.get(key)
            if row is None:
                self.s.add(OddsSnapshot(match_id=match_id, source_id=self.source.id,
                                        bookmaker=odd.bookmaker, market=odd.market,
                                        selection=odd.selection, price=odd.price,
                                        snapshot_label=odd.snapshot_label,
                                        captured_at=odd.captured_at))
                changed = True
            elif row.price != odd.price:
                row.price = odd.price
                changed = True
        return changed
