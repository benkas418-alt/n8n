"""Bilan (D76): what the tickets and the forecasts of the last days gave.

Each morning the cycle archives the day's tickets (`archive`). The Bilan settles them with the
scores, and with the goal order for first goal, 1UP, 2UP and the double chance with early
payout. It also compares, match by match, the favourite of the model and of the bookmakers
with the result.
"""

import json
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

from sqlalchemy import Engine, text

ARCHIVE = "tickets_archive.json"
KEEP_DAYS = 60


def archive(artifacts_dir, payload: dict, today: date) -> int:
    """Keep the tickets of `today` (first version of the day wins). Returns tickets kept."""
    path = Path(artifacts_dir) / ARCHIVE
    data = json.loads(path.read_text()) if path.exists() else {}
    day = next((d for d in payload.get("days", []) if d["date"] == today.isoformat()), None)
    if day is None or today.isoformat() in data:
        return 0
    data[today.isoformat()] = {"tickets": day["tickets"]}
    cutoff = (today - timedelta(days=KEEP_DAYS)).isoformat()
    data = {k: v for k, v in data.items() if k >= cutoff}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, default=str))
    return len(day["tickets"])


def settle(key: str, hg: int, ag: int, goals: list[str] | None) -> int | None:
    """1 won, 0 lost, None unknown. `goals`: "H"/"A" in order, None when not known."""
    res = "1" if hg > ag else "X" if hg == ag else "2"
    if key in ("1", "X", "2"):
        return int(key == res)
    if key in ("1X", "X2", "12"):
        return int(res in key)
    if key[0] in "+-":
        over = hg + ag > float(key[1:])
        return int(over == (key[0] == "+"))
    if key in ("BTTS_Y", "BTTS_N"):
        return int((hg > 0 and ag > 0) == (key == "BTTS_Y"))
    kind, sel = key.split("_")
    if kind == "FG":
        if hg + ag == 0:
            return 0
        if goals is None or len(goals) != hg + ag:
            return None
        return int(goals[0] == ("H" if sel == "1" else "A"))
    need = 2 if kind in ("2UP", "DC2UP") else 1
    if kind in ("1UP", "2UP"):
        side_wins = (hg > ag) if sel == "1" else (ag > hg)
        if side_wins:
            return 1
        scored = hg if sel == "1" else ag
        if scored < need:
            return 0
        if goals is None or len(goals) != hg + ag:
            return None
        return int(_best_lead(goals, "H" if sel == "1" else "A") >= need)
    # DC1UP / DC2UP: the double chance on the final score, or a covered side leading by `need`.
    if res in sel:
        return 1
    if goals is None or len(goals) != hg + ag:
        return None
    covered = {"1X": "H", "X2": "A", "12": "HA"}[sel]
    return int(any(_best_lead(goals, s) >= need for s in covered))


def _best_lead(goals: list[str], side: str) -> int:
    lead = best = 0
    for g in goals:
        lead += 1 if g == side else -1
        best = max(best, lead)
    return best


def _results(conn, ids: list[int]) -> dict[int, dict]:
    if not ids:
        return {}
    rows = conn.execute(text("""
        SELECT o.match_id, o.home_goals, o.away_goals,
               (SELECT array_agg(CASE WHEN e.team_id = m.home_team_id THEN 'H' ELSE 'A' END
                                 ORDER BY e.minute, coalesce(e.extra_minute, 0), e.id)
                FROM match_events e WHERE e.match_id = o.match_id AND e.type = 'goal') AS goals
        FROM match_outcomes o JOIN matches m ON m.id = o.match_id
        WHERE o.match_id = ANY(:ids) AND o.home_goals IS NOT NULL"""), {"ids": ids}).all()
    out = {}
    for r in rows:
        goals = list(r.goals) if r.goals else ([] if r.home_goals + r.away_goals == 0 else None)
        out[r.match_id] = {"hg": r.home_goals, "ag": r.away_goals, "goals": goals}
    return out


