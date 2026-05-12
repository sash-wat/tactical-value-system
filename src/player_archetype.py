from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd

from src.player_preprocessor import PLAYER_FEATURE_LABELS

# Maps each feature → a unique archetype name.
# One name per feature so the dedup walkdown always resolves cleanly.
ARCHETYPE_MAP = {
    "g_shooting":                        "The Finishers",
    "xgoals_p96":                        "The Gunslingers",
    "g_passing":                         "The Architects",
    "xassists_p96":                      "The Playmakers",
    "passes_completed_over_expected_p100": "The Metronomes",
    "g_dribbling":                       "Progressive Carriers",
    "avg_vertical_distance_yds":         "Vertical Threats",
    "g_receiving":                       "Box Infiltrators",
    "g_interrupting":                    "The Enforcers",
    "share_team_touches":                "The Orchestrators",
}

BALANCED_ARCHETYPE = "Balanced Roles"
THRESHOLD = 0.4  # min z-score for a cluster centroid to claim an identity


def name_archetypes(
    df_scaled: pd.DataFrame,
    clusters: Iterable[int],
) -> tuple[dict[int, str], pd.DataFrame]:
    """
    Scan cluster centroids and assign human-readable archetype names.
    If two clusters share the same dominant feature, the lower-ranked one
    walks down the centroid feature list until a distinct name is found.
    Returns (archetype_names dict, centroids DataFrame).
    """
    df_temp = df_scaled.copy()
    df_temp["cluster"] = list(clusters)
    centroids = df_temp.groupby("cluster").mean()

    archetype_names: dict[int, str] = {}
    used_names: set[str] = set()

    for cluster_id in centroids.index:
        c_stats = centroids.loc[cluster_id]
        # Walk features from most to least dominant until we get a unique name
        ranked_features = c_stats.abs().sort_values(ascending=False).index

        assigned = BALANCED_ARCHETYPE
        for feature in ranked_features:
            if abs(c_stats[feature]) <= THRESHOLD:
                break
            candidate = ARCHETYPE_MAP.get(feature, "The Enigmas")
            if candidate not in used_names:
                assigned = candidate
                break

        used_names.add(assigned)
        archetype_names[int(cluster_id)] = assigned

    return archetype_names, centroids


def build_player_profiles(
    df_scaled: pd.DataFrame,
    clusters: Iterable[int],
    probs: np.ndarray,
    player_names: Iterable[str],
    positions: Iterable[str],
) -> dict[str, dict]:
    """
    Build a per-player profile dict suitable for JSON export.
    Each entry includes archetype, primary metric, z-score, confidence, and position.
    """
    cluster_list = list(clusters)
    name_list = list(player_names)
    position_list = list(positions)

    archetype_names, centroids = name_archetypes(df_scaled, cluster_list)

    profiles: dict[str, dict] = {}
    for i, (player, cluster_id) in enumerate(zip(name_list, cluster_list)):
        archetype = archetype_names[int(cluster_id)]
        confidence = float(probs[i].max())

        if archetype == BALANCED_ARCHETYPE:
            primary_metric = "None"
            z_score = 0.0
        else:
            c_stats = centroids.loc[cluster_id]
            dominant_feature = c_stats.abs().idxmax()
            primary_metric = PLAYER_FEATURE_LABELS.get(dominant_feature, dominant_feature)
            z_score = float(df_scaled.iloc[i][dominant_feature])

        profiles[player] = {
            "archetype": archetype,
            "position": position_list[i],
            "primary_metric": primary_metric,
            "z_score": z_score,
            "confidence": confidence,
        }

    return profiles
