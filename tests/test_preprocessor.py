import pandas as pd
import pytest

from src.preprocessor import (
    TACTICAL_FEATURES,
    build_tactical_feature_frame,
    preprocess_tactical_data,
    transform_tactical_features,
)


def _frame():
    return pd.DataFrame(
        [
            {
                "team_name": "Alpha FC",
                "count_games": 2,
                "passing": 4.0,
                "receiving": 6.0,
                "interrupting": 8.0,
                "dribbling": 10.0,
                "claiming": 12.0,
                "attempted_passes_for": 400.0,
                "pass_completion_percentage_for": 0.80,
                "avg_vertical_distance_for": 7.0,
                "avg_vertical_distance_against": 8.0,
            },
            {
                "team_name": "Beta SC",
                "count_games": 4,
                "passing": 12.0,
                "receiving": 16.0,
                "interrupting": 20.0,
                "dribbling": 24.0,
                "claiming": 28.0,
                "attempted_passes_for": 800.0,
                "pass_completion_percentage_for": 0.70,
                "avg_vertical_distance_for": 6.0,
                "avg_vertical_distance_against": 9.0,
            },
            {
                "team_name": "Gamma Town",
                "count_games": 1,
                "passing": 6.0,
                "receiving": 7.0,
                "interrupting": 8.0,
                "dribbling": 9.0,
                "claiming": 10.0,
                "attempted_passes_for": 250.0,
                "pass_completion_percentage_for": 0.75,
                "avg_vertical_distance_for": 6.5,
                "avg_vertical_distance_against": 8.5,
            },
        ]
    )


def test_build_tactical_feature_frame_normalizes_cumulative_metrics_per_game():
    frame = build_tactical_feature_frame(_frame())

    assert list(frame.columns) == TACTICAL_FEATURES
    assert frame.loc[0, "passing"] == 2.0
    assert frame.loc[1, "passing"] == 3.0
    assert frame.loc[0, "attempted_passes_for"] == 200.0
    assert frame.loc[1, "attempted_passes_for"] == 200.0
    assert frame.loc[0, "pass_completion_percentage_for"] == 0.80


def test_transform_tactical_features_uses_supplied_reference_scaler():
    frame = build_tactical_feature_frame(_frame())

    scaled = transform_tactical_features(
        frame,
        mean=[2.5, 3.5, 4.5, 5.5, 6.5, 200.0, 0.75, 6.5, 8.5],
        scale=[0.5, 0.5, 0.5, 0.5, 0.5, 1.0, 0.05, 0.5, 0.5],
    )

    assert scaled.loc[0, "passing"] == -1.0
    assert scaled.loc[1, "passing"] == 1.0
    assert scaled.loc[0, "attempted_passes_for"] == 0.0
    assert scaled.loc[1, "pass_completion_percentage_for"] == pytest.approx(-1.0)


def test_preprocess_tactical_data_imputes_partial_missing_values():
    df = _frame()
    df.loc[0, "passing"] = None

    df_scaled, _ = preprocess_tactical_data(df)

    assert not df_scaled.isna().any(axis=None)


def test_preprocess_tactical_data_rejects_missing_features():
    df = _frame().drop(columns=["passing"])

    with pytest.raises(ValueError, match="Missing features"):
        preprocess_tactical_data(df)
