"""Scenarios that adjust the market price (D72, step 1).

The market 1X2 is the starting point. Each scenario of `stories.SCENARIOS` that applies
to a side moves that side's score by a learnt weight:

    score_home = log p_home + sum(w_k * flag_k(home side))
    score_away = log p_away + sum(w_k * flag_k(away side))
    score_draw = log p_draw
    p = softmax(scores)

The weights come from maximum likelihood on past matches only, with a ridge penalty that
keeps them near 0 until many matches support them. The test is walk-forward: for each
season, weights learnt on the earlier seasons, scored on that season against the market.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from footintel.analysis.stories import SCENARIOS, flags, team_rows

CODES = [s.code for s in SCENARIOS]


@dataclass
class MatchSet:
    match_id: np.ndarray
    season: np.ndarray
    competition: np.ndarray
    logp: np.ndarray  # (n, 3) log market probabilities home, draw, away
    fh: np.ndarray  # (n, k) scenario flags of the home side
    fa: np.ndarray  # (n, k) scenario flags of the away side
    y: np.ndarray  # (n,) 0 home, 1 draw, 2 away; -1 not played


def match_set(features: pd.DataFrame) -> MatchSet:
    rows = team_rows(features)
    fl = flags(rows).astype(float)
    home, away = rows["is_home"].to_numpy(), ~rows["is_home"].to_numpy()
    h = rows[home].set_index("match_id")
    a = rows[away].set_index("match_id")
    fh = fl[home].set_index(h.index)[CODES]
    fa = fl[away].set_index(a.index)[CODES].reindex(h.index)
    p = np.column_stack([h["p_win"], h["p_draw"], a["p_win"].reindex(h.index)])
    p = p / p.sum(axis=1, keepdims=True)
    hg, ag = h["home_goals"].to_numpy(), h["away_goals"].to_numpy()
    y = np.where(np.isnan(hg) | np.isnan(ag), -1, np.where(hg > ag, 0, np.where(hg == ag, 1, 2)))
    ok = np.isfinite(p).all(axis=1) & (p > 0).all(axis=1)
    return MatchSet(h.index.to_numpy()[ok], h["season"].to_numpy()[ok], h["competition"].to_numpy()[ok],
                    np.log(p[ok]), fh.to_numpy()[ok], fa.fillna(0).to_numpy()[ok], y[ok])


def probs(ms: MatchSet, w: np.ndarray, idx=slice(None)) -> np.ndarray:
    s = ms.logp[idx].copy()
    s[:, 0] += ms.fh[idx] @ w
    s[:, 2] += ms.fa[idx] @ w
    s -= s.max(axis=1, keepdims=True)
    e = np.exp(s)
    return e / e.sum(axis=1, keepdims=True)


def fit(ms: MatchSet, idx: np.ndarray, ridge: float = 200.0) -> np.ndarray:
    """Weights on matches `idx` (played ones). Ridge: a weight needs many matches to move."""
    idx = idx[ms.y[idx] >= 0]
    y = ms.y[idx]
    onehot = np.eye(3)[y]

    def loss(w):
        p = probs(ms, w, idx)
        nll = -np.log(p[np.arange(len(y)), y]).sum() + 0.5 * ridge * (w @ w)
        g_score = p - onehot  # d nll / d score
        grad = ms.fh[idx].T @ g_score[:, 0] + ms.fa[idx].T @ g_score[:, 2] + ridge * w
        return nll, grad

    return minimize(loss, np.zeros(len(CODES)), jac=True, method="L-BFGS-B").x


def log_loss(p: np.ndarray, y: np.ndarray) -> float:
    return float(-np.log(p[np.arange(len(y)), y]).mean())


def walk_forward(ms: MatchSet, test_seasons: list[int], ridge: float = 200.0) -> pd.DataFrame:
    """Per test season: matches, market log loss, adjusted log loss, and the weights used."""
    out = []
    for s in test_seasons:
        train = np.where((ms.season < s) & (ms.y >= 0))[0]
        test = np.where((ms.season == s) & (ms.y >= 0))[0]
        if len(train) < 1000 or len(test) == 0:
            continue
        w = fit(ms, train, ridge)
        y = ms.y[test]
        market = np.exp(ms.logp[test])
        adj = probs(ms, w, test)
        touched = (ms.fh[test].any(axis=1) | ms.fa[test].any(axis=1))
        out.append({"season": s, "n": len(test), "n_touched": int(touched.sum()),
                    "market": log_loss(market, y), "adjusted": log_loss(adj, y),
                    "max_shift": float(np.abs(adj - market).max()),
                    "mean_shift": float(np.abs(adj - market)[touched].mean()) if touched.any() else 0.0}
                   | {f"w_{c}": wi for c, wi in zip(CODES, w, strict=True)})
    return pd.DataFrame(out)


# --- Weekly learning and daily use (D72) ---------------------------------------------

WEIGHTS_FILE = "scenario_weights.json"
CHECK_SEASONS = 3  # the adjustment stays on only if it beat the market over these seasons
MAX_WEIGHT = 0.25  # about 5 points of probability at most per scenario
# Shown to the owner only when it matters: a weight of 0.05 or more, a move of 1 point or more.
NOTE_MIN_WEIGHT = 0.05
NOTE_MIN_SHIFT = 0.01


def learn(features: pd.DataFrame, current_season: int, ridge: float = 200.0) -> dict:
    """Self-check on the last seasons (walk-forward), then weights from all played matches.
    `active` is False when the adjustment did not beat the market in the self-check."""
    ms = match_set(features)
    check = walk_forward(ms, list(range(current_season - CHECK_SEASONS, current_season + 1)), ridge)
    n = int(check["n"].sum()) if len(check) else 0
    gain = float((check["n"] * (check["market"] - check["adjusted"])).sum() / n) if n else 0.0
    w = np.clip(fit(ms, np.where(ms.y >= 0)[0], ridge), -MAX_WEIGHT, MAX_WEIGHT)
    return {"weights": {c: round(float(x), 4) for c, x in zip(CODES, w, strict=True)},
            "n_matches": int((ms.y >= 0).sum()), "check_matches": n,
            "check_gain_per_1000": round(gain * 1000, 3), "active": gain > 0,
            "seasons_won": int((check["adjusted"] < check["market"]).sum()) if len(check) else 0,
            "seasons_checked": len(check)}


def save(result: dict, artifacts_dir) -> None:
    import json
    from datetime import UTC, datetime
    from pathlib import Path

    Path(artifacts_dir).mkdir(parents=True, exist_ok=True)
    (Path(artifacts_dir) / WEIGHTS_FILE).write_text(json.dumps(result | {"learnt_at": datetime.now(UTC).isoformat()}))


def load(artifacts_dir) -> dict | None:
    import json
    from pathlib import Path

    p = Path(artifacts_dir) / WEIGHTS_FILE
    return json.loads(p.read_text()) if p.exists() else None


def _side_rows(snap: dict, p_home: float, p_draw: float, p_away: float) -> pd.DataFrame:
    cols = ["form5_ppg", "gf5", "ga5", "sot5_for", "sot5_against", "rest_days", "games_14d", "europe_7d"]
    out = []
    for s, o, home, p in (("h", "a", True, p_home), ("a", "h", False, p_away)):
        r = {"is_home": home, "p_win": p, "p_draw": p_draw}
        for c in cols:
            r[f"{c}_s"], r[f"{c}_o"] = snap.get(f"{c}_{s}"), snap.get(f"{c}_{o}")
        out.append(r)
    return pd.DataFrame(out).astype({f"{c}_{x}": float for c in cols for x in "so"})


def adjust(p_home: float, p_away: float, snap: dict | None, learnt: dict | None,
           home: str, away: str) -> tuple[float, float, list[dict]]:
    """Market 1X2 moved by the scenarios that apply. Returns the new home and away win
    probabilities and one plain sentence per scenario that moved them."""
    if not snap or not learnt or not learnt.get("active"):
        return p_home, p_away, []
    from footintel.analysis.stories import SCENARIO_BY_CODE

    p_draw = max(1e-6, 1 - p_home - p_away)
    fl = flags(_side_rows(snap, p_home, p_draw, p_away))
    w = np.array([learnt["weights"].get(c, 0.0) for c in CODES])
    logp = np.log([p_home, p_draw, p_away])
    s = logp + np.array([fl.iloc[0][CODES].to_numpy(float) @ w, 0.0, fl.iloc[1][CODES].to_numpy(float) @ w])
    p = np.exp(s - s.max())
    p /= p.sum()
    notes = []
    for i, team in ((0, home), (1, away)):
        for c in CODES:
            if fl.iloc[i][c] and abs(learnt["weights"].get(c, 0.0)) >= NOTE_MIN_WEIGHT:
                up = learnt["weights"][c] > 0
                notes.append({"team": team, "scenario": c,
                              "text": f"{team} : {SCENARIO_BY_CODE[c].label}. Dans ce cas, par le passé, "
                                      f"l'équipe a {'gagné un peu plus' if up else 'gagné un peu moins'} "
                                      f"souvent que ne le disaient les bookmakers."})
    if notes and max(abs(p[0] - p_home), abs(p[2] - p_away)) < NOTE_MIN_SHIFT:
        notes = []
    if notes:
        side, base = (0, p_home) if abs(p[0] - p_home) >= abs(p[2] - p_away) else (2, p_away)
        team = home if side == 0 else away
        notes.append({"team": team, "scenario": "total",
                      "text": f"Résultat : la chance de victoire de {team} passe de {base:.0%} à {p[side]:.0%}."})
    return float(p[0]), float(p[2]), notes
