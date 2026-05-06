from src.data_loader import load_team_xgoals
from src.preprocessor import preprocess_tactical_data
from src.clustering import cluster_teams
import pandas as pd

from src.visualizer import plot_clusters

def run_phase_1():
    print("Loading MLS 2025 data...")
    try:
        df = load_team_xgoals('mls', '2025')
    except Exception as e:
        print(f"Error loading data: {e}")
        return
    
    print("Preprocessing...")
    df_scaled, team_names = preprocess_tactical_data(df)
    
    print("Clustering teams...")
    clusters, model = cluster_teams(df_scaled, n_clusters=4)
    
    df['cluster'] = clusters
    result = df[['team_name', 'cluster']].sort_values('cluster')
    print("\n--- Tactical Clusters (MLS 2025) ---")
    print(result.to_string(index=False))
    
    print("Generating visualization...")
    plot_clusters(df_scaled, clusters, df['team_name'])
    
    return df

if __name__ == "__main__":
    run_phase_1()
