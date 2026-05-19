import json
from pathlib import Path
import numpy as np

FEATURE_MAP = {
    "passing": "Passing Impact (g+)",
    "receiving": "Receiving Impact (g+)",
    "shooting": "Shooting Impact (g+)",
    "interrupting": "Defensive Disruption (g+)",
    "dribbling": "Dribbling Impact (g+)",
    "claiming": "Claiming Impact (g+)",
    "xgoals_for": "Attacking Threat (xG)",
    "xgoals_against": "Defensive Vulnerability (xGA)",
    "shots_for": "Shot Volume",
    "shots_against": "Shots Conceded",
    "attempted_passes_for": "Possession Volume",
    "pass_completion_percentage_for": "Possession Quality",
    "avg_vertical_distance_for": "Attacking Directness",
    "pass_completion_percentage_against": "Opponent Pass Completion",
    "avg_vertical_distance_against": "Opponent Directness",
}

class TaxonomyScorer:
    def __init__(self, model_path: str = None):
        if model_path is None:
            # Resolve default path relative to repo root
            repo_root = Path(__file__).resolve().parents[1]
            model_path = str(repo_root / "src" / "models" / "phase1_taxonomy_v1.json")
            
        with open(model_path, "r") as f:
            self.model_data = json.load(f)
            
        self.version = self.model_data["version"]
        self.features = self.model_data["features"]
        self.scaler_mean = np.array(self.model_data["scaler"]["mean"])
        self.scaler_scale = np.array(self.model_data["scaler"]["scale"])
        self.hybrid_threshold = self.model_data["hyperparameters"]["hybrid_threshold"]
        
        # Load identities
        self.identities = {}
        for cid, info in self.model_data["identities"].items():
            self.identities[int(cid)] = {
                "name": info["name"],
                "centroid": np.array(info["centroid"])
            }

    def score_team(self, team_name: str, raw_features: dict, mean: np.ndarray = None, scale: np.ndarray = None) -> dict:
        # Get game count for normalization
        games = float(raw_features.get("count_games", 1.0))
        if np.isnan(games) or games <= 0.0:
            games = 1.0

        # Cumulative features to normalize
        CUMULATIVE_FEATURES = {"passing", "receiving", "interrupting", "dribbling", "claiming", "attempted_passes_for"}

        # 1. Align features and fill missing values
        x_raw = []
        for feat in self.features:
            val = raw_features.get(feat, 0.0)
            try:
                val_f = float(val)
            except (ValueError, TypeError):
                val_f = 0.0
            
            if feat in CUMULATIVE_FEATURES:
                val_f = val_f / games
                
            x_raw.append(val_f)
                
        x_raw = np.array(x_raw)
        
        # 2. Scale features using the provided scaler or global parameters
        s_mean = mean if mean is not None else self.scaler_mean
        s_scale = scale if scale is not None else self.scaler_scale
        x_scaled = (x_raw - s_mean) / (s_scale + 1e-9)
        
        # 3. Compute distance and similarity to all centroids
        similarities = {}
        distances = {}
        for cid, info in self.identities.items():
            dist = np.linalg.norm(x_scaled - info["centroid"])
            distances[cid] = dist
            similarities[cid] = 1.0 / (1.0 + dist)
            
        # 4. Sort identities by similarity
        sorted_ids = sorted(similarities.keys(), key=lambda k: similarities[k], reverse=True)
        primary_cid = sorted_ids[0]
        secondary_cid = sorted_ids[1]
        
        primary_name = self.identities[primary_cid]["name"]
        secondary_name = self.identities[secondary_cid]["name"]
        
        s1 = similarities[primary_cid]
        s2 = similarities[secondary_cid]
        
        # 5. Check hybrid status
        # margin = (sim_1 - sim_2) / sim_1
        margin = (s1 - s2) / (s1 + 1e-9)
        is_hybrid = bool(margin < self.hybrid_threshold)
        
        # 6. Generate explanation
        explanation = self._generate_explanation(team_name, x_scaled, primary_cid, primary_name)
        
        # 7. Extract primary driver feature (for backward compatibility)
        primary_centroid = self.identities[primary_cid]["centroid"]
        alignments = [
            (feat, val, float(val * cent)) 
            for feat, val, cent in zip(self.features, x_scaled, primary_centroid)
        ]
        alignments.sort(key=lambda item: item[2], reverse=True)
        top_feature, top_val, _ = alignments[0]
        
        # 8. Compile the results
        scores_payload = {
            self.identities[cid]["name"]: float(similarities[cid]) 
            for cid in sorted_ids
        }
        trait_scores_payload = {
            feat: float(val) for feat, val in zip(self.features, x_scaled)
        }
        
        return {
            # Backward-compatible fields
            "identity": primary_name,
            "metric": FEATURE_MAP.get(top_feature, top_feature),
            "z_score": float(top_val),
            
            # New redesigned fields
            "primary_cluster_id": int(primary_cid),
            "primary_identity": primary_name,
            "secondary_identity": secondary_name,
            "hybrid_flag": is_hybrid,
            "hybrid_margin": float(margin),
            "explanation": explanation,
            "scores": scores_payload,
            "trait_scores": trait_scores_payload
        }

    def _generate_explanation(self, team_name: str, x_scaled: np.ndarray, primary_cid: int, primary_name: str) -> str:
        if primary_name == "Balanced Systems":
            return f"{team_name} exhibits a balanced tactical profile with no extreme statistical outliers."
            
        centroid = self.identities[primary_cid]["centroid"]
        alignments = []
        for feat, val, cent in zip(self.features, x_scaled, centroid):
            alignments.append((feat, val, cent, val * cent))
            
        # Sort by alignment descending
        alignments.sort(key=lambda item: item[3], reverse=True)
        
        top_feats = []
        for feat, val, cent, align in alignments:
            # We want features with significant deviation (abs > 0.3) aligned with the centroid direction
            if align > 0.05 and abs(val) > 0.3:
                direction = "above" if val > 0 else "below"
                display_name = FEATURE_MAP.get(feat, feat)
                top_feats.append(f"{direction}-average {display_name} (Z-score: {val:+.1f})")
            if len(top_feats) == 2:
                break
                
        if len(top_feats) == 2:
            return f"{team_name} is classified under {primary_name} primarily due to its {top_feats[0]} and {top_feats[1]}."
        elif len(top_feats) == 1:
            return f"{team_name} is classified under {primary_name} primarily due to its {top_feats[0]}."
        else:
            return f"{team_name} is classified under {primary_name} based on its overall similarity to the tactical centroid."
