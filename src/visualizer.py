import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
import numpy as np

def plot_clusters(df_scaled, clusters, team_names, output_path='tactical_clusters.png'):
    pca = PCA(n_components=2)
    xy = pca.fit_transform(df_scaled)
    
    # Analyze PCA components to generate descriptive axis names
    features = df_scaled.columns
    def get_axis_desc(weights):
        pos_idx = np.argmax(weights)
        neg_idx = np.argmin(weights)
        pos_trait = features[pos_idx].replace('_', ' ').title()
        neg_trait = features[neg_idx].replace('_', ' ').title()
        
        if weights[neg_idx] < 0:
            return f"← More {neg_trait}  |  More {pos_trait} →"
        return f"More {pos_trait} →"
        
    c1_desc = get_axis_desc(pca.components_[0])
    c2_desc = get_axis_desc(pca.components_[1])

    cluster_names = {}
    df_temp = df_scaled.copy()
    df_temp['cluster'] = clusters
    centroids = df_temp.groupby('cluster').mean()
    
    for c in centroids.index:
        dominant_trait = centroids.loc[c].idxmax()
        if dominant_trait == 'creation_volume':
            name = "High-Volume Creators"
        elif dominant_trait == 'low_block_strength':
            name = "Low-Block"
        elif dominant_trait == 'set_piece_reliance':
            name = "Set-Piece Specialists"
        elif dominant_trait == 'disruption':
            name = "High-Press / Disruptors"
        else:
            name = f"Cluster {c}"
            
        if list(cluster_names.values()).count(name) > 0:
            name = f"{name} II"
        cluster_names[c] = name

    named_clusters = [cluster_names[c] for c in clusters]

    plt.figure(figsize=(14, 10))
    plt.style.use('dark_background')
    
    sns.scatterplot(x=xy[:, 0], y=xy[:, 1], hue=named_clusters, palette='Set2', s=150, alpha=0.9, edgecolor='w')
    
    for i, name in enumerate(team_names):
        plt.annotate(name, (xy[i, 0] + 0.05, xy[i, 1] + 0.05), fontsize=9, alpha=0.8)
        
    plt.title('Tactical Identity Groupings (MLS 2025)', fontsize=16, pad=20)
    plt.xlabel(c1_desc, fontsize=12, fontweight='bold', color='#cbd5e1')
    plt.ylabel(c2_desc, fontsize=12, fontweight='bold', color='#cbd5e1')
    plt.legend(title='Tactical Identity', loc='center left', bbox_to_anchor=(1, 0.5))
    plt.grid(True, linestyle='--', alpha=0.2)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='#0B0F19')
    print(f"Saved cluster visualization to {output_path}")
