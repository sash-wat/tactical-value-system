import pandas as pd

from src.taxonomy_scorer import TaxonomyScorer


def test_taxonomy_scorer_loads_and_scores():
    scorer = TaxonomyScorer()

    assert scorer.version == "phase1_taxonomy_v1"
    assert len(scorer.features) == 9
    assert 5 <= len(scorer.identities) <= 7
    assert all(identity["description"] for identity in scorer.identities.values())


def test_taxonomy_scorer_exposes_artifact_reference_window():
    scorer = TaxonomyScorer()

    assert scorer.artifact["reference_window"]["season_start"] == 2020
    assert scorer.artifact["reference_window"]["season_end"] == 2023


def test_score_team_uses_frozen_scaler_for_trait_scores():
    scorer = TaxonomyScorer()
    raw_features = {feat: float(mean) for feat, mean in zip(scorer.features, scorer.scaler_mean)}
    raw_features["count_games"] = 1.0

    result = scorer.score_team("Average FC", raw_features)

    assert result["primary_identity"]
    assert result["primary_identity_description"]
    assert result["secondary_identity"]
    assert result["secondary_identity_description"]
    assert max(abs(value) for value in result["trait_scores"].values()) < 1e-6


def test_score_team_returns_identity_scores_sorted_high_to_low():
    scorer = TaxonomyScorer()
    raw_features = {feat: float(mean) for feat, mean in zip(scorer.features, scorer.scaler_mean)}
    raw_features["count_games"] = 1.0

    result = scorer.score_team("Average FC", raw_features)
    score_values = list(result["identity_scores"].values())

    assert abs(sum(score_values) - 1.0) < 1e-6
    assert score_values == sorted(score_values, reverse=True)


def test_score_team_reports_hybrid_with_runner_up_gap_and_reasoning():
    scorer = TaxonomyScorer()
    scorer.hybrid_threshold = 0.20

    identity_items = sorted(scorer.identities.items())
    best_pair = None
    best_distance = None
    for left_idx, (_, left_identity) in enumerate(identity_items):
        for _, right_identity in identity_items[left_idx + 1:]:
            distance = float(
                pd.Series(left_identity["centroid"] - right_identity["centroid"]).pow(2).sum() ** 0.5
            )
            if best_distance is None or distance < best_distance:
                best_distance = distance
                best_pair = (left_identity["centroid"], right_identity["centroid"])

    left_centroid, right_centroid = best_pair
    midpoint = (left_centroid + right_centroid) / 2.0

    raw_features = {
        feat: float((midpoint[i] * scorer.scaler_scale[i]) + scorer.scaler_mean[i])
        for i, feat in enumerate(scorer.features)
    }
    raw_features["count_games"] = 1.0

    result = scorer.score_team("Hybrid United", raw_features)

    assert result["hybrid_flag"] is True
    assert result["secondary_identity"]
    assert "top_feature_deltas" in result["assignment_explanation"]
    assert "score_gap" in result["assignment_explanation"]
    assert result["assignment_explanation"]["runner_up_identity"] == result["secondary_identity"]
    assert result["assignment_explanation"]["winner_description"]


def test_taxonomy_scorer_can_score_multiple_rows_without_dynamic_scaler_override():
    scorer = TaxonomyScorer()
    df = pd.DataFrame(
        [
            {
                "team_name": "One FC",
                "count_games": 1,
                **{feat: float(mean) for feat, mean in zip(scorer.features, scorer.scaler_mean)},
            },
            {
                "team_name": "Two FC",
                "count_games": 1,
                **{feat: float(mean) for feat, mean in zip(scorer.features, scorer.scaler_mean)},
            },
        ]
    )

    results = [scorer.score_team(row["team_name"], row.to_dict()) for _, row in df.iterrows()]

    assert len(results) == 2
    assert all("identity_scores" in result for result in results)
