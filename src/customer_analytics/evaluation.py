"""Model evaluation helpers."""

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)


def find_best_f1_threshold(y_true: pd.Series, probabilities: np.ndarray) -> float:
    """Choose a churn threshold that balances precision and recall."""

    candidate_thresholds = np.arange(0.05, 0.95, 0.01)
    scores = [
        f1_score(y_true, probabilities >= threshold, zero_division=0)
        for threshold in candidate_thresholds
    ]
    return round(float(candidate_thresholds[int(np.argmax(scores))]), 2)


def classification_metrics(
    y_true: pd.Series,
    probabilities: np.ndarray,
    threshold: float,
) -> dict:
    """Return classification metrics at a chosen probability threshold."""

    predictions = probabilities >= threshold
    return {
        "threshold": threshold,
        "accuracy": round(accuracy_score(y_true, predictions), 3),
        "precision": round(precision_score(y_true, predictions, zero_division=0), 3),
        "recall": round(recall_score(y_true, predictions, zero_division=0), 3),
        "f1": round(f1_score(y_true, predictions, zero_division=0), 3),
        "roc_auc": round(roc_auc_score(y_true, probabilities), 3),
        "confusion_matrix": confusion_matrix(y_true, predictions).tolist(),
    }


def regression_metrics(y_true: pd.Series, predictions: np.ndarray) -> dict:
    """Return common regression metrics for spend forecasting."""

    rmse = np.sqrt(mean_squared_error(y_true, predictions))
    return {
        "r2": round(r2_score(y_true, predictions), 3),
        "mae": round(mean_absolute_error(y_true, predictions), 3),
        "rmse": round(float(rmse), 3),
    }

