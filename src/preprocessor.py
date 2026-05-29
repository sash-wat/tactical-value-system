from __future__ import annotations

import numpy as np
import pandas as pd

TACTICAL_FEATURES = [
    "passing",
    "receiving",
    "interrupting",
    "dribbling",
    "claiming",
    "attempted_passes_for",
    "pass_completion_percentage_for",
    "avg_vertical_distance_for",
    "avg_vertical_distance_against",
]

CUMULATIVE_TACTICAL_FEATURES = {
    "passing",
    "receiving",
    "interrupting",
    "dribbling",
    "claiming",
    "attempted_passes_for",
}


def build_tactical_feature_frame(df: pd.DataFrame) -> pd.DataFrame:
    missing = [feature for feature in TACTICAL_FEATURES if feature not in df.columns]
    if missing:
        raise ValueError(f"Missing features: {missing}")
    if "team_name" not in df.columns:
        raise ValueError("Missing team_name column")

    df_features = df[TACTICAL_FEATURES].apply(pd.to_numeric, errors="coerce")
    if df_features.isna().all(axis=None):
        raise ValueError("No numeric tactical feature values found")

    games = pd.to_numeric(df.get("count_games", 1.0), errors="coerce").fillna(1.0).clip(lower=1.0)
    for feature in CUMULATIVE_TACTICAL_FEATURES:
        df_features[feature] = df_features[feature] / games

    df_features = df_features.fillna(df_features.mean())
    if df_features.isna().any(axis=None):
        empty_columns = df_features.columns[df_features.isna().any()].tolist()
        raise ValueError(f"Unable to impute empty feature columns: {empty_columns}")

    return df_features


def transform_tactical_features(
    df_features: pd.DataFrame,
    mean: list[float] | np.ndarray,
    scale: list[float] | np.ndarray,
) -> pd.DataFrame:
    mean_arr = np.asarray(mean, dtype=float)
    scale_arr = np.asarray(scale, dtype=float)
    safe_scale = np.where(scale_arr == 0.0, 1.0, scale_arr)
    scaled = (df_features.to_numpy(dtype=float) - mean_arr) / safe_scale
    return pd.DataFrame(scaled, columns=TACTICAL_FEATURES, index=df_features.index)


def preprocess_tactical_data(df: pd.DataFrame):
    df_features = build_tactical_feature_frame(df)
    mean = df_features.mean().to_numpy(dtype=float)
    scale = df_features.std(ddof=0).replace(0.0, 1.0).to_numpy(dtype=float)
    df_scaled = transform_tactical_features(df_features, mean=mean, scale=scale)
    return df_scaled, df["team_name"]
