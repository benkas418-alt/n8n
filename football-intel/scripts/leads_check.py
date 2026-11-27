"""D112: the two leads of D111, rules fixed before looking at these seasons.
Lead 1: Hermès's mean home-win probability is above the observed rate and above the market's.
Lead 2: when Hermès gives the home side 3 to 8 points less than the market, Hermès's 1X2 log loss
is lower than the market's on those matches (paired, 95 % interval entirely below 0).

Run from football-intel/: python scripts/leads_check.py preds_2016_2020.pkl [preds_2026.pkl]
Each file is a pickled walk_forward() frame with market_implied and routed_competition."""
import pickle

import numpy as np
def boot(d, n=4000, seed=0):
    rng = np.random.default_rng(seed)
    return np.percentile([d[rng.integers(0, len(d), len(d))].mean() for _ in range(n)], [2.5, 97.5])
def run(path, label):
    with open(path, "rb") as fh:
        P = pickle.load(fh)
    H = P[P.model == "routed_competition"].set_index("match_id"); M = P[P.model == "market_implied"].set_index("match_id").dropna(subset=["p_home"])
    ids = M.index.intersection(H.index.dropna()); H, M = H.loc[ids].dropna(subset=["p_home"]), M.loc[ids]
    ids = H.index; M = M.loc[ids]
    y = np.where(H.home_goals > H.away_goals, 0, np.where(H.home_goals == H.away_goals, 1, 2))
    ph = H[["p_home", "p_draw", "p_away"]].to_numpy(); pm = M[["p_home", "p_draw", "p_away"]].to_numpy()
    n = len(y)
    lh = -np.log(np.clip(ph[np.arange(n), y], 1e-12, 1)); lm = -np.log(np.clip(pm[np.arange(n), y], 1e-12, 1))
    print(f"\n=== {label} : {n} matchs avec cotes ===")
    obs = (y == 0)
    dh, dm = ph[:, 0] - obs, pm[:, 0] - obs
    print(f"Piste 1 : victoire domicile annoncée Hermès {ph[:,0].mean()*100:.1f} %, marché {pm[:,0].mean()*100:.1f} %, réel {obs.mean()*100:.1f} %")
    print(f"   Hermès moins réel {dh.mean()*100:+.2f} pts IC {np.round(boot(dh)*100,2)} ; Hermès moins marché {(ph[:,0]-pm[:,0]).mean()*100:+.2f} pts IC {np.round(boot(ph[:,0]-pm[:,0])*100,2)}")
    for s in sorted(H.season.unique()):
        m = (H.season == s).to_numpy()
        print(f"   saison {s}: n={m.sum()} Hermès {ph[m,0].mean()*100:.1f} marché {pm[m,0].mean()*100:.1f} réel {obs[m].mean()*100:.1f}")
    gap = ph[:, 0] - pm[:, 0]
    sel = (gap > -.08) & (gap <= -.03)
    d = lh[sel] - lm[sel]
    ci = boot(d)
    print(f"Piste 2 : {sel.sum()} matchs où Hermès donne 3 à 8 pts de moins au domicile")
    print(f"   victoire domicile : Hermès {ph[sel,0].mean()*100:.1f} %, marché {pm[sel,0].mean()*100:.1f} %, réel {obs[sel].mean()*100:.1f} %")
    print(f"   écart de log loss Hermès moins marché {d.mean():+.4f} IC {np.round(ci,4)} -> {'CONFIRMÉE' if ci[1] < 0 else 'NON confirmée'}")
    for s in sorted(H.season.unique()):
        m = sel & (H.season == s).to_numpy()
        if m.sum():
            print(f"   saison {s}: n={m.sum()} Hermès {ph[m,0].mean()*100:.1f} marché {pm[m,0].mean()*100:.1f} réel {obs[m].mean()*100:.1f} écart {(lh[m]-lm[m]).mean():+.4f}")
    return ph, pm, y, H.season.to_numpy()
if __name__ == "__main__":
    import sys

    for path in sys.argv[1:]:
        run(path, path)
