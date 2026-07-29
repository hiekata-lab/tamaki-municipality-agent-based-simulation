import argparse
import os
import pandas as pd
import numpy as np
from src.constants import (
    COL_AGE_GROUP,
    COL_DAYS_SIMULATED,
    COL_DURATION,
    COL_END_TIME,
    COL_HEALTH,
    COL_LOCATION,
    COL_NEXT_LOC,
    COL_SCENARIO,
    COL_SEX_EN,
    COL_SIM_ACTIVITY,
    COL_STARTING_TIME,
    COL_UNIQUE_SIMULATION_ID,
    COL_X,
    COL_Y,
    TRANSPORTATION_MODES,
)


def generate_transport_tables(sim_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)

    csv_path = os.path.join(sim_dir, "aggregated.csv")
    df = pd.read_csv(csv_path, parse_dates=[COL_STARTING_TIME, COL_END_TIME])

    # Load Location Graph
    graph_df = pd.read_json("data/processed/locations_graph.json", orient="index")
    loc_x = graph_df[COL_X]
    loc_y = graph_df[COL_Y]

    # Filter for Transport
    df_t = df[df[COL_SIM_ACTIVITY].isin(TRANSPORTATION_MODES)].copy()

    # Vectorized Distance Calculation
    df_t["x1"] = df_t[COL_LOCATION].map(loc_x)
    df_t["y1"] = df_t[COL_LOCATION].map(loc_y)
    df_t["x2"] = df_t[COL_NEXT_LOC].map(loc_x)
    df_t["y2"] = df_t[COL_NEXT_LOC].map(loc_y)
    df_t["dist"] = np.sqrt(
        (df_t["x1"] - df_t["x2"]) ** 2 + (df_t["y1"] - df_t["y2"]) ** 2
    )
    df_t["trips"] = 1

    # Aggregate by sim ID and transport mode
    df_t_agg = (
        df_t.groupby([COL_UNIQUE_SIMULATION_ID, COL_SIM_ACTIVITY])
        .agg(duration=(COL_DURATION, "sum"), trips=("trips", "sum"), dist=("dist", "sum"))
        .reset_index()
    )

    # Load Metadata
    df_meta = df[
        [COL_UNIQUE_SIMULATION_ID, COL_SCENARIO, COL_AGE_GROUP, COL_SEX_EN, COL_HEALTH]
    ].drop_duplicates()

    # Cross demographics with all transport modes
    df_meta_cross = (
        df_meta.assign(key=1)
        .merge(pd.DataFrame({COL_SIM_ACTIVITY: TRANSPORTATION_MODES, "key": 1}), on="key")
        .drop("key", axis=1)
    )
    df_full = pd.merge(
        df_meta_cross, df_t_agg, on=[COL_UNIQUE_SIMULATION_ID, COL_SIM_ACTIVITY], how="left"
    ).fillna(0)
    df_full = pd.merge(
        df_full,
        df[[COL_UNIQUE_SIMULATION_ID, COL_DAYS_SIMULATED]].drop_duplicates(),
        on=COL_UNIQUE_SIMULATION_ID,
        how="left",
    )

    # Save total distance before normalizing
    df_full["total_dist"] = df_full["dist"]

    # Normalize metrics by simulation days
    df_full["duration"] /= df_full["days_simulated"]
    df_full["avg_trips"] = df_full["trips"] / df_full["days_simulated"]
    df_full["dist"] /= df_full["days_simulated"]

    # Pivot DataFrames
    def pivot_and_save(val_col, agg_func, out_filename):
        df_group = (
            df_full.groupby(
                [COL_SCENARIO, COL_AGE_GROUP, COL_SEX_EN, COL_HEALTH] + ["activity"]
            )[val_col]
            .agg(agg_func)
            .reset_index()
        )
        df_pivot = df_group.pivot_table(
            index=[COL_SCENARIO, COL_AGE_GROUP, COL_SEX_EN, COL_HEALTH],
            columns="activity",
            values=val_col,
        ).reset_index()
        path = os.path.join(out_dir, out_filename)
        df_pivot.to_csv(path, index=False)
        print(f"  Saved {path}")

    pivot_and_save("trips", "sum", "results_transport_mode_trips_total_count.csv")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate transport mode trips total count table"
    )

    parser.add_argument(
        "--sim-dir", type=str, default=".", help="Path to simulation dir"
    )

    parser.add_argument(
        "--out-dir", type=str, default="tables", help="Output directory for tables"
    )
    args = parser.parse_args()

    generate_transport_tables(args.sim_dir, args.out_dir)
