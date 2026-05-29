from pathlib import Path

import pytest


def test_load_taxonomy_artifact_requires_reference_metadata(tmp_path: Path):
    from src.taxonomy_artifact import load_taxonomy_artifact

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

    with pytest.raises(ValueError, match="reference_window"):
        load_taxonomy_artifact(path)


def test_load_taxonomy_artifact_parses_identity_and_reference_sections():
    from src.taxonomy_artifact import load_taxonomy_artifact

    artifact = load_taxonomy_artifact("src/models/phase1_taxonomy_v1.json")

    assert artifact["version"] == "phase1_taxonomy_v1"
    assert artifact["reference_window"]["season_start"] == 2020
    assert artifact["reference_window"]["season_end"] == 2023
    assert artifact["taxonomy_size"] >= 5
    assert artifact["identities"]
