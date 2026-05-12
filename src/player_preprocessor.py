from __future__ import annotations

import pandas as pd
from sklearn.preprocessing import StandardScaler

# Features that define a player's tactical identity.
# g_ features are goals_added_above_avg (position-normalised by ASA).
# g_fouling is intentionally excluded — discipline ≠ tactical identity.
PLAYER_FEATURES = [
    "g_passing",
    "g_receiving",
    "g_shooting",
    "g_dribbling",
    "g_interrupting",
    "xgoals_p96",
    "xassists_p96",
    "passes_completed_over_expected_p100",
    "avg_vertical_distance_yds",
    "share_team_touches",
]

# Human-readable labels for each feature (used in UI/reports)
PLAYER_FEATURE_LABELS = {
    "g_passing": "Passing Impact",
    "g_receiving": "Receiving Impact",
    "g_shooting": "Shooting Impact",
    "g_dribbling": "Dribbling Impact",
    "g_interrupting": "Defensive Disruption",
    "xgoals_p96": "Shot Quality (xG/96)",
    "xassists_p96": "Chance Creation (xA/96)",
    "passes_completed_over_expected_p100": "Pass Quality Above Model",
    "avg_vertical_distance_yds": "Attacking Directness",
    "share_team_touches": "Ball Involvement",
}


def preprocess_player_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    """
    Select, impute, and scale tactical features from the raw player DataFrame.

    Returns:
        df_scaled   — scaled feature matrix (n_players × n_features)
        player_names — Series of player names aligned to df_scaled rows
        positions    — Series of general_position labels aligned to df_scaled rows
    """
    missing = [f for f in PLAYER_FEATURES if f not in df.columns]
    if missing:
        raise ValueError(f"Missing player features: {missing}")

    df_features = df[PLAYER_FEATURES].apply(pd.to_numeric, errors="coerce")
    df_features = df_features.fillna(df_features.mean())

    scaler = StandardScaler()
    scaled_values = scaler.fit_transform(df_features)
    df_scaled = pd.DataFrame(scaled_values, columns=PLAYER_FEATURES)

    player_names = df["player_name"].reset_index(drop=True)
    positions = df["general_position"].reset_index(drop=True)

    return df_scaled, player_names, positions
