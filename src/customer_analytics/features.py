"""Feature engineering utilities."""

import numpy as np
import pandas as pd


def build_customer_order_features(transactions: pd.DataFrame) -> pd.DataFrame:
    """Aggregate transaction-level data into customer-level purchase features."""

    analysis_date = transactions["order_date"].max() + pd.Timedelta(days=1)
    order_features = (
        transactions.groupby("customer_id")
        .agg(
            total_orders=("transaction_id", "count"),
            total_spend=("order_amount", "sum"),
            average_order_value=("order_amount", "mean"),
            order_value_std=("order_amount", "std"),
            discount_rate=("discount_used", "mean"),
            discount_order_count=("discount_used", "sum"),
            first_order_date=("order_date", "min"),
            last_order_date=("order_date", "max"),
        )
        .reset_index()
    )
    order_features["recency_days"] = (
        analysis_date - order_features["last_order_date"]
    ).dt.days
    order_features["active_customer_days"] = (
        order_features["last_order_date"] - order_features["first_order_date"]
    ).dt.days + 1
    active_months = np.maximum(order_features["active_customer_days"] / 30.44, 1)
    order_features["orders_per_active_month"] = order_features["total_orders"] / active_months
    order_features["average_gap_days"] = np.where(
        order_features["total_orders"] > 1,
        order_features["active_customer_days"] / (order_features["total_orders"] - 1),
        order_features["active_customer_days"],
    )
    return order_features


def build_customer_modeling_table(
    customers: pd.DataFrame,
    transactions: pd.DataFrame,
) -> pd.DataFrame:
    """Merge customer profiles with aggregated transaction behavior."""

    order_features = build_customer_order_features(transactions)
    customer_data = customers.merge(order_features, on="customer_id", how="left")

    numeric_fill_values = {
        "total_orders": 0,
        "total_spend": 0,
        "average_order_value": 0,
        "order_value_std": 0,
        "discount_rate": 0,
        "discount_order_count": 0,
        "recency_days": 999,
        "active_customer_days": 0,
        "orders_per_active_month": 0,
        "average_gap_days": 999,
    }
    customer_data = customer_data.fillna(value=numeric_fill_values)
    customer_data["spend_per_visit"] = customer_data["total_spend"] / np.maximum(
        customer_data["visits_per_month"],
        1,
    )
    customer_data["has_discount_history"] = (
        customer_data["discount_order_count"] > 0
    ).astype(int)
    return customer_data
