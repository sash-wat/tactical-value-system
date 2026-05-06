from src.data_loader import load_team_xgoals
from src.preprocessor import preprocess_tactical_data
from src.clustering import cluster_teams
import pandas as pd

def run_phase_1():
    print("Loading USLC 2023 data...")
    try:
        df = load_team_xgoals('uslc', '2023')
    except Exception as e:
        print(f"Error loading data: {e}")
        return
    
    print("Preprocessing...")
    df_scaled, team_names = preprocess_tactical_data(df)
    
    print("Clustering teams...")
    clusters, model = cluster_teams(df_scaled, n_clusters=4)
    
    df['cluster'] = clusters
    result = df[['team_name', 'cluster']].sort_values('cluster')
    print("\n--- Tactical Clusters (USLC 2023) ---")
    print(result.to_string(index=False))
    return df

if __name__ == "__main__":
    run_phase_1()
