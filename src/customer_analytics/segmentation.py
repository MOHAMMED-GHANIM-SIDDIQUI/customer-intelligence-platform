"""Customer segmentation workflow."""

from dataclasses import dataclass

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from customer_analytics.config import SEGMENT_FEATURES


@dataclass
class SegmentationResult:
    """Artifacts produced by the segmentation workflow."""

    customer_segments: pd.DataFrame
    segment_profile: pd.DataFrame
    model: Pipeline
    pca_coordinates: pd.DataFrame
    explained_variance_2d: float


def fit_customer_segments(
    customer_data: pd.DataFrame,
    n_segments: int,
    random_state: int,
) -> SegmentationResult:
    """Fit KMeans on full scaled features and use PCA only for visualization."""

    feature_matrix = customer_data[SEGMENT_FEATURES]
    model = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("clusterer", KMeans(n_clusters=n_segments, random_state=random_state, n_init=10)),
        ]
    )

    segment_labels = model.fit_predict(feature_matrix)
    customer_segments = customer_data.copy()
    customer_segments["segment"] = segment_labels

    scaled_features = model.named_steps["scaler"].transform(feature_matrix)
    pca = PCA(n_components=2, random_state=random_state)
    coordinates = pca.fit_transform(scaled_features)
    pca_coordinates = pd.DataFrame(
        {
            "customer_id": customer_segments["customer_id"],
            "pca_1": coordinates[:, 0],
            "pca_2": coordinates[:, 1],
            "segment": segment_labels,
        }
    )

    segment_profile = (
        customer_segments.groupby("segment")[SEGMENT_FEATURES]
        .mean()
        .round(2)
        .sort_index()
    )

    return SegmentationResult(
        customer_segments=customer_segments,
        segment_profile=segment_profile,
        model=model,
        pca_coordinates=pca_coordinates,
        explained_variance_2d=round(float(pca.explained_variance_ratio_.sum()), 3),
    )

