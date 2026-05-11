from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


DEFAULT_LEAGUES = ["mls", "uslc", "nwsl", "usl1"]
DEFAULT_SEASONS = ["2020", "2021", "2022", "2023", "2024", "2025", "2026"]


def parse_args():
    parser = argparse.ArgumentParser(description="Generate TVMS tactical cluster assets.")
    parser.add_argument("--league", action="append", choices=DEFAULT_LEAGUES, help="League to generate. Repeat for multiple.")
    parser.add_argument("--season", action="append", help="Season to generate. Repeat for multiple.")
    parser.add_argument("--output-dir", default="assets", help="Directory for generated PNG and JSON assets.")
    parser.add_argument("--clusters", type=int, default=4, help="Number of K-Means clusters.")
    return parser.parse_args()


def write_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def generate_combo(league: str, season: str, output_dir: Path, n_clusters: int):
    import pandas as pd
    from sklearn.decomposition import PCA

    from src.clustering import cluster_teams
    from src.data_loader import load_tactical_data
    from src.preprocessor import TACTICAL_FEATURES, preprocess_tactical_data
    from src.visualizer import plot_clusters

    print(f"Generating {league.upper()} {season}...")
    df = load_tactical_data(league, season)
    if df.empty:
        print(f"No data for {league} {season}")
        return

    df_scaled, _ = preprocess_tactical_data(df)
    pca = PCA(n_components=2)
    pca.fit(df_scaled)
    clusters, model, probs = cluster_teams(df_scaled, n_clusters=n_clusters)

    image_path = output_dir / f"tactical_clusters_{league}_{season}.png"
    title = f"Tactical Identity Groupings ({league.upper()} {season})"
    team_identities = plot_clusters(df_scaled, clusters, df["team_name"], output_path=image_path, title=title)

    teams_path = output_dir / f"teams_{league}_{season}.json"
    write_json(teams_path, team_identities)

    metadata_path = output_dir / f"metadata_{league}_{season}.json"
    write_json(
        metadata_path,
        {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "league": league,
            "season": season,
            "features": TACTICAL_FEATURES,
            "n_clusters": n_clusters,
            "cluster_model": "GaussianMixture",
            "cluster_random_state": model.random_state,
            "cluster_n_init": model.n_init,
            "pca_explained_variance_ratio": [float(value) for value in pca.explained_variance_ratio_],
        },
    )

    print(f"Saved {image_path}, {teams_path}, and {metadata_path}")


def main():
    args = parse_args()
    leagues = args.league or DEFAULT_LEAGUES
    seasons = args.season or DEFAULT_SEASONS
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for league in leagues:
        for season in seasons:
            try:
                generate_combo(league, season, output_dir, args.clusters)
            except Exception as exc:
                print(f"Error on {league} {season}: {exc}")


if __name__ == "__main__":
    main()
