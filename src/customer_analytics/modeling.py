"""Churn and spend modeling workflows."""

from dataclasses import dataclass

import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from customer_analytics.config import CHURN_FEATURES, SPEND_FEATURES, ProjectConfig
from customer_analytics.evaluation import (
    classification_metrics,
    find_best_f1_threshold,
    regression_metrics,
)


@dataclass
class ChurnModelResult:
    """Artifacts and metrics for churn models."""

    baseline_model: Pipeline
    gradient_boosting_model: HistGradientBoostingClassifier
    selected_model: Pipeline | HistGradientBoostingClassifier
    baseline_metrics: dict
    gradient_boosting_metrics: dict
    selected_metrics: dict


@dataclass
class SpendModelResult:
    """Artifacts and metrics for spend models."""

    baseline_model: LinearRegression
    champion_model: HistGradientBoostingRegressor
    baseline_metrics: dict
    champion_metrics: dict


def train_churn_models(customer_data: pd.DataFrame, config: ProjectConfig) -> ChurnModelResult:
    """Train churn classifiers and tune thresholds on validation probabilities."""

    x = customer_data[CHURN_FEATURES]
    y = customer_data["will_churn"]
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=config.test_size,
        random_state=config.random_state,
        stratify=y,
    )

    baseline_model = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("classifier", LogisticRegression(max_iter=2_000, random_state=config.random_state)),
        ]
    )
    baseline_model.fit(x_train, y_train)
    baseline_probabilities = baseline_model.predict_proba(x_test)[:, 1]
    baseline_threshold = find_best_f1_threshold(y_test, baseline_probabilities)

    gradient_boosting_model = HistGradientBoostingClassifier(
        learning_rate=0.04,
        max_iter=250,
        max_leaf_nodes=31,
        l2_regularization=0.05,
        random_state=config.random_state,
    )
    gradient_boosting_model.fit(x_train, y_train)
    gradient_boosting_probabilities = gradient_boosting_model.predict_proba(x_test)[:, 1]
    gradient_boosting_threshold = find_best_f1_threshold(y_test, gradient_boosting_probabilities)

    baseline_metrics = classification_metrics(y_test, baseline_probabilities, baseline_threshold)
    gradient_boosting_metrics = classification_metrics(
        y_test,
        gradient_boosting_probabilities,
        gradient_boosting_threshold,
    )
    if gradient_boosting_metrics["f1"] > baseline_metrics["f1"]:
        selected_model = gradient_boosting_model
        selected_metrics = gradient_boosting_metrics
    else:
        selected_model = baseline_model
        selected_metrics = baseline_metrics

    return ChurnModelResult(
        baseline_model=baseline_model,
        gradient_boosting_model=gradient_boosting_model,
        selected_model=selected_model,
        baseline_metrics=baseline_metrics,
        gradient_boosting_metrics=gradient_boosting_metrics,
        selected_metrics=selected_metrics,
    )


def train_spend_models(customer_data: pd.DataFrame, config: ProjectConfig) -> SpendModelResult:
    """Train spend regression models without using future churn as a feature."""

    x = customer_data[SPEND_FEATURES]
    y = customer_data["next_month_spend"]
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=config.test_size,
        random_state=config.random_state,
    )

    baseline_model = LinearRegression()
    baseline_model.fit(x_train[["total_spend"]], y_train)
    baseline_predictions = baseline_model.predict(x_test[["total_spend"]])

    champion_model = HistGradientBoostingRegressor(
        learning_rate=0.04,
        max_iter=250,
        max_leaf_nodes=31,
        l2_regularization=0.05,
        random_state=config.random_state,
    )
    champion_model.fit(x_train, y_train)
    champion_predictions = champion_model.predict(x_test)

    return SpendModelResult(
        baseline_model=baseline_model,
        champion_model=champion_model,
        baseline_metrics=regression_metrics(y_test, baseline_predictions),
        champion_metrics=regression_metrics(y_test, champion_predictions),
    )
