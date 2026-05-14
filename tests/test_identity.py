import numpy as np
import pandas as pd

from src.identity import build_team_identities, describe_pca_axes, name_clusters


def test_name_clusters_uses_centroid_outlier_trait():
    df_scaled = pd.DataFrame(
        {
            "passing": [1.5, 1.1, -1.0, -1.2],
            "receiving": [0.1, 0.0, 0.2, 0.1],
        }
    )
    clusters = [0, 0, 1, 1]

    names, centroids = name_clusters(df_scaled, clusters)

    assert names[0] == "High-Volume Passing"
    assert names[1] == "Balanced Systems"
    assert centroids.loc[0, "passing"] == 1.3


def test_build_team_identities_reports_team_z_score_for_cluster_trait():
    df_scaled = pd.DataFrame(
        {
            "passing": [1.5, 1.1, -1.0, -1.2],
            "receiving": [0.1, 0.0, 0.2, 0.1],
        }
    )
    identities = build_team_identities(df_scaled, [0, 0, 1, 1], ["A", "B", "C", "D"])

    assert identities["A"] == {
        "identity": "High-Volume Passing",
        "metric": "Passing Impact",
        "z_score": 1.5,
    }
    assert identities["C"]["identity"] == "Balanced Systems"


def test_describe_pca_axes_uses_distinct_strongest_drivers():
    components = np.array([[0.9, 0.1, 0.0], [0.8, 0.7, 0.0]])

    assert describe_pca_axes(["passing", "receiving", "shooting"], components) == (
        "Primary Driver: Passing Impact",
        "Primary Driver: Receiving Impact",
    )
