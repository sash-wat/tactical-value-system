from src.data_loader import load_tactical_data
from src.preprocessor import preprocess_tactical_data
from src.clustering import cluster_teams
from src.visualizer import plot_clusters
import pandas as pd
from sklearn.decomposition import PCA
import os
import json

os.makedirs('assets', exist_ok=True)

leagues = ['mls', 'uslc', 'nwsl', 'usl1']
seasons = ['2020', '2021', '2022', '2023', '2024', '2025', '2026']

for l in leagues:
    for s in seasons:
        print(f"Generating {l.upper()} {s}...")
        try:
            df = load_tactical_data(l, s)
            if df.empty:
                print(f"No data for {l} {s}")
                continue
                
            df_scaled, team_names = preprocess_tactical_data(df)
            df_2d = pd.DataFrame(PCA(n_components=2).fit_transform(df_scaled), columns=['pca1', 'pca2'])
            clusters, model = cluster_teams(df_2d, n_clusters=4)
            
            path = f"assets/tactical_clusters_{l}_{s}.png"
            title = f"Tactical Identity Groupings ({l.upper()} {s})"
            team_identities = plot_clusters(df_scaled, clusters, df['team_name'], output_path=path, title=title)
            
            json_path = f"assets/teams_{l}_{s}.json"
            with open(json_path, 'w') as f:
                json.dump(team_identities, f)
                
            print(f"Saved {path} and {json_path}")
        except Exception as e:
            print(f"Error on {l} {s}: {e}")
