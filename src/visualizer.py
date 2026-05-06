import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA

def plot_clusters(df_scaled, clusters, team_names, output_path='tactical_clusters.png'):
    # Reduce the 5 g+ features to 2 dimensions for visualization
    pca = PCA(n_components=2)
    xy = pca.fit_transform(df_scaled)
    
    plt.figure(figsize=(14, 10))
    # Use a visually appealing dark theme for the plot to match the website vibe
    plt.style.use('dark_background')
    
    sns.scatterplot(x=xy[:, 0], y=xy[:, 1], hue=clusters, palette='Set1', s=150, alpha=0.8, edgecolor='w')
    
    # Annotate points with team names
    for i, name in enumerate(team_names):
        plt.annotate(name, (xy[i, 0] + 0.05, xy[i, 1] + 0.05), fontsize=9, alpha=0.8)
        
    plt.title('Tactical DNA Clusters (USLC 2023)', fontsize=16, pad=20)
    plt.xlabel(f'PCA Component 1 ({pca.explained_variance_ratio_[0]:.1%} variance)', fontsize=12)
    plt.ylabel(f'PCA Component 2 ({pca.explained_variance_ratio_[1]:.1%} variance)', fontsize=12)
    plt.legend(title='Tactical Cluster', loc='best')
    plt.grid(True, linestyle='--', alpha=0.2)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='#0B0F19')
    print(f"Saved cluster visualization to {output_path}")
