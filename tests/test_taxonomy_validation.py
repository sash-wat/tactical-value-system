import pandas as pd

from src.taxonomy_validation import summarize_validation_results


def test_summarize_validation_results_reports_temporal_and_league_coverage():
    scored = pd.DataFrame(
        [
            {
                "league": "mls",
                "season": "2024",
                "primary_identity": "Identity 1",
                "secondary_identity": "Identity 2",
                "hybrid_flag": False,
                "distance_to_primary": 0.4,
            },
            {
                "league": "nwsl",
                "season": "2024",
                "primary_identity": "Identity 2",
                "secondary_identity": "Identity 1",
                "hybrid_flag": True,
                "distance_to_primary": 0.6,
            },
        ]
    )

    summary = summarize_validation_results(scored)

    assert summary["n_scored_rows"] == 2
    assert summary["league_identity_coverage"]["mls"]["Identity 1"] == 1
    assert "hybrid_rate" in summary
    assert "distance_summary" in summary
