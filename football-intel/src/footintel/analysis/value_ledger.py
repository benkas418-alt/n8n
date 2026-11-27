"""betPawa value ledger (D103): three separate data sets and three separate measures.

Data sets, never mixed:
- market observations: every betPawa price seen (`reference/betpawa_prices.csv`), history kept;
- real selections: the selections of the coupons really played (`reference/betpawa_coupon_legs.csv`);
- coupons: what was staked and paid (`reference/betpawa_coupons.csv`). Money is counted per coupon,
  never per selection, because the selections of one coupon win or lose together.

Measures, never mixed:
- EV at placement: price x fair probability known BEFORE the capture, minus 1;
- CLV: price x fair probability at the close (after the capture), minus 1;
- ROI: net gain / stakes of settled coupons.

Pure functions only: the database work stays in `scripts/betpawa_value.py`.
"""

from collections import defaultdict
from datetime import UTC, datetime, timedelta

import numpy as np

LOCAL = timedelta(hours=2)  # Africa/Lubumbashi, no daylight saving
SETTLED = {"gagné", "perdu", "remboursé", "annulé"}
REFUNDED = {"remboursé", "annulé"}
MIN_MATCHES_CI = 20
MIN_MATCHES_HINT = 100
BANDS = ((1.0, 1.30, "moins de 1,30"), (1.30, 1.60, "1,30 à 1,59"), (1.60, 2.00, "1,60 à 1,99"),
         (2.00, 1e9, "2,00 ou plus"))


def fair_probs(prices: dict[str, float]) -> tuple[float, ...] | None:
    """Probabilities without the bookmaker's margin (power method, D114), in the order of `prices`.
    None when a price is missing or not above 1: no fair price rather than a wrong one."""
    from footintel.analysis import demargin

    f = demargin.fair_probs(list(prices.values())) if prices else None
    return tuple(f) if f else None


def overround(prices: dict[str, float]) -> float:
    """The bookmaker's margin: sum of 1/price minus 1 (0.05 = 5 %)."""
    return sum(1 / p for p in prices.values()) - 1


def to_utc(stamp: str) -> datetime:
    """A capture time; without a zone it is Lubumbashi time, as the owner reads it on betPawa."""
    t = datetime.fromisoformat(stamp)
    return (t - LOCAL).replace(tzinfo=UTC) if t.tzinfo is None else t.astimezone(UTC)


def latest_per_key(rows: list[dict], key, when: str = "captured_at") -> list[dict]:
    """One row per key: the last one captured. The input list is left whole (history kept)."""
    last: dict = {}
    for r in rows:
        k = key(r)
        if k not in last or to_utc(r[when]) >= to_utc(last[k][when]):
            last[k] = r
    return list(last.values())


def ev(price: float, prob: float | None) -> float | None:
    return None if prob is None else price * prob - 1


def placement_reference(snapshots: list[tuple[datetime, float]], captured: datetime) -> tuple[datetime, float] | None:
    """The last (time, fair probability) known at the capture. Later snapshots are never used:
    a price seen after the bet was not known when it was placed."""
    def utc(t: datetime) -> datetime:  # a naive time here is UTC (database and snapshot labels)
        return t.replace(tzinfo=UTC) if t.tzinfo is None else t

    before = [s for s in snapshots if utc(s[0]) <= utc(captured)]
    return max(before, key=lambda s: utc(s[0])) if before else None


def cluster_ci(values: list[float], groups: list, samples: int = 2000, seed: int = 0) -> tuple[float, float]:
    """95 % interval of the mean when whole groups (matches, coupons) are resampled together."""
    by: dict = defaultdict(list)
    for v, g in zip(values, groups, strict=True):
        by[g].append(v)
    keys = list(by)
    rng = np.random.default_rng(seed)
    means = [np.mean([x for i in rng.choice(len(keys), len(keys)) for x in by[keys[i]]]) for _ in range(samples)]
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def coupon_money(coupons: list[dict]) -> dict:
    """Stakes, returns, net and ROI of settled coupons. A refunded or void coupon returns its stake."""
    out = {"coupons": len(coupons), "won": 0, "lost": 0, "refunded": 0, "open": 0,
           "stakes": 0.0, "returned": 0.0}
    for c in coupons:
        status, stake = c["status"], float(c["stake_fc"])
        if status not in SETTLED:
            out["open"] += 1
            continue
        out["stakes"] += stake
        if status in REFUNDED:
            out["refunded"] += 1
            out["returned"] += stake
        elif status == "gagné":
            out["won"] += 1
            out["returned"] += float(c["payout_fc"])
        else:
            out["lost"] += 1
    out["net"] = out["returned"] - out["stakes"]
    out["roi"] = out["net"] / out["stakes"] if out["stakes"] else None
    return out


def coupon_roi_ci(coupons: list[dict], samples: int = 2000, seed: int = 0) -> tuple[float, float] | None:
    """95 % interval of the ROI, resampling whole coupons (ratio of sums, as the ROI itself)."""
    settled = [c for c in coupons if c["status"] in SETTLED]
    if len(settled) < 2:
        return None
    stake = np.array([float(c["stake_fc"]) for c in settled])
    back = np.array([float(c["stake_fc"]) if c["status"] in REFUNDED else float(c["payout_fc"] or 0)
                     if c["status"] == "gagné" else 0.0 for c in settled])
    rng = np.random.default_rng(seed)
    rois = []
    for _ in range(samples):
        i = rng.integers(0, len(settled), len(settled))
        rois.append(back[i].sum() / stake[i].sum() - 1)
    return float(np.percentile(rois, 2.5)), float(np.percentile(rois, 97.5))


def sample_warning(n_matches: int) -> str:
    """Plain words on what a sample can say."""
    if n_matches < MIN_MATCHES_CI:
        return f"échantillon trop faible ({n_matches} matchs) : aucune conclusion possible"
    if n_matches < MIN_MATCHES_HINT:
        return f"indicatif seulement ({n_matches} matchs)"
    return ""


def odds_band(price: float) -> str:
    return next(label for lo, hi, label in BANDS if lo <= price < hi)


def settlement_agrees(ours: int | None, betpawa: str) -> bool | None:
    """Our settlement of a selection against betPawa's. None when one of them is unknown."""
    if ours is None or betpawa not in ("gagné", "perdu"):
        return None
    return ours == (1 if betpawa == "gagné" else 0)
