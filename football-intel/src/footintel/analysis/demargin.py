"""Bookmaker margin removal (D114).

The "power" method finds k such that the prices' implied probabilities raised to k sum to 1.
It takes more margin from outsiders than from favourites, as bookmakers do. Tested on 76,557
matches (2016-2025) and 2,075 of 2026-27: truer than the proportional method in 9 seasons out
of 10 and on 2026-27; favourites announced at 60-70 % win 64.9 % of the time with it, 67.8 %
with the proportional method (docs/RESULTS.md, scripts/margin_methods_check.py).

Model inputs (`features.builder.market_probabilities`) keep the proportional method: changing
them is a model change and needs its own test.
"""

from collections.abc import Sequence

from scipy.optimize import brentq


def fair_probs(prices: Sequence[float]) -> list[float] | None:
    """Fair probabilities from decimal prices, in the same order. None when a price is missing
    or not above 1. Prices without a margin are only normalised."""
    if not prices or any(p is None or p <= 1 for p in prices):
        return None
    q = [1 / p for p in prices]
    total = sum(q)
    if total <= 1.0001:
        return [x / total for x in q]
    k = brentq(lambda k: sum(x ** k for x in q) - 1, 1.0, 50.0)
    out = [x ** k for x in q]
    s = sum(out)
    return [x / s for x in out]
