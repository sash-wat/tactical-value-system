from itscalledsoccer.client import AmericanSoccerAnalysis
import pandas as pd

def load_team_xgoals(leagues, season):
    asa = AmericanSoccerAnalysis()
    # Fetch team xgoals which contains g+ components at team level
    df = asa.get_team_xgoals(leagues=leagues, season_name=season)
    teams_df = asa.get_teams(leagues=leagues)
    df = df.merge(teams_df[['team_id', 'team_name']], on='team_id', how='left')
    return df
