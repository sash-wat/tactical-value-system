from itscalledsoccer.client import AmericanSoccerAnalysis
import inspect

asa = AmericanSoccerAnalysis()
print("get_team_xgoals signature:")
print(inspect.signature(asa.get_team_xgoals))

# Also see what it returns by default vs with shot_pattern?
df = asa.get_team_xgoals(leagues='mls', season_name='2025')
print("\nColumns:")
print(df.columns)
