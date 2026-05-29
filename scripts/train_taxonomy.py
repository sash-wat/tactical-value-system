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
MODEL_VERSION = "phase1_taxonomy_v1"
FEATURE_SCHEMA_VERSION = "phase1_v1"

FEATURE_LABELS = {
    "passing": "Passing Progression",
    "receiving": "Advanced Occupation",
    "interrupting": "Disruption",
    "dribbling": "Ball Carrying",
    "claiming": "Aerial Control",
    "attempted_passes_for": "Possession Volume",
    "pass_completion_percentage_for": "Circulation",
    "avg_vertical_distance_for": "Verticality",
    "avg_vertical_distance_against": "Pressing",
}


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


def _fit_candidate(scaled_values: np.ndarray, n_identities: int) -> tuple[GaussianMixture, np.ndarray, np.ndarray]:
    gmm = GaussianMixture(
        n_components=n_identities,
        random_state=42,
        n_init=20,
        reg_covar=1e-5,
    )
    labels = gmm.fit_predict(scaled_values)
    probabilities = gmm.predict_proba(scaled_values)
    return gmm, labels, probabilities


def _summarize_candidate(labels: np.ndarray, cohort: pd.DataFrame) -> dict:
    label_series = pd.Series(labels, name="cluster")
    counts = label_series.value_counts().sort_index()
    mls_mask = cohort["league"] == "mls"
    mls_counts = label_series[mls_mask].value_counts().sort_index()

    return {
        "cluster_counts": {int(cluster_id): int(count) for cluster_id, count in counts.items()},
        "min_cluster_size": int(counts.min()),
        "max_cluster_share": float(counts.max() / len(label_series)),
        "mls_unique_identities": int(mls_counts.size),
        "mls_max_cluster_share": float(mls_counts.max() / mls_counts.sum()) if not mls_counts.empty else 1.0,
    }


def _candidate_is_plausible(summary: dict) -> bool:
    return (
        summary["min_cluster_size"] >= 4
        and summary["max_cluster_share"] <= 0.40
        and summary["mls_unique_identities"] >= 4
        and summary["mls_max_cluster_share"] <= 0.45
    )


