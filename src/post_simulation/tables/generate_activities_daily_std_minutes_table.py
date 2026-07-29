import argparse
import os
import pandas as pd
import numpy as np
from src.constants import (
    COL_ACTIVITY,
    COL_AGE_GROUP,
    COL_AGENT_UUID,
    COL_DAYS_SIMULATED,
    COL_DURATION,
    COL_END_TIME,
    COL_HEALTH,
    COL_NORMALIZED_DURATION,
    COL_SCENARIO,
    COL_SEX_EN,
    COL_SIM_ACTIVITY,
    COL_SIMULATION_UUID,
    COL_STARTING_TIME,
    VALIDATION_ACTIVITIES,
)


def generate_std_table(sim_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)

    csv_path = os.path.join(sim_dir, "aggregated.csv")

    df = pd.read_csv(csv_path, parse_dates=[COL_STARTING_TIME, COL_END_TIME])

    df_act = (
        df.dropna(subset=[COL_SIM_ACTIVITY])
        .groupby([COL_SIMULATION_UUID, COL_DAYS_SIMULATED, COL_SIM_ACTIVITY])[
            COL_DURATION
        ]
        .sum()
        .reset_index()
    )
    df_act[COL_NORMALIZED_DURATION] = (
        df_act[COL_DURATION] / df_act[COL_DAYS_SIMULATED]
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

    activities_df = pd.DataFrame({COL_SIM_ACTIVITY: VALIDATION_ACTIVITIES})
    df_full = pd.merge(
        df_meta.merge(activities_df, how="cross"),
        df_act,
        on=[COL_SIMULATION_UUID, COL_SIM_ACTIVITY],
        how="left",
    ).fillna({COL_NORMALIZED_DURATION: 0})

    df_std = (
        df_full.groupby(
            [COL_SCENARIO, COL_AGE_GROUP, COL_SEX_EN, COL_HEALTH, COL_SIM_ACTIVITY]
        )[COL_NORMALIZED_DURATION]
        .std()
        .reset_index()
        .rename(columns={COL_SIM_ACTIVITY: COL_ACTIVITY, COL_NORMALIZED_DURATION: "Std"})
    )

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
