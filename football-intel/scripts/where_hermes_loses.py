"""D111: where does Hermès lose against the market? Same priced matches, walk-forward.

Run from football-intel/: python scripts/where_hermes_loses.py preds.pkl
`preds.pkl` is a pickled walk_forward() frame with the models market_implied and
routed_competition (for example 2021-2025, as in docs/RESULTS.md)."""
import pickle
import sys

import numpy as np
import pandas as pd
from sqlalchemy import text

sys.path.insert(0, "src")
from footintel.db.session import get_engine


def ll(q, y):
    q = np.clip(np.asarray(q, float), 1e-6, 1 - 1e-6)
    return -(y * np.log(q) + (1 - y) * np.log(1 - q))


def boot(d, n=2000, seed=0):
    rng = np.random.default_rng(seed)
    return np.percentile([d[rng.integers(0, len(d), len(d))].mean() for _ in range(n)], [2.5, 97.5])


def market_over(engine, ids, label):
    q = text("""SELECT match_id, max(price) FILTER (WHERE selection='over') o, max(price) FILTER (WHERE selection='under') u
                FROM odds_snapshots WHERE market='OU2.5' AND bookmaker='market_avg' AND snapshot_label=:l
                AND match_id = ANY(:ids) GROUP BY match_id""")
    with engine.connect() as c:
        r = pd.read_sql(q, c, params={"l": label, "ids": list(map(int, ids))}).dropna()
    r = r[(r.o > 1) & (r.u > 1)]
    return dict(zip(r.match_id, (1 / r.o) / (1 / r.o + 1 / r.u)))


with open(sys.argv[1], "rb") as fh:
    P = pickle.load(fh)
H = P[P.model == "routed_competition"].set_index("match_id"); M = P[P.model == "market_implied"].set_index("match_id").dropna(subset=["p_home"])
ids = M.index.intersection(H.index); H, M = H.loc[ids], M.loc[ids]
y = np.where(H.home_goals > H.away_goals, 0, np.where(H.home_goals == H.away_goals, 1, 2))
ph = H[["p_home", "p_draw", "p_away"]].to_numpy(); pm = M[["p_home", "p_draw", "p_away"]].to_numpy()
lh = -np.log(np.clip(ph[np.arange(len(y)), y], 1e-12, 1)); lm = -np.log(np.clip(pm[np.arange(len(y)), y], 1e-12, 1))
d = lh - lm
oh = np.eye(3)[y]; bh = ((ph - oh) ** 2).sum(1); bm = ((pm - oh) ** 2).sum(1)
print(f"1X2, {len(d)} matchs : log loss Hermès {lh.mean():.4f} marché {lm.mean():.4f} écart {d.mean():+.4f} IC {np.round(boot(d),4)}")
print(f"      Brier Hermès {bh.mean():.4f} marché {bm.mean():.4f} écart {(bh-bm).mean():+.4f} IC {np.round(boot(bh-bm),4)}")
def table(name, key):
    print(f"\n-- par {name} (écart positif = Hermès moins bon) --")
    for k, idx in pd.Series(range(len(d)), index=key).groupby(level=0):
        i = idx.to_numpy()
        if len(i) < 150: continue
        ci = boot(d[i], 1000)
        flag = " <== Hermès perd" if ci[0] > 0 else (" <== Hermès gagne" if ci[1] < 0 else "")
        print(f"  {k!s:22s} n={len(i):5d} écart {d[i].mean():+.4f} IC {np.round(ci,4)}{flag}")
table("compétition", H.competition.to_numpy())
table("saison", H.season.to_numpy())
fav = pm.max(1)
table("force du favori (marché)", pd.cut(fav, [0, .45, .55, .65, .75, 1], labels=["<45 %", "45-55 %", "55-65 %", "65-75 %", ">75 %"]).astype(str))
table("favori", np.where(pm[:, 0] >= pm[:, 2], "favori à domicile", "favori à l'extérieur"))
gap = ph - pm
table("désaccord sur le favori", pd.cut(np.abs(gap[:, 0] - gap[:, 2]), [-1, .04, .08, .15, 2], labels=["<4 pts", "4-8 pts", "8-15 pts", ">15 pts"]).astype(str))
print("\n-- biais : probabilité annoncée moyenne contre réalité, par issue --")
for j, nm in enumerate(("domicile", "nul", "extérieur")):
    print(f"  {nm:9s} Hermès {ph[:, j].mean()*100:.1f} %  marché {pm[:, j].mean()*100:.1f} %  réel {(y == j).mean()*100:.1f} %")
print("\n-- quand Hermès s'écarte du marché, qui a raison ? (sur la victoire domicile) --")
for lo, hi in ((-1, -.08), (-.08, -.03), (-.03, .03), (.03, .08), (.08, 1)):
    m = (gap[:, 0] > lo) & (gap[:, 0] <= hi)
    print(f"  Hermès {lo*100:+.0f}..{hi*100:+.0f} pts vs marché: n={m.sum():5d}  Hermès {ph[m,0].mean()*100:.1f} %  marché {pm[m,0].mean()*100:.1f} %  réel {(y[m]==0).mean()*100:.1f} %")
eng = get_engine()
mk = market_over(eng, list(ids), "pre_closing")
o_ids = [i for i in ids if i in mk]
Ho = H.loc[o_ids]; yo = ((Ho.home_goals + Ho.away_goals) > 2.5).astype(float).to_numpy()
mo = np.array([mk[i] for i in o_ids]); do = ll(Ho.p_over_2_5.to_numpy(), yo) - ll(mo, yo)
print(f"\n-- plus de 2,5 buts, Hermès contre bookmakers, {len(o_ids)} matchs : écart {do.mean():+.4f} IC {np.round(boot(do),4)} --")
for k, idx in pd.Series(range(len(do)), index=Ho.competition.to_numpy()).groupby(level=0):
    i = idx.to_numpy()
    if len(i) >= 150:
        ci = boot(do[i], 1000); print(f"  {k:22s} n={len(i):5d} écart {do[i].mean():+.4f} IC {np.round(ci,4)}{' <== Hermès perd' if ci[0] > 0 else ''}")
print(f"  biais : Hermès annonce {Ho.p_over_2_5.mean()*100:.1f} %, bookmakers {mo.mean()*100:.1f} %, réel {yo.mean()*100:.1f} %")
