"""Common interface and goal-market helpers for all prediction models."""

from abc import ABC, abstractmethod

import numpy as np
import pandas as pd
from scipy.stats import poisson

CLASSES = ["H", "D", "A"]
PROB_COLS = ["p_home", "p_draw", "p_away"]
GOAL_COLS = ["exp_home_goals", "exp_away_goals", "p_over_1_5", "p_over_2_5", "p_over_3_5", "p_btts"]
MAX_GOALS = 10


def encode_result(df: pd.DataFrame) -> np.ndarray:
    """0 = home win, 1 = draw, 2 = away win."""
    hg, ag = df["home_goals"].to_numpy(), df["away_goals"].to_numpy()
    return np.where(hg > ag, 0, np.where(hg == ag, 1, 2))


def score_matrix(lam_home: float, lam_away: float) -> np.ndarray:
    goals = np.arange(MAX_GOALS + 1)
    m = np.outer(poisson.pmf(goals, lam_home), poisson.pmf(goals, lam_away))
    return m / m.sum()


def markets_from_lambdas(lam_home: np.ndarray, lam_away: np.ndarray) -> pd.DataFrame:
    rows = []
    goals = np.arange(MAX_GOALS + 1)
    total = goals[:, None] + goals[None, :]
    for lh, la in zip(lam_home, lam_away, strict=True):
        m = score_matrix(lh, la)
        rows.append({
            "p_home": np.tril(m, -1).sum(),
            "p_draw": np.trace(m),
            "p_away": np.triu(m, 1).sum(),
            "exp_home_goals": lh,
            "exp_away_goals": la,
            "p_over_1_5": m[total > 1.5].sum(),
            "p_over_2_5": m[total > 2.5].sum(),
            "p_over_3_5": m[total > 3.5].sum(),
            "p_btts": m[1:, 1:].sum(),
        })
    return pd.DataFrame(rows)


class ProbModel(ABC):
    name: str
    family: str
    features: list[str] = []

    @abstractmethod
    def fit(self, train: pd.DataFrame) -> "ProbModel": ...

    @abstractmethod
    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """Return PROB_COLS (rows sum to 1, or NaN when the model cannot predict) and,
        when supported, GOAL_COLS. The index matches `df`."""

    def params(self) -> dict:
        return {}
