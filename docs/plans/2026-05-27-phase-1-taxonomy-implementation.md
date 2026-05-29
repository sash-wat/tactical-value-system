# Phase 1 Stable Taxonomy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the remaining season-specific Phase 1 clustering path with a frozen taxonomy scoring flow that uses reference-window preprocessing, outputs primary/secondary identities plus hybrid diagnostics, and produces statistically grounded explanations.

**Architecture:** Keep the existing `phase1_taxonomy_v1` model artifact as the frozen reference model, but move preprocessing and inference onto explicit, reusable functions. The core flow becomes raw team data -> normalized tactical features -> frozen-scaler transform -> taxonomy scorer -> assets/CLI outputs, with tests covering preprocessing, scoring, and orchestration expectations.

**Tech Stack:** Python, pandas, NumPy, pytest, scikit-learn-compatible scaling conventions, existing TVMS codebase

---

### Task 1: Freeze Tactical Preprocessing

**Files:**
- Modify: `src/preprocessor.py`
- Modify: `tests/test_preprocessor.py`

- [ ] **Step 1: Write the failing preprocessing tests**

```python
import pandas as pd

from src.preprocessor import (
    TACTICAL_FEATURES,
    build_tactical_feature_frame,
    transform_tactical_features,
)


def _raw_frame():
    return pd.DataFrame(
        [
            {
                "team_name": "Alpha FC",
                "count_games": 2,
                "passing": 4.0,
                "receiving": 6.0,
                "interrupting": 8.0,
                "dribbling": 10.0,
                "claiming": 12.0,
                "attempted_passes_for": 400.0,
                "pass_completion_percentage_for": 0.80,
                "avg_vertical_distance_for": 7.0,
                "avg_vertical_distance_against": 8.0,
            },
            {
                "team_name": "Beta SC",
                "count_games": 4,
                "passing": 12.0,
                "receiving": 16.0,
                "interrupting": 20.0,
                "dribbling": 24.0,
                "claiming": 28.0,
                "attempted_passes_for": 800.0,
                "pass_completion_percentage_for": 0.70,
                "avg_vertical_distance_for": 6.0,
                "avg_vertical_distance_against": 9.0,
            },
        ]
    )


def test_build_tactical_feature_frame_normalizes_cumulative_metrics_per_game():
    frame = build_tactical_feature_frame(_raw_frame())

    assert list(frame.columns) == TACTICAL_FEATURES
    assert frame.loc[0, "passing"] == 2.0
    assert frame.loc[1, "passing"] == 3.0
    assert frame.loc[0, "attempted_passes_for"] == 200.0
    assert frame.loc[1, "attempted_passes_for"] == 200.0
    assert frame.loc[0, "pass_completion_percentage_for"] == 0.80


def test_transform_tactical_features_uses_supplied_reference_scaler():
    frame = build_tactical_feature_frame(_raw_frame())

    scaled = transform_tactical_features(
        frame,
        mean=[2.5, 3.5, 4.5, 5.5, 6.5, 200.0, 0.75, 6.5, 8.5],
        scale=[0.5, 0.5, 0.5, 0.5, 0.5, 1.0, 0.05, 0.5, 0.5],
    )

    assert scaled.loc[0, "passing"] == -1.0
    assert scaled.loc[1, "passing"] == 1.0
    assert scaled.loc[0, "attempted_passes_for"] == 0.0
    assert scaled.loc[1, "pass_completion_percentage_for"] == -1.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_preprocessor.py -v`
Expected: FAIL with import errors for `build_tactical_feature_frame` and `transform_tactical_features`

- [ ] **Step 3: Implement explicit feature-building and frozen-scaler transform**

