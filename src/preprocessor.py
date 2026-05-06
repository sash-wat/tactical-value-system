import pandas as pd
from sklearn.preprocessing import StandardScaler

def preprocess_tactical_data(df):
    # Select tactical features (g+ components)
    features = ['passing', 'dribbling', 'interrupting', 'receiving', 'shooting']
    
    # Check if features exist
    if not all(f in df.columns for f in features):
        raise ValueError(f"DataFrame must contain all g+ features: {features}")
        
    df_scaled = df[features].copy()
    
    # Scale features
    scaler = StandardScaler()
    df_scaled_values = scaler.fit_transform(df_scaled)
    
    return pd.DataFrame(df_scaled_values, columns=features), df['team_name']
