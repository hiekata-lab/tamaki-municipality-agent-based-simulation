import argparse
import os
import pandas as pd
import numpy as np
from src.constants import (
    COL_ACTIVITY,
    COL_AGE_GROUP,
    COL_DAYS_SIMULATED,
    COL_DURATION,
    COL_END_TIME,
    COL_HEALTH,
    COL_SCENARIO,
    COL_SEX_EN,
    COL_SIM_ACTIVITY,
    COL_STARTING_TIME,
    COL_UNIQUE_SIMULATION_ID,
    SIM_ACTIVITY_TO_VAL_ACTIVIY_MAP,
)


def generate_std_table(sim_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)

    csv_path = os.path.join(sim_dir, "aggregated.csv")

    df = pd.read_csv(csv_path, parse_dates=[COL_STARTING_TIME, COL_END_TIME])

    df["mapped_act"] = df[COL_SIM_ACTIVITY].map(SIM_ACTIVITY_TO_VAL_ACTIVIY_MAP)
    df_act = (
        df.dropna(subset=["mapped_act"])
        .groupby([COL_UNIQUE_SIMULATION_ID, "mapped_act"])[COL_DURATION]
        .sum()
        .reset_index()
    )

    df_act = pd.merge(
        df_act,
        df[[COL_UNIQUE_SIMULATION_ID, COL_DAYS_SIMULATED]].drop_duplicates(),
        on=COL_UNIQUE_SIMULATION_ID,
        how="left",
    )
    df_act[COL_DURATION] /= df_act[COL_DAYS_SIMULATED]

    df_meta = df[
        [COL_UNIQUE_SIMULATION_ID, COL_SCENARIO, COL_AGE_GROUP, COL_SEX_EN, COL_HEALTH]
    ].drop_duplicates()

    df_full = pd.merge(df_meta, df_act, on=COL_UNIQUE_SIMULATION_ID, how="left")
    df_full = df_full.pivot_table(
        index=[
            COL_UNIQUE_SIMULATION_ID,
            COL_SCENARIO,
            COL_AGE_GROUP,
            COL_SEX_EN,
            COL_HEALTH,
        ],
        columns="mapped_act",
        values=COL_DURATION,
        fill_value=0,
    ).reset_index()

    df_melt = pd.melt(
        df_full,
        id_vars=[
            COL_UNIQUE_SIMULATION_ID,
            COL_SCENARIO,
            COL_AGE_GROUP,
            COL_SEX_EN,
            COL_HEALTH,
        ],
        value_vars=[
            c for c in SIM_ACTIVITY_TO_VAL_ACTIVIY_MAP.values() if c in df_full.columns
        ],
        var_name=COL_ACTIVITY,
        value_name=COL_DURATION,
    )

    df_std = (
        df_melt.groupby(
            [COL_SCENARIO, COL_AGE_GROUP, COL_SEX_EN, COL_HEALTH, COL_ACTIVITY]
        )[COL_DURATION]
        .std()
        .reset_index()
    )
    df_std = df_std.rename(columns={COL_DURATION: "Std"})

    df_pivot = df_std.pivot_table(
        index=[COL_SCENARIO, COL_AGE_GROUP, COL_SEX_EN, COL_HEALTH],
        columns=COL_ACTIVITY,
        values="Std",
    )

    path = os.path.join(out_dir, "results_activities_std_minutes.csv")
    df_pivot.to_csv(path)
    print(f"  Saved {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate activities daily std minutes table"
    )

    parser.add_argument(
        "--sim-dir", type=str, default=".", help="Path to simulation dir"
    )

    parser.add_argument(
        "--out-dir", type=str, default="tables", help="Output directory for tables"
    )
    args = parser.parse_args()

    generate_std_table(args.sim_dir, args.out_dir)