def _build_identity_profile(centroid: pd.Series, used_names: set[str]) -> tuple[str, str]:
    ranked = centroid.sort_values(ascending=False).index.tolist()
    top_two = ranked[:2]
    top_three = ranked[:3]

    description = None
    if top_two[0] == "interrupting":
        if top_two[1] in {"pass_completion_percentage_for", "passing"}:
            base = "Disruptive Circulation"
            description = (
                "Above-average defensive disruption paired with clean circulation. "
                "These teams win the ball, reconnect passes quickly, and usually keep the opponent from playing directly."
            )
        elif top_two[1] == "avg_vertical_distance_against":
            base = "High Press Disruption"
            description = (
                "Aggressive ball-winning teams that press high and make opponents play through immediate pressure."
            )
        else:
            base = "Disruptive Defense"
            description = (
                "Defense-first teams whose defining edge is their ability to interrupt opposition possessions."
            )
    elif top_two[0] == "attempted_passes_for":
        base = "Possession Control"
        description = (
            "High-volume, high-completion possession teams that slow the game down, keep the ball, "
            "and minimize direct attacking sequences."
        )
    elif top_two[0] == "pass_completion_percentage_for":
        if "interrupting" in top_three:
            base = "Disruptive Circulation"
            description = (
                "Above-average defensive disruption paired with clean circulation. "
                "These teams win the ball, reconnect passes quickly, and usually keep the opponent from playing directly."
            )
        else:
            base = "Efficient Circulation"
            description = "Teams that are primarily defined by efficient passing and secure circulation."
    elif top_two[0] == "avg_vertical_distance_for":
        if top_two[1] == "avg_vertical_distance_against":
            if centroid["passing"] > 1.0 and centroid["attempted_passes_for"] < -1.5:
                base = "Transition Surge"
                description = (
                    "An extreme direct-transition profile: very high attacking directness and pressure, "
                    "with little reliance on possession volume or passing security."
                )
            else:
                base = "Direct Transition"
                description = (
                    "Direct teams that attack forward quickly and press assertively without needing large possession shares."
                )
        elif top_two[1] == "claiming":
            base = "Aerial Transition"
            description = (
                "Direct teams that lean on aerial wins and second balls to launch transitions rather than sustained possession."
            )
        else:
            base = "Direct Vertical Play"
            description = "Teams that prioritize direct ball progression and vertical attacks."
    elif top_two[0] == "claiming":
        if top_two[1] == "avg_vertical_distance_for":
            base = "Aerial Transition"
            description = (
                "Direct teams that lean on aerial wins and second balls to launch transitions rather than sustained possession."
            )
        elif top_two[1] == "passing":
            base = "Aerial Progression"
            description = (
                "Teams that mix above-average aerial control with progressive passing, often advancing play through longer entries "
                "and second-ball control more than sustained circulation."
            )
        else:
            base = "Aerial Control"
            description = "Teams that are primarily defined by above-average aerial control."
    elif top_two[0] == "passing":
        if top_two[1] == "claiming":
            base = "Aerial Progression"
            description = (
                "Teams that mix above-average aerial control with progressive passing, often advancing play through longer entries "
                "and second-ball control more than sustained circulation."
            )
        elif top_two[1] == "avg_vertical_distance_for":
            base = "Direct Transition"
            description = (
                "Direct teams that attack forward quickly and press assertively without needing large possession shares."
            )
        else:
            base = "Passing Progression"
            description = "Teams that are primarily defined by progressive passing value."
    elif "attempted_passes_for" in top_two and "pass_completion_percentage_for" in top_three:
        base = "Possession Control"
        description = (
            "High-volume, high-completion possession teams that slow the game down, keep the ball, "
            "and minimize direct attacking sequences."
        )
    elif "avg_vertical_distance_for" in top_two:
        base = "Direct Vertical Play"
        description = "Teams that prioritize direct ball progression and vertical attacks."
    elif "interrupting" in top_two and "avg_vertical_distance_against" in top_three:
        base = "High Press Disruption"
        description = (
            "Aggressive ball-winning teams that press high and make opponents play through immediate pressure."
        )
    elif "receiving" in top_two:
        base = "Territorial Occupation"
        description = (
            "Teams that push receivers into advanced zones, carry the ball forward, and defend high enough to spend long stretches "
            "in the opponent's half without relying on pure possession volume."
        )
    elif "dribbling" in top_two:
        base = "Ball-Carrying Attack"
        description = "Teams that are primarily defined by above-average dribbling and carry-driven progression."
    elif "claiming" in top_two:
        base = "Aerial Control"
        description = "Teams that are primarily defined by above-average aerial control."
    elif "passing" in top_two:
        base = "Passing Progression"
        description = "Teams that are primarily defined by progressive passing value."
    elif "pass_completion_percentage_for" in top_two:
        base = "Efficient Circulation"
        description = "Teams that are primarily defined by efficient passing and secure circulation."
    elif "avg_vertical_distance_against" in top_two:
        base = "Front-Foot Pressure"
        description = "Teams that are primarily defined by front-foot pressure and their ability to press opponents into quicker actions."
    else:
        base = FEATURE_LABELS.get(top_two[0], top_two[0])
        description = f"Teams primarily defined by {FEATURE_LABELS.get(top_two[0], top_two[0]).lower()}."

    if base in used_names:
        qualifier = None
        for feature in ranked[1:4]:
            candidate = FEATURE_LABELS.get(feature, feature)
            candidate_lower = candidate.lower()
            base_lower = base.lower()
            is_redundant = (
                candidate_lower in base_lower
                or (candidate_lower == "pressing" and "pressure" in base_lower)
                or (candidate_lower == "verticality" and "vertical" in base_lower)
            )
            if not is_redundant:
                qualifier = candidate
                break
        qualifier = qualifier or FEATURE_LABELS.get(top_two[1], top_two[1])
        base = f"{base} / {qualifier}"
        description = f"{description} Secondary emphasis: {qualifier}."

    used_names.add(base)
    return base, description


def _name_identities(means: pd.DataFrame, cluster_counts: dict[int, int], weights: np.ndarray, covariances: np.ndarray) -> dict[int, dict]:
    used_names: set[str] = set()
    identities = {}
    for cluster_id in means.index.tolist():
        centroid = means.loc[cluster_id]
        ranked = centroid.sort_values(ascending=False)
        name, description = _build_identity_profile(centroid, used_names)
        identities[int(cluster_id)] = {
            "name": name,
            "description": description,
            "centroid": centroid.tolist(),
            "weight": float(weights[cluster_id]),
            "covariance": covariances[cluster_id].tolist(),
            "cluster_size": int(cluster_counts.get(int(cluster_id), 0)),
            "top_features": [
                {
                    "feature": feature,
                    "feature_label": FEATURE_LABELS.get(feature, feature),
                    "centroid_z": float(value),
                }
                for feature, value in ranked.head(3).items()
            ],
        }
    return identities


def _calibrate_hybrid_threshold(probabilities: np.ndarray) -> float:
    margins = []
    for row in probabilities:
        sorted_scores = sorted((float(score) for score in row), reverse=True)
        margin = (sorted_scores[0] - sorted_scores[1]) / (sorted_scores[0] + 1e-9)
        margins.append(margin)

    percentile_threshold = float(np.percentile(margins, 5))
    return float(np.clip(percentile_threshold, 0.10, 0.50))


