"""Model probabilities per betting market, for the odds checker.

The checker compares a bookmaker's odds with the model: fair odds = 1 / p and
theoretical value = p x odds - 1. A positive value only means something if p is
well calibrated, so every market carries a reliability note from the backtests.
"""

import numpy as np
from scipy.optimize import least_squares
from scipy.stats import poisson

GOALS = np.arange(16)

# From docs/RESULTS.md: what the backtests and live checks say about each market.
RELIABILITY = {
    "1x2": "Au niveau du marché en backtest (log loss 0,9655 contre 0,9678), sans avantage démontré.",
    "goals": "Plus/moins : légèrement meilleur que le marché en backtest, avantage non démontré.",
    "btts": "Point faible : à peine mieux qu'un taux fixe en backtest, moins bon ce week-end.",
    "1up": "Approximation : buts supposés arriver dans un ordre aléatoire.",
    "no_odds": "Match sans cotes de référence : prédiction moins fiable (données insuffisantes).",
    "market": "Marché : moyenne des bookmakers (The Odds API), marge de chacun retirée. "
              "En coupe, aucun test ne montre encore si le modèle ou le marché est le plus juste.",
}


def _fit_lambdas(p_home: float, p_away: float, start: tuple[float, float]) -> tuple[float, float]:
    """Goal rates whose independent-Poisson 1X2 matches the model's 1X2."""
    def res(x):
        lh, la = np.exp(x)
        m = np.outer(poisson.pmf(GOALS, lh), poisson.pmf(GOALS, la))
        return [np.tril(m, -1).sum() - p_home, np.triu(m, 1).sum() - p_away]
    lh, la = np.exp(least_squares(res, np.log(np.clip(start, 0.2, 5.0))).x)
    return float(lh), float(la)


def ever_leads(lh: float, la: float) -> tuple[float, float]:
    """P(home leads at some point), P(away leads at some point), goals in random order."""
    q = lh / (lh + la)
    pn = poisson.pmf(GOALS, lh + la)
    out = []
    for side_q in (q, 1 - q):
        dp, reached, by_n = {0: 1.0}, 0.0, [0.0]
        for _ in range(1, len(GOALS)):
            new, hit = {}, 0.0
            for s, p in dp.items():
                if s + 1 >= 1:
                    hit += p * side_q
                else:
                    new[s + 1] = new.get(s + 1, 0.0) + p * side_q
                new[s - 1] = new.get(s - 1, 0.0) + p * (1 - side_q)
            reached += hit
            dp = new
            by_n.append(reached)
        out.append(float(sum(pn[n] * by_n[n] for n in range(len(GOALS)))))
    return out[0], out[1]


def market_probabilities(pred: dict) -> list[dict]:
    """One row per selection: key, label, probability, reliability note key."""
    ph, pd_, pa = pred["p_home"], pred["p_draw"], pred["p_away"]
    rows = [("1", "1 (victoire domicile)", ph, "1x2"), ("X", "X (nul)", pd_, "1x2"),
            ("2", "2 (victoire extérieur)", pa, "1x2"), ("1X", "1X (double chance)", ph + pd_, "1x2"),
            ("X2", "X2 (double chance)", pd_ + pa, "1x2"), ("12", "12 (pas de nul)", ph + pa, "1x2")]
    for line, col in ((1.5, "p_over_1_5"), (2.5, "p_over_2_5"), (3.5, "p_over_3_5")):
        p = pred.get(col)
        if p is not None:
            rows += [(f"O{line}", f"Plus de {line} buts", p, "goals"),
                     (f"U{line}", f"Moins de {line} buts", 1 - p, "goals")]
    if pred.get("p_btts") is not None:
        rows += [("BTTS_Y", "Les deux marquent : oui", pred["p_btts"], "btts"),
                 ("BTTS_N", "Les deux marquent : non", 1 - pred["p_btts"], "btts")]
    if pred.get("exp_home_goals") and pred.get("exp_away_goals"):
        lh, la = _fit_lambdas(ph, pa, (pred["exp_home_goals"], pred["exp_away_goals"]))
        up_h, up_a = ever_leads(lh, la)
        rows += [("1UP_1", "1X2 1UP : domicile mène à un moment", up_h, "1up"),
                 ("1UP_2", "1X2 1UP : extérieur mène à un moment", up_a, "1up")]
    return [{"key": k, "label": lab, "prob": round(float(p), 4), "note": note} for k, lab, p, note in rows]


def market_consensus(prices: list[tuple[str, str, float]]) -> dict | None:
    """Fair 1X2 probabilities from several bookmakers: each one's margin removed in
    proportion, then the mean. Also the best price offered for each selection."""
    books: dict[str, dict[str, float]] = {}
    for bookmaker, selection, price in prices:
        books.setdefault(bookmaker, {})[selection] = price
    fair = []
    for b in books.values():
        if set(b) == {"H", "D", "A"}:
            inv = {k: 1 / v for k, v in b.items()}
            total = sum(inv.values())
            fair.append({k: v / total for k, v in inv.items()})
    if not fair:
        return None
    mean = {k: float(np.mean([f[k] for f in fair])) for k in ("H", "D", "A")}
    best = {k: max(b[k] for b in books.values() if k in b) for k in ("H", "D", "A")}
    return {"1": round(mean["H"], 4), "X": round(mean["D"], 4), "2": round(mean["A"], 4),
            "1X": round(mean["H"] + mean["D"], 4), "X2": round(mean["D"] + mean["A"], 4),
            "12": round(mean["H"] + mean["A"], 4), "best": best, "n_bookmakers": len(fair)}
