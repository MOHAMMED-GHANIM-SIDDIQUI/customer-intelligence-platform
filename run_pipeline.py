"""Run the refactored customer analytics pipeline."""

from pprint import pprint

from customer_analytics.config import ProjectConfig
from customer_analytics.pipeline import run_pipeline


def main() -> None:
    """Execute the case study and print the key outputs."""

    result = run_pipeline(ProjectConfig())

    print("\nSegment profile")
    print(result.segmentation.segment_profile)
    print(f"\n2D PCA explained variance: {result.segmentation.explained_variance_2d}")

    print("\nBaseline churn metrics")
    pprint(result.churn.baseline_metrics)

    print("\nGradient boosting churn metrics")
    pprint(result.churn.gradient_boosting_metrics)

    print("\nSelected churn metrics")
    pprint(result.churn.selected_metrics)

    print("\nBaseline spend metrics")
    pprint(result.spend.baseline_metrics)

    print("\nChampion spend metrics")
    pprint(result.spend.champion_metrics)

    print("\nSample customer actions")
    print(result.customer_actions.head(10))


if __name__ == "__main__":
    main()
