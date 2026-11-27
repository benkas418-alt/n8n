"""D118: does betPawa (Cameroon) follow Pinnacle late in the last 90 minutes before kick-off?

Run from football-intel/: ODDS_PAPI_KEY=... python scripts/betpawa_lag.py
Spends 1 request per league for the fixtures (5 in all); the price histories are free
(one call every 5 seconds). Writes OUT_DIR/prices.csv (every 1X2 and 2UP price with its
time, for later checks) and prints the result.

The official line-ups come out about 60 to 75 minutes before kick-off. For each finished
match, with A = kick-off - 90 minutes and K = kick-off:
- p_pin(t), p_bp(t): fair 1X2 probabilities at time t (last price at or before t,
  margin removed by the power method, D114);
- the moved outcome: the one whose Pinnacle probability rose most between A and K;
- t_half: the first time Pinnacle has made half of that rise; the bet time is t_half + 5 min;
- EV = betPawa price at the bet time x Pinnacle's fair probability at K - 1.

Rule fixed before the run: a window exists if, on the matches where Pinnacle moved by
3 points or more, the mean EV at the bet time is above 0 with a 95 % bootstrap interval
entirely above 0, on 30 matches or more. The same EV at A (before the move) is the
comparison. The data is betPawa Cameroon: a window here is a reason to check betPawa
DR Congo, not a proof for it.
"""

import csv
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import httpx
import numpy as np

sys.path.insert(0, "src")
from footintel.analysis.demargin import fair_probs

BASE = "https://api.oddspapi.io/v4"
KEY = os.environ.get("ODDS_PAPI_KEY", "").strip()
OUT = Path(os.environ.get("OUT_DIR", "betpawa-lag"))
SINCE = os.environ.get("SINCE", "2026-08-01T00:00:00Z")
LEAGUES = {"Premier League": 17, "LaLiga": 8, "Serie A": 23, "Ligue 1": 34, "Bundesliga": 35}
BOOK, PIN = "betpawa.cm", "pinnacle"
M_1X2, M_2UP = "101", "10761"
MOVE, REACT = 0.03, timedelta(minutes=5)


def get(path: str, **params):
    for _ in range(8):
        r = httpx.get(f"{BASE}{path}", params={"apiKey": KEY, **params}, timeout=60)
        if r.status_code != 429:
            break
        time.sleep(float(r.json().get("error", {}).get("retryMs", 5000)) / 1000 + 0.5)
    if r.status_code >= 400:
        raise RuntimeError(f"{path}: HTTP {r.status_code} {r.text[:200].replace(KEY, '***')}")
    return r.json()


def ts(s: str) -> datetime:
    return datetime.fromisoformat(s[:19])


def series(market: dict) -> dict[str, list[tuple[datetime, float]]]:
    """Outcome id -> [(time, price)] sorted by time, active prices only."""
    out = {}
    for oid, o in market.get("outcomes", {}).items():
        rows = [(ts(h["createdAt"]), h["price"]) for h in o.get("players", {}).get("0", [])
                if h.get("price") and h["price"] > 1 and h.get("active", True)]
        out[oid] = sorted(rows)
    return out


def at(s: list[tuple[datetime, float]], t: datetime) -> float | None:
    last = None
    for when, price in s:
        if when > t:
            break
        last = price
    return last


def fair_at(ser: dict, order: list[str], t: datetime) -> list[float] | None:
    prices = [at(ser.get(o, []), t) for o in order]
    if None in prices:
        return None
    return fair_probs(prices)


def boot_ci(x: np.ndarray) -> tuple[float, float]:
    rng = np.random.default_rng(0)
    b = rng.choice(x, (4000, len(x))).mean(axis=1)
    return float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


