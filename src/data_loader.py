from itscalledsoccer.client import AmericanSoccerAnalysis
import pandas as pd

def load_tactical_data(leagues, season):
    asa = AmericanSoccerAnalysis()
    
    # 1. Fetch g+ data
    df_gplus = asa.get_team_goals_added(leagues=leagues, season_name=season)
    rows = []
    for idx, row in df_gplus.iterrows():
        team_data = {'team_id': row['team_id']}
        for item in row['data']:
            action = item['action_type'].lower()
            team_data[action] = item['goals_added_for']
        rows.append(team_data)
    df = pd.DataFrame(rows)
    
    # 2. Fetch base xgoals
    df_xg = asa.get_team_xgoals(leagues=leagues, season_name=season)
    df = df.merge(df_xg[['team_id', 'xgoals_for', 'xgoals_against', 'shots_for', 'shots_against']], on='team_id', how='left')
    
    # 3. Fetch xpass data
    df_pass = asa.get_team_xpass(leagues=leagues, season_name=season)
    pass_cols = ['team_id', 'attempted_passes_for', 'pass_completion_percentage_for', 
                 'avg_vertical_distance_for', 'pass_completion_percentage_against', 
                 'avg_vertical_distance_against']
    df = df.merge(df_pass[pass_cols], on='team_id', how='left')
    
    # 4. Merge team names
    teams_df = asa.get_teams(leagues=leagues)
    df = df.merge(teams_df[['team_id', 'team_name']], on='team_id', how='left')
    
    return df
