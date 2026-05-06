from itscalledsoccer.client import AmericanSoccerAnalysis
import pandas as pd
asa = AmericanSoccerAnalysis()

df_pass = asa.get_team_xpass(leagues='mls', season_name='2025')
print("Passing columns:")
print(df_pass.columns)
