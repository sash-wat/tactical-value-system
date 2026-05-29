from __future__ import annotations

import pandas as pd


def summarize_validation_results(scored: pd.DataFrame) -> dict:
    if scored.empty:
        return {
            "n_scored_rows": 0,
            "hybrid_rate": 0.0,
            "league_identity_coverage": {},
            "season_identity_coverage": {},
            "distance_summary": {"mean": 0.0, "median": 0.0, "max": 0.0},
        }

    league_identity_coverage = (
        scored.groupby(["league", "primary_identity"]).size().unstack(fill_value=0).to_dict(orient="index")
    )
    season_identity_coverage = (
        scored.groupby(["season", "primary_identity"]).size().unstack(fill_value=0).to_dict(orient="index")
    )

    return {
        "n_scored_rows": int(len(scored)),
        "hybrid_rate": float(scored["hybrid_flag"].mean()),
        "league_identity_coverage": league_identity_coverage,
        "season_identity_coverage": season_identity_coverage,
        "distance_summary": {
            "mean": float(scored["distance_to_primary"].mean()),
            "median": float(scored["distance_to_primary"].median()),
            "max": float(scored["distance_to_primary"].max()),
        },
    }
