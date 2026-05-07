from src.data_loader import load_tactical_data
import pandas as pd

df = load_tactical_data('mls', '2026')
miami = df[df['team_name'].str.contains('Miami', na=False)]
print("--- Inter Miami 2026 Raw Stats ---")
print(miami[['team_name', 'xgoals_for', 'shooting', 'receiving']].to_string())

# Also check who the top xG teams are
print("\n--- Top 5 xG Teams 2026 ---")
print(df[['team_name', 'xgoals_for']].sort_values('xgoals_for', ascending=False).head(5).to_string())
