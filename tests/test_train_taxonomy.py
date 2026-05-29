import pandas as pd

from scripts.train_taxonomy import build_reference_cohort, discover_taxonomy


def test_build_reference_cohort_preserves_league_and_season_metadata():
    source = {
        ("mls", "2020"): pd.DataFrame(
            [
                {
                    "team_name": "Alpha FC",
                    "count_games": 1,
                    "passing": 1.0,
                    "receiving": 2.0,
                    "interrupting": 3.0,
                    "dribbling": 4.0,
                    "claiming": 5.0,
                    "attempted_passes_for": 100.0,
                    "pass_completion_percentage_for": 0.8,
                    "avg_vertical_distance_for": 6.0,
                    "avg_vertical_distance_against": 7.0,
                }
            ]
        )
    }

    cohort = build_reference_cohort(source)

    assert list(cohort[["league", "season"]].iloc[0]) == ["mls", "2020"]


def test_discover_taxonomy_returns_between_five_and_seven_identities():
    df = pd.DataFrame(
        [
            {
                "team_name": f"Team {idx}",
                "league": "mls",
                "season": "2020",
                "count_games": 1,
                "passing": float(idx),
                "receiving": float(idx + 1),
                "interrupting": float(idx + 2),
                "dribbling": float(idx + 3),
                "claiming": float(idx + 4),
                "attempted_passes_for": float(200 + idx),
                "pass_completion_percentage_for": 0.7 + idx * 0.001,
                "avg_vertical_distance_for": 6.0 + idx * 0.1,
                "avg_vertical_distance_against": 8.0 - idx * 0.05,
            }
            for idx in range(14)
        ]
    )

    model = discover_taxonomy(df)

    assert 5 <= model["n_identities"] <= 7
    assert len(model["identities"]) == model["n_identities"]
