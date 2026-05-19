import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
import json
from pathlib import Path

from src.identity import describe_pca_axes

def plot_clusters(df_scaled, clusters, team_names, output_path='tactical_clusters.png', title='Tactical Identity Groupings'):
    pca = PCA(n_components=2)
    xy = pca.fit_transform(df_scaled)

    c1_desc, c2_desc = describe_pca_axes(df_scaled.columns, pca.components_)
    
    # Load stable taxonomy names
    repo_root = Path(__file__).resolve().parents[1]
    model_path = repo_root / "src" / "models" / "phase1_taxonomy_v1.json"
    with open(model_path, "r") as f:
        model_data = json.load(f)
    
    id_names = {int(cid): info["name"] for cid, info in model_data["identities"].items()}
    named_clusters = [id_names.get(c, f"Cluster {c}") for c in clusters]

    plt.figure(figsize=(14, 10))
    plt.style.use('dark_background')
    
    sns.scatterplot(x=xy[:, 0], y=xy[:, 1], hue=named_clusters, palette='Set2', s=150, alpha=0.9, edgecolor='w')
    
    for i, name in enumerate(team_names):
        plt.annotate(name, (xy[i, 0] + 0.05, xy[i, 1] + 0.05), fontsize=9, alpha=0.8)
        
    plt.title(title, fontsize=16, pad=20)
    plt.xlabel(c1_desc, fontsize=12, fontweight='bold', color='#cbd5e1')
    plt.ylabel(c2_desc, fontsize=12, fontweight='bold', color='#cbd5e1')
    plt.legend(title='Tactical Identity', loc='center left', bbox_to_anchor=(1, 0.5))
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='#0B0F19')
    else:
        plt.show()
        
    plt.close()
