from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from src.preprocessor import build_tactical_feature_frame, transform_tactical_features
from src.taxonomy_artifact import load_taxonomy_artifact


FEATURE_MAP = {
    "passing": "Passing Impact (g+)",
    "receiving": "Receiving Impact (g+)",
    "interrupting": "Defensive Disruption (g+)",
    "dribbling": "Dribbling Impact (g+)",
    "claiming": "Claiming Impact (g+)",
    "attempted_passes_for": "Possession Volume",
    "pass_completion_percentage_for": "Possession Quality",
    "avg_vertical_distance_for": "Attacking Directness",
    "avg_vertical_distance_against": "Opponent Directness",
}


class TaxonomyScorer:
    def __init__(self, model_path: str | None = None):
        if model_path is None:
            repo_root = Path(__file__).resolve().parents[1]
            model_path = str(repo_root / "src" / "models" / "phase1_taxonomy_v1.json")

        self.artifact = load_taxonomy_artifact(model_path)

        self.version = self.artifact["version"]
        self.features = self.artifact["features"]
        self.scaler_mean = np.array(self.artifact["scaler"]["mean"], dtype=float)
        self.scaler_scale = np.array(self.artifact["scaler"]["scale"], dtype=float)
        self.hybrid_threshold = float(self.artifact["hyperparameters"]["hybrid_threshold"])
        self.identities = {
            int(cid): {
                "name": info["name"],
                "description": info.get("description", ""),
                "centroid": np.array(info["centroid"], dtype=float),
                "weight": float(info.get("weight", 1.0)),
                "covariance": np.array(
                    info.get(
                        "covariance",
                        np.eye(len(self.features)),
                    ),
                    dtype=float,
                ),
            }
            for cid, info in self.artifact["identities"].items()
        }

    def _scale_team(self, team_name: str, raw_features: dict) -> pd.Series:
        row = {"team_name": team_name, **raw_features}
        frame = build_tactical_feature_frame(pd.DataFrame([row]))
        scaled = transform_tactical_features(frame, mean=self.scaler_mean, scale=self.scaler_scale)
        return scaled.iloc[0]

    def _build_assignment_explanation(
        self,
        *,
        x_scaled: pd.Series,
        primary_cid: int,
        secondary_cid: int,
        primary_score: float,
        secondary_score: float,
        score_gap: float,
    ) -> dict:
        primary = self.identities[primary_cid]
        secondary = self.identities[secondary_cid]

        deltas = []
        for index, feature in enumerate(self.features):
            team_value = float(x_scaled[feature])
            primary_centroid = float(primary["centroid"][index])
            secondary_centroid = float(secondary["centroid"][index])
            primary_delta = abs(team_value - primary_centroid)
            secondary_delta = abs(team_value - secondary_centroid)
            deltas.append(
                {
                    "feature": feature,
                    "feature_label": FEATURE_MAP.get(feature, feature),
                    "team_z_score": team_value,
                    "primary_centroid_z": primary_centroid,
                    "runner_up_centroid_z": secondary_centroid,
                    "separation_gain": float(secondary_delta - primary_delta),
                }
            )

        deltas.sort(key=lambda item: item["separation_gain"], reverse=True)
        top_feature_deltas = deltas[:3]
        top_labels = ", ".join(item["feature_label"] for item in top_feature_deltas[:2])
        rationale = (
            f"Closer to {primary['name']} than {secondary['name']} by {score_gap:.4f} similarity points, "
            f"driven most by {top_labels}."
        )

        return {
            "model_version": self.version,
            "winner_identity": primary["name"],
            "winner_description": primary["description"],
            "runner_up_identity": secondary["name"],
            "runner_up_description": secondary["description"],
            "winner_score": float(primary_score),
            "runner_up_score": float(secondary_score),
            "score_gap": float(score_gap),
            "top_feature_deltas": top_feature_deltas,
            "rationale": rationale,
        }

    def score_team(self, team_name: str, raw_features: dict) -> dict:
        x_scaled = self._scale_team(team_name, raw_features)
        x_vector = x_scaled.to_numpy(dtype=float)

        distances = {}
        log_scores = {}
        for cid, info in self.identities.items():
            covariance = info["covariance"]
            delta = x_vector - info["centroid"]
            sign, logdet = np.linalg.slogdet(covariance)
            if sign <= 0:
                covariance = covariance + np.eye(len(self.features)) * 1e-6
                sign, logdet = np.linalg.slogdet(covariance)
            solved = np.linalg.solve(covariance, delta)
            mahalanobis_sq = float(delta.T @ solved)
            distances[cid] = float(np.sqrt(max(mahalanobis_sq, 0.0)))
            log_scores[cid] = float(np.log(info["weight"] + 1e-12) - 0.5 * (logdet + mahalanobis_sq))

        max_log = max(log_scores.values())
        normalized = {cid: float(np.exp(score - max_log)) for cid, score in log_scores.items()}
        denom = sum(normalized.values())
        similarities = {cid: value / denom for cid, value in normalized.items()}

        sorted_ids = sorted(similarities, key=lambda cid: similarities[cid], reverse=True)
        primary_cid = sorted_ids[0]
        secondary_cid = sorted_ids[1]
        primary = self.identities[primary_cid]
        secondary = self.identities[secondary_cid]
        primary_name = primary["name"]
        secondary_name = secondary["name"]

        primary_score = float(similarities[primary_cid])
        secondary_score = float(similarities[secondary_cid])
        score_gap = primary_score - secondary_score
        hybrid_margin = score_gap / (primary_score + 1e-9)
        hybrid_flag = bool(hybrid_margin < self.hybrid_threshold)

        identity_scores = {
            self.identities[cid]["name"]: float(similarities[cid]) for cid in sorted_ids
        }
        trait_scores = {feature: float(x_scaled[feature]) for feature in self.features}
        explanation = self._build_assignment_explanation(
            x_scaled=x_scaled,
            primary_cid=primary_cid,
            secondary_cid=secondary_cid,
            primary_score=primary_score,
            secondary_score=secondary_score,
            score_gap=score_gap,
        )

        lead_feature = explanation["top_feature_deltas"][0]

        return {
            "identity": primary_name,
            "identity_description": primary["description"],
            "metric": lead_feature["feature_label"],
            "z_score": float(lead_feature["team_z_score"]),
            "primary_cluster_id": int(primary_cid),
            "primary_identity": primary_name,
            "primary_identity_description": primary["description"],
            "secondary_identity": secondary_name,
            "secondary_identity_description": secondary["description"],
            "hybrid_flag": hybrid_flag,
            "hybrid_margin": float(hybrid_margin),
            "identity_scores": identity_scores,
            "scores": identity_scores,
            "trait_scores": trait_scores,
            "assignment_explanation": explanation,
            "explanation": explanation["rationale"],
            "distances": {
                self.identities[cid]["name"]: float(distances[cid]) for cid in sorted_ids
            },
        }
