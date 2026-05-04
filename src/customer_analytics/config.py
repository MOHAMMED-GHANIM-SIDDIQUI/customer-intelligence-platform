"""Shared configuration for the customer analytics pipeline."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ProjectConfig:
    """Central place for sample sizes, random state, and model settings."""

    random_state: int = 42
    n_customers: int = 5_000
    n_transactions: int = 40_000
    n_segments: int = 5
    test_size: float = 0.25
    validation_size: float = 0.25


CUSTOMER_COLUMNS = [
    "customer_id",
    "country",
    "age",
    "income",
    "tenure_months",
    "visits_per_month",
]

TRANSACTION_COLUMNS = [
    "transaction_id",
    "customer_id",
    "order_date",
    "order_amount",
    "discount_used",
]

SEGMENT_FEATURES = [
    "income",
    "tenure_months",
    "visits_per_month",
    "total_orders",
    "total_spend",
    "average_order_value",
    "discount_rate",
    "recency_days",
    "orders_per_active_month",
    "spend_per_visit",
    "order_value_std",
]

CHURN_FEATURES = [
    "tenure_months",
    "visits_per_month",
    "total_orders",
    "total_spend",
    "average_order_value",
    "discount_rate",
    "income",
    "recency_days",
    "orders_per_active_month",
    "spend_per_visit",
    "order_value_std",
]

SPEND_FEATURES = [
    "income",
    "tenure_months",
    "visits_per_month",
    "total_orders",
    "total_spend",
    "average_order_value",
    "discount_rate",
    "recency_days",
    "orders_per_active_month",
    "spend_per_visit",
    "order_value_std",
]
