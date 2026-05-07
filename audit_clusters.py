from src.data_loader import load_tactical_data
from src.preprocessor import preprocess_tactical_data
from src.clustering import cluster_teams
import pandas as pd
from sklearn.decomposition import PCA
import numpy as np

def audit(year):
    print(f"\n--- AUDIT: MLS {year} ---")
    df = load_tactical_data('mls', year)
    df_scaled, team_names = preprocess_tactical_data(df)
    
    # Matching main.py logic exactly
    df_2d = pd.DataFrame(PCA(n_components=2).fit_transform(df_scaled), columns=['pca1', 'pca2'])
    clusters, model = cluster_teams(df_2d, n_clusters=4)
    
    df_scaled['cluster'] = clusters
    centroids = df_scaled.groupby('cluster').mean()
    
    metrics_to_check = ['avg_vertical_distance_against', 'xgoals_for', 'xgoals_against', 'avg_vertical_distance_for']
    print(centroids[metrics_to_check].to_string())
    
    # Current assignment logic
    remaining = list(centroids.index)
    assignments = {}
    
    # 1. Hounds
    best_h = centroids.loc[remaining, 'avg_vertical_distance_against'].idxmax()
    assignments['High-Press Hounds'] = best_h
    remaining.remove(best_h)
    
    # 2. Open Defenses
    best_o = centroids.loc[remaining, 'xgoals_against'].idxmax()
    assignments['Open Defenses'] = best_o
    remaining.remove(best_o)
    
    # 3. Vertical Threats
    best_v = centroids.loc[remaining, 'avg_vertical_distance_for'].idxmax()
    assignments['Vertical Threats'] = best_v
    remaining.remove(best_v)
    
    # 4. Juggernauts
    assignments['Attacking Juggernauts'] = remaining[0]
    
    print("\nCurrent Assignments:")
    for name, c in assignments.items():
        print(f"{name}: Cluster {c}")

audit('2025')
audit('2026')
