import argparse
import os
import pandas as pd
import numpy as np
from src.constants import (
    COL_ACTIVITY,
    COL_AGE_GROUP,
    COL_HEALTH,
    COL_SCENARIO,
    COL_SEX_EN,
    SIM_TO_ACTIVITY_MAPPING,
)


def generate_std_table(sim_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)

    csv_path = os.path.join(sim_dir, "aggregated.csv")

    df = pd.read_csv(csv_path, parse_dates=["starting_time", "end_time"])

    df["mapped_act"] = df["activity"].map(SIM_TO_ACTIVITY_MAPPING)
    df_act = (
        df.dropna(subset=["mapped_act"])
        .groupby(["unique_simulation_id", "mapped_act"])["duration"]
        .sum()
        .reset_index()
    )

    df_act = pd.merge(
        df_act,
        df[["unique_simulation_id", "days_simulated"]].drop_duplicates(),
        on="unique_simulation_id",
        how="left",
    )
    df_act["duration"] /= df_act["days_simulated"]

    df_meta = df[
        ["unique_simulation_id", COL_SCENARIO, COL_AGE_GROUP, COL_SEX_EN, COL_HEALTH]
    ].drop_duplicates()

    df_full = pd.merge(df_meta, df_act, on="unique_simulation_id", how="left")
    df_full = df_full.pivot_table(
        index=[
            "unique_simulation_id",
            COL_SCENARIO,
            COL_AGE_GROUP,
            COL_SEX_EN,
            COL_HEALTH,
        ],
        columns="mapped_act",
        values="duration",
        fill_value=0,
    ).reset_index()

    df_melt = pd.melt(
        df_full,
        id_vars=[
            "unique_simulation_id",
            COL_SCENARIO,
            COL_AGE_GROUP,
            COL_SEX_EN,
            COL_HEALTH,
        ],
        value_vars=[
            c for c in SIM_TO_ACTIVITY_MAPPING.values() if c in df_full.columns
        ],
        var_name=COL_ACTIVITY,
        value_name="duration",
    )

    df_std = (
        df_melt.groupby(
            [COL_SCENARIO, COL_AGE_GROUP, COL_SEX_EN, COL_HEALTH, COL_ACTIVITY]
        )["duration"]
        .std()
        .reset_index()
    )
    df_std = df_std.rename(columns={"duration": "Std"})

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
