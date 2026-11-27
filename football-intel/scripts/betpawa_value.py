"""Are betPawa prices above the market's fair price? The test of D68.

Run from football-intel/: python scripts/betpawa_value.py [--csv reference/betpawa_prices.csv]

Each row of the CSV is one betPawa price seen before the match (screenshot or OddsPapi),
with team names as stored in our database. For each row:

- fair probability from the sharpest price we hold: Pinnacle close, then the market
  average close, then the pre-closing prices, then The Odds API (margin removed);
  1UP, 2UP and first goal from that 1X2 with the same goal-order calculation as the site
  (D66); BTTS has no market price: it comes from the same goal rates (independent Poisson);
- expected value = price x fair probability - 1;
- settlement from the score, and from the goal events for 1UP, 2UP and first goal.

A real edge shows as a mean expected value above 0 with its interval above 0, and the
settled return agreeing over enough rows (150 at least before any conclusion).
"""

import argparse
import csv
import sys
from collections import defaultdict

import numpy as np
from sqlalchemy import text

sys.path.insert(0, "src")
from footintel.analysis.tickets import dc_up  # noqa: E402
from footintel.analysis.value import _fit_lambdas  # noqa: E402
from footintel.api.dashboard import _market_order  # noqa: E402
from footintel.db.session import get_engine  # noqa: E402

MARKETS = {"1X2": {"H", "D", "A"}, "DC": {"1X", "12", "X2"}, "BTTS": {"Y", "N"}, "OU2.5": {"O", "U"},
           "OU1.5": {"O", "U"}, "OU3.5": {"O", "U"},
           "1UP": {"1", "2"}, "2UP": {"1", "2"}, "FG": {"1", "2", "0"},
           "DC1UP": {"1X", "X2", "12"}, "DC2UP": {"1X", "X2", "12"}}
# Sharpest first: (bookmaker, snapshot label or None for the latest The Odds API snapshot).
# Only a starting point for the goal-rate fit when no prediction is stored.
DEFAULT_GOALS = (1.4, 1.1)
SOURCES = [("pinnacle", "closing"), ("market_avg", "closing"), ("pinnacle", "pre_closing"),
           ("market_avg", "pre_closing")]


def fair3(prices: dict) -> tuple | None:
    if {"H", "D", "A"} - prices.keys() or min(prices.values()) <= 1:
        return None
    inv = {k: 1 / prices[k] for k in "HDA"}
    s = sum(inv.values())
    return tuple(inv[k] / s for k in "HDA")


def market_1x2(conn, match_id: int) -> tuple[tuple | None, str]:
    rows = conn.execute(text("""SELECT o.bookmaker, o.snapshot_label, o.selection, o.price, d.code
        FROM odds_snapshots o JOIN data_sources d ON d.id = o.source_id
        WHERE o.match_id = :m AND o.market = '1X2'"""), {"m": match_id}).all()
    by = defaultdict(dict)
    for book, label, sel, price, src in rows:
        by[(book, label, src == "the_odds_api")][sel] = price
    for book, label in SOURCES:
        for (b, lab, odds_api), prices in by.items():
            if b == book and lab == label and not odds_api and (p := fair3(prices)):
                return p, f"{book} {label}"
    api = [(lab, fair3(p)) for (b, lab, odds_api), p in by.items() if odds_api]
    api = [x for x in api if x[1]]
    if api:
        last = max(lab for lab, _ in api)
        probs = np.array([p for lab, p in api if lab == last])
        return tuple(probs.mean(axis=0)), f"the_odds_api {len(probs)} books"
    return None, "no price"


def market_over(conn, match_id: int) -> float | None:
    rows = conn.execute(text("""SELECT snapshot_label, selection, price FROM odds_snapshots
        WHERE match_id = :m AND market = 'OU2.5' AND bookmaker = 'market_avg'"""), {"m": match_id}).all()
    by = defaultdict(dict)
    for label, sel, price in rows:
        by[label][sel] = price
    for label in ["closing", "pre_closing"] + sorted(by, reverse=True):
        p = by.get(label, {})
        if p.get("over", 0) > 1 and p.get("under", 0) > 1:
            return (1 / p["over"]) / (1 / p["over"] + 1 / p["under"])
    return None


