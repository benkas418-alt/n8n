"""D113: calibration of the 1X2 by probability band, Hermès against the market, with Wilson
intervals. Every outcome of every match is one point (home, draw, away).

Run from football-intel/: python scripts/calibration_1x2.py preds_a.pkl [preds_b.pkl ...]
Each file is a pickled walk_forward() frame with market_implied and routed_competition."""
import pickle
import sys

import numpy as np
import pandas as pd
from statsmodels.stats.proportion import proportion_confint

BANDS = [0, .1, .2, .3, .4, .5, .6, .7, .8, 1]


def load(paths):
    frames = []
    for path in paths:
        with open(path, "rb") as fh:
            frames.append(pickle.load(fh))
    p = pd.concat(frames)
    h = p[p.model == "routed_competition"].set_index("match_id").dropna(subset=["p_home"])
    m = p[p.model == "market_implied"].set_index("match_id").dropna(subset=["p_home"])
    ids = h.index.intersection(m.index)
    return h.loc[ids], m.loc[ids]


def points(frame):
    y = np.where(frame.home_goals > frame.away_goals, 0, np.where(frame.home_goals == frame.away_goals, 1, 2))
    probs = frame[["p_home", "p_draw", "p_away"]].to_numpy()
    return probs.ravel(), (np.eye(3)[y]).ravel()


def table(name, p, y):
    df = pd.DataFrame({"p": p, "y": y})
    df["band"] = pd.cut(df.p, BANDS)
    print(f"\n{name}")
    worst = 0.0
    for band, g in df.groupby("band", observed=True):
        lo, hi = proportion_confint(int(g.y.sum()), len(g), method="wilson")
        inside = lo <= g.p.mean() <= hi
        worst = max(worst, abs(g.p.mean() - g.y.mean()))
        print(f"  {band!s:12s} n={len(g):6d} annoncé {g.p.mean()*100:5.1f} % réel {g.y.mean()*100:5.1f} %"
              f" (intervalle {lo*100:.1f}-{hi*100:.1f} %){'' if inside else '  <== hors intervalle'}")
    print(f"  plus grand écart annoncé-réel : {worst*100:.1f} points")


if __name__ == "__main__":
    h, m = load(sys.argv[1:])
    print(f"{len(h)} matchs avec cotes, saisons {sorted(h.season.unique())}")
    table("Hermès", *points(h))
    table("Marché (cotes sans marge)", *points(m))
