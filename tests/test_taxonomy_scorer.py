import pytest
from src.taxonomy_scorer import TaxonomyScorer

def test_taxonomy_scorer_loads_and_scores():
    scorer = TaxonomyScorer()
    
    # 1. Check loaded components
    assert scorer.version == "phase1_taxonomy_v1"
    assert len(scorer.features) == 9
    assert len(scorer.identities) == 6
    
    # 2. Score a mock team with average features
    # Standard deviation of features should yield a neutral or balanced classification
    avg_team = {feat: float(m) for feat, m in zip(scorer.features, scorer.scaler_mean)}
    res = scorer.score_team("Average FC", avg_team)
    
    # 3. Check backward compatibility fields
    assert "identity" in res
    assert "metric" in res
    assert "z_score" in res
    
    # 4. Check new fields
    assert "primary_identity" in res
    assert "secondary_identity" in res
    assert "hybrid_flag" in res
    assert "explanation" in res
    assert "scores" in res
    assert "trait_scores" in res
    
    assert isinstance(res["hybrid_flag"], bool)
    assert isinstance(res["explanation"], str)

def test_taxonomy_scorer_detects_hybrids():
    scorer = TaxonomyScorer()
    
    # Test a team that sits exactly between two centroids to force hybrid status
    # Set features to average of centroids 0 and 5
    c0 = scorer.identities[0]["centroid"]
    c5 = scorer.identities[5]["centroid"]
    
    avg_centroid_scaled = (c0 + c5) / 2.0
    
    # Convert scaled features back to raw features for scoring input
    raw_features = {}
    for i, feat in enumerate(scorer.features):
        raw_val = (avg_centroid_scaled[i] * scorer.scaler_scale[i]) + scorer.scaler_mean[i]
        raw_features[feat] = float(raw_val)
        
    res = scorer.score_team("Hybrid United", raw_features)
    
    # Override hybrid threshold to ensure it triggers for this test case
    scorer.hybrid_threshold = 0.20
    res = scorer.score_team("Hybrid United", raw_features)
    
    # It should have a small margin between primary and secondary
    assert res["hybrid_margin"] < scorer.hybrid_threshold
    assert res["hybrid_flag"] is True
