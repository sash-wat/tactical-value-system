from src.data_loader import load_tactical_data
from src.preprocessor import preprocess_tactical_data
from src.clustering import cluster_teams
import pandas as pd
from sklearn.decomposition import PCA
import numpy as np

def debug_2026():
    df = load_tactical_data('mls', '2026')
    df_scaled, team_names = preprocess_tactical_data(df)
    df_2d = pd.DataFrame(PCA(n_components=2).fit_transform(df_scaled), columns=['pca1', 'pca2'])
    clusters, model = cluster_teams(df_2d, n_clusters=4)
    
    df['cluster'] = clusters
    df_scaled['cluster'] = clusters
    centroids = df_scaled.groupby('cluster').mean()
    
    # Matching the visualizer's assignment logic exactly
    remaining = list(centroids.index)
    assignments = {}
    
    # Priority List from visualizer.py
    priority = [
        {'name': 'Attacking Juggernauts', 'metric': 'xgoals_for'},
        {'name': 'Vertical Threats', 'metric': 'avg_vertical_distance_for'},
        {'name': 'Open Defenses', 'metric': 'xgoals_against'},
        {'name': 'High-Press Hounds', 'metric': 'avg_vertical_distance_against'}
    ]
    
    for p in priority:
        if not remaining: break
        best_c = centroids.loc[remaining, p['metric']].idxmax()
        assignments[best_c] = p['name']
        remaining.remove(best_c)
        
    for c in remaining:
        assignments[c] = f"Hybrid {c}"
        
    df['assigned_name'] = df['cluster'].map(assignments)
    
    print("--- 2026 Assignments Debug ---")
    for c in sorted(assignments.keys()):
        print(f"Cluster {c} ({assignments[c]}) Stats:")
        print(centroids.loc[c, ['xgoals_for', 'avg_vertical_distance_against', 'xgoals_against', 'avg_vertical_distance_for']])
        teams = df[df['cluster'] == c]['team_name'].tolist()
        print(f"Teams: {teams}\n")

debug_2026()
