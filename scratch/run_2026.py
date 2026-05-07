from src.data_loader import load_tactical_data
from src.preprocessor import preprocess_tactical_data
from src.clustering import cluster_teams
from src.visualizer import plot_clusters
import pandas as pd
from sklearn.decomposition import PCA

def run_2026_check():
    print("Loading MLS 2026 data...")
    try:
        df = load_tactical_data('mls', '2026')
    except Exception as e:
        print(f"Error loading data: {e}")
        return
    
    print("Preprocessing...")
    df_scaled, team_names = preprocess_tactical_data(df)
    
    print("Clustering teams...")
    df_2d = pd.DataFrame(PCA(n_components=2).fit_transform(df_scaled), columns=['pca1', 'pca2'])
    clusters, model = cluster_teams(df_2d, n_clusters=4)
    
    print("Generating visualization for 2026...")
    # We will pass the filename as requested
    plot_clusters(df_scaled, clusters, df['team_name'], output_path='2026.png', title='Tactical Identity Groupings (MLS 2026)')
    
    print("Done. Visualization saved to 2026.png")

if __name__ == "__main__":
    run_2026_check()
