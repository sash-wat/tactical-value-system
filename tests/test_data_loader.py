import pandas as pd
from src.data_loader import load_team_xgoals

def test_load_team_xgoals():
    df = load_team_xgoals(leagues='uslc', season='2023')
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert 'team_name' in df.columns
