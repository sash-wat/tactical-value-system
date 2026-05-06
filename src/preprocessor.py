import pandas as pd
from sklearn.preprocessing import StandardScaler

def preprocess_tactical_data(df):
    features = [
        'passing', 'receiving', 'shooting', 'interrupting', 'dribbling', 'claiming',
        'xgoals_for', 'xgoals_against', 'shots_for', 'shots_against',
        'attempted_passes_for', 'pass_completion_percentage_for', 
        'avg_vertical_distance_for', 'pass_completion_percentage_against', 
        'avg_vertical_distance_against'
    ]
    
    # Check if features exist
    missing = [f for f in features if f not in df.columns]
    if missing:
        raise ValueError(f"Missing features: {missing}")
        
    df_scaled = df[features].copy()
    
    # Scale features
    scaler = StandardScaler()
    df_scaled_values = scaler.fit_transform(df_scaled)
    
    return pd.DataFrame(df_scaled_values, columns=features), df['team_name']