def fair_prob(market: str, sel: str, p: tuple, p_over: float | None,
              eh: float, ea: float) -> float | None:
    h, d, a = p
    if market == "1X2":
        return {"H": h, "D": d, "A": a}[sel]
    if market == "DC":
        return {"1X": h + d, "12": h + a, "X2": d + a}[sel]
    if market == "OU2.5":
        return None if p_over is None else (p_over if sel == "O" else 1 - p_over)
    if market in ("OU1.5", "OU3.5"):
        # Other goal lines from the goal rates fitted on the 1X2 and the over 2.5.
        from scipy.stats import poisson

        lh, la = _fit_lambdas(h, a, (eh, ea), p_over)
        over = 1 - poisson.cdf(int(float(market[2:])), lh + la)
        return over if sel == "O" else 1 - over
    if market == "BTTS":
        lh, la = _fit_lambdas(h, a, (eh, ea), p_over)
        yes = (1 - np.exp(-lh)) * (1 - np.exp(-la))
        return yes if sel == "Y" else 1 - yes
    if market in ("DC1UP", "DC2UP"):
        lh, la = _fit_lambdas(h, a, (eh, ea), p_over)
        return dict(zip(("1X", "X2", "12"), dc_up(lh, la, 1 if market == "DC1UP" else 2)))[sel]
    m = _market_order(round(h, 4), round(a, 4), None if p_over is None else round(p_over, 4),
                      round(eh, 3), round(ea, 3))
    return m.get(f"{market}_{sel}")


