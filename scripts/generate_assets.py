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

    from src.data_loader import load_tactical_data
    from src.visualizer import plot_clusters
    from src.taxonomy_scorer import TaxonomyScorer

    print(f"Generating {league.upper()} {season} using stable taxonomy scorer...")
    df = load_tactical_data(league, season)
    if df.empty:
        print(f"No data for {league} {season}")
        return

    scorer = TaxonomyScorer()

    # Preprocess and scale features using the frozen normalizer parameters
    df_features = df[scorer.features].apply(pd.to_numeric, errors='coerce').fillna(0.0)
    
    # Normalize cumulative features per game
    games = pd.to_numeric(df["count_games"], errors='coerce').fillna(1.0).clip(lower=1.0)
    CUMULATIVE_FEATURES = ["passing", "receiving", "interrupting", "dribbling", "claiming", "attempted_passes_for"]
    for feat in CUMULATIVE_FEATURES:
        df_features[feat] = df_features[feat] / games

    # Calculate relative mean and scale for the specific league-season
    mean = df_features.mean().values
    scale = df_features.std().fillna(1.0).replace(0.0, 1.0).values

    scaled_values = (df_features.values - mean) / (scale + 1e-9)
    df_scaled = pd.DataFrame(scaled_values, columns=scorer.features)

    # Fit PCA dynamically for the 2D visualization projection
    pca = PCA(n_components=2)
    pca.fit(df_scaled)

    # Score each team and build outputs
    team_identities = {}
    clusters = []
    for idx, row in df.iterrows():
        team_name = row["team_name"]
        raw_feats = row.to_dict() # Pass full row dictionary to include count_games
        score_res = scorer.score_team(team_name, raw_feats, mean=mean, scale=scale)
        team_identities[team_name] = score_res
        clusters.append(score_res["primary_cluster_id"])

    image_path = output_dir / f"tactical_clusters_{league}_{season}.png"
    title = f"Tactical Identity Groupings ({league.upper()} {season})"
    
    # Save visualization scatter plot
    plot_clusters(df_scaled, clusters, df["team_name"], output_path=image_path, title=title)

    teams_path = output_dir / f"teams_{league}_{season}.json"
    write_json(teams_path, team_identities)

    metadata_path = output_dir / f"metadata_{league}_{season}.json"
    write_json(
        metadata_path,
        {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "league": league,
            "season": season,
            "features": scorer.features,
            "n_clusters": len(scorer.identities),
            "cluster_model": f"GaussianMixture ({scorer.version})",
            "pca_explained_variance_ratio": [float(value) for value in pca.explained_variance_ratio_],
        },
    )

    print(f"Saved {image_path}, {teams_path}, and {metadata_path}")


def generate_players(league: str, season: str, output_dir: Path):
    from src.clustering import cluster_teams
    from src.player_loader import load_player_data
    from src.player_preprocessor import PLAYER_FEATURES, preprocess_player_data
    from src.player_archetype import build_player_profiles

    print(f"  Generating player archetypes for {league.upper()} {season}...")
    df = load_player_data(league, season)
    if df.empty:
        print(f"  No player data for {league} {season}")
        return

    df_scaled, player_names, positions = preprocess_player_data(df)
    clusters, model, probs = cluster_teams(df_scaled)

    profiles = build_player_profiles(df_scaled, clusters, probs, player_names, positions)

    players_path = output_dir / f"players_{league}_{season}.json"
    write_json(players_path, profiles)

    player_meta_path = output_dir / f"player_metadata_{league}_{season}.json"
    write_json(
        player_meta_path,
        {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "league": league,
            "season": season,
            "features": PLAYER_FEATURES,
            "n_players": len(profiles),
            "n_archetypes": model.n_components,
            "cluster_model": "GaussianMixture",
        },
    )
    print(f"  Saved {players_path} ({len(profiles)} players, {model.n_components} archetypes)")


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
                generate_players(league, season, output_dir)
            except Exception as exc:
                print(f"Error on {league} {season}: {exc}")


if __name__ == "__main__":
    main()
