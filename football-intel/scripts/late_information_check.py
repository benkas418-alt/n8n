"""D116: how much the 1X2 price learns between the Friday (or Tuesday) snapshot and kick-off, per league.
Gain = log loss of the Friday fair price minus log loss of the closing fair price, per match.
A positive gain means that news arrived late (line-ups, injuries, informed money).

Run from football-intel/: python scripts/late_information_check.py <DATA_DIR>/raw/football_data_uk"""

import glob
import sys

import numpy as np
import pandas as pd

from footintel.analysis.demargin import fair_probs

R = sys.argv[1]
NAMES = {
    "E0": "Premier League",
    "E1": "Championship",
    "E2": "League One",
    "E3": "League Two",
    "EC": "National League",
    "SP1": "Liga",
    "SP2": "Liga 2",
    "I1": "Serie A",
    "I2": "Serie B",
    "D1": "Bundesliga",
    "D2": "2. Bundesliga",
    "F1": "Ligue 1",
    "F2": "Ligue 2",
    "N1": "Eredivisie",
    "B1": "Belgique",
    "P1": "Portugal",
    "T1": "Turquie",
    "G1": "Grèce",
    "SC0": "Écosse 1",
    "SC1": "Écosse 2",
    "SC2": "Écosse 3",
    "SC3": "Écosse 4",
}
rows = []
for season in ["1920", "2021", "2122", "2223", "2324", "2425", "2526"]:
    for f in glob.glob(f"{R}/{season}/*.csv"):
        div = f.split("/")[-1][:-4]
        d = pd.read_csv(f, encoding="latin-1", on_bad_lines="skip")
        need = ["AvgH", "AvgD", "AvgA", "AvgCH", "AvgCD", "AvgCA", "FTR"]
        if not all(c in d for c in need):
            continue
        d = d.dropna(subset=need)
        for r in d.itertuples():
            a = fair_probs([r.AvgH, r.AvgD, r.AvgA])
            c = fair_probs([r.AvgCH, r.AvgCD, r.AvgCA])
            if a is None or c is None:
                continue
            k = {"H": 0, "D": 1, "A": 2}.get(r.FTR)
            if k is None:
                continue
            rows.append(
                (
                    div,
                    season,
                    -np.log(a[k]) + np.log(c[k]),
                    1 / r.AvgCH + 1 / r.AvgCD + 1 / r.AvgCA - 1,
                    abs(a[0] - c[0]) + abs(a[2] - c[2]),
                )
            )
df = pd.DataFrame(rows, columns=["div", "season", "gain", "margin", "move"])
rng = np.random.default_rng(0)
out = []
for div, g in df.groupby("div"):
    x = g.gain.to_numpy()
    bs = [x[rng.integers(0, len(x), len(x))].mean() for _ in range(1000)]
    out.append(
        (
            NAMES.get(div, div),
            len(x),
            1000 * x.mean(),
            1000 * np.percentile(bs, 2.5),
            1000 * np.percentile(bs, 97.5),
            100 * g.margin.mean(),
            100 * g.move.mean(),
        )
    )
o = pd.DataFrame(
    out,
    columns=[
        "ligue",
        "matchs",
        "gain_milliemes",
        "ic_bas",
        "ic_haut",
        "marge_cloture_%",
        "mouvement_pts",
    ],
)
print(o.sort_values("gain_milliemes", ascending=False).round(2).to_string(index=False))
x = df.gain.to_numpy()
print("toutes", len(x), round(1000 * x.mean(), 2))
