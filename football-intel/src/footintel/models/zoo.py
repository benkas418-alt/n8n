"""Named model configurations. A registry name always builds the same configuration."""

from collections.abc import Callable

import pandas as pd

from footintel.models.base import GOAL_COLS, PROB_COLS, ProbModel
from footintel.models.baseline import EloPoisson, MarketImplied, NaiveFrequency
from footintel.models.ml import CORE_FEATURES, WITH_MARKET_FEATURES, logistic, random_forest, xgboost

class Composite(ProbModel):
    """1X2 from one model, goal markets from another. Versioned as one unit."""

    family = "composite"

    def __init__(self, name: str, outcome: ProbModel, goals: ProbModel):
        self.name, self.outcome, self.goals = name, outcome, goals
        self.features = sorted(set(outcome.features) | set(goals.features))

    def fit(self, train: pd.DataFrame) -> "Composite":
        self.outcome.fit(train)
        self.goals.fit(train)
        return self

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        return pd.concat([self.outcome.predict(df)[PROB_COLS], self.goals.predict(df)[GOAL_COLS]],
                         axis=1)

    def params(self) -> dict:
        return {"outcome": self.outcome.name, "outcome_params": self.outcome.params(),
                "goals": self.goals.name, "goals_params": self.goals.params()}


MODEL_FACTORIES: dict[str, Callable[[], ProbModel]] = {
    "logreg_market_goals": lambda: Composite(
        "logreg_market_goals", logistic(WITH_MARKET_FEATURES, "logreg_market"), EloPoisson()),
    "logreg_core_goals": lambda: Composite(
        "logreg_core_goals", logistic(CORE_FEATURES, "logreg_core"), EloPoisson()),
    "naive_frequency": NaiveFrequency,
    "elo_poisson": EloPoisson,
    "market_implied": MarketImplied,
    "logreg_core": lambda: logistic(CORE_FEATURES, "logreg_core"),
    "logreg_market": lambda: logistic(WITH_MARKET_FEATURES, "logreg_market"),
    "rf_core": lambda: random_forest(CORE_FEATURES, "rf_core"),
    "xgb_core": lambda: xgboost(CORE_FEATURES, "xgb_core"),
}

# Reference models are compared against, never deployed for predictions.
REFERENCE_MODELS = {"naive_frequency", "market_implied"}


def build(name: str) -> ProbModel:
    try:
        return MODEL_FACTORIES[name]()
    except KeyError:
        raise ValueError(f"Unknown model {name!r}. Known: {sorted(MODEL_FACTORIES)}") from None
