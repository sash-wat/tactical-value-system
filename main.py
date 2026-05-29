# pyrefly: ignore [missing-import]
import pandas as pd

from src.data_loader import load_tactical_data
from src.preprocessor import build_tactical_feature_frame, transform_tactical_features
from src.taxonomy_scorer import TaxonomyScorer
from src.visualizer import plot_clusters


def run_phase_1():
    print("Loading MLS 2025 data...")
    try:
        df = load_tactical_data("mls", "2025")
    except Exception as exc:
        print(f"Error loading data: {exc}")
        return

    print("Scoring teams against frozen taxonomy...")
    scorer = TaxonomyScorer()
    feature_frame = build_tactical_feature_frame(df)
    df_scaled = transform_tactical_features(
        feature_frame,
        mean=scorer.scaler_mean,
        scale=scorer.scaler_scale,
    )

    cluster_ids = []
    result_rows = []
    for _, row in df.iterrows():
        score_result = scorer.score_team(row["team_name"], row.to_dict())
        cluster_ids.append(score_result["primary_cluster_id"])
        result_rows.append(
            {
                "team_name": row["team_name"],
                "primary_identity": score_result["primary_identity"],
                "secondary_identity": score_result["secondary_identity"],
                "hybrid_flag": score_result["hybrid_flag"],
            }
        )

    result_df = pd.DataFrame(result_rows)
    print("\n--- Tactical Taxonomy Assignments (MLS 2025) ---")
    print(result_df.to_string(index=False))

    print("Generating visualization...")
    plot_clusters(df_scaled, cluster_ids, df["team_name"])

    return result_rows


if __name__ == "__main__":
    run_phase_1()
