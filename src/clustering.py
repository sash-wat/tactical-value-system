from sklearn.mixture import GaussianMixture
import numpy as np

def cluster_teams(df_scaled, n_clusters=None):
    if n_clusters is None:
        bics = []
        n_range = range(3, 9)  # minimum 3 archetypes — 2 is never useful UX
        for n in n_range:
            gmm = GaussianMixture(n_components=n, random_state=42, n_init=10)
            gmm.fit(df_scaled)
            bics.append(gmm.bic(df_scaled))
        n_clusters = n_range[np.argmin(bics)]
        print(f"Optimal cluster count (BIC): {n_clusters}")

    gmm = GaussianMixture(n_components=n_clusters, random_state=42, n_init=10)
    gmm.fit(df_scaled)
    clusters = gmm.predict(df_scaled)
    probs = gmm.predict_proba(df_scaled)
    return clusters, gmm, probs
