"""Model B: supervised 1X2 classifiers on pre-match features."""

from typing import ClassVar

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler

from footintel.features.builder import (
    CONTEXT_FEATURES,
    ELO_FEATURES,
    MARKET_FEATURES,
    side_features,
)
from footintel.models.base import (
    GOAL_COLS,
    PROB_COLS,
    ProbModel,
    encode_result,
    markets_from_lambdas,
)

CORE_FEATURES = ELO_FEATURES + side_features("h") + side_features("a") + CONTEXT_FEATURES
WITH_MARKET_FEATURES = CORE_FEATURES + MARKET_FEATURES


def _preprocess() -> list:
    # Missing values: median from the training fold plus a missing-indicator column,
    # so "no data" stays visible to the model instead of looking like an average.
    # Clipping z-scores stops an out-of-range input (a near-constant feature, a bad
    # price) from pushing a linear model to probabilities of 0 or 1.
    return [("impute", SimpleImputer(strategy="median", add_indicator=True)),
            ("scale", StandardScaler()),
            ("clip", FunctionTransformer(np.clip, kw_args={"a_min": -5.0, "a_max": 5.0}))]


class SklearnClassifierModel(ProbModel):
    def __init__(self, name: str, family: str, features: list[str], estimator, params: dict):
        self.name, self.family, self.features = name, family, list(features)
        self.estimator = estimator
        self._params = params

    def fit(self, train: pd.DataFrame) -> "SklearnClassifierModel":
        self.pipeline_ = Pipeline(_preprocess() + [("clf", self.estimator)])
        self.pipeline_.fit(train[self.features], encode_result(train))
        return self

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        proba = self.pipeline_.predict_proba(df[self.features])
        full = np.zeros((len(df), 3))
        full[:, self.pipeline_.classes_] = proba
        return pd.DataFrame(full, columns=PROB_COLS, index=df.index)

    def params(self) -> dict:
        return {**self._params, "features": self.features}


def logistic(features: list[str], name: str, c: float = 0.5) -> SklearnClassifierModel:
    return SklearnClassifierModel(name, "logistic_regression", features,
                                  LogisticRegression(C=c, max_iter=3000), {"C": c})


def random_forest(features: list[str], name: str) -> SklearnClassifierModel:
    params = {"n_estimators": 300, "min_samples_leaf": 40, "max_features": "sqrt"}
    est = RandomForestClassifier(**params, n_jobs=-1, random_state=42)
    return SklearnClassifierModel(name, "random_forest", features, est, params)


def xgboost(features: list[str], name: str) -> SklearnClassifierModel:
    from xgboost import XGBClassifier  # heavy import, only when used

    params = {"n_estimators": 300, "max_depth": 3, "learning_rate": 0.03,
              "subsample": 0.8, "colsample_bytree": 0.8, "min_child_weight": 20}
    est = XGBClassifier(objective="multi:softprob", eval_metric="mlogloss", n_jobs=4,
                        random_state=42, **params)
    return SklearnClassifierModel(name, "xgboost", features, est, params)


def neural_net(features: list[str], name: str) -> SklearnClassifierModel:
    """Neural network (D98 test): two hidden layers trained by backpropagation (Adam).
    Early stopping on a 10 % slice of the training fold, and an L2 penalty, keep it from
    learning the noise of past seasons."""
    from sklearn.neural_network import MLPClassifier

    params = {"hidden_layer_sizes": (64, 32), "alpha": 1e-3, "learning_rate_init": 1e-3,
              "batch_size": 512, "max_iter": 200, "early_stopping": True, "validation_fraction": 0.1,
              "n_iter_no_change": 10}
    return SklearnClassifierModel(name, "neural_net", features, MLPClassifier(random_state=42, **params), params)



def lightgbm(features: list[str], name: str) -> SklearnClassifierModel:
    """LightGBM (D99 test, shown next to the active model since D105). Many small trees
    with few leaves and at least 200 matches per leaf, so it cannot learn single matches."""
    from lightgbm import LGBMClassifier  # heavy import, only when used

    params = {"n_estimators": 400, "learning_rate": 0.02, "num_leaves": 15, "min_child_samples": 200,
              "subsample": 0.8, "subsample_freq": 1, "colsample_bytree": 0.8, "reg_lambda": 1.0}
    return SklearnClassifierModel(name, "lightgbm", features,
                                  LGBMClassifier(random_state=42, verbose=-1, **params), params)


class LightGBMGoals(ProbModel):
    """D107: goals of each team from two LightGBM regressors (Poisson loss), then the same
    score table as Hermès, so every goal market (over/under, BTTS, scores) comes from them."""

    family = "lightgbm_poisson"
    PARAMS: ClassVar[dict] = {"n_estimators": 400, "learning_rate": 0.02, "num_leaves": 15, "min_child_samples": 200,
              "subsample": 0.8, "subsample_freq": 1, "colsample_bytree": 0.8, "reg_lambda": 1.0}

    def __init__(self, name: str, features: list[str]):
        self.name, self.features = name, list(features)

    def _pipe(self) -> Pipeline:
        from lightgbm import LGBMRegressor

        return Pipeline(_preprocess() + [("reg", LGBMRegressor(objective="poisson", random_state=42,
                                                                verbose=-1, **self.PARAMS))])

    def fit(self, train: pd.DataFrame) -> "LightGBMGoals":
        train = train[train[["home_goals", "away_goals"]].notna().all(axis=1)]
        self.home_ = self._pipe().fit(train[self.features], train["home_goals"])
        self.away_ = self._pipe().fit(train[self.features], train["away_goals"])
        return self

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        x = df[self.features]
        lam_h = np.clip(self.home_.predict(x), 0.05, 8.0)
        lam_a = np.clip(self.away_.predict(x), 0.05, 8.0)
        out = markets_from_lambdas(lam_h, lam_a)
        out.index = df.index
        return out[PROB_COLS + GOAL_COLS]

    def params(self) -> dict:
        return {**self.PARAMS, "features": self.features}
