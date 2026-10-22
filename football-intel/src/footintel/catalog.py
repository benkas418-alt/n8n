"""Static catalog of sources and competitions, and its idempotent seeding.

Add a competition here and run `footintel db seed`. No schema change is needed.
"""

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from footintel.db.models import Competition, CompetitionSourceCode, DataSource

FOOTBALL_DATA = "football_data_uk"
API_FOOTBALL = "api_football"
OPENFOOTBALL = "openfootball"


@dataclass(frozen=True)
class SourceDef:
    code: str
    name: str
    kind: str
    base_url: str
    terms_url: str
    terms_note: str


@dataclass(frozen=True)
class CompetitionDef:
    code: str
    name: str
    country: str | None
    type: str
    # External code per source. A missing key means the source does not cover it.
    source_codes: dict[str, str]
    # Context leagues are imported only to rate the clubs met in European cups.
    is_target: bool = True
    # Starting Elo of a club in this league (assumption, see docs/DECISIONS.md D14).
    elo_prior: float = 1500.0
    # Three-letter code used by openfootball, e.g. "ENG" in "Arsenal FC (ENG)".
    country_code: str | None = None


SOURCES = [
    SourceDef(
        code=FOOTBALL_DATA,
        name="Football-Data.co.uk",
        kind="csv",
        base_url="https://www.football-data.co.uk",
        terms_url="https://www.football-data.co.uk/disclaimer.php",
        terms_note=(
            "Free CSV files. Leagues only (no cups, no UEFA competitions). "
            "Odds are pre-closing and closing prices without an exact capture time."
        ),
    ),
    SourceDef(
        code=API_FOOTBALL,
        name="API-Football (api-sports.io)",
        kind="api",
        base_url="https://v3.football.api-sports.io",
        terms_url="https://www.api-football.com/terms",
        terms_note="Needs an API key (header x-apisports-key). Quotas depend on the plan.",
    ),
    SourceDef(
        code=OPENFOOTBALL,
        name="openfootball (champions-league repository)",
        kind="text",
        base_url="https://github.com/openfootball/champions-league",
        terms_url="https://github.com/openfootball/football.json#license",
        terms_note=(
            "Public domain. UEFA results only, from 2011-12 (CL), 2020-21 (EL), 2021-22 "
            "(Conference League). No current season, no odds, no statistics."
        ),
    ),
]

# API-Football league ids are not listed here: they must be read from the
# /leagues endpoint with a real key before use (see docs/DATA_SOURCES.md).
FD_NEW = "new:"  # prefix for football-data.co.uk files under /new/ (one file per country)

