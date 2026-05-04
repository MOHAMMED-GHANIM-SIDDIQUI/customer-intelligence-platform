"""End-to-end orchestration for the customer analytics project."""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from customer_analytics.config import ProjectConfig, SPEND_FEATURES
from customer_analytics.data_generation import add_simulated_targets, build_synthetic_sources
from customer_analytics.features import build_customer_modeling_table
from customer_analytics.modeling import ChurnModelResult, SpendModelResult, train_churn_models, train_spend_models
from customer_analytics.segmentation import SegmentationResult, fit_customer_segments


@dataclass
class PipelineResult:
    """Container for all data, model artifacts, and business outputs."""

    customers: pd.DataFrame
    transactions: pd.DataFrame
    customer_data: pd.DataFrame
    segmentation: SegmentationResult
    churn: ChurnModelResult
    spend: SpendModelResult
    customer_actions: pd.DataFrame


def build_customer_actions(
    customer_data: pd.DataFrame,
    segmentation: SegmentationResult,
    churn: ChurnModelResult,
    spend: SpendModelResult,
) -> pd.DataFrame:
    """Create a business-facing table that can be exported to CRM tools."""

    scored_customers = segmentation.customer_segments.copy()
    churn_probability = churn.selected_model.predict_proba(scored_customers[churn.selected_model.feature_names_in_])[:, 1]
    predicted_spend = spend.champion_model.predict(scored_customers[SPEND_FEATURES])

    actions = pd.DataFrame(
        {
            "customer_id": scored_customers["customer_id"],
            "segment": scored_customers["segment"],
            "churn_probability": churn_probability.round(3),
            "predicted_next_month_spend": np.maximum(predicted_spend.round(2), 0),
        }
    )
    actions["risk_band"] = pd.cut(
        actions["churn_probability"],
        bins=[0, 0.2, 0.5, 1.0],
        labels=["low", "medium", "high"],
        include_lowest=True,
    )
    actions["recommended_action"] = actions["risk_band"].map(
        {
            "low": "standard nurture",
            "medium": "engagement campaign",
            "high": "retention offer review",
        }
    )
    return actions


def run_pipeline(config: ProjectConfig | None = None) -> PipelineResult:
    """Run the full project from raw synthetic sources to scored customers."""

    config = config or ProjectConfig()
    customers, transactions = build_synthetic_sources(config)
    customer_features = build_customer_modeling_table(customers, transactions)
    customer_data = add_simulated_targets(customer_features, config)

    segmentation = fit_customer_segments(
        customer_data=customer_data,
        n_segments=config.n_segments,
        random_state=config.random_state,
    )
    churn = train_churn_models(customer_data, config)
    spend = train_spend_models(customer_data, config)
    customer_actions = build_customer_actions(customer_data, segmentation, churn, spend)

    return PipelineResult(
        customers=customers,
        transactions=transactions,
        customer_data=customer_data,
        segmentation=segmentation,
        churn=churn,
        spend=spend,
        customer_actions=customer_actions,
    )
