"""Synthetic data generation for the customer analytics case study."""

import numpy as np
import pandas as pd

from customer_analytics.config import ProjectConfig


def generate_customers(config: ProjectConfig) -> pd.DataFrame:
    """Create a synthetic customer profile table."""

    rng = np.random.default_rng(config.random_state)
    customers = pd.DataFrame(
        {
            "customer_id": np.arange(1, config.n_customers + 1),
            "country": rng.choice(["US", "UK"], size=config.n_customers, p=[0.6, 0.4]),
            "age": rng.integers(18, 70, size=config.n_customers),
            "income": rng.normal(60_000, 20_000, size=config.n_customers).round(0),
            "tenure_months": rng.integers(1, 60, size=config.n_customers),
            "visits_per_month": rng.poisson(6, size=config.n_customers),
        }
    )
    customers["income"] = customers["income"].clip(lower=5_000)
    return customers


def generate_transactions(customers: pd.DataFrame, config: ProjectConfig) -> pd.DataFrame:
    """Create synthetic order-level transactions for known customers."""

    rng = np.random.default_rng(config.random_state + 1)
    return pd.DataFrame(
        {
            "transaction_id": np.arange(1, config.n_transactions + 1),
            "customer_id": rng.choice(customers["customer_id"], size=config.n_transactions),
            "order_date": pd.to_datetime("2023-01-01")
            + pd.to_timedelta(rng.integers(0, 365, size=config.n_transactions), unit="D"),
            "order_amount": rng.gamma(shape=4, scale=20, size=config.n_transactions).round(2),
            "discount_used": rng.choice([0, 1], size=config.n_transactions, p=[0.7, 0.3]),
        }
    )


def add_simulated_targets(customer_data: pd.DataFrame, config: ProjectConfig) -> pd.DataFrame:
    """Add churn and next-month spend targets for demo training.

    These labels are still synthetic, so they should be treated as case-study
    targets rather than evidence of real predictive power.
    """

    rng = np.random.default_rng(config.random_state + 2)
    enriched_data = customer_data.copy()

    churn_probability = (
        0.30
        - 0.003 * enriched_data["tenure_months"]
        - 0.00001 * enriched_data["total_spend"]
        - 0.02 * enriched_data["visits_per_month"]
        + 0.001 * enriched_data["recency_days"]
        + 0.08 * enriched_data["discount_rate"]
        - 0.01 * enriched_data["orders_per_active_month"]
    )
    churn_probability = churn_probability.clip(lower=0.05, upper=0.80)
    enriched_data["will_churn"] = rng.binomial(1, churn_probability)

    base_spend = (
        0.35 * enriched_data["average_order_value"] * enriched_data["visits_per_month"]
        + 0.08 * enriched_data["total_spend"]
        - 0.25 * enriched_data["recency_days"]
    )
    noise = rng.normal(0, 50, len(enriched_data))
    next_month_spend = (base_spend + noise).round(2).clip(lower=0)
    enriched_data["next_month_spend"] = next_month_spend * (1 - enriched_data["will_churn"])

    return enriched_data


def build_synthetic_sources(config: ProjectConfig) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Generate the two raw source tables used by the project."""

    customers = generate_customers(config)
    transactions = generate_transactions(customers, config)
    return customers, transactions
