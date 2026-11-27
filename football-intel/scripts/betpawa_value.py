"""Are betPawa prices above the market's fair price? The test of D68.

Run from football-intel/: python scripts/betpawa_value.py [--csv reference/betpawa_prices.csv]

Each row of the CSV is one betPawa price seen before the match: "screenshot" (a price on
the screen, often every outcome of a market) or "betslip" (a selection the owner really bet, D102),
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
        # D102: the snapshot label carries its time, so the ledger shows when the reference was taken.
        return tuple(probs.mean(axis=0)), f"the_odds_api {last} ({len(probs)} books)"
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


def placement_1x2(conn, match_id: int, captured) -> tuple[tuple | None, str]:
    """D103: the 1X2 fair probability known at the capture: the last The Odds API snapshot taken
    before it (margin removed, averaged over its books), else the last prediction of the site made
    before it. Never a closing price: it was not known when the bet was placed."""
    from datetime import datetime

    from footintel.analysis.value_ledger import placement_reference

    rows = conn.execute(text("""SELECT o.bookmaker, o.snapshot_label, o.selection, o.price
        FROM odds_snapshots o JOIN data_sources d ON d.id = o.source_id
        WHERE o.match_id = :m AND o.market = '1X2' AND d.code = 'the_odds_api'"""), {"m": match_id}).all()
    by: dict = defaultdict(dict)
    for book, label, sel, price in rows:
        by[(label, book)][sel] = price
    snaps: dict = defaultdict(list)
    for (label, _), prices in by.items():
        if "@" in str(label) and (f := fair3(prices)):
            snaps[label].append(f)
    timed = []
    for label, probs in snaps.items():
        try:
            t = datetime.fromisoformat(label.split("@", 1)[1])
        except ValueError:
            continue
        timed.append((t, (tuple(np.mean(probs, axis=0)), f"the_odds_api {label} ({len(probs)} books)")))
    pick = placement_reference([(t, v) for t, v in timed], captured)
    if pick:
        return pick[1]
    pred = conn.execute(text("""SELECT p_home, p_draw, p_away, predicted_at FROM predictions
        WHERE match_id = :m AND predicted_at <= :t ORDER BY predicted_at DESC LIMIT 1"""),
        {"m": match_id, "t": captured}).first()
    if pred and pred.p_home is not None:
        return (pred.p_home, pred.p_draw, pred.p_away), f"prédiction du site {pred.predicted_at:%Y-%m-%d %H:%M} UTC"
    return None, "indisponible"


def evaluate(conn, r: dict) -> dict | None:
    """One price (observation or played selection): match, CLV at the close, EV at placement, settlement."""
    from footintel.analysis.value_ledger import ev, to_utc

    market, sel = r["market"].upper(), r["selection"].upper()
    if sel not in MARKETS.get(market, set()):
        print(f"skip {r['home']} - {r['away']}: marché inconnu {market} {sel}")
        return None
    found = conn.execute(text("""SELECT m.id, c.code, m.kickoff_utc FROM matches m
        JOIN teams th ON th.id = m.home_team_id JOIN teams ta ON ta.id = m.away_team_id
        JOIN competitions c ON c.id = m.competition_id WHERE th.name = :h AND ta.name = :a
        AND m.kickoff_date BETWEEN CAST(:d AS date) - 1 AND CAST(:d AS date) + 1"""),
        {"h": r["home"], "a": r["away"], "d": r["match_date"]}).first()
    if found is None:
        print(f"skip {r['home']} - {r['away']} {r['match_date']}: match introuvable")
        return None
    m = found.id
    pred = conn.execute(text("""SELECT p_over_2_5, exp_home_goals, exp_away_goals
        FROM predictions WHERE match_id = :m ORDER BY predicted_at DESC LIMIT 1"""), {"m": m}).first()
    p_over = market_over(conn, m) or (pred.p_over_2_5 if pred else None)
    eh, ea = ((pred.exp_home_goals, pred.exp_away_goals)
              if pred and pred.exp_home_goals and pred.exp_away_goals else DEFAULT_GOALS)
    price = float(r["price"])
    p_close, ref = market_1x2(conn, m)
    prob_close = fair_prob(market, sel, p_close, p_over, eh, ea) if p_close else None
    p_place, ref_place = placement_1x2(conn, m, to_utc(r["captured_at"]))
    prob_place = fair_prob(market, sel, p_place, p_over, eh, ea) if p_place else None
    score = conn.execute(text("SELECT home_goals, away_goals FROM match_outcomes WHERE match_id = :m"),
                         {"m": m}).first()
    won = None
    if score:
        evs = conn.execute(text("""SELECT e.team_id = mm.home_team_id AS home FROM match_events e
            JOIN matches mm ON mm.id = e.match_id WHERE e.match_id = :m AND e.type = 'goal'
            ORDER BY e.minute, coalesce(e.extra_minute, 0), e.id"""), {"m": m}).all()
        goals = ["H" if g.home else "A" for g in evs] if evs or score.home_goals + score.away_goals == 0 else None
        won = settle(market, sel, score.home_goals, score.away_goals, goals)
    weak = "the_odds_api" in ref and int(ref.rsplit("(", 1)[1].split()[0]) < 3 if "(" in ref else False
    return {**r, "market": market, "selection": sel, "match_id": m, "competition": found.code,
            "kickoff_utc": found.kickoff_utc.isoformat() if found.kickoff_utc else "",
            "fair": prob_close, "ref": ref + (" — référence faible (moins de 3 bookmakers)" if weak else ""),
            "clv": ev(price, prob_close), "fair_place": prob_place, "ref_place": ref_place,
            "ev_place": ev(price, prob_place), "won": won}


def main() -> None:
    from footintel.analysis.value_ledger import (
        coupon_money,
        coupon_roi_ci,
        latest_per_key,
        settlement_agrees,
    )

    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="reference/betpawa_prices.csv")
    ap.add_argument("--coupons", default="reference/betpawa_coupons.csv")
    ap.add_argument("--legs", default="reference/betpawa_coupon_legs.csv")
    ap.add_argument("--ledger", default="reports/betpawa_ledger.csv", help="one row per selection (D101)")
    args = ap.parse_args()

    def read(path):
        try:
            with open(path, encoding="utf-8") as fh:
                return list(csv.DictReader(fh))
        except FileNotFoundError:
            return []

    prices, coupons, legs = read(args.csv), read(args.coupons), read(args.legs)
    placed = {c["coupon_id"]: c["placed_at"] for c in coupons}

    # 1. Coupons: the real money, one bet per coupon (D103).
    print("1. COUPONS (argent réel, un pari par coupon)")
    money = coupon_money(coupons)
    if not coupons:
        print("  Aucun coupon enregistré.")
    else:
        print(f"  {money['coupons']} coupons : {money['won']} gagnés, {money['lost']} perdus, "
              f"{money['refunded']} remboursés, {money['open']} en cours.")
        if money["stakes"]:
            print(f"  Mises {money['stakes']:,.0f} FC, retours {money['returned']:,.2f} FC, net {money['net']:+,.2f} FC, "
                  f"ROI {money['roi']:+.1%}.")
            ci = coupon_roi_ci(coupons)
            if ci:
                print(f"  Intervalle du ROI (coupons rééchantillonnés) : {ci[0]:+.0%} à {ci[1]:+.0%}.")
            print("  Attention : " + (f"{money['coupons']} coupons seulement, le ROI peut changer de signe "
                                       "avec quelques coupons de plus." if money["coupons"] < 30 else "voir l'intervalle."))
        weeks: dict = defaultdict(list)
        for c in coupons:
            weeks[c["placed_at"][:10]].append(c)
        for day, cs in sorted(weeks.items()):
            m = coupon_money(cs)
            roi = f", ROI {m['roi']:+.1%}" if m["roi"] is not None else ""
            print(f"    {day} : {len(cs)} coupon(s), net {m['net']:+,.2f} FC{roi}")

    engine = get_engine()
    with engine.connect() as conn:
        played = []
        for x in legs:
            e = evaluate(conn, {**x, "captured_at": placed.get(x["coupon_id"], x["match_date"]), "source": "coupon"})
            if e:
                played.append(e)
        # Market observations: the last price of each selection; the file keeps every price (history).
        obs_all = [e for r in prices if (e := evaluate(conn, r))]
    obs = latest_per_key(obs_all, lambda o: (o["match_id"], o["market"], o["selection"]))

    # 2. Played selections: quality of the prices taken, never counted as separate bets.
    print("\n2. SÉLECTIONS JOUÉES (qualité des cotes prises ; l'argent est compté au point 1)")
    if not played:
        print("  Aucune sélection jouée enregistrée.")
    for market in sorted({o["market"] for o in played}):
        rows = [o for o in played if o["market"] == market]
        won = sum(o["result"] == "gagné" for o in rows)
        lost = sum(o["result"] == "perdu" for o in rows)
        print("  " + quality_line(market, rows) + f" ; résultats betPawa : {won} gagnées, {lost} perdues, "
              f"dans {len({o['coupon_id'] for o in rows})} coupons")
    agree = [settlement_agrees(o["won"], o["result"]) for o in played]
    checked = [a for a in agree if a is not None]
    if checked:
        print(f"  Contrôle du règlement : notre calcul est d'accord avec betPawa sur {sum(checked)} sélections "
              f"sur {len(checked)}.")
        for o, a in zip(played, agree, strict=True):
            if a is False:
                print(f"    désaccord : {o['home']} - {o['away']} {o['market']} {o['selection']} (betPawa : {o['result']})")

    # 3. Market observations: is betPawa above the fair price, market by market?
    print(f"\n3. OBSERVATIONS DE MARCHÉ ({len(obs_all)} cotes, {len(obs)} sélections distinctes, "
          "la dernière cote relevée de chacune)")
    for market in sorted({o["market"] for o in obs}):
        print("  " + quality_line(market, [o for o in obs if o["market"] == market]))
    bands: dict = defaultdict(list)
    from footintel.analysis.value_ledger import odds_band
    for o in obs:
        if o["clv"] is not None:
            bands[odds_band(float(o["price"]))].append(o)
    if bands:
        print("  Par plage de cotes (CLV) :")
        for label, rows in bands.items():
            print(f"    {label} : " + quality_line("", rows).lstrip(": "))
    print(reference_timing(obs))
    write_ledger(obs + played, args.ledger)


def quality_line(market: str, rows: list[dict]) -> str:
    """Selections, matches, competitions, odds range, mean CLV and mean EV at placement, with their sample warning."""
    from footintel.analysis.value_ledger import cluster_ci, sample_warning

    odds = sorted(float(o["price"]) for o in rows)
    out = (f"{market}: {len(rows)} sélections, {len({o['match_id'] for o in rows})} matchs, "
           f"{len({o['competition'] for o in rows})} compétitions, cotes {odds[0]:.2f} à {odds[-1]:.2f}")
    for key, name in (("clv", "CLV"), ("ev_place", "EV au placement")):
        vals = [o for o in rows if o[key] is not None]
        if not vals:
            out += f" ; {name} : indisponible"
            continue
        n_match = len({o["match_id"] for o in vals})
        out += f" ; {name} moyenne {np.mean([o[key] for o in vals]):+.1%} sur {len(vals)}"
        warn = sample_warning(n_match)
        if n_match >= 20:
            lo, hi = cluster_ci([o[key] for o in vals], [o["match_id"] for o in vals])
            out += f" [{lo:+.1%} ; {hi:+.1%}]"
        if warn:
            out += f" ({warn})"
    return out


def reference_timing(obs: list[dict]) -> str:
    """Where each closing fair price comes from. A closing price is taken at kick-off, after the
    capture: a betPawa price above it is the closing-line test. A snapshot keeps its own time."""
    count: dict = defaultdict(int)
    for o in obs:
        if o["fair"] is not None:
            ref = o["ref"]
            count["clôture (après le relevé)" if " closing" in ref else "avant clôture" if "pre_closing" in ref
                  else "instantané The Odds API (heure dans le registre)"] += 1
    missing = sum(o["fair"] is None for o in obs)
    return ("Référence de la cote juste (CLV) : " + ", ".join(f"{k} {v}" for k, v in count.items())
            + f" ; sans référence : {missing}.")


LEDGER_FIELDS = ["source", "coupon_id", "captured_at", "match_date", "kickoff_utc", "competition", "home", "away",
                 "market", "selection", "price", "fair_close", "ref_close", "clv", "fair_place", "ref_place",
                 "ev_place", "our_result", "betpawa_result"]


def write_ledger(rows: list[dict], path: str) -> None:
    """One row per selection (observation or played): prices, both references and both measures,
    our settlement and betPawa's. Same data, same file: the rows are sorted."""
    from pathlib import Path

    Path(path).parent.mkdir(parents=True, exist_ok=True)

    def num(x, fmt=".4f"):
        return "" if x is None else format(x, fmt)

    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=LEDGER_FIELDS)
        w.writeheader()
        for o in sorted(rows, key=lambda o: (o.get("source", ""), o.get("coupon_id", ""), o["match_date"],
                                             o["home"], o["market"], o["selection"], o["captured_at"])):
            w.writerow({"source": o.get("source", ""), "coupon_id": o.get("coupon_id", ""),
                        **{k: o.get(k, "") for k in ("captured_at", "match_date", "kickoff_utc", "competition",
                                                    "home", "away", "market", "selection", "price")},
                        "fair_close": num(o["fair"]), "ref_close": o["ref"], "clv": num(o["clv"]),
                        "fair_place": num(o["fair_place"]), "ref_place": o["ref_place"], "ev_place": num(o["ev_place"]),
                        "our_result": "" if o["won"] is None else ("gagné" if o["won"] else "perdu"),
                        "betpawa_result": o.get("result", "")})
    print(f"Registre écrit : {path} ({len(rows)} lignes)")


if __name__ == "__main__":
    main()
