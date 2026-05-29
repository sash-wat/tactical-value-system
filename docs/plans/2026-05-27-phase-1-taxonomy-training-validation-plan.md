# Phase 1 Taxonomy Training And Validation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rework the Phase 1 taxonomy training pipeline so `phase1_taxonomy_v1` is trained from a documented `2020-2023` reference cohort, exported as a richer frozen artifact, and validated against `2024+` scoring seasons before downstream assets are regenerated.

**Architecture:** Treat training, artifact serialization, validation, and downstream regeneration as separate units. The core flow becomes pooled reference data load -> shared tactical preprocessing -> candidate taxonomy discovery -> frozen artifact export -> `2024+` validation -> asset regeneration, with tests around artifact shape, training behavior, and validation summaries.

**Tech Stack:** Python, pandas, NumPy, scikit-learn, pytest, existing TVMS data loader and preprocessing modules

---

### Task 1: Add A Formal Taxonomy Artifact Schema

**Files:**
- Create: `src/taxonomy_artifact.py`
- Create: `tests/test_taxonomy_artifact.py`
- Modify: `src/taxonomy_scorer.py`

- [ ] **Step 1: Write the failing artifact tests**

```python
from pathlib import Path

from src.taxonomy_artifact import load_taxonomy_artifact


def test_load_taxonomy_artifact_requires_reference_metadata(tmp_path: Path):
    path = tmp_path / "taxonomy.json"
    path.write_text(
        """
        {
          "version": "phase1_taxonomy_v1",
          "trained_at": "2026-05-27T00:00:00",
          "features": ["passing"],
          "scaler": {"mean": [0.0], "scale": [1.0]},
          "identities": {"0": {"name": "Example", "centroid": [0.0]}},
          "hyperparameters": {"hybrid_threshold": 0.1}
        }
        """.strip(),
        encoding="utf-8",
    )

    try:
        load_taxonomy_artifact(path)
    except ValueError as exc:
        assert "reference_window" in str(exc)
    else:
        raise AssertionError("Expected ValueError for missing reference metadata")


def test_load_taxonomy_artifact_parses_identity_and_reference_sections():
    artifact = load_taxonomy_artifact("src/models/phase1_taxonomy_v1.json")

    assert artifact["version"] == "phase1_taxonomy_v1"
    assert artifact["reference_window"]["season_start"] == 2020
    assert artifact["reference_window"]["season_end"] == 2023
    assert artifact["taxonomy_size"] >= 5
    assert artifact["identities"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_taxonomy_artifact.py -v`
Expected: FAIL because `src/taxonomy_artifact.py` does not exist yet

- [ ] **Step 3: Implement artifact loading and validation**

```python
from __future__ import annotations

import json
from pathlib import Path


REQUIRED_TOP_LEVEL_KEYS = {
    "version",
    "trained_at",
    "feature_schema_version",
    "reference_window",
    "training_summary",
    "features",
    "scaler",
    "identities",
    "hyperparameters",
}


def load_taxonomy_artifact(path: str | Path) -> dict:
    artifact_path = Path(path)
    data = json.loads(artifact_path.read_text(encoding="utf-8"))

    missing = REQUIRED_TOP_LEVEL_KEYS - set(data.keys())
    if missing:
        raise ValueError(f"Taxonomy artifact missing keys: {sorted(missing)}")

    reference_window = data["reference_window"]
    for key in ["season_start", "season_end", "leagues"]:
        if key not in reference_window:
            raise ValueError(f"Taxonomy artifact reference_window missing key: {key}")

    data["taxonomy_size"] = len(data["identities"])
    return data


def write_taxonomy_artifact(path: str | Path, payload: dict) -> None:
    Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
```

