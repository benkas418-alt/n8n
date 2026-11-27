"""betPawa value (D68, D101-D104): every price the owner recorded, against the fair price.

For each price: the match, the fair probability at the close (CLV) and the one known at the
capture (EV at placement), and the settlement. `build_report` gathers the three data sets of
D103 (observations, played selections, coupons) into one JSON-ready report for the site's
"Valeur" page and for `scripts/betpawa_value.py`.
"""

import csv
from collections import defaultdict
from pathlib import Path

import numpy as np
from sqlalchemy import Engine, text

from footintel.analysis.tickets import dc_up
from footintel.analysis.value import _fit_lambdas
from footintel.api.dashboard import _market_order

REFERENCE = Path(__file__).resolve().parents[3] / "reference"

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


def evaluate(conn, r: dict, alerts: list | None = None) -> dict | None:
    """One price (observation or played selection): match, CLV at the close, EV at placement, settlement."""
    from footintel.analysis.value_ledger import ev, to_utc

    market, sel = r["market"].upper(), r["selection"].upper()
    if sel not in MARKETS.get(market, set()):
        (alerts if alerts is not None else []).append(f"Marché inconnu : {r['home']} - {r['away']} {market} {sel}.")
        return None
    found = conn.execute(text("""SELECT m.id, c.code, m.kickoff_utc FROM matches m
        JOIN teams th ON th.id = m.home_team_id JOIN teams ta ON ta.id = m.away_team_id
        JOIN competitions c ON c.id = m.competition_id WHERE th.name = :h AND ta.name = :a
        AND m.kickoff_date BETWEEN CAST(:d AS date) - 1 AND CAST(:d AS date) + 1"""),
        {"h": r["home"], "a": r["away"], "d": r["match_date"]}).first()
    if found is None:
        (alerts if alerts is not None else []).append(
            f"Match introuvable : {r['home']} - {r['away']} du {r['match_date']} (nom d'équipe à vérifier).")
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

def read_csv(path: Path) -> list[dict]:
    try:
        with open(path, encoding="utf-8") as fh:
            return list(csv.DictReader(fh))
    except FileNotFoundError:
        return []


def collect(engine: Engine, ref: Path = REFERENCE) -> dict:
    """The three data sets, each price evaluated, plus the data alerts (D104)."""
    from footintel.analysis.value_ledger import latest_per_key

    prices, coupons, legs = (read_csv(ref / f) for f in
                             ("betpawa_prices.csv", "betpawa_coupons.csv", "betpawa_coupon_legs.csv"))
    placed = {c["coupon_id"]: c["placed_at"] for c in coupons}
    alerts: list[str] = []
    with engine.connect() as conn:
        played, obs_all = [], []
        for x in legs:
            if x["coupon_id"] not in placed:
                alerts.append(f"Sélection sans coupon : {x['home']} - {x['away']} (coupon {x['coupon_id']}).")
            e = evaluate(conn, {**x, "captured_at": placed.get(x["coupon_id"], x["match_date"]), "source": "coupon"},
                         alerts)
            if e:
                played.append(e)
        for r in prices:
            if e := evaluate(conn, r, alerts):
                obs_all.append(e)
    for c in coupons:
        n = sum(x["coupon_id"] == c["coupon_id"] for x in legs)
        if str(n) != str(c["n_legs"]):
            alerts.append(f"Coupon {c['coupon_id']} : {n} sélections enregistrées pour {c['n_legs']} annoncées.")
        if not c.get("settled_at"):
            pass  # betPawa does not show the settlement time on the slips: left empty, never invented
    obs = latest_per_key(obs_all, lambda o: (o["match_id"], o["market"], o["selection"]))
    missing_close = [o for o in obs + played if o["fair"] is None]
    if missing_close:
        alerts.append(f"{len(missing_close)} sélections sans cote de clôture de référence : CLV impossible pour elles.")
    missing_place = [o for o in obs + played if o["fair_place"] is None]
    if missing_place:
        alerts.append(f"{len(missing_place)} sélections sans prix connu avant le relevé : EV au placement impossible.")
    unsettled = [o for o in played if o["won"] is None]
    if unsettled:
        alerts.append(f"{len(unsettled)} sélections jouées sans score ou sans ordre des buts : règlement à vérifier.")
    return {"coupons": coupons, "played": played, "obs_all": obs_all, "obs": obs, "alerts": alerts}


def market_stats(rows: list[dict]) -> dict:
    """Counts, odds range, mean CLV and EV at placement with match-clustered intervals and warnings."""
    from footintel.analysis.value_ledger import cluster_ci, sample_warning

    odds = sorted(float(o["price"]) for o in rows)
    out = {"selections": len(rows), "matches": len({o["match_id"] for o in rows}),
           "competitions": len({o["competition"] for o in rows}),
           "coupons": len({o["coupon_id"] for o in rows if o.get("coupon_id")}),
           "odds_min": odds[0] if odds else None, "odds_max": odds[-1] if odds else None,
           "won": sum(o.get("result") == "gagné" for o in rows), "lost": sum(o.get("result") == "perdu" for o in rows)}
    for key in ("clv", "ev_place"):
        vals = [o for o in rows if o[key] is not None]
        n_match = len({o["match_id"] for o in vals})
        stat = {"n": len(vals), "matches": n_match, "mean": float(np.mean([o[key] for o in vals])) if vals else None,
                "ci": None, "warning": sample_warning(n_match) if vals else "indisponible"}
        if n_match >= 20:
            stat["ci"] = cluster_ci([o[key] for o in vals], [o["match_id"] for o in vals])
        out[key] = stat
    return out


def build_report(engine: Engine, ref: Path = REFERENCE) -> dict:
    """The "Valeur" page (D104): money per coupon, quality of the prices, history and alerts."""
    from footintel.analysis.value_ledger import coupon_money, coupon_roi_ci, odds_band

    d = collect(engine, ref)
    coupons = sorted(d["coupons"], key=lambda c: c["placed_at"])
    money = coupon_money(coupons)
    money["roi_ci"] = coupon_roi_ci(coupons)
    cum, history = 0.0, []
    for c in coupons:
        m = coupon_money([c])
        if m["stakes"]:
            cum += m["net"]
            history.append({"date": c["placed_at"][:10], "coupon": c["coupon_id"], "stake": float(c["stake_fc"]),
                            "net": m["net"], "cumulative": cum, "status": c["status"]})
    by_comp: dict = defaultdict(list)
    for o in d["played"]:
        by_comp[o["competition"]].append(o)
    bands: dict = defaultdict(list)
    for o in d["obs"]:
        bands[odds_band(float(o["price"]))].append(o)
    played_markets = {m: market_stats([o for o in d["played"] if o["market"] == m])
                      for m in sorted({o["market"] for o in d["played"]})}
    obs_markets = {m: market_stats([o for o in d["obs"] if o["market"] == m])
                   for m in sorted({o["market"] for o in d["obs"]})}
    return {"money": money, "history": history, "played": played_markets, "observed": obs_markets,
            "competitions": {k: market_stats(v) for k, v in sorted(by_comp.items())},
            "bands": {k: market_stats(v) for k, v in bands.items()},
            "counts": {"prices": len(d["obs_all"]), "selections": len(d["obs"]), "played": len(d["played"]),
                       "coupons": len(coupons)},
            "reference": reference_timing(d["obs"]), "alerts": d["alerts"]}
