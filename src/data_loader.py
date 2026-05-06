from itscalledsoccer.client import AmericanSoccerAnalysis
import pandas as pd

def load_team_xgoals(leagues, season):
    asa = AmericanSoccerAnalysis()
    # Fetch team goals added which contains g+ components at team level
    df_gplus = asa.get_team_goals_added(leagues=leagues, season_name=season)
    
    rows = []
    for idx, row in df_gplus.iterrows():
        team_id = row['team_id']
        team_data = {'team_id': team_id}
        for item in row['data']:
            action = item['action_type'].lower()
            team_data[action] = item['goals_added_for']
        rows.append(team_data)
        
    df = pd.DataFrame(rows)
    teams_df = asa.get_teams(leagues=leagues)
    df = df.merge(teams_df[['team_id', 'team_name']], on='team_id', how='left')
    return df