COMPETITIONS = [
    CompetitionDef("ENG-PL", "Premier League", "England", "league", {FOOTBALL_DATA: "E0"},
                   country_code="ENG"),
    CompetitionDef("ENG-FAC", "FA Cup", "England", "cup", {}, country_code="ENG"),
    CompetitionDef("ENG-EFL", "EFL Cup", "England", "cup", {}, country_code="ENG"),
    CompetitionDef("ESP-LL", "La Liga", "Spain", "league", {FOOTBALL_DATA: "SP1"},
                   country_code="ESP"),
    CompetitionDef("ESP-CDR", "Copa del Rey", "Spain", "cup", {}, country_code="ESP"),
    CompetitionDef("ITA-SA", "Serie A", "Italy", "league", {FOOTBALL_DATA: "I1"},
                   country_code="ITA"),
    CompetitionDef("ITA-CI", "Coppa Italia", "Italy", "cup", {}, country_code="ITA"),
    CompetitionDef("GER-BL", "Bundesliga", "Germany", "league", {FOOTBALL_DATA: "D1"},
                   country_code="GER"),
    CompetitionDef("GER-DFB", "DFB-Pokal", "Germany", "cup", {}, country_code="GER"),
    CompetitionDef("UEFA-CL", "UEFA Champions League", None, "continental",
                   {OPENFOOTBALL: "cl.txt"}),
    CompetitionDef("UEFA-EL", "UEFA Europa League", None, "continental",
                   {OPENFOOTBALL: "el.txt"}),
    CompetitionDef("UEFA-ECL", "UEFA Conference League", None, "continental",
                   {OPENFOOTBALL: "conf.txt"}),
    # Context leagues: domestic form of clubs met in European cups. Not predicted.
    CompetitionDef("FRA-L1", "Ligue 1", "France", "league", {FOOTBALL_DATA: "F1"},
                   is_target=False, elo_prior=1480, country_code="FRA"),
    CompetitionDef("NED-ERE", "Eredivisie", "Netherlands", "league", {FOOTBALL_DATA: "N1"},
                   is_target=False, elo_prior=1440, country_code="NED"),
    CompetitionDef("POR-PL", "Primeira Liga", "Portugal", "league", {FOOTBALL_DATA: "P1"},
                   is_target=False, elo_prior=1450, country_code="POR"),
    CompetitionDef("BEL-PRO", "Pro League", "Belgium", "league", {FOOTBALL_DATA: "B1"},
                   is_target=False, elo_prior=1420, country_code="BEL"),
    CompetitionDef("TUR-SL", "Süper Lig", "Turkey", "league", {FOOTBALL_DATA: "T1"},
                   is_target=False, elo_prior=1410, country_code="TUR"),
    CompetitionDef("SCO-PREM", "Scottish Premiership", "Scotland", "league",
                   {FOOTBALL_DATA: "SC0"}, is_target=False, elo_prior=1380, country_code="SCO"),
    CompetitionDef("GRE-SL", "Super League Greece", "Greece", "league", {FOOTBALL_DATA: "G1"},
                   is_target=False, elo_prior=1380, country_code="GRE"),
    CompetitionDef("AUT-BL", "Austrian Bundesliga", "Austria", "league",
                   {FOOTBALL_DATA: FD_NEW + "AUT"}, is_target=False, elo_prior=1390,
                   country_code="AUT"),
    CompetitionDef("SUI-SL", "Swiss Super League", "Switzerland", "league",
                   {FOOTBALL_DATA: FD_NEW + "SWZ"}, is_target=False, elo_prior=1390,
                   country_code="SUI"),
    CompetitionDef("DEN-SL", "Danish Superliga", "Denmark", "league",
                   {FOOTBALL_DATA: FD_NEW + "DNK"}, is_target=False, elo_prior=1370,
                   country_code="DEN"),
    CompetitionDef("NOR-ES", "Eliteserien", "Norway", "league", {FOOTBALL_DATA: FD_NEW + "NOR"},
                   is_target=False, elo_prior=1340, country_code="NOR"),
    CompetitionDef("SWE-AS", "Allsvenskan", "Sweden", "league", {FOOTBALL_DATA: FD_NEW + "SWE"},
                   is_target=False, elo_prior=1340, country_code="SWE"),
    CompetitionDef("POL-EK", "Ekstraklasa", "Poland", "league", {FOOTBALL_DATA: FD_NEW + "POL"},
                   is_target=False, elo_prior=1340, country_code="POL"),
]

COMPETITION_BY_CODE = {c.code: c for c in COMPETITIONS}
COUNTRY_BY_CODE = {c.country_code: c.country for c in COMPETITIONS if c.country_code and c.country}


def seed_catalog(session: Session) -> dict[str, int]:
    """Insert or update sources and competitions. Safe to run many times."""
    created = {"sources": 0, "competitions": 0, "codes": 0}
    sources: dict[str, DataSource] = {}
    for sdef in SOURCES:
        src = session.scalar(select(DataSource).where(DataSource.code == sdef.code))
        if src is None:
            src = DataSource(code=sdef.code)
            session.add(src)
            created["sources"] += 1
        src.name, src.kind, src.base_url = sdef.name, sdef.kind, sdef.base_url
        src.terms_url, src.terms_note = sdef.terms_url, sdef.terms_note
        sources[sdef.code] = src
    session.flush()

    for cdef in COMPETITIONS:
        comp = session.scalar(select(Competition).where(Competition.code == cdef.code))
        if comp is None:
            comp = Competition(code=cdef.code)
            session.add(comp)
            created["competitions"] += 1
        comp.name, comp.country, comp.type = cdef.name, cdef.country, cdef.type
        comp.is_target = cdef.is_target
        session.flush()
        for source_code, external in cdef.source_codes.items():
            src = sources[source_code]
            exists = session.scalar(
                select(CompetitionSourceCode).where(
                    CompetitionSourceCode.source_id == src.id,
                    CompetitionSourceCode.external_code == external,
                )
            )
            if exists is None:
                session.add(
                    CompetitionSourceCode(
                        competition_id=comp.id, source_id=src.id, external_code=external
                    )
                )
                created["codes"] += 1
    session.flush()
    return created


def get_source(session: Session, code: str) -> DataSource:
    src = session.scalar(select(DataSource).where(DataSource.code == code))
    if src is None:
        raise LookupError(f"Source {code!r} is not seeded. Run `footintel db seed`.")
    return src
