from itscalledsoccer.client import AmericanSoccerAnalysis
import pandas as pd

REQUIRED_XGOALS_COLUMNS = ['team_id', 'xgoals_for', 'xgoals_against', 'shots_for', 'shots_against']
REQUIRED_XPASS_COLUMNS = [
    'team_id',
    'attempted_passes_for',
    'pass_completion_percentage_for',
    'avg_vertical_distance_for',
    'pass_completion_percentage_against',
    'avg_vertical_distance_against',
]

def _require_columns(df, columns, source):
    missing = [column for column in columns if column not in df.columns]
    if missing:
        raise ValueError(f"{source} response missing columns: {missing}")

def load_tactical_data(leagues, season):
    asa = AmericanSoccerAnalysis()
    
    # 1. Fetch g+ data
    df_gplus = asa.get_team_goals_added(leagues=leagues, season_name=season)
    _require_columns(df_gplus, ['team_id', 'data'], 'goals_added')
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
    _require_columns(df_xg, REQUIRED_XGOALS_COLUMNS, 'xgoals')
    df = df.merge(df_xg[REQUIRED_XGOALS_COLUMNS], on='team_id', how='left')
    
    # 3. Fetch xpass data
    df_pass = asa.get_team_xpass(leagues=leagues, season_name=season)
    _require_columns(df_pass, REQUIRED_XPASS_COLUMNS, 'xpass')
    df = df.merge(df_pass[REQUIRED_XPASS_COLUMNS], on='team_id', how='left')
    
    # 4. Merge team names
    teams_df = asa.get_teams(leagues=leagues)
    _require_columns(teams_df, ['team_id', 'team_name'], 'teams')
    df = df.merge(teams_df[['team_id', 'team_name']], on='team_id', how='left')
    
    return df