```python
import numpy as np
import pandas as pd

TACTICAL_FEATURES = [
    "passing",
    "receiving",
    "interrupting",
    "dribbling",
    "claiming",
    "attempted_passes_for",
    "pass_completion_percentage_for",
    "avg_vertical_distance_for",
    "avg_vertical_distance_against",
]

CUMULATIVE_TACTICAL_FEATURES = {
    "passing",
    "receiving",
    "interrupting",
    "dribbling",
    "claiming",
    "attempted_passes_for",
}


def build_tactical_feature_frame(df: pd.DataFrame) -> pd.DataFrame:
    missing = [f for f in TACTICAL_FEATURES if f not in df.columns]
    if missing:
        raise ValueError(f"Missing features: {missing}")
    if "team_name" not in df.columns:
        raise ValueError("Missing team_name column")

    df_features = df[TACTICAL_FEATURES].apply(pd.to_numeric, errors="coerce")
    games = pd.to_numeric(df.get("count_games", 1.0), errors="coerce").fillna(1.0).clip(lower=1.0)

    for feature in CUMULATIVE_TACTICAL_FEATURES:
        df_features[feature] = df_features[feature] / games

    df_features = df_features.fillna(df_features.mean())
    if df_features.isna().any(axis=None):
        empty_columns = df_features.columns[df_features.isna().any()].tolist()
        raise ValueError(f"Unable to impute empty feature columns: {empty_columns}")

    return df_features


def transform_tactical_features(
    df_features: pd.DataFrame,
    mean: list[float] | np.ndarray,
    scale: list[float] | np.ndarray,
) -> pd.DataFrame:
    mean_arr = np.asarray(mean, dtype=float)
    scale_arr = np.asarray(scale, dtype=float)
    safe_scale = np.where(scale_arr == 0.0, 1.0, scale_arr)
    scaled = (df_features.to_numpy(dtype=float) - mean_arr) / safe_scale
    return pd.DataFrame(scaled, columns=TACTICAL_FEATURES, index=df_features.index)


def preprocess_tactical_data(df: pd.DataFrame):
    df_features = build_tactical_feature_frame(df)
    mean = df_features.mean().to_numpy(dtype=float)
    scale = df_features.std(ddof=0).replace(0.0, 1.0).to_numpy(dtype=float)
    df_scaled = transform_tactical_features(df_features, mean=mean, scale=scale)
    return df_scaled, df["team_name"]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_preprocessor.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_preprocessor.py src/preprocessor.py
git commit -m "feat: freeze phase 1 tactical preprocessing"
```

---

### Task 2: Harden Frozen Taxonomy Scoring

**Files:**
- Modify: `src/taxonomy_scorer.py`
- Modify: `tests/test_taxonomy_scorer.py`

- [ ] **Step 1: Write the failing scorer tests**

```python
from src.taxonomy_scorer import TaxonomyScorer


def test_score_team_uses_frozen_scaler_for_trait_scores():
    scorer = TaxonomyScorer()
    raw_features = {feat: float(mean) for feat, mean in zip(scorer.features, scorer.scaler_mean)}
    raw_features["count_games"] = 1.0

    result = scorer.score_team("Average FC", raw_features)

    assert result["primary_identity"]
    assert result["secondary_identity"]
    assert max(abs(value) for value in result["trait_scores"].values()) < 1e-6


def test_score_team_returns_identity_scores_sorted_high_to_low():
    scorer = TaxonomyScorer()
    raw_features = {feat: float(mean) for feat, mean in zip(scorer.features, scorer.scaler_mean)}
    raw_features["count_games"] = 1.0

    result = scorer.score_team("Average FC", raw_features)
    score_values = list(result["identity_scores"].values())

    assert score_values == sorted(score_values, reverse=True)


def test_score_team_reports_hybrid_with_runner_up_gap_and_reasoning():
    scorer = TaxonomyScorer()
    c0 = scorer.identities[0]["centroid"]
    c5 = scorer.identities[5]["centroid"]
    midpoint = (c0 + c5) / 2.0

    raw_features = {
        feat: float((midpoint[i] * scorer.scaler_scale[i]) + scorer.scaler_mean[i])
        for i, feat in enumerate(scorer.features)
    }
    raw_features["count_games"] = 1.0

    result = scorer.score_team("Hybrid United", raw_features)

    assert result["secondary_identity"]
    assert "top_feature_deltas" in result["assignment_explanation"]
    assert "score_gap" in result["assignment_explanation"]
    assert result["assignment_explanation"]["runner_up_identity"] == result["secondary_identity"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_taxonomy_scorer.py -v`
Expected: FAIL because `identity_scores` and `assignment_explanation` do not match the expected shape

