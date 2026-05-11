import pandas as pd
import pytest

from src.preprocessor import TACTICAL_FEATURES, preprocess_tactical_data


def _frame():
    rows = []
    for idx, team in enumerate(["One FC", "Two SC", "Three Town"]):
        row = {"team_name": team}
        for feature_idx, feature in enumerate(TACTICAL_FEATURES):
            row[feature] = idx + feature_idx
        rows.append(row)
    return pd.DataFrame(rows)


def test_preprocess_tactical_data_scales_features_and_keeps_team_names():
    df_scaled, team_names = preprocess_tactical_data(_frame())

    assert list(df_scaled.columns) == TACTICAL_FEATURES
    assert list(team_names) == ["One FC", "Two SC", "Three Town"]
    assert df_scaled.round(6).mean().abs().max() == 0


def test_preprocess_tactical_data_imputes_partial_missing_values():
    df = _frame()
    df.loc[0, "passing"] = None

    df_scaled, _ = preprocess_tactical_data(df)

    assert not df_scaled.isna().any(axis=None)


def test_preprocess_tactical_data_rejects_missing_features():
    df = _frame().drop(columns=["passing"])

    with pytest.raises(ValueError, match="Missing features"):
        preprocess_tactical_data(df)
