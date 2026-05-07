import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
import numpy as np

def plot_clusters(df_scaled, clusters, team_names, output_path='tactical_clusters.png', title='Tactical Identity Groupings'):
    pca = PCA(n_components=2)
    xy = pca.fit_transform(df_scaled)
    
    # Translate raw metric names into explainable tactical concepts
    FEATURE_MAP = {
        'passing': 'Passing Impact',
        'receiving': 'Receiving Impact',
        'shooting': 'Shooting Impact',
        'interrupting': 'Defensive Disruption',
        'dribbling': 'Dribbling Impact',
        'claiming': 'Claiming Impact',
        'xgoals_for': 'Attacking Threat (xG)',
        'xgoals_against': 'Defensive Vulnerability (xGA)',
        'shots_for': 'Shot Volume',
        'shots_against': 'Shots Conceded',
        'attempted_passes_for': 'Possession Volume',
        'pass_completion_percentage_for': 'Possession Quality',
        'avg_vertical_distance_for': 'Attacking Directness',
        'pass_completion_percentage_against': 'Opponent Pass Completion',
        'avg_vertical_distance_against': 'Opponent Directness'
    }

    # Chippy, sharp names for clusters based on their dominant defining trait
    CHIPPY_NAMES = {
        'passing': 'The Metronomes',
        'receiving': 'Box Infiltrators',
        'shooting': 'The Gunslingers',
        'interrupting': 'The Disruptors',
        'dribbling': 'Progressive Carriers',
        'claiming': 'Air Superiority',
        'xgoals_for': 'Attacking Juggernauts',
        'xgoals_against': 'Open Defenses',
        'shots_for': 'Volume Shooters',
        'shots_against': 'Siege Defenders',
        'attempted_passes_for': 'The Architects',
        'pass_completion_percentage_for': 'Tiki-Taka Purists',
        'avg_vertical_distance_for': 'Vertical Threats',
        'pass_completion_percentage_against': 'Passive Observers',
        'avg_vertical_distance_against': 'High-Press Hounds'
    }

    # Analyze PCA components to generate single descriptive axis names
    features = df_scaled.columns
    def get_axis_descs(comp1, comp2):
        # Find the absolute strongest driver for each axis
        idx1 = np.argmax(np.abs(comp1))
        
        # Prevent duplicate drivers
        sorted_idx2 = np.argsort(np.abs(comp2))[::-1]
        idx2 = sorted_idx2[0] if sorted_idx2[0] != idx1 else sorted_idx2[1]
        
        t1 = FEATURE_MAP.get(features[idx1], features[idx1])
        t2 = FEATURE_MAP.get(features[idx2], features[idx2])
        
        return f"Primary Driver: {t1}", f"Primary Driver: {t2}"
        
    c1_desc, c2_desc = get_axis_descs(pca.components_[0], pca.components_[1])

    # Tactical Anchors for Identification
    ANCHORS = {
        'avg_vertical_distance_against': 'High-Press Hounds',
        'xgoals_against': 'Open Defenses',
        'avg_vertical_distance_for': 'Vertical Threats',
        'xgoals_for': 'Attacking Juggernauts'
    }

    cluster_names = {}
    df_temp = df_scaled.copy()
    df_temp['cluster'] = clusters
    centroids = df_temp.groupby('cluster').mean()
    
    # Threshold-based identification: Only assign names to tactical outliers
    for c in centroids.index:
        c_stats = centroids.loc[c, list(ANCHORS.keys())]
        best_trait = c_stats.idxmax()
        peak_value = c_stats.max()
        
        # If the peak trait is at least 0.5 standard deviations above the mean, assign identity
        if peak_value > 0.5:
            cluster_names[c] = ANCHORS[best_trait]
        else:
            cluster_names[c] = 'Balanced Systems'
    
    # Ensure unique names in legend if multiple clusters hit the same anchor
    final_names = {}
    name_counts = {}
    for c, name in cluster_names.items():
        if name not in name_counts:
            name_counts[name] = 0
            final_names[c] = name
        else:
            name_counts[name] += 1
            final_names[c] = f"{name} ({name_counts[name] + 1})"

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
    plt.grid(True, linestyle='--', alpha=0.2)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='#0B0F19')
    print(f"Saved cluster visualization to {output_path}")
