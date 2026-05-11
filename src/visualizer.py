import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA

from src.identity import build_team_identities, describe_pca_axes, name_clusters, unique_legend_names

def plot_clusters(df_scaled, clusters, team_names, output_path='tactical_clusters.png', title='Tactical Identity Groupings'):
    pca = PCA(n_components=2)
    xy = pca.fit_transform(df_scaled)

    c1_desc, c2_desc = describe_pca_axes(df_scaled.columns, pca.components_)
    cluster_names, _ = name_clusters(df_scaled, clusters)
    final_names = unique_legend_names(cluster_names)
    named_clusters = [final_names[c] for c in clusters]

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

    return build_team_identities(df_scaled, clusters, team_names)