def analyse(fx: dict, hist: dict, order: list[str], rows_out: list) -> dict | None:
    books = hist.get("bookmakers", {})
    pin = series(books.get(PIN, {}).get("markets", {}).get(M_1X2, {}))
    paw = series(books.get(BOOK, {}).get("markets", {}).get(M_1X2, {}))
    for book, mk in ((PIN, M_1X2), (BOOK, M_1X2), (BOOK, M_2UP)):
        for oid, s in series(books.get(book, {}).get("markets", {}).get(mk, {})).items():
            rows_out.extend({"fixture": fx["fixtureId"], "start": fx["startTime"][:19], "book": book,
                             "market": mk, "outcome": oid, "time": w.isoformat(), "price": p}
                            for w, p in s)
    k_time = ts(fx["startTime"])
    a_time = k_time - timedelta(minutes=90)
    pa, pk = fair_at(pin, order, a_time), fair_at(pin, order, k_time - timedelta(seconds=1))
    ba = fair_at(paw, order, a_time)
    if not pa or not pk or not ba:
        return None
    rise = [pk[i] - pa[i] for i in range(3)]
    k = int(np.argmax(rise))
    late_paw = [w for o in order for w, _ in paw.get(o, []) if a_time < w < k_time]
    res = {"move": rise[k], "paw_updates": len(late_paw)}
    if rise[k] < MOVE:
        return res
    half = pa[k] + rise[k] / 2
    pin_times = sorted({w for o in order for w, _ in pin.get(o, []) if a_time <= w < k_time})
    t_half = next((w for w in pin_times if (fair_at(pin, order, w) or [0, 0, 0])[k] >= half), None)
    if t_half is None:
        return res
    t_bet = min(t_half + REACT, k_time - timedelta(seconds=1))
    price_a, price_bet = at(paw.get(order[k], []), a_time), at(paw.get(order[k], []), t_bet)
    bk = fair_at(paw, order, k_time - timedelta(seconds=1))
    if not price_a or not price_bet or not bk:
        return res
    res.update(ev_a=price_a * pk[k] - 1, ev_bet=price_bet * pk[k] - 1,
               followed=(bk[k] - ba[k]) / rise[k], minutes_before=(k_time - t_half).total_seconds() / 60)
    return res


def main() -> None:
    if not KEY:
        sys.exit("ODDS_PAPI_KEY is not set")
    OUT.mkdir(parents=True, exist_ok=True)
    order = next([str(o["outcomeId"]) for o in m["outcomes"]] for m in get("/markets")
                 if str(m["marketId"]) == M_1X2)
    results, rows = [], []
    for league, tid in LEAGUES.items():
        fixtures = [f for f in get("/fixtures", tournamentId=tid, **{"from": SINCE}) if f.get("statusId") == 2]
        print(f"{league}: {len(fixtures)} finished matches", flush=True)
        for f in fixtures:
            time.sleep(5)
            try:
                hist = get("/historical-odds", fixtureId=f["fixtureId"], bookmakers=f"{PIN},{BOOK}")
            except RuntimeError as exc:
                print(f"  skip {f['fixtureId']}: {exc}")
                continue
            r = analyse(f, hist, order, rows)
            if r:
                results.append({"league": league, **r})
    with open(OUT / "prices.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["fixture", "start", "book", "market", "outcome", "time", "price"])
        w.writeheader()
        w.writerows(rows)
    moved = [r for r in results if "ev_bet" in r]
    ups = np.array([r["paw_updates"] for r in results])
    print(f"\nMatches with both books 90 min before kick-off: {len(results)}")
    print(f"betPawa 1X2 price changes in the last 90 min: median {np.median(ups):.0f}, "
          f"none in {np.mean(ups == 0):.0%} of matches")
    print(f"Pinnacle moved by {MOVE:.0%} or more: {len(moved)} matches")
    if len(moved) < 2:
        return
    for key, label in (("ev_a", "betPawa price 90 min before"), ("ev_bet", "betPawa price 5 min after the move")):
        x = np.array([r[key] for r in moved])
        lo, hi = boot_ci(x)
        print(f"  {label}: EV {x.mean():+.2%} [{lo:+.2%} ; {hi:+.2%}], above fair in {np.mean(x > 0):.0%}")
    fol = np.array([r["followed"] for r in moved])
    mins = np.array([r["minutes_before"] for r in moved])
    print(f"  Share of Pinnacle's move that betPawa made by kick-off: median {np.median(fol):.0%}")
    print(f"  Pinnacle's half-move came {np.median(mins):.0f} min before kick-off (median)")
    x = np.array([r["ev_bet"] for r in moved])
    lo, _ = boot_ci(x)
    verdict = "window" if len(moved) >= 30 and x.mean() > 0 and lo > 0 else "no window"
    print(f"\nRule (30+ matches, mean EV > 0, interval above 0): {verdict}")


if __name__ == "__main__":
    main()
