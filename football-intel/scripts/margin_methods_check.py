"""D114: which way of removing the bookmaker margin gives the truest probabilities?
Rules fixed before the run (28/11/2026):
- methods: proportional (current), power, Shin;
- data: average pre-match prices of football-data.co.uk, every league in the files;
- a method replaces proportional if, on 2016-2025, its 1X2 log loss is lower with a paired 95 %
  interval entirely below 0, and the 2026-27 difference has the same sign.

Run from football-intel/: python scripts/margin_methods_check.py [path to raw football_data_uk]"""
import glob
import sys

import numpy as np
import pandas as pd
from scipy.optimize import brentq

RAW = sys.argv[1] if len(sys.argv) > 1 else "data/raw/football_data_uk"


def proportional(q):
    return q / q.sum()


def power(q):
    k = brentq(lambda k: (q ** k).sum() - 1, 1.0, 10.0)
    return q ** k


def shin(q):
    s = q.sum()

    def probs(z):
        return (np.sqrt(z * z + 4 * (1 - z) * q * q / s) - z) / (2 * (1 - z))
    z = brentq(lambda z: probs(z).sum() - 1, 0.0, 0.4)
    return probs(z)


METHODS = {"proportionnelle": proportional, "puissance": power, "Shin": shin}


def boot(d, n=2000, seed=0):
    rng = np.random.default_rng(seed)
    return np.percentile([d[rng.integers(0, len(d), len(d))].mean() for _ in range(n)], [2.5, 97.5])


def pick(row, names):
    for n in names:
        v = row.get(n)
        if v is not None and not pd.isna(v):
            return float(v)
    return np.nan


def load():
    rows = []
    for path in sorted(glob.glob(f"{RAW}/*/*.csv")):
        season_dir = path.split("/")[-2]
        if not season_dir.isdigit() or len(season_dir) != 4:
            continue
        season = 2000 + int(season_dir[:2])
        if season < 2016:
            continue
        try:
            df = pd.read_csv(path, encoding="latin-1", on_bad_lines="skip")
        except (pd.errors.ParserError, UnicodeDecodeError, pd.errors.EmptyDataError) as exc:
            print(f"skipped {path}: {exc}")  # a broken file is skipped, never guessed
            continue
        for r in df.to_dict("records"):
            h = pick(r, ("AvgH", "BbAvH")); d = pick(r, ("AvgD", "BbAvD")); a = pick(r, ("AvgA", "BbAvA"))
            o = pick(r, ("Avg>2.5", "BbAv>2.5")); u = pick(r, ("Avg<2.5", "BbAv<2.5"))
            hg, ag = pick(r, ("FTHG",)), pick(r, ("FTAG",))
            if np.isnan([h, d, a, hg, ag]).any() or min(h, d, a) <= 1 or 1 / h + 1 / d + 1 / a <= 1.001:
                continue  # missing or margin-free prices: a data error, left out for every method
            rows.append({"season": season, "league": path.split("/")[-1][:-4], "h": h, "d": d, "a": a,
                         "o": o, "u": u, "hg": hg, "ag": ag})
    return pd.DataFrame(rows)


def main():
    X = load()
    y = np.where(X.hg > X.ag, 0, np.where(X.hg == X.ag, 1, 2))
    q = 1 / X[["h", "d", "a"]].to_numpy()
    P = {m: np.array([f(r) for r in q]) for m, f in METHODS.items()}
    L = {m: -np.log(np.clip(p[np.arange(len(y)), y], 1e-12, 1)) for m, p in P.items()}
    past, now = (X.season < 2026).to_numpy(), (X.season == 2026).to_numpy()
    print(f"1X2 : {past.sum()} matchs 2016-2025, {now.sum()} matchs 2026-27")
    for m in ("puissance", "Shin"):
        d = L[m] - L["proportionnelle"]
        ci = boot(d[past])
        ok = ci[1] < 0 and d[now].mean() < 0
        print(f"  {m:10s} 2016-2025 écart {d[past].mean():+.5f} IC {np.round(ci, 5)} ; 2026-27 {d[now].mean():+.5f}"
              f" -> {'ADOPTÉE' if ok else 'non adoptée'}")
        for s in sorted(X.season.unique()):
            k = (X.season == s).to_numpy()
            print(f"      saison {s}: {d[k].mean():+.5f}")
    print("\nFavoris : issues annoncées entre 60 et 70 % (2016-2025)")
    oh = np.eye(3)[y]
    for m, p in P.items():
        sel = (p > .6) & (p <= .7) & past[:, None]
        print(f"  {m:15s} n={sel.sum():6d} annoncé {p[sel].mean()*100:.1f} % réel {oh[sel].mean()*100:.1f} %")
    for lo, hi in ((0, .1), (.1, .2)):
        print(f"Outsiders {int(lo*100)}-{int(hi*100)} % :")
        for m, p in P.items():
            sel = (p > lo) & (p <= hi) & past[:, None]
            print(f"  {m:15s} n={sel.sum():6d} annoncé {p[sel].mean()*100:.1f} % réel {oh[sel].mean()*100:.1f} %")
    ok = X.o.notna() & X.u.notna() & (X.o > 1) & (X.u > 1) & (1 / X.o + 1 / X.u > 1.001)
    Xo = X[ok]
    yo = ((Xo.hg + Xo.ag) > 2.5).astype(float).to_numpy()
    qo = 1 / Xo[["o", "u"]].to_numpy()
    po = {m: np.array([f(r) for r in qo])[:, 0] for m, f in METHODS.items()}
    lo_ = {m: -(yo * np.log(p) + (1 - yo) * np.log(1 - p)) for m, p in po.items()}
    pp, pn = (Xo.season < 2026).to_numpy(), (Xo.season == 2026).to_numpy()
    print(f"\nPlus de 2,5 buts : {pp.sum()} matchs 2016-2025, {pn.sum()} matchs 2026-27")
    for m in ("puissance", "Shin"):
        d = lo_[m] - lo_["proportionnelle"]
        ci = boot(d[pp])
        print(f"  {m:10s} 2016-2025 écart {d[pp].mean():+.5f} IC {np.round(ci, 5)} ; 2026-27 {d[pn].mean():+.5f}")


if __name__ == "__main__":
    main()
