"""D120: does Hermès do better than the market outside the four target leagues?

Run from football-intel/ with the database of a daily cycle:
    python scripts/other_leagues_check.py [out.pkl]

Same walk-forward as every Hermès test (train on the seasons before, judge one season),
2021-22 to 2025-26, but judged on the leagues that are not targets. Three prices per match:
Hermès (`routed_competition`), the Friday market (`market_implied`, the price Hermès reads)
and the closing market (bookmakers' average just before kick-off, margin removed by the
power method, D114). D116 found that late news weighs more in these leagues.

Rules fixed before the run:
- Main test, all these leagues together: Hermès gains on a price only under rule D9
  (paired 1X2 log loss at least 0.002 lower, 95 % interval entirely below 0).
- A single league is only a lead, never a decision: its 99 % interval must be entirely
  below 0 and the gain must be there in both halves (2021-2022 and 2023-2025).
"""

import pickle
import sys

import numpy as np
import pandas as pd
from sqlalchemy import text

sys.path.insert(0, "src")
from footintel.analysis.demargin import fair_probs
from footintel.cli import _features
from footintel.db.session import get_engine
from footintel.evaluation.backtest import PROB_COLS, walk_forward

TARGETS = {"ENG-PL", "ESP-LL", "ITA-SA", "GER-BL", "FRA-L1"}
SEASONS = [2021, 2022, 2023, 2024, 2025]
rng = np.random.default_rng(3)


def closing(engine, ids: list[int]) -> pd.DataFrame:
    sql = text("""SELECT match_id, selection, avg(price) price FROM odds_snapshots
                  WHERE market = '1X2' AND bookmaker = 'market_avg' AND snapshot_label = 'closing'
                    AND match_id = ANY(:ids) GROUP BY 1, 2""")
    with engine.connect() as c:
        df = pd.read_sql(sql, c, params={"ids": ids})
    wide = df.pivot_table(index="match_id", columns="selection", values="price").dropna()
    rows = []
    for mid, r in wide.iterrows():
        p = fair_probs([r["H"], r["D"], r["A"]])
        if p:
            rows.append({"match_id": mid, "p_home": p[0], "p_draw": p[1], "p_away": p[2]})
    return pd.DataFrame(rows)


def loss(frame: pd.DataFrame) -> pd.Series:
    y = np.select([frame.home_goals > frame.away_goals, frame.home_goals == frame.away_goals], [0, 1], 2)
    p = frame[PROB_COLS].to_numpy()[np.arange(len(frame)), y]
    return pd.Series(-np.log(np.clip(p, 1e-15, 1)), index=frame.index)


def ci(x: np.ndarray, level: float) -> tuple[float, float]:
    b = [x[rng.integers(0, len(x), len(x))].mean() for _ in range(2000)]
    a = (100 - level) / 2
    return float(np.percentile(b, a)), float(np.percentile(b, 100 - a))


def main(out: str | None) -> None:
    engine = get_engine()
    feats = _features(engine)
    feats["is_target"] = ~feats["competition"].isin(TARGETS)
    preds = walk_forward(feats, ["routed_competition", "market_implied"], SEASONS)
    if out:
        with open(out, "wb") as fh:
            pickle.dump(preds, fh)
    h = preds[preds.model == "routed_competition"].set_index("match_id").dropna(subset=PROB_COLS)
    f = preds[preds.model == "market_implied"].set_index("match_id").dropna(subset=PROB_COLS)
    c = closing(engine, [int(i) for i in h.index]).set_index("match_id")
    ids = h.index.intersection(f.index).intersection(c.index)
    h, f = h.loc[ids], f.loc[ids]
    c = c.loc[ids].join(h[["home_goals", "away_goals"]])
    d = pd.DataFrame({"league": h.competition, "season": h.season,
                      "h_f": loss(h) - loss(f), "h_c": loss(h) - loss(c), "f_c": loss(f) - loss(c)})
    print(f"Matches with Hermès, Friday and closing prices: {len(d)} in {d.league.nunique()} leagues")
    print("\nAll leagues together (negative = Hermès better; D9: <= -0.002 and 95 % interval below 0)")
    for col, name in (("h_f", "Hermès - Friday market"), ("h_c", "Hermès - closing market"),
                      ("f_c", "Friday - closing market")):
        lo, hi = ci(d[col].to_numpy(), 95)
        passed = d[col].mean() <= -0.002 and hi < 0
        print(f"  {name}: {d[col].mean():+.5f} [{lo:+.5f} ; {hi:+.5f}]  D9: {'yes' if passed else 'no'}")
    print("\nBy league (lead only if the 99 % interval is below 0 and both halves are negative)")
    for col, name in (("h_f", "Hermès - Friday"), ("h_c", "Hermès - closing")):
        print(f"  {name}")
        for lg, g in d.groupby("league"):
            lo, hi = ci(g[col].to_numpy(), 99)
            early = g.loc[g.season <= 2022, col].mean()
            late = g.loc[g.season >= 2023, col].mean()
            lead = hi < 0 and early < 0 and late < 0
            print(f"    {lg:9} n={len(g):5} {g[col].mean():+.5f} [{lo:+.5f} ; {hi:+.5f}] "
                  f"halves {early:+.5f} / {late:+.5f}{'  LEAD' if lead else ''}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
