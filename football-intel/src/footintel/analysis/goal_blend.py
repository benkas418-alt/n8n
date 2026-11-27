"""Hermès 1.1 (D109): who answers the goal questions of a match.

Tests D107 and D108 ranked the sources for over/under and both-teams-score, on matches with
bookmakers' 1X2 odds: the bookmakers first, LightGBM second, Hermès third. Without those odds,
Hermès is as good as LightGBM. The winner (1X2) always stays Hermès's.

1. bookmakers: their over 2.5 price exists -> goal rates fitted to their fair 1X2 and over 2.5;
2. lightgbm: the match has 1X2 odds and a LightGBM prediction -> LightGBM's goal markets;
3. hermes: otherwise, Hermès's own goal markets.
"""

import numpy as np
from scipy.stats import poisson

GOAL_KEYS = ("p_over_1_5", "p_over_2_5", "p_over_3_5", "p_btts", "exp_home_goals", "exp_away_goals")
SOURCE_FR = {"bookmakers": "les bookmakers (sans leur marge)", "lightgbm": "LightGBM", "hermes": "Hermès"}
_GOALS = np.arange(11)


def markets_from_rates(lh: float, la: float) -> dict[str, float]:
    grid = np.outer(poisson.pmf(_GOALS, lh), poisson.pmf(_GOALS, la))
    total = _GOALS[:, None] + _GOALS[None, :]
    return {"p_over_1_5": float(grid[total > 1.5].sum()), "p_over_2_5": float(grid[total > 2.5].sum()),
            "p_over_3_5": float(grid[total > 3.5].sum()), "p_btts": float(grid[1:, 1:].sum()),
            "exp_home_goals": float(lh), "exp_away_goals": float(la)}


def bookmaker_goals(m1x2: tuple[float, float, float], over: float, start: tuple[float, float]) -> dict:
    from footintel.analysis.value import _fit_lambdas

    lh, la = _fit_lambdas(m1x2[0], m1x2[2], start, over)
    out = markets_from_rates(lh, la)
    out["p_over_2_5"] = float(over)  # their own price, not the fitted one
    return out


def blend_goals(row: dict, m1x2: tuple | None, over: float | None, lgbm: dict | None) -> str:
    """Replace the goal markets of `row` (a Hermès prediction) in place; return the source."""
    if row.get("p_home") is None:
        return "hermes"
    has_odds = m1x2 is not None and all(v is not None for v in m1x2)
    if has_odds and over is not None:
        start = (row.get("exp_home_goals") or 1.4, row.get("exp_away_goals") or 1.1)
        row.update(bookmaker_goals(tuple(float(v) for v in m1x2), over, start))
        return "bookmakers"
    if has_odds and lgbm and lgbm.get("p_over_2_5") is not None:
        row.update({k: lgbm[k] for k in GOAL_KEYS if lgbm.get(k) is not None})
        return "lightgbm"
    return "hermes"
