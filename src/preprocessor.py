import pandas as pd
from sklearn.preprocessing import StandardScaler

TACTICAL_FEATURES = [
    'passing', 'receiving', 'interrupting', 'dribbling', 'claiming',
    'attempted_passes_for', 'pass_completion_percentage_for',
    'avg_vertical_distance_for', 'avg_vertical_distance_against'
]

def preprocess_tactical_data(df):
    missing = [f for f in TACTICAL_FEATURES if f not in df.columns]
    if missing:
        raise ValueError(f"Missing features: {missing}")
    if 'team_name' not in df.columns:
        raise ValueError("Missing team_name column")
        
    df_features = df[TACTICAL_FEATURES].apply(pd.to_numeric, errors='coerce')
    if df_features.isna().all(axis=None):
        raise ValueError("No numeric tactical feature values found")

    df_features = df_features.fillna(df_features.mean())
    if df_features.isna().any(axis=None):
        empty_columns = df_features.columns[df_features.isna().any()].tolist()
        raise ValueError(f"Unable to impute empty feature columns: {empty_columns}")
    
    scaler = StandardScaler()
    df_scaled_values = scaler.fit_transform(df_features)
    
    return pd.DataFrame(df_scaled_values, columns=TACTICAL_FEATURES), df['team_name']
