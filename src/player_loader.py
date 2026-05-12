from __future__ import annotations

import pandas as pd
from itscalledsoccer.client import AmericanSoccerAnalysis

MIN_MINUTES = 500
_96 = 96  # normalization base


def _expand_gplus(df_gplus: pd.DataFrame) -> pd.DataFrame:
    """Unpack the nested 'data' column from get_player_goals_added into flat columns."""
    rows = []
    for _, row in df_gplus.iterrows():
        record = {
            "player_id": row["player_id"],
            "general_position": row["general_position"],
            "minutes_played": row["minutes_played"],
        }
        for item in row["data"]:
            action = item["action_type"].lower()
            # Use goals_added_above_avg — already position-normalised by ASA
            record[f"g_{action}"] = item["goals_added_above_avg"]
        rows.append(record)
    return pd.DataFrame(rows)


def load_player_data(leagues: str, season: str) -> pd.DataFrame:
    """
    Fetch and merge player g+, xgoals, and xpass data from ASA.
    Returns a flat DataFrame with one row per player, filtered to MIN_MINUTES.
    All volume stats are normalised per 96 minutes.

    Note: ASA returns team_id as a list for players who switched teams mid-season.
    We drop team_id entirely and aggregate everything to one row per player_id.
    """
    asa = AmericanSoccerAnalysis()

    # --- g+ components (above-avg, position-normalised) ---
    df_gplus_raw = asa.get_player_goals_added(leagues=leagues, season_name=season)
    df_gplus = _expand_gplus(df_gplus_raw)

    # --- xGoals (volume stats → per-96 normalised) ---
    df_xg = asa.get_player_xgoals(leagues=leagues, season_name=season)
    df_xg = df_xg[["player_id", "minutes_played", "xgoals", "xassists"]].copy()
    df_xg["xgoals_p96"] = df_xg["xgoals"] / df_xg["minutes_played"] * _96
    df_xg["xassists_p96"] = df_xg["xassists"] / df_xg["minutes_played"] * _96
    df_xg = df_xg.drop(columns=["xgoals", "xassists", "minutes_played"])

    # --- xPass (passing style metrics) ---
    df_xp = asa.get_player_xpass(leagues=leagues, season_name=season)
    df_xp = df_xp[
        [
            "player_id",
            "passes_completed_over_expected_p100",
            "avg_vertical_distance_yds",
            "share_team_touches",
        ]
    ].copy()

    # --- Player names ---
    df_players = asa.get_players()
    name_cols = [c for c in df_players.columns if "name" in c.lower()]
    if not name_cols:
        raise ValueError("Could not find player name column in get_players() response.")
    name_col = name_cols[0]
    df_players = df_players[["player_id", name_col]].rename(
        columns={name_col: "player_name"}
    )

    # --- Aggregate to one row per player (handles multi-team players) ---
    gplus_cols = [c for c in df_gplus.columns if c.startswith("g_")]
    df_gplus_agg = df_gplus.groupby("player_id", as_index=False).agg(
        general_position=("general_position", "first"),
        minutes_played=("minutes_played", "sum"),
        **{col: (col, "mean") for col in gplus_cols},
    )

    df_xg_agg = df_xg.groupby("player_id", as_index=False).agg(
        xgoals_p96=("xgoals_p96", "mean"),
        xassists_p96=("xassists_p96", "mean"),
    )

    df_xp_agg = df_xp.groupby("player_id", as_index=False).agg(
        passes_completed_over_expected_p100=("passes_completed_over_expected_p100", "mean"),
        avg_vertical_distance_yds=("avg_vertical_distance_yds", "mean"),
        share_team_touches=("share_team_touches", "mean"),
    )

    # --- Merge all on player_id (no team_id ambiguity) ---
    df = df_gplus_agg.merge(df_xg_agg, on="player_id", how="left")
    df = df.merge(df_xp_agg, on="player_id", how="left")
    df = df.merge(df_players, on="player_id", how="left")

    # --- Minimum minutes filter ---
    df = df[df["minutes_played"] >= MIN_MINUTES].reset_index(drop=True)

    return df