def settle(market: str, sel: str, hg: int, ag: int, goals: list[str] | None) -> int | None:
    """1 won, 0 lost, None unknown. goals: 'H'/'A' in order, None when the events are missing."""
    if market == "1X2":
        return int(sel == ("H" if hg > ag else "D" if hg == ag else "A"))
    if market == "DC":
        r = "H" if hg > ag else "D" if hg == ag else "A"
        return int(r in {"1X": "HD", "12": "HA", "X2": "DA"}[sel])
    if market.startswith("OU"):
        return int((hg + ag > float(market[2:])) == (sel == "O"))
    if market == "BTTS":
        return int((hg > 0 and ag > 0) == (sel == "Y"))
    if goals is None or len(goals) != hg + ag:
        return None
    if market == "FG":
        return int((goals[0] if goals else "0") == {"1": "H", "2": "A", "0": "0"}[sel])
    lead, best = 0, {"H": 0, "A": 0}
    for g in goals:
        lead += 1 if g == "H" else -1
        best["H"], best["A"] = max(best["H"], lead), max(best["A"], -lead)
    need = 2 if market in ("2UP", "DC2UP") else 1
    if market in ("DC1UP", "DC2UP"):
        # Early payout at a `need`-goal lead of a covered team, else a double chance on the final score.
        final = {"1X": hg >= ag, "X2": ag >= hg, "12": hg != ag}[sel]
        covered = {"1X": ("H",), "X2": ("A",), "12": ("H", "A")}[sel]
        lead, best = 0, {"H": 0, "A": 0}
        for g in goals:
            lead += 1 if g == "H" else -1
            best["H"], best["A"] = max(best["H"], lead), max(best["A"], -lead)
        return int(final or any(best[t] >= need for t in covered))
    side = "H" if sel == "1" else "A"
    # betPawa rule: paid as soon as the team leads by `need`, else settled on the final result.
    return int(best[side] >= need or (hg > ag if side == "H" else ag > hg))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="reference/betpawa_prices.csv")
    ap.add_argument("--ledger", default="reports/betpawa_ledger.csv", help="one row per selection (D101)")
    args = ap.parse_args()
    with open(args.csv, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        print("No betPawa price recorded yet.")
        return
    engine = get_engine()
    out = []
    with engine.connect() as conn:
        for r in rows:
            market, sel = r["market"].upper(), r["selection"].upper()
            if sel not in MARKETS.get(market, set()):
                print(f"skip {r}: unknown market or selection")
                continue
            found = conn.execute(text("""SELECT m.id, c.code FROM matches m JOIN teams th ON th.id = m.home_team_id
                JOIN teams ta ON ta.id = m.away_team_id JOIN competitions c ON c.id = m.competition_id
                WHERE th.name = :h AND ta.name = :a
                AND m.kickoff_date BETWEEN CAST(:d AS date) - 1 AND CAST(:d AS date) + 1"""),
                {"h": r["home"], "a": r["away"], "d": r["match_date"]}).first()
            m, comp = (found.id, found.code) if found else (None, None)
            if m is None:
                print(f"skip {r['home']} - {r['away']} {r['match_date']}: match not found")
                continue
            p, src = market_1x2(conn, m)
            pred = conn.execute(text("""SELECT p_over_2_5, exp_home_goals, exp_away_goals
                FROM predictions WHERE match_id = :m ORDER BY predicted_at DESC LIMIT 1"""), {"m": m}).first()
            p_over = market_over(conn, m) or (pred.p_over_2_5 if pred else None)
            eh, ea = ((pred.exp_home_goals, pred.exp_away_goals)
                      if pred and pred.exp_home_goals and pred.exp_away_goals else DEFAULT_GOALS)
            prob = fair_prob(market, sel, p, p_over, eh, ea) if p else None
            score = conn.execute(text("SELECT home_goals, away_goals FROM match_outcomes WHERE match_id = :m"),
                                 {"m": m}).first()
            won = None
            if score:
                ev = conn.execute(text("""SELECT e.team_id = mm.home_team_id AS home FROM match_events e
                    JOIN matches mm ON mm.id = e.match_id WHERE e.match_id = :m AND e.type = 'goal'
                    ORDER BY e.minute, coalesce(e.extra_minute, 0), e.id"""), {"m": m}).all()
                goals = ["H" if g.home else "A" for g in ev] if ev or score.home_goals + score.away_goals == 0 else None
                won = settle(market, sel, score.home_goals, score.away_goals, goals)
            price = float(r["price"])
            out.append({**r, "match_id": m, "competition": comp, "fair": prob, "ref": src,
                        "ev": None if prob is None else price * prob - 1,
                        "ret": None if won is None else won * price - 1})

    # D101: one observation per selection (the last price captured before the match), a ledger
    # with every field, and intervals that resample matches, not rows: two bets on one match move together.
    last: dict = {}
    for o in out:
        k = (o["match_id"], o["market"].upper(), o["selection"].upper())
        if k not in last or o["captured_at"] >= last[k]["captured_at"]:
            last[k] = o
    obs = sorted(last.values(), key=lambda o: (o["match_date"], o["home"], o["market"]))
    print(f"{len(out)} cotes lues, {len(obs)} sélections distinctes (la dernière cote relevée de chacune).")
    write_ledger(obs, args.ledger)
    for o in obs:
        fair_odds = f"{1 / o['fair']:.2f}" if o["fair"] else "—"
        ev = f"{o['ev']:+.1%}" if o["ev"] is not None else "—"
        ret = "—" if o["ret"] is None else ("gagné" if o["ret"] > 0 else "perdu")
        print(f"{o['match_date']} {o['home']} - {o['away']} {o['market']} {o['selection']} @ {o['price']}"
              f" | juste {fair_odds} ({o['ref']}) | EV {ev} | {ret}")
    print()
    for market in sorted({o["market"] for o in obs}):
        print(market_line(market, [o for o in obs if o["market"] == market]))


def cluster_ci(values: list[float], groups: list, samples: int = 2000, seed: int = 0) -> tuple[float, float]:
    """95 % interval of the mean when whole matches are resampled."""
    by = defaultdict(list)
    for v, g in zip(values, groups, strict=True):
        by[g].append(v)
    keys = list(by)
    rng = np.random.default_rng(seed)
    means = []
    for _ in range(samples):
        pick = [x for k in rng.choice(len(keys), len(keys)) for x in by[keys[k]]]
        means.append(np.mean(pick))
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def market_line(market: str, rows: list[dict]) -> str:
    """Prices, matches, competitions and odds range, then the expected value and the settled return."""
    priced = [o for o in rows if o["ev"] is not None]
    settled = [o for o in rows if o["ret"] is not None]
    odds = sorted(float(o["price"]) for o in rows)
    head = (f"{market}: {len(rows)} sélections sur {len({o['match_id'] for o in rows})} matchs, "
            f"{len({o['competition'] for o in rows})} compétitions, cotes {odds[0]:.2f} à {odds[-1]:.2f} "
            f"(médiane {np.median(odds):.2f})")
    if not priced:
        return head + "; pas de prix juste"
    line = head + f"; EV moyenne {np.mean([o['ev'] for o in priced]):+.1%}"
    if len({o["match_id"] for o in priced}) >= 20:
        lo, hi = cluster_ci([o["ev"] for o in priced], [o["match_id"] for o in priced])
        line += f" [{lo:+.1%} ; {hi:+.1%}]"
    if settled:
        won = sum(o["ret"] > 0 for o in settled)
        line += f"; {len(settled)} réglées ({won} gagnées), rendement {np.mean([o['ret'] for o in settled]):+.1%}"
        if len({o["match_id"] for o in settled}) >= 20:
            lo, hi = cluster_ci([o["ret"] for o in settled], [o["match_id"] for o in settled])
            line += f" [{lo:+.1%} ; {hi:+.1%}]"
    return line


LEDGER_FIELDS = ["captured_at", "match_date", "competition", "home", "away", "market", "selection", "price",
                 "fair_odds", "fair_prob", "ref", "ev", "won", "profit"]


def write_ledger(obs: list[dict], path: str) -> None:
    """One row per selection: what betPawa offered, the fair price, the result, the profit for a stake of 1."""
    from pathlib import Path

    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=LEDGER_FIELDS)
        w.writeheader()
        for o in obs:
            w.writerow({**{k: o[k] for k in ("captured_at", "match_date", "competition", "home", "away", "market",
                                             "selection", "price", "ref")},
                        "fair_odds": f"{1 / o['fair']:.3f}" if o["fair"] else "",
                        "fair_prob": f"{o['fair']:.4f}" if o["fair"] else "",
                        "ev": f"{o['ev']:.4f}" if o["ev"] is not None else "",
                        "won": "" if o["ret"] is None else int(o["ret"] > 0),
                        "profit": "" if o["ret"] is None else f"{o['ret']:.4f}"})
    print(f"Registre écrit : {path}")

if __name__ == "__main__":
    main()