Update `src/taxonomy_scorer.py` to load the artifact via `load_taxonomy_artifact(...)` instead of opening JSON directly.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_taxonomy_artifact.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_taxonomy_artifact.py src/taxonomy_artifact.py src/taxonomy_scorer.py
git commit -m "feat: add formal phase 1 taxonomy artifact schema"
```

---

### Task 2: Rework Reference-Cohort Training

**Files:**
- Modify: `scripts/train_taxonomy.py`
- Create: `tests/test_train_taxonomy.py`
- Modify: `src/models/phase1_taxonomy_v1.json`

- [ ] **Step 1: Write the failing training tests**

```python
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
            {"team_name": f"Team {idx}", "league": "mls", "season": "2020", "count_games": 1,
             "passing": float(idx), "receiving": float(idx + 1), "interrupting": float(idx + 2),
             "dribbling": float(idx + 3), "claiming": float(idx + 4),
             "attempted_passes_for": float(200 + idx), "pass_completion_percentage_for": 0.7 + idx * 0.001,
             "avg_vertical_distance_for": 6.0 + idx * 0.1, "avg_vertical_distance_against": 8.0 - idx * 0.05}
            for idx in range(14)
        ]
    )

    model = discover_taxonomy(df)

    assert 5 <= model["n_identities"] <= 7
    assert len(model["identities"]) == model["n_identities"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_train_taxonomy.py -v`
Expected: FAIL because `build_reference_cohort` and `discover_taxonomy` are not exported

- [ ] **Step 3: Rewrite training into explicit reference-cohort and discovery helpers**

```python
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.data_loader import load_tactical_data
from src.preprocessor import TACTICAL_FEATURES, build_tactical_feature_frame
from src.taxonomy_artifact import write_taxonomy_artifact

LEAGUES = ["mls", "uslc", "nwsl", "usl1"]
SEASONS = ["2020", "2021", "2022", "2023"]


def build_reference_cohort(source_frames: dict[tuple[str, str], pd.DataFrame] | None = None) -> pd.DataFrame:
    frames = []
    iterable = source_frames.items() if source_frames is not None else [
        ((league, season), load_tactical_data(league, season))
        for league in LEAGUES
        for season in SEASONS
    ]

    for (league, season), df in iterable:
        if df.empty:
            continue
        cohort_df = df.copy()
        cohort_df["league"] = league
        cohort_df["season"] = season
        frames.append(cohort_df)

    if not frames:
        raise ValueError("No reference cohort data loaded")

    return pd.concat(frames, ignore_index=True)


def discover_taxonomy(df_all: pd.DataFrame) -> dict:
    feature_frame = build_tactical_feature_frame(df_all)
    scaler = StandardScaler()
    scaled = scaler.fit_transform(feature_frame)

    best = None
    for n_identities in range(5, 8):
        gmm = GaussianMixture(n_components=n_identities, random_state=42, n_init=10)
        labels = gmm.fit_predict(scaled)
        bic = gmm.bic(scaled)
        if best is None or bic < best["bic"]:
            centroids = pd.DataFrame(scaled, columns=TACTICAL_FEATURES).assign(cluster=labels).groupby("cluster").mean()
            best = {
                "bic": bic,
                "n_identities": n_identities,
                "labels": labels,
                "gmm": gmm,
                "centroids": centroids,
                "scaler": scaler,
            }

    return {
        "n_identities": best["n_identities"],
        "labels": best["labels"],
        "centroids": best["centroids"],
        "scaler": best["scaler"],
        "identities": best["centroids"].to_dict(orient="index"),
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_train_taxonomy.py -v`
Expected: PASS

- [ ] **Step 5: Add artifact export with richer metadata and retrain `phase1_taxonomy_v1.json`**

```python
def export_taxonomy_artifact(df_all: pd.DataFrame, discovered: dict, output_path: Path) -> None:
    labels = discovered["labels"]
    centroids = discovered["centroids"]
    scaler = discovered["scaler"]

    identity_names = {
        int(cluster_id): f"Identity {cluster_id + 1}"
        for cluster_id in centroids.index.tolist()
    }

    payload = {
        "version": "phase1_taxonomy_v1",
        "trained_at": pd.Timestamp.now().isoformat(),
        "feature_schema_version": "phase1_v1",
        "reference_window": {
            "season_start": 2020,
            "season_end": 2023,
            "leagues": LEAGUES,
        },
        "training_summary": {
            "n_team_seasons": int(len(df_all)),
            "n_identities": int(discovered["n_identities"]),
            "league_counts": df_all["league"].value_counts().sort_index().to_dict(),
            "season_counts": df_all["season"].value_counts().sort_index().to_dict(),
        },
        "features": TACTICAL_FEATURES,
        "scaler": {
            "mean": scaler.mean_.tolist(),
            "scale": scaler.scale_.tolist(),
        },
        "identities": {
            str(cluster_id): {
                "name": identity_names[int(cluster_id)],
                "centroid": centroids.loc[cluster_id].tolist(),
            }
            for cluster_id in centroids.index.tolist()
        },
        "hyperparameters": {
            "hybrid_threshold": 0.1,
        },
    }
    write_taxonomy_artifact(output_path, payload)
```

After exporting, run:

Run: `python scripts/train_taxonomy.py`
Expected: `src/models/phase1_taxonomy_v1.json` is regenerated with `reference_window`, `training_summary`, and `feature_schema_version`

- [ ] **Step 6: Commit**

```bash
git add tests/test_train_taxonomy.py scripts/train_taxonomy.py src/models/phase1_taxonomy_v1.json
git commit -m "feat: rework phase 1 reference cohort training pipeline"
```

---

### Task 3: Add Taxonomy Validation For 2024+

**Files:**
- Create: `src/taxonomy_validation.py`
- Create: `scripts/validate_taxonomy.py`
- Create: `tests/test_taxonomy_validation.py`

- [ ] **Step 1: Write the failing validation tests**

```python
import pandas as pd

from src.taxonomy_validation import summarize_validation_results


def test_summarize_validation_results_reports_temporal_and_league_coverage():
    scored = pd.DataFrame(
        [
            {"league": "mls", "season": "2024", "primary_identity": "Identity 1", "secondary_identity": "Identity 2", "hybrid_flag": False, "distance_to_primary": 0.4},
            {"league": "nwsl", "season": "2024", "primary_identity": "Identity 2", "secondary_identity": "Identity 1", "hybrid_flag": True, "distance_to_primary": 0.6},
        ]
    )

    summary = summarize_validation_results(scored)

    assert summary["n_scored_rows"] == 2
    assert summary["league_identity_coverage"]["mls"]["Identity 1"] == 1
    assert "hybrid_rate" in summary
    assert "distance_summary" in summary
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_taxonomy_validation.py -v`
Expected: FAIL because `src/taxonomy_validation.py` does not exist yet

- [ ] **Step 3: Implement validation summary helpers and CLI**

```python
from __future__ import annotations

import pandas as pd


def summarize_validation_results(scored: pd.DataFrame) -> dict:
    return {
        "n_scored_rows": int(len(scored)),
        "hybrid_rate": float(scored["hybrid_flag"].mean()) if len(scored) else 0.0,
        "league_identity_coverage": (
            scored.groupby(["league", "primary_identity"]).size().unstack(fill_value=0).to_dict(orient="index")
            if len(scored)
            else {}
        ),
        "distance_summary": {
            "mean": float(scored["distance_to_primary"].mean()) if len(scored) else 0.0,
            "max": float(scored["distance_to_primary"].max()) if len(scored) else 0.0,
        },
    }
```

```python
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


def main():
    scorer = TaxonomyScorer()
    rows = []
    for league in ["mls", "uslc", "nwsl", "usl1"]:
        for season in ["2024", "2025", "2026"]:
            df = load_tactical_data(league, season)
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

    summary = summarize_validation_results(pd.DataFrame(rows))
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_taxonomy_validation.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_taxonomy_validation.py src/taxonomy_validation.py scripts/validate_taxonomy.py
git commit -m "feat: add phase 1 taxonomy validation pipeline"
```

---

### Task 4: Regenerate Assets And Align Metadata

**Files:**
- Modify: `scripts/generate_assets.py`
- Modify: `assets/metadata_*.json`
- Modify: `assets/teams_*.json`

- [ ] **Step 1: Add metadata assertions to the scorer tests**

```python
from src.taxonomy_scorer import TaxonomyScorer


def test_taxonomy_scorer_exposes_artifact_version_and_reference_window():
    scorer = TaxonomyScorer()

    assert scorer.version == "phase1_taxonomy_v1"
    assert scorer.artifact["reference_window"]["season_start"] == 2020
    assert scorer.artifact["reference_window"]["season_end"] == 2023
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_taxonomy_scorer.py::test_taxonomy_scorer_exposes_artifact_version_and_reference_window -v`
Expected: FAIL because the scorer does not yet retain the loaded artifact payload

- [ ] **Step 3: Expose artifact metadata and propagate it into generated outputs**

```python
class TaxonomyScorer:
    def __init__(self, model_path: str | None = None):
        artifact = load_taxonomy_artifact(model_path or default_path)
        self.artifact = artifact
        self.version = artifact["version"]
        ...
```

Update `scripts/generate_assets.py` metadata payloads to include:

```python
{
    "model_version": scorer.version,
    "reference_window": scorer.artifact["reference_window"],
    "feature_schema_version": scorer.artifact["feature_schema_version"],
    "training_summary": scorer.artifact["training_summary"],
}
```

Then regenerate outputs:

Run: `python scripts/generate_assets.py`
Expected: team and metadata JSON files are rewritten with frozen taxonomy metadata

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_taxonomy_scorer.py::test_taxonomy_scorer_exposes_artifact_version_and_reference_window -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_taxonomy_scorer.py src/taxonomy_scorer.py scripts/generate_assets.py assets
git commit -m "feat: regenerate phase 1 assets from validated taxonomy artifact"
```

---

### Task 5: End-To-End Verification

**Files:**
- Verify only: `tests/test_taxonomy_artifact.py`
- Verify only: `tests/test_train_taxonomy.py`
- Verify only: `tests/test_taxonomy_validation.py`
- Verify only: `tests/test_taxonomy_scorer.py`
- Verify only: `src/models/phase1_taxonomy_v1.json`

- [ ] **Step 1: Run the new training and validation test group**

Run: `pytest tests/test_taxonomy_artifact.py tests/test_train_taxonomy.py tests/test_taxonomy_validation.py tests/test_taxonomy_scorer.py -v`
Expected: PASS

- [ ] **Step 2: Run the full Python test suite**

Run: `pytest -v`
Expected: PASS

- [ ] **Step 3: Rebuild the reference taxonomy artifact**

Run: `python scripts/train_taxonomy.py`
Expected: `src/models/phase1_taxonomy_v1.json` is regenerated from `2020-2023`

- [ ] **Step 4: Run the validation CLI**

Run: `python scripts/validate_taxonomy.py`
Expected: prints a validation summary covering `2024+` league coverage, hybrid rate, and distance summary

- [ ] **Step 5: Regenerate public assets**

Run: `python scripts/generate_assets.py`
Expected: refreshed `assets/teams_*.json`, `assets/metadata_*.json`, and plot files consistent with the retrained taxonomy

- [ ] **Step 6: Commit**

```bash
git add scripts/train_taxonomy.py scripts/validate_taxonomy.py src/taxonomy_artifact.py src/taxonomy_validation.py src/models/phase1_taxonomy_v1.json tests/test_taxonomy_artifact.py tests/test_train_taxonomy.py tests/test_taxonomy_validation.py tests/test_taxonomy_scorer.py assets
git commit -m "feat: train and validate stable phase 1 taxonomy"
```