- [ ] **Step 3: Rewrite the scorer around frozen preprocessing and structured explanations**

```python
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.preprocessor import TACTICAL_FEATURES, build_tactical_feature_frame, transform_tactical_features


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

        with open(model_path, "r", encoding="utf-8") as handle:
            model_data = json.load(handle)

        self.version = model_data["version"]
        self.features = model_data["features"]
        self.scaler_mean = np.array(model_data["scaler"]["mean"], dtype=float)
        self.scaler_scale = np.array(model_data["scaler"]["scale"], dtype=float)
        self.hybrid_threshold = float(model_data["hyperparameters"]["hybrid_threshold"])
        self.identities = {
            int(cid): {"name": info["name"], "centroid": np.array(info["centroid"], dtype=float)}
            for cid, info in model_data["identities"].items()
        }

    def _scale_team(self, raw_features: dict) -> pd.Series:
        frame = build_tactical_feature_frame(pd.DataFrame([raw_features | {"team_name": "__team__"}]))
        scaled = transform_tactical_features(frame, mean=self.scaler_mean, scale=self.scaler_scale)
        return scaled.iloc[0]

    def score_team(self, team_name: str, raw_features: dict) -> dict:
        x_scaled = self._scale_team(raw_features)
        distances = {}
        similarities = {}
        for cid, info in self.identities.items():
            dist = float(np.linalg.norm(x_scaled.to_numpy(dtype=float) - info["centroid"]))
            distances[cid] = dist
            similarities[cid] = 1.0 / (1.0 + dist)

        sorted_ids = sorted(similarities, key=lambda cid: similarities[cid], reverse=True)
        primary_cid = sorted_ids[0]
        secondary_cid = sorted_ids[1]
        primary_name = self.identities[primary_cid]["name"]
        secondary_name = self.identities[secondary_cid]["name"]

        primary_score = similarities[primary_cid]
        secondary_score = similarities[secondary_cid]
        score_gap = primary_score - secondary_score
        hybrid_margin = score_gap / (primary_score + 1e-9)
        hybrid_flag = bool(hybrid_margin < self.hybrid_threshold)

        identity_scores = {
            self.identities[cid]["name"]: float(similarities[cid])
            for cid in sorted_ids
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

        return {
            "identity": primary_name,
            "metric": explanation["top_feature_deltas"][0]["feature_label"],
            "z_score": float(explanation["top_feature_deltas"][0]["team_z_score"]),
            "primary_cluster_id": int(primary_cid),
            "primary_identity": primary_name,
            "secondary_identity": secondary_name,
            "hybrid_flag": hybrid_flag,
            "hybrid_margin": float(hybrid_margin),
            "identity_scores": identity_scores,
            "trait_scores": trait_scores,
            "assignment_explanation": explanation,
        }

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
        for feature in self.features:
            team_value = float(x_scaled[feature])
            primary_delta = team_value - float(primary["centroid"][self.features.index(feature)])
            secondary_delta = team_value - float(secondary["centroid"][self.features.index(feature)])
            separation_gain = abs(secondary_delta) - abs(primary_delta)
            deltas.append(
                {
                    "feature": feature,
                    "feature_label": FEATURE_MAP.get(feature, feature),
                    "team_z_score": team_value,
                    "primary_centroid_z": float(primary["centroid"][self.features.index(feature)]),
                    "runner_up_centroid_z": float(secondary["centroid"][self.features.index(feature)]),
                    "separation_gain": float(separation_gain),
                }
            )

        deltas.sort(key=lambda item: item["separation_gain"], reverse=True)
        top_feature_deltas = deltas[:3]
        rationale = (
            f"Closer to {primary['name']} than {secondary['name']} by {score_gap:.4f} similarity points, "
            f"driven most by {top_feature_deltas[0]['feature_label']} and {top_feature_deltas[1]['feature_label']}."
        )

        return {
            "model_version": self.version,
            "winner_identity": primary["name"],
            "runner_up_identity": secondary["name"],
            "winner_score": float(primary_score),
            "runner_up_score": float(secondary_score),
            "score_gap": float(score_gap),
            "top_feature_deltas": top_feature_deltas,
            "rationale": rationale,
        }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_taxonomy_scorer.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_taxonomy_scorer.py src/taxonomy_scorer.py
git commit -m "feat: harden frozen phase 1 taxonomy scoring"
```

