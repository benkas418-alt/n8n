"""Static catalog of sources and competitions, and its idempotent seeding.

Add a competition here (for example the Conference League) and run
`footintel db seed`. No schema change is needed.
"""

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from footintel.db.models import Competition, CompetitionSourceCode, DataSource

FOOTBALL_DATA = "football_data_uk"
API_FOOTBALL = "api_football"


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
]

# API-Football league ids are not listed here: they must be read from the
# /leagues endpoint with a real key before use (see docs/DATA_SOURCES.md).
COMPETITIONS = [
    CompetitionDef("ENG-PL", "Premier League", "England", "league", {FOOTBALL_DATA: "E0"}),
    CompetitionDef("ENG-FAC", "FA Cup", "England", "cup", {}),
    CompetitionDef("ENG-EFL", "EFL Cup", "England", "cup", {}),
    CompetitionDef("ESP-LL", "La Liga", "Spain", "league", {FOOTBALL_DATA: "SP1"}),
    CompetitionDef("ESP-CDR", "Copa del Rey", "Spain", "cup", {}),
    CompetitionDef("ITA-SA", "Serie A", "Italy", "league", {FOOTBALL_DATA: "I1"}),
    CompetitionDef("ITA-CI", "Coppa Italia", "Italy", "cup", {}),
    CompetitionDef("GER-BL", "Bundesliga", "Germany", "league", {FOOTBALL_DATA: "D1"}),
    CompetitionDef("GER-DFB", "DFB-Pokal", "Germany", "cup", {}),
    CompetitionDef("UEFA-CL", "UEFA Champions League", None, "continental", {}),
    CompetitionDef("UEFA-EL", "UEFA Europa League", None, "continental", {}),
]


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
