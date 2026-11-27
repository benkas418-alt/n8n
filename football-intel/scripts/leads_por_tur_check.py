"""D120, second part: are the Portugal and Turkey leads real on seasons never used to find them?

Run from football-intel/ with the database of a daily cycle:
    python scripts/leads_por_tur_check.py

The first part (scripts/other_leagues_check.py, 2021-2025) found Hermès better than the Friday
price in POR-PL and TUR-SL only. Same walk-forward here on 2016-2020 (independent seasons)
and on 2026-27 so far (reported, too small to decide).

Rules fixed before the run, for each league, on 2016-2020:
1. Hermès's paired 1X2 log loss minus the Friday price's is below 0 with a 95 % interval
   entirely below 0.
2. Hermès's picks gain on the closing price: a pick is an outcome where Hermès's probability
   times the Friday average price is 1.03 or more; its closing-line value is the Friday price
   times Pinnacle's closing fair probability (power method) minus 1. Mean above 0 with a 95 %
   interval entirely above 0.
A lead is confirmed only if both hold. Even then the price is a bookmakers' average, not
betPawa's: a confirmed lead is a reason to check betPawa's prices in that league.
"""

import sys

import numpy as np
import pandas as pd
from sqlalchemy import text

sys.path.insert(0, "src")
from footintel.analysis.demargin import fair_probs
from footintel.cli import _features
from footintel.db.session import get_engine
from footintel.evaluation.backtest import PROB_COLS, walk_forward

LEAGUES = ("POR-PL", "TUR-SL")
SEL = {"H": "p_home", "D": "p_draw", "A": "p_away"}
rng = np.random.default_rng(11)


def prices(engine, ids: list[int]) -> tuple[pd.DataFrame, pd.DataFrame]:
    sql = text("""SELECT match_id, bookmaker, snapshot_label, selection, avg(price) price FROM odds_snapshots
                  WHERE market = '1X2' AND match_id = ANY(:ids)
                    AND ((bookmaker = 'market_avg' AND snapshot_label = 'pre_closing')
                         OR (bookmaker = 'pinnacle' AND snapshot_label = 'closing'))
                  GROUP BY 1, 2, 3, 4""")
    with engine.connect() as c:
        df = pd.read_sql(sql, c, params={"ids": ids})
    friday = df[df.bookmaker == "market_avg"].pivot_table(index="match_id", columns="selection", values="price")
    pin = df[df.bookmaker == "pinnacle"].pivot_table(index="match_id", columns="selection", values="price").dropna()
    fair = {mid: fair_probs([r["H"], r["D"], r["A"]]) for mid, r in pin.iterrows()}
    close = pd.DataFrame({mid: dict(zip("HDA", p, strict=True)) for mid, p in fair.items() if p}).T
    return friday, close


def loss(frame: pd.DataFrame) -> np.ndarray:
    y = np.select([frame.home_goals > frame.away_goals, frame.home_goals == frame.away_goals], [0, 1], 2)
    return -np.log(np.clip(frame[PROB_COLS].to_numpy()[np.arange(len(frame)), y], 1e-15, 1))


def ci(x: np.ndarray) -> tuple[float, float]:
    b = [x[rng.integers(0, len(x), len(x))].mean() for _ in range(3000)]
    return float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


def judge(preds: pd.DataFrame, engine, label: str) -> None:
    friday, close = prices(engine, [int(i) for i in preds.match_id.unique()])
    print(f"\n== {label}")
    for lg in LEAGUES:
        p = preds[preds.competition == lg]
        h = p[p.model == "routed_competition"].set_index("match_id").dropna(subset=PROB_COLS)
        f = p[p.model == "market_implied"].set_index("match_id").dropna(subset=PROB_COLS)
        ids = h.index.intersection(f.index)
        if len(ids) < 30:
            print(f"  {lg}: {len(ids)} matches, too few")
            continue
        d = loss(h.loc[ids]) - loss(f.loc[ids])
        lo, hi = ci(d)
        rule1 = d.mean() < 0 and hi < 0
        clv = []
        for mid in ids.intersection(friday.index).intersection(close.index):
            for s, col in SEL.items():
                price = friday.loc[mid, s]
                if pd.notna(price) and h.loc[mid, col] * price >= 1.03:
                    clv.append(price * close.loc[mid, s] - 1)
        clv = np.array(clv)
        line = (f"  {lg}: n={len(ids)}  Hermès - Friday {d.mean():+.5f} [{lo:+.5f} ; {hi:+.5f}]"
                f" rule 1: {'yes' if rule1 else 'no'}")
        if len(clv) >= 30:
            clo, chi = ci(clv)
            rule2 = clv.mean() > 0 and clo > 0
            line += (f" | picks {len(clv)}, closing-line value {clv.mean():+.2%} [{clo:+.2%} ; {chi:+.2%}]"
                     f" rule 2: {'yes' if rule2 else 'no'}")
            if label.startswith("2016"):
                line += f"  => {'CONFIRMED' if rule1 and rule2 else 'not confirmed'}"
        else:
            line += f" | {len(clv)} picks with a closing price, too few"
        print(line)


def main() -> None:
    engine = get_engine()
    feats = _features(engine)
    feats["is_target"] = feats["competition"].isin(LEAGUES)
    judge(walk_forward(feats, ["routed_competition", "market_implied"], [2016, 2017, 2018, 2019, 2020]),
          engine, "2016-2020 (decides)")
    judge(walk_forward(feats, ["routed_competition", "market_implied"], [2026]), engine, "2026-27 so far (reported)")


if __name__ == "__main__":
    main()
