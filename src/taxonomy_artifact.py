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
