import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.mixture import GaussianMixture

# Add project root to path
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.data_loader import load_tactical_data
from src.preprocessor import TACTICAL_FEATURES
from src.identity import FEATURE_MAP, IDENTITY_NAMES, BALANCED_IDENTITY

LEAGUES = ["mls", "uslc", "nwsl", "usl1"]
SEASONS = ["2020", "2021", "2022", "2023"]

def train_taxonomy():
    print("Loading 2020-2023 reference cohort data across all leagues...")
    all_dfs = []
    for league in LEAGUES:
        for season in SEASONS:
            try:
                df = load_tactical_data(league, season)
                if not df.empty:
                    # Keep metadata for tracking
                    df["league"] = league
                    df["season"] = season
                    all_dfs.append(df)
            except Exception as e:
                print(f"Error loading {league} {season}: {e}")
                
    if not all_dfs:
        raise ValueError("No data loaded successfully.")
        
    df_all = pd.concat(all_dfs, ignore_index=True)
    print(f"Total reference cohort size: {len(df_all)} team-seasons.")
    
    # 1. Standard Scaling (Pooled)
    df_features = df_all[TACTICAL_FEATURES].apply(pd.to_numeric, errors='coerce')
    df_features = df_features.fillna(df_features.mean())
    
    scaler = StandardScaler()
    scaled_values = scaler.fit_transform(df_features)
    df_scaled = pd.DataFrame(scaled_values, columns=TACTICAL_FEATURES)
    
    # 2. Fit Gaussian Mixture Model
    # We lock 6 clusters for the taxonomy size (5-7 requested)
    n_clusters = 6
    print(f"Fitting Gaussian Mixture Model with {n_clusters} components...")
    gmm = GaussianMixture(n_components=n_clusters, random_state=42, n_init=10)
    gmm.fit(scaled_values)
    
    clusters = gmm.predict(scaled_values)
    probs = gmm.predict_proba(scaled_values)
    
    # Add cluster assignments to data
    df_all["cluster"] = clusters
    for i in range(n_clusters):
        df_all[f"prob_{i}"] = probs[:, i]
        
    # 3. Calculate Centroids
    df_scaled["cluster"] = clusters
    centroids = df_scaled.groupby("cluster").mean()
    
    # 4. Name the clusters based on centroid feature deviations
    cluster_names = {}
    used_names = set()
    
    for cluster_id in range(n_clusters):
        c_stats = centroids.loc[cluster_id]
        ranked_features = c_stats.sort_values(ascending=False).index
        
        assigned = BALANCED_IDENTITY
        for feature in ranked_features:
            if c_stats[feature] <= 0.3:  # Lower threshold slightly for clear separation in GMM
                break
            candidate = IDENTITY_NAMES.get(feature, "The Enigmas")
            if candidate not in used_names:
                assigned = candidate
                break
                
        # Resolve duplicates if any
        if assigned != BALANCED_IDENTITY and assigned in used_names:
            assigned = f"Balanced System {cluster_id}"
            
        used_names.add(assigned)
        cluster_names[cluster_id] = assigned
        print(f"Cluster {cluster_id} assigned identity: '{assigned}'")
        print("  Top features:")
        for feat in ranked_features[:3]:
            print(f"    - {feat}: {c_stats[feat]:.3f}")
            
    # 5. Calibrate the hybrid threshold theta using distance-based similarity
    # similarity = 1 / (1 + distance_to_centroid)
    # margin = (sim_1 - sim_2) / sim_1
    margins = []
    
    # centroids as an array of shape (n_clusters, n_features)
    centroid_matrix = centroids.loc[range(n_clusters)].values
    
    for row in scaled_values:
        # Compute Euclidean distance to all centroids
        distances = np.linalg.norm(centroid_matrix - row, axis=1)
        similarities = 1.0 / (1.0 + distances)
        
        sorted_s = sorted(similarities, reverse=True)
        s1, s2 = sorted_s[0], sorted_s[1]
        
        margin = (s1 - s2) / (s1 + 1e-9)
        margins.append(margin)
        
    # Set threshold to 15th percentile of margins
    hybrid_threshold = float(np.percentile(margins, 15))
    print(f"Calibrated hybrid threshold (15th percentile of distance-based relative margins): {hybrid_threshold:.4f}")
    
    # 6. Save parameters to src/models/phase1_taxonomy_v1.json
    model_dir = REPO_ROOT / "src" / "models"
    model_dir.mkdir(parents=True, exist_ok=True)
    
    model_data = {
      "version": "phase1_taxonomy_v1",
      "trained_at": pd.Timestamp.now().isoformat(),
      "features": TACTICAL_FEATURES,
      "scaler": {
        "mean": scaler.mean_.tolist(),
        "scale": scaler.scale_.tolist()
      },
      "identities": {
        str(cid): {
          "name": name,
          "centroid": centroids.loc[cid].tolist()
        } for cid, name in cluster_names.items()
      },
      "hyperparameters": {
        "hybrid_threshold": hybrid_threshold
      }
    }
    
    output_path = model_dir / "phase1_taxonomy_v1.json"
    with open(output_path, "w") as f:
        json.dump(model_data, f, indent=2)
    print(f"Successfully saved model parameters to {output_path}")

if __name__ == "__main__":
    train_taxonomy()
