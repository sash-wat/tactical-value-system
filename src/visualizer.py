import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def plot_clusters(df_scaled, clusters, team_names, output_path='tactical_clusters.png'):
    # Extract the user-requested axes directly instead of using PCA
    xy = df_scaled[['passing_vs_shooting', 'interrupting']].values

    # 2. Dynamically name the clusters based on their dominant g+ trait
    cluster_names = {}
    df_temp = df_scaled.copy()
    df_temp['cluster'] = clusters
    centroids = df_temp.groupby('cluster').mean()
    
    for c in centroids.index:
        dominant_trait = centroids.loc[c].idxmax()
        if dominant_trait in ['passing', 'receiving']:
            name = "The Architects (Possession)"
        elif dominant_trait == 'interrupting':
            name = "The Disruptors (Pressing)"
        elif dominant_trait == 'dribbling':
            name = "Progressive Carriers (Dribbling)"
        elif dominant_trait == 'shooting':
            name = "Direct Punishers (Shooting)"
        else:
            name = f"Cluster {c}"
            
        # Prevent duplicate names
        if list(cluster_names.values()).count(name) > 0:
            name = f"{name} II"
        cluster_names[c] = name

    named_clusters = [cluster_names[c] for c in clusters]

    plt.figure(figsize=(14, 10))
    # Use a visually appealing dark theme for the plot to match the website vibe
    plt.style.use('dark_background')
    
    sns.scatterplot(x=xy[:, 0], y=xy[:, 1], hue=named_clusters, palette='Set2', s=150, alpha=0.9, edgecolor='w')
    
    # Annotate points with team names
    for i, name in enumerate(team_names):
        plt.annotate(name, (xy[i, 0] + 0.05, xy[i, 1] + 0.05), fontsize=9, alpha=0.8)
        
    plt.title('Tactical DNA Clusters (MLS 2025)', fontsize=16, pad=20)
    plt.xlabel('← More Shooting  |  More Passing →', fontsize=12, fontweight='bold', color='#cbd5e1')
    plt.ylabel('More Interrupting →', fontsize=12, fontweight='bold', color='#cbd5e1')
    plt.legend(title='Dominant Tactical Identity', loc='center left', bbox_to_anchor=(1, 0.5))
    plt.grid(True, linestyle='--', alpha=0.2)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='#0B0F19')
    print(f"Saved cluster visualization to {output_path}")