def discover_taxonomy(df_all: pd.DataFrame) -> dict:
    feature_frame = build_tactical_feature_frame(df_all)
    scaler = StandardScaler()
    scaled_values = scaler.fit_transform(feature_frame)

    best = None
    candidates = []
    for n_identities in range(5, 8):
        gmm, labels, probabilities = _fit_candidate(scaled_values, n_identities)
        centroids = (
            pd.DataFrame(scaled_values, columns=TACTICAL_FEATURES)
            .assign(cluster=labels)
            .groupby("cluster")
            .mean()
            .sort_index()
        )
        means = pd.DataFrame(gmm.means_, columns=TACTICAL_FEATURES).sort_index()
        summary = _summarize_candidate(labels, df_all)
        candidate = {
            "bic": float(gmm.bic(scaled_values)),
            "n_identities": n_identities,
            "labels": labels,
            "probabilities": probabilities,
            "means": means,
            "centroids": centroids,
            "weights": gmm.weights_,
            "covariances": gmm.covariances_,
            "scaler": scaler,
            "summary": summary,
            "plausible": _candidate_is_plausible(summary),
        }
        candidates.append(candidate)

    plausible_candidates = [candidate for candidate in candidates if candidate["plausible"]]
    search_space = plausible_candidates or candidates
    best = min(search_space, key=lambda candidate: candidate["bic"])

    identities = _name_identities(
        best["means"],
        best["summary"]["cluster_counts"],
        best["weights"],
        best["covariances"],
    )
    hybrid_threshold = _calibrate_hybrid_threshold(best["probabilities"])

    return {
        "n_identities": best["n_identities"],
        "labels": best["labels"],
        "probabilities": best["probabilities"],
        "means": best["means"],
        "centroids": best["centroids"],
        "weights": best["weights"],
        "covariances": best["covariances"],
        "scaler": best["scaler"],
        "identities": identities,
        "candidate_metrics": [
            {
                "n_identities": candidate["n_identities"],
                "bic": candidate["bic"],
                "plausible": candidate["plausible"],
                **candidate["summary"],
            }
            for candidate in candidates
        ],
        "selected_summary": best["summary"],
        "hybrid_threshold": hybrid_threshold,
    }


def export_taxonomy_artifact(df_all: pd.DataFrame, discovered: dict, output_path: Path) -> None:
    scaler = discovered["scaler"]
    identities = discovered["identities"]

    payload = {
        "version": MODEL_VERSION,
        "trained_at": pd.Timestamp.now().isoformat(),
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "reference_window": {
            "season_start": int(min(int(season) for season in SEASONS)),
            "season_end": int(max(int(season) for season in SEASONS)),
            "leagues": LEAGUES,
        },
        "training_summary": {
            "n_team_seasons": int(len(df_all)),
            "n_identities": int(discovered["n_identities"]),
            "league_counts": df_all["league"].value_counts().sort_index().to_dict(),
            "season_counts": df_all["season"].value_counts().sort_index().to_dict(),
            "selected_candidate": discovered["selected_summary"],
            "candidate_metrics": discovered["candidate_metrics"],
        },
        "features": TACTICAL_FEATURES,
        "scaler": {
            "mean": scaler.mean_.tolist(),
            "scale": scaler.scale_.tolist(),
        },
        "identities": {
            str(cluster_id): identity_payload for cluster_id, identity_payload in identities.items()
        },
        "hyperparameters": {
            "hybrid_threshold": discovered["hybrid_threshold"],
            "hybrid_threshold_method": "5th percentile of relative posterior gap, clamped to [0.10, 0.50]",
        },
    }
    write_taxonomy_artifact(output_path, payload)


def train_taxonomy() -> Path:
    print("Loading 2020-2023 reference cohort data across all leagues...")
    df_all = build_reference_cohort()
    print(f"Total reference cohort size: {len(df_all)} team-seasons.")

    discovered = discover_taxonomy(df_all)
    print(f"Selected taxonomy size: {discovered['n_identities']} identities.")
    for metric in discovered["candidate_metrics"]:
        print(
            "Candidate",
            metric["n_identities"],
            "BIC=",
            f"{metric['bic']:.2f}",
            "plausible=",
            metric["plausible"],
            "mls_unique_identities=",
            metric["mls_unique_identities"],
            "mls_max_cluster_share=",
            f"{metric['mls_max_cluster_share']:.3f}",
        )

    model_dir = REPO_ROOT / "src" / "models"
    model_dir.mkdir(parents=True, exist_ok=True)
    output_path = model_dir / f"{MODEL_VERSION}.json"
    export_taxonomy_artifact(df_all, discovered, output_path)
    print(f"Saved taxonomy artifact to {output_path}")
    return output_path


if __name__ == "__main__":
    train_taxonomy()