---

### Task 3: Replace Remaining Phase 1 Clustering Entrypoints

**Files:**
- Modify: `main.py`
- Modify: `scripts/generate_assets.py`

- [ ] **Step 1: Write the failing orchestration tests**

```python
import pandas as pd

from src.taxonomy_scorer import TaxonomyScorer


def test_taxonomy_scorer_can_score_multiple_rows_without_dynamic_scaler_override():
    scorer = TaxonomyScorer()
    df = pd.DataFrame(
        [
            {"team_name": "One FC", "count_games": 1, **{feat: float(mean) for feat, mean in zip(scorer.features, scorer.scaler_mean)}},
            {"team_name": "Two FC", "count_games": 1, **{feat: float(mean) for feat, mean in zip(scorer.features, scorer.scaler_mean)}},
        ]
    )

    results = [scorer.score_team(row["team_name"], row.to_dict()) for _, row in df.iterrows()]

    assert len(results) == 2
    assert all("identity_scores" in result for result in results)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_taxonomy_scorer.py::test_taxonomy_scorer_can_score_multiple_rows_without_dynamic_scaler_override -v`
Expected: FAIL because the scorer tests do not yet cover the production output path

- [ ] **Step 3: Update the CLI and asset generation flow to use the frozen scorer only**

```python
from src.data_loader import load_tactical_data
from src.taxonomy_scorer import TaxonomyScorer
from src.preprocessor import build_tactical_feature_frame, transform_tactical_features
from src.visualizer import plot_clusters


def run_phase_1():
    print("Loading MLS 2025 data...")
    df = load_tactical_data("mls", "2025")

    scorer = TaxonomyScorer()
    feature_frame = build_tactical_feature_frame(df)
    df_scaled = transform_tactical_features(
        feature_frame,
        mean=scorer.scaler_mean,
        scale=scorer.scaler_scale,
    )

    scored_rows = []
    cluster_ids = []
    for _, row in df.iterrows():
        result = scorer.score_team(row["team_name"], row.to_dict())
        scored_rows.append(
            {
                "team_name": row["team_name"],
                "primary_identity": result["primary_identity"],
                "secondary_identity": result["secondary_identity"],
                "hybrid_flag": result["hybrid_flag"],
            }
        )
        cluster_ids.append(result["primary_cluster_id"])

    print(pd.DataFrame(scored_rows).to_string(index=False))
    plot_clusters(df_scaled, cluster_ids, df["team_name"])
    return scored_rows
```

Use the same `build_tactical_feature_frame` + `transform_tactical_features(... scorer.scaler_mean/scaler_scale ...)` pattern inside `scripts/generate_assets.py`, and remove the dynamic `mean=` / `scale=` override path from that file.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_taxonomy_scorer.py::test_taxonomy_scorer_can_score_multiple_rows_without_dynamic_scaler_override -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add main.py scripts/generate_assets.py tests/test_taxonomy_scorer.py
git commit -m "feat: route phase 1 entrypoints through frozen taxonomy scorer"
```

---

### Task 4: Full Verification

**Files:**
- Verify only: `tests/test_preprocessor.py`
- Verify only: `tests/test_taxonomy_scorer.py`
- Verify only: `tests/test_identity.py`
- Verify only: `tests/test_data_loader.py`

- [ ] **Step 1: Run targeted taxonomy verification**

Run: `pytest tests/test_preprocessor.py tests/test_taxonomy_scorer.py -v`
Expected: PASS

- [ ] **Step 2: Run the full Python test suite**

Run: `pytest -v`
Expected: PASS

- [ ] **Step 3: Smoke-test the CLI entrypoint**

Run: `python main.py`
Expected: prints MLS 2025 primary/secondary identity assignments without calling the old clustering path

- [ ] **Step 4: Commit final verification-safe implementation state**

```bash
git add src/preprocessor.py src/taxonomy_scorer.py main.py scripts/generate_assets.py tests/test_preprocessor.py tests/test_taxonomy_scorer.py
git commit -m "feat: implement stable phase 1 taxonomy scoring flow"
```
