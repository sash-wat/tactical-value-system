from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd


FEATURE_MAP = {
    "passing": "Passing Impact",
    "receiving": "Receiving Impact",
    "shooting": "Shooting Impact",
    "interrupting": "Defensive Disruption",
    "dribbling": "Dribbling Impact",
    "claiming": "Claiming Impact",
    "xgoals_for": "Attacking Threat (xG)",
    "xgoals_against": "Defensive Vulnerability (xGA)",
    "shots_for": "Shot Volume",
    "shots_against": "Shots Conceded",
    "attempted_passes_for": "Possession Volume",
    "pass_completion_percentage_for": "Possession Quality",
    "avg_vertical_distance_for": "Attacking Directness",
    "pass_completion_percentage_against": "Opponent Pass Completion",
    "avg_vertical_distance_against": "Opponent Directness",
}

IDENTITY_NAMES = {
    "passing": "The Metronomes",
    "receiving": "Box Infiltrators",
    "shooting": "The Gunslingers",
    "interrupting": "The Disruptors",
    "dribbling": "Progressive Carriers",
    "claiming": "Air Superiority",
    "xgoals_for": "Attacking Juggernauts",
    "xgoals_against": "Open Defenses",
    "shots_for": "Volume Shooters",
    "shots_against": "Siege Defenders",
    "attempted_passes_for": "The Architects",
    "pass_completion_percentage_for": "Tiki-Taka Purists",
    "avg_vertical_distance_for": "Vertical Threats",
    "pass_completion_percentage_against": "Passive Observers",
    "avg_vertical_distance_against": "High-Press Hounds",
}

BALANCED_IDENTITY = "Balanced Systems"


def describe_pca_axes(features: Iterable[str], components: np.ndarray) -> tuple[str, str]:
    feature_list = list(features)
    if components.shape[0] < 2:
        raise ValueError("At least two PCA components are required.")

    idx1 = int(np.argmax(np.abs(components[0])))
    sorted_idx2 = np.argsort(np.abs(components[1]))[::-1]
    idx2 = int(sorted_idx2[0] if sorted_idx2[0] != idx1 else sorted_idx2[1])

    axis_1 = FEATURE_MAP.get(feature_list[idx1], feature_list[idx1])
    axis_2 = FEATURE_MAP.get(feature_list[idx2], feature_list[idx2])
    return f"Primary Driver: {axis_1}", f"Primary Driver: {axis_2}"


def name_clusters(
    df_scaled: pd.DataFrame,
    clusters: Iterable[int],
    threshold: float = 0.5,
) -> tuple[dict[int, str], pd.DataFrame]:
    df_temp = df_scaled.copy()
    df_temp["cluster"] = list(clusters)
    centroids = df_temp.groupby("cluster").mean()

    cluster_names = {}
    for cluster_id in centroids.index:
        c_stats = centroids.loc[cluster_id]
        best_trait = c_stats.idxmax()
        peak_value = c_stats.max()
        if peak_value > threshold:
            cluster_names[int(cluster_id)] = IDENTITY_NAMES.get(best_trait, "The Enigmas")
        else:
            cluster_names[int(cluster_id)] = BALANCED_IDENTITY

    return cluster_names, centroids


def unique_legend_names(cluster_names: dict[int, str]) -> dict[int, str]:
    final_names = {}
    name_counts = {}
    for cluster_id, name in cluster_names.items():
        if name not in name_counts:
            name_counts[name] = 0
            final_names[cluster_id] = name
        else:
            name_counts[name] += 1
            final_names[cluster_id] = f"{name} ({name_counts[name] + 1})"
    return final_names


def build_team_identities(
    df_scaled: pd.DataFrame,
    clusters: Iterable[int],
    team_names: Iterable[str],
    threshold: float = 0.5,
) -> dict[str, dict[str, str | float]]:
    cluster_list = list(clusters)
    team_list = list(team_names)
    cluster_names, centroids = name_clusters(df_scaled, cluster_list, threshold=threshold)

    team_identities = {}
    for team_idx, (team, cluster_id) in enumerate(zip(team_list, cluster_list)):
        identity = cluster_names[int(cluster_id)]
        if identity == BALANCED_IDENTITY:
            metric_name = "None"
            team_z = 0.0
        else:
            c_stats = centroids.loc[cluster_id]
            best_trait = c_stats.idxmax()
            metric_name = FEATURE_MAP.get(best_trait, best_trait)
            team_z = df_scaled.iloc[team_idx][best_trait]

        team_identities[team] = {
            "identity": identity,
            "metric": metric_name,
            "z_score": float(team_z),
        }

    return team_identities
