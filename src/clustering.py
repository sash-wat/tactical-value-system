from sklearn.cluster import KMeans

def cluster_teams(df_scaled, n_clusters=4):
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(df_scaled)
    return clusters, kmeans
