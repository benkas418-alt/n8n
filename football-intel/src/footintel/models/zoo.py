"""Named model configurations. A registry name always builds the same configuration."""

from collections.abc import Callable

import pandas as pd

from footintel.models.base import GOAL_COLS, PROB_COLS, ProbModel
from footintel.models.baseline import EloPoisson, MarketImplied, NaiveFrequency, PoissonFeatures
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


class RoutedByOdds(ProbModel):
    """Use the odds model where pre-match odds exist, the Elo model elsewhere.

    Backtest 2021-2025 (docs/RESULTS.md): one logistic model trained on every match
    learned a weak odds weight (many rows without odds) and lost to the market in
    domestic leagues; training it only on rows with odds removed that loss. Cups have
    no odds in our sources, so they go to the Elo-Poisson model."""

    family = "routed"

    def __init__(self, name: str):
        self.name = name
        self.with_odds = logistic(WITH_MARKET_FEATURES, f"{name}:with_odds")
        self.without_odds = EloPoisson()
        self.features = sorted(set(self.with_odds.features) | set(self.without_odds.features))

    def fit(self, train: pd.DataFrame) -> "RoutedByOdds":
        self.with_odds.fit(train[train["mkt_p_home"].notna()])
        self.without_odds.fit(train)
        return self

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        goals = self.without_odds.predict(df)
        out = goals[PROB_COLS].copy()
        has_odds = df["mkt_p_home"].notna()
        if has_odds.any():
            out.loc[has_odds, PROB_COLS] = self.with_odds.predict(df[has_odds])[PROB_COLS]
        return pd.concat([out, goals[GOAL_COLS]], axis=1)

    def params(self) -> dict:
        return {"with_odds": self.with_odds.params(), "without_odds": self.without_odds.params()}


class RoutedCompetitionAware(ProbModel):
    """Configuration chosen from the level study (docs/RESULTS.md, run 8):
    - with pre-match odds: logistic on Elo, team form and market features;
    - without odds (European cups): logistic on Elo and competition trends;
    - goal markets: Poisson GLM on Elo, competition trends and team attack/defence.
    Season phase is left out: it showed no gain and slightly worse goal log loss."""

    family = "routed"

    def __init__(self, name: str):
        from footintel.analysis.ablation import COMPETITION, GOAL_TEAM

        self.name = name
        self.with_odds = logistic(WITH_MARKET_FEATURES, f"{name}:with_odds")
        self.without_odds = logistic(COMPETITION, f"{name}:without_odds")
        self.goals = PoissonFeatures(f"{name}:goals", COMPETITION + GOAL_TEAM)
        self.features = sorted(set(self.with_odds.features) | set(self.without_odds.features)
                               | set(self.goals.features))

    def fit(self, train: pd.DataFrame) -> "RoutedCompetitionAware":
        self.with_odds.fit(train[train["mkt_p_home"].notna()])
        self.without_odds.fit(train)
        self.goals.fit(train)
        return self

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        out = self.without_odds.predict(df)[PROB_COLS].copy()
        has_odds = df["mkt_p_home"].notna()
        if has_odds.any():
            out.loc[has_odds, PROB_COLS] = self.with_odds.predict(df[has_odds])[PROB_COLS]
        return pd.concat([out, self.goals.predict(df)[GOAL_COLS]], axis=1)

    def params(self) -> dict:
        return {"with_odds": self.with_odds.params(), "without_odds": self.without_odds.params(),
                "goals": self.goals.params()}


MODEL_FACTORIES: dict[str, Callable[[], ProbModel]] = {
    "routed_competition": lambda: RoutedCompetitionAware("routed_competition"),
    "routed_odds_elo": lambda: RoutedByOdds("routed_odds_elo"),
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
