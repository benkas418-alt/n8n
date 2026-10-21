"""Calls the REAL sources to check that the columns and envelopes we rely on still exist.

Run with: pytest -m live
"""

import httpx
import pytest

from footintel.config import get_settings
from footintel.connectors.football_data_uk import BASE_URL, parse_csv, season_url

pytestmark = pytest.mark.live

REQUIRED_SEASON_COLUMNS = {"Div", "Date", "Time", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR",
                           "HS", "AS", "HST", "AST", "AvgH", "AvgD", "AvgA", "Avg>2.5", "Avg<2.5"}


def _get(url: str) -> httpx.Response:
    return httpx.get(url, follow_redirects=True, timeout=20,
                     headers={"User-Agent": get_settings().user_agent})


@pytest.mark.parametrize("div", ["E0", "SP1", "I1", "D1"])
def test_football_data_last_complete_season_has_required_columns(div):
    r = _get(season_url(2025, div))
    assert r.status_code == 200
    text = r.content.decode("utf-8-sig")
    header = set(text.splitlines()[0].split(","))
    assert REQUIRED_SEASON_COLUMNS <= header, REQUIRED_SEASON_COLUMNS - header
    records = parse_csv(text, season_start_year=2025)
    assert len(records) >= 300 and all(r.outcome is not None for r in records)


def test_football_data_fixtures_file_is_reachable():
    r = _get(f"{BASE_URL}/fixtures.csv")
    assert r.status_code == 200
    assert {"Div", "Date", "HomeTeam", "AwayTeam"} <= set(
        r.content.decode("utf-8-sig").splitlines()[0].split(","))


def test_api_football_envelope():
    """Without a key the API answers 403 with its standard envelope (seen 2026-10-21)."""
    settings = get_settings()
    headers = {}
    if settings.api_football_enabled:
        headers["x-apisports-key"] = settings.api_football_key.get_secret_value()
    r = httpx.get(f"{settings.api_football_base_url}/status", headers=headers, timeout=20)
    body = r.json()
    assert {"get", "parameters", "errors", "results", "paging", "response"} <= set(body)
    if not settings.api_football_enabled:
        assert r.status_code == 403 and "token" in body["errors"]
