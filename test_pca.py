import pandas as pd
from src.data_loader import load_tactical_data
from src.preprocessor import preprocess_tactical_data
from sklearn.decomposition import PCA
import numpy as np

df = load_tactical_data('mls', '2025')
df_scaled, team_names = preprocess_tactical_data(df)
pca = PCA(n_components=2)
pca.fit(df_scaled)

features = df_scaled.columns
print("PCA 1 Top Pos:", features[np.argmax(pca.components_[0])])
print("PCA 1 Top Neg:", features[np.argmin(pca.components_[0])])
print("PCA 2 Top Pos:", features[np.argmax(pca.components_[1])])
print("PCA 2 Top Neg:", features[np.argmin(pca.components_[1])])
