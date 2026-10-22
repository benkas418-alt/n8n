"""Named model configurations. A registry name always builds the same configuration."""

from collections.abc import Callable

import numpy as np
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

    def __init__(self, name: str, trend_groups: tuple[str, ...] = (), dixon_coles: bool = False,
                 calibrate_without_odds: bool = False):
        from footintel.analysis.ablation import COMPETITION, GOAL_TEAM
        from footintel.features.trend_features import group_columns

        self.name, self.trend_groups = name, tuple(trend_groups)
        extra = [c for g in trend_groups for c in group_columns(g)]
        self.with_odds = logistic(WITH_MARKET_FEATURES, f"{name}:with_odds")
        self.without_odds = logistic(COMPETITION + extra, f"{name}:without_odds")
        self.goals = PoissonFeatures(f"{name}:goals", COMPETITION + GOAL_TEAM + extra,
                                     dixon_coles=dixon_coles)
        self.calibrate_without_odds, self.temperature_ = calibrate_without_odds, 1.0
        self.features = sorted(set(self.with_odds.features) | set(self.without_odds.features)
                               | set(self.goals.features))

    def fit(self, train: pd.DataFrame) -> "RoutedCompetitionAware":
        self.with_odds.fit(train[train["mkt_p_home"].notna()])
        if self.calibrate_without_odds:
            self.temperature_ = self._fit_temperature(train)
        self.without_odds.fit(train)
        self.goals.fit(train)
        return self

    def _fit_temperature(self, train: pd.DataFrame) -> float:
        """Temperature for matches without odds, fitted out of sample on the training window:
        fit on the earliest 80 % of dates, score the matches without odds in the rest."""
        import copy

        from scipy.optimize import minimize_scalar

        from footintel.models.base import encode_result

        cut = train["kickoff_date"].quantile(0.8)
        early, late = train[train["kickoff_date"] <= cut], train[train["kickoff_date"] > cut]
        late = late[late["mkt_p_home"].isna() & late["home_goals"].notna()]
        if len(late) < 100:
            return 1.0
        logp = np.log(copy.deepcopy(self.without_odds).fit(early).predict(late)[PROB_COLS]
                      .to_numpy(float).clip(1e-12, 1))
        y = encode_result(late)

        def nll(t: float) -> float:
            z = logp / t
            z = z - z.max(axis=1, keepdims=True)
            p = np.exp(z) / np.exp(z).sum(axis=1, keepdims=True)
            return float(-np.log(p[np.arange(len(y)), y]).mean())

        return float(minimize_scalar(nll, bounds=(0.5, 2.0), method="bounded").x)

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        out = self.without_odds.predict(df)[PROB_COLS].copy()
        # Versions saved before calibration existed have no temperature: 1.0 keeps them unchanged.
        temperature = getattr(self, "temperature_", 1.0)
        if temperature != 1.0:
            z = np.log(out.to_numpy(float).clip(1e-12, 1)) / temperature
            z = np.exp(z - z.max(axis=1, keepdims=True))
            out[PROB_COLS] = z / z.sum(axis=1, keepdims=True)
        has_odds = df["mkt_p_home"].notna()
        if has_odds.any():
            out.loc[has_odds, PROB_COLS] = self.with_odds.predict(df[has_odds])[PROB_COLS]
        return pd.concat([out, self.goals.predict(df)[GOAL_COLS]], axis=1)

    def params(self) -> dict:
        return {"with_odds": self.with_odds.params(), "without_odds": self.without_odds.params(),
                "goals": self.goals.params(), "trend_groups": list(self.trend_groups),
                "temperature_without_odds": getattr(self, "temperature_", 1.0)}


MODEL_FACTORIES: dict[str, Callable[[], ProbModel]] = {
    "routed_competition": lambda: RoutedCompetitionAware("routed_competition"),
    # Candidate from the trend study: team scoring profile on goal markets and cup 1X2
    # (where it showed gains); the odds model is left unchanged.
    "routed_competition_scoring": lambda: RoutedCompetitionAware(
        "routed_competition_scoring", ("team_scoring_profile",)),
    # Phase 6 candidates (D30, D31): cup calibration and low-score correction.
    "routed_competition_cal": lambda: RoutedCompetitionAware(
        "routed_competition_cal", calibrate_without_odds=True),
    "routed_competition_dc": lambda: RoutedCompetitionAware("routed_competition_dc", dixon_coles=True),
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
