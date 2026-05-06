from itscalledsoccer.client import AmericanSoccerAnalysis
import pandas as pd
asa = AmericanSoccerAnalysis()

df_all = asa.get_team_xgoals(leagues='mls', season_name='2025')
df_sp = asa.get_team_xgoals(leagues='mls', season_name='2025', shot_pattern='Set piece')

print("All xG for first team:", df_all.iloc[0]['xgoals_for'])
print("Set Piece xG for first team:", df_sp.iloc[0]['xgoals_for'])
