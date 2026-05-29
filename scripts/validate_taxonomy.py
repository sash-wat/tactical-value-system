from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.data_loader import load_tactical_data
from src.taxonomy_scorer import TaxonomyScorer
from src.taxonomy_validation import summarize_validation_results

LEAGUES = ["mls", "uslc", "nwsl", "usl1"]
SEASONS = ["2024", "2025", "2026"]


def validate_taxonomy() -> dict:
    scorer = TaxonomyScorer()
    rows = []

    for league in LEAGUES:
        for season in SEASONS:
            df = load_tactical_data(league, season)
            if df.empty:
                continue
            for _, row in df.iterrows():
                result = scorer.score_team(row["team_name"], row.to_dict())
                rows.append(
                    {
                        "league": league,
                        "season": season,
                        "team_name": row["team_name"],
                        "primary_identity": result["primary_identity"],
                        "secondary_identity": result["secondary_identity"],
                        "hybrid_flag": result["hybrid_flag"],
                        "distance_to_primary": result["distances"][result["primary_identity"]],
                    }
                )

    return summarize_validation_results(pd.DataFrame(rows))


def main():
    print(json.dumps(validate_taxonomy(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
