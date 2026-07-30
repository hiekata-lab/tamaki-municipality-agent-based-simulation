import os
from typing import List
import pandas as pd
from src.constants import (
    COL_AGE_GROUP,
    COL_AGENT_UUID,
    COL_DAYS_SIMULATED,
    COL_DIST,
    COL_DURATION,
    COL_HEALTH,
    COL_ID,
    COL_LOCATION_NAME,
    COL_SCENARIO,
    COL_SEX_EN,
    COL_SIM_ACTIVITY,
    COL_SIMULATION_UUID,
    COL_X,
    COL_Y,
    TRANSPORTATION_MODES,
)
from src.post_simulation.tables.utils.io import (
    load_aggregated_simulation_data,
    save_table_csv,
)


def load_normalized_transport_data(sim_dir: str) -> pd.DataFrame:
    """Loads simulation data, filters transport modes, cross-joins demographic metadata, and normalizes duration, trips, and distance by simulation days."""
    df = load_aggregated_simulation_data(sim_dir)

    df_t = df[df[COL_SIM_ACTIVITY].isin(TRANSPORTATION_MODES)].copy()
    df_t["trips"] = 1

    df_t_agg = (
        df_t.groupby([COL_SIMULATION_UUID, COL_SIM_ACTIVITY])
        .agg(
            duration=(COL_DURATION, "sum"),
            trips=("trips", "sum"),
            dist=(COL_DIST, "sum"),
        )
        .reset_index()
    )

    df_meta = df[
        [
            COL_SIMULATION_UUID,
            COL_AGENT_UUID,
            COL_SCENARIO,
            COL_AGE_GROUP,
            COL_SEX_EN,
            COL_HEALTH,
        ]
    ].drop_duplicates()

    modes_df = pd.DataFrame({COL_SIM_ACTIVITY: TRANSPORTATION_MODES})
    df_full = pd.merge(
        df_meta.merge(modes_df, how="cross"),
        df_t_agg,
        on=[COL_SIMULATION_UUID, COL_SIM_ACTIVITY],
        how="left",
    ).fillna(0)

    df_full = pd.merge(
        df_full,
        df[[COL_SIMULATION_UUID, COL_DAYS_SIMULATED]].drop_duplicates(),
        on=COL_SIMULATION_UUID,
        how="left",
    )

    df_full["total_dist"] = df_full["dist"]
    df_full["duration"] /= df_full["days_simulated"]
    df_full["avg_trips"] = df_full["trips"] / df_full["days_simulated"]
    df_full["dist"] /= df_full["days_simulated"]

    return df_full


def export_grouped_pivot_table(
    df: pd.DataFrame,
    group_cols: List[str],
    val_col: str,
    agg_func: str,
    output_path: str,
    category_col: str = COL_SIM_ACTIVITY,
) -> pd.DataFrame:
    """Groups data by group_cols and category_col, aggregates val_col using agg_func, pivots into wide format, and saves to CSV."""
    df_group = (
        df.groupby(group_cols + [category_col])[val_col]
        .agg(agg_func)
        .reset_index()
    )
    df_pivot = df_group.pivot_table(
        index=group_cols,
        columns=category_col,
        values=val_col,
    ).reset_index()

    save_table_csv(df_pivot, output_path, index=False)
    return df_pivot


def generate_location_legend_table(
    location_series: pd.Series,
    output_path: str,
    graph_json_path: str = "data/processed/locations_graph.json",
) -> pd.DataFrame:
    """Generates a location legend table mapping unique locations to IDs and spatial (X, Y) coordinates."""
    graph_df = pd.read_json(graph_json_path, orient="index")
    loc_x = graph_df[COL_X]
    loc_y = graph_df[COL_Y]

    unique_locs = location_series.drop_duplicates().dropna().reset_index(drop=True)
    legend_df = pd.DataFrame(
        {COL_ID: range(1, len(unique_locs) + 1), COL_LOCATION_NAME: unique_locs}
    )
    legend_df[COL_X] = legend_df[COL_LOCATION_NAME].map(loc_x)
    legend_df[COL_Y] = legend_df[COL_LOCATION_NAME].map(loc_y)

    save_table_csv(legend_df, output_path, index=False)
    return legend_df
