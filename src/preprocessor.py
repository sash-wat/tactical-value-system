import pandas as pd
from sklearn.preprocessing import StandardScaler

def preprocess_tactical_data(df):
    # Calculate the 4 tactical identity metrics requested by the user
    df['creation_volume'] = df['xgoals_for'] + df['receiving']
    df['low_block_strength'] = df['xgoals_against'] / df['shots_against']
    df['set_piece_reliance'] = df['xgoals_set_piece']
    df['disruption'] = df['interrupting']
    
    features = ['creation_volume', 'low_block_strength', 'set_piece_reliance', 'disruption']
        
    df_scaled = df[features].copy()
    
    # Scale features
    scaler = StandardScaler()
    df_scaled_values = scaler.fit_transform(df_scaled)
    
    return pd.DataFrame(df_scaled_values, columns=features), df['team_name']