def ticket_results(engine: Engine, artifacts_dir, days: int = 7, today: date | None = None) -> list[dict]:
    path = Path(artifacts_dir) / ARCHIVE
    if not path.exists():
        return []
    today = today or datetime.now(UTC).date()
    data = json.loads(path.read_text())
    keep = sorted((k for k in data if k >= (today - timedelta(days=days)).isoformat()), reverse=True)
    ids = sorted({leg["match_id"] for k in keep for t in data[k]["tickets"] for leg in t["legs"]})
    with engine.connect() as conn:
        res = _results(conn, ids)
    out = []
    for k in keep:
        tickets = []
        for t in data[k]["tickets"]:
            legs = []
            for leg in t["legs"]:
                r = res.get(leg["match_id"])
                won = settle(leg["key"], r["hg"], r["ag"], r["goals"]) if r else None
                legs.append({"match": leg["match"], "label": leg["label"], "price": leg["price"],
                             "score": f"{r['hg']}-{r['ag']}" if r else None, "won": won})
            state = ("perdu" if any(x["won"] == 0 for x in legs) else
                     "gagné" if all(x["won"] == 1 for x in legs) else "en cours")
            tickets.append({"tag": t["tag"], "name": t["name"], "odds": t["odds"], "state": state,
                            "right": sum(x["won"] == 1 for x in legs), "legs": legs})
        out.append({"date": k, "tickets": tickets})
    return out


def _market(conn, match_id: int) -> tuple[float, float, float] | None:
    """Bookmakers' 1X2 without margin: Pinnacle or the average at the close, else the latest
    The Odds API snapshot averaged over its books."""
    rows = conn.execute(text("""SELECT o.bookmaker, o.snapshot_label, o.selection, o.price, d.code
        FROM odds_snapshots o JOIN data_sources d ON d.id = o.source_id
        WHERE o.match_id = :m AND o.market = '1X2'"""), {"m": match_id}).all()
    by: dict = {}
    for book, lab, sel, price, src in rows:
        by.setdefault((book, lab, src == "the_odds_api"), {})[sel] = price

    def fair(p):
        if {"H", "D", "A"} - p.keys() or min(p.values()) <= 1:
            return None
        inv = [1 / p[k] for k in "HDA"]
        return tuple(x / sum(inv) for x in inv)

    for want in (("pinnacle", "closing"), ("market_avg", "closing"), ("pinnacle", "pre_closing"),
                 ("market_avg", "pre_closing")):
        for (b, lab, api), p in by.items():
            if (b, lab) == want and not api and (f := fair(p)):
                return f
    api = [(lab, fair(p)) for (b, lab, a), p in by.items() if a]
    api = [x for x in api if x[1]]
    if not api:
        return None
    last = max(lab for lab, _ in api)
    probs = [p for lab, p in api if lab == last]
    return tuple(sum(p[i] for p in probs) / len(probs) for i in range(3))


def forecast_results(engine: Engine, days: int = 7, today: date | None = None,
                     competitions: tuple[str, ...] | None = None) -> list[dict]:
    """Finished matches of the last days: the model's and the bookmakers' favourite, and the result."""
    today = today or datetime.now(UTC).date()
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT DISTINCT ON (m.id) m.id, m.kickoff_date, c.code AS competition, th.name AS home, ta.name AS away,
                   o.home_goals, o.away_goals, p.p_home, p.p_draw, p.p_away
            FROM matches m JOIN match_outcomes o ON o.match_id = m.id
            JOIN competitions c ON c.id = m.competition_id
            JOIN teams th ON th.id = m.home_team_id JOIN teams ta ON ta.id = m.away_team_id
            JOIN predictions p ON p.match_id = m.id
            WHERE m.kickoff_date BETWEEN :a AND :b AND o.home_goals IS NOT NULL AND c.is_target
              AND (CAST(:comps AS text[]) IS NULL OR c.code = ANY(CAST(:comps AS text[])))
              AND (m.kickoff_utc IS NULL OR p.predicted_at <= m.kickoff_utc)
            ORDER BY m.id, p.predicted_at DESC"""),
            {"a": today - timedelta(days=days), "b": today,
             "comps": list(competitions) if competitions else None}).all()
        out = []
        for r in rows:
            res = 0 if r.home_goals > r.away_goals else 1 if r.home_goals == r.away_goals else 2
            model = (r.p_home, r.p_draw, r.p_away)
            mk = _market(conn, r.id)
            pick = lambda p: max(range(3), key=lambda i: p[i])
            out.append({"date": r.kickoff_date.isoformat(), "competition": r.competition, "home": r.home,
                        "away": r.away, "score": f"{r.home_goals}-{r.away_goals}", "result": res,
                        "model": [round(x, 3) for x in model], "model_right": pick(model) == res,
                        "market": [round(x, 3) for x in mk] if mk else None,
                        "market_right": (pick(mk) == res) if mk else None})
    return sorted(out, key=lambda x: (x["date"], x["home"]), reverse=True)
