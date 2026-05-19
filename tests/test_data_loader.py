import pandas as pd
import pytest

from src.data_loader import load_tactical_data


class FakeASA:
    def get_team_goals_added(self, leagues, season_name):
        return pd.DataFrame(
            [
                {
                    "team_id": "one",
                    "data": [
                        {"action_type": "Passing", "goals_added_for": 1.2},
                        {"action_type": "Receiving", "goals_added_for": 0.4},
                    ],
                },
                {
                    "team_id": "two",
                    "data": [
                        {"action_type": "Passing", "goals_added_for": -0.2},
                        {"action_type": "Receiving", "goals_added_for": 0.9},
                    ],
                },
            ]
        )

    def get_team_xgoals(self, leagues, season_name):
        return pd.DataFrame(
            [
                {"team_id": "one", "xgoals_for": 2.1, "xgoals_against": 1.0, "shots_for": 13, "shots_against": 7},
                {"team_id": "two", "xgoals_for": 1.4, "xgoals_against": 1.8, "shots_for": 9, "shots_against": 12},
            ]
        )

    def get_team_xpass(self, leagues, season_name):
        return pd.DataFrame(
            [
                {
                    "team_id": "one",
                    "count_games": 34,
                    "attempted_passes_for": 500,
                    "pass_completion_percentage_for": 82.0,
                    "avg_vertical_distance_for": 5.1,
                    "pass_completion_percentage_against": 75.0,
                    "avg_vertical_distance_against": 7.2,
                },
                {
                    "team_id": "two",
                    "count_games": 34,
                    "attempted_passes_for": 390,
                    "pass_completion_percentage_for": 76.0,
                    "avg_vertical_distance_for": 7.0,
                    "pass_completion_percentage_against": 79.0,
                    "avg_vertical_distance_against": 4.2,
                },
            ]
        )

    def get_teams(self, leagues):
        return pd.DataFrame(
            [
                {"team_id": "one", "team_name": "One FC"},
                {"team_id": "two", "team_name": "Two SC"},
            ]
        )


def test_load_tactical_data_merges_asa_sources(monkeypatch):
    monkeypatch.setattr("src.data_loader.AmericanSoccerAnalysis", FakeASA)

    df = load_tactical_data(leagues="uslc", season="2023")

    assert list(df["team_name"]) == ["One FC", "Two SC"]
    assert df.loc[0, "passing"] == 1.2
    assert df.loc[1, "receiving"] == 0.9
    assert "avg_vertical_distance_against" in df.columns


def test_load_tactical_data_rejects_missing_source_columns(monkeypatch):
    class BadASA(FakeASA):
        def get_team_xpass(self, leagues, season_name):
            return pd.DataFrame([{"team_id": "one"}])

    monkeypatch.setattr("src.data_loader.AmericanSoccerAnalysis", BadASA)

    with pytest.raises(ValueError, match="xpass response missing columns"):
        load_tactical_data(leagues="uslc", season="2023")
