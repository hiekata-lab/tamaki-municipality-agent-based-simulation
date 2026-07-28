import os
import pandas as pd
import numpy as np
from src.constants import (
    COL_ACTIVITY,
    COL_AGE,
    COL_HEALTH,
    COL_SCENARIO,
    COL_SEX,
    SIM_TO_ACTIVITY_MAPPING,
)
from src.tools import (
    load_and_preprocess_simulation_data,
    load_simulation_metadata,
    get_sim_and_out_parser,
)

def generate_std_table(sim_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)

    df = load_and_preprocess_simulation_data(sim_dir)

    df["mapped_act"] = df["activity"].map(SIM_TO_ACTIVITY_MAPPING)
    df_act = (
        df.dropna(subset=["mapped_act"])
        .groupby(["unique_simulation_id", "mapped_act"])["duration"]
        .sum()
        .reset_index()
    )

    df_act = pd.merge(df_act, df[["unique_simulation_id", "days_simulated"]].drop_duplicates(), on="unique_simulation_id", how="left")
    df_act["duration"] /= df_act["days_simulated"]

    df_meta = load_simulation_metadata(sim_dir)

    df_full = pd.merge(df_meta, df_act, on="unique_simulation_id", how="left")
    df_full = df_full.pivot_table(
        index=["unique_simulation_id", COL_SCENARIO, COL_AGE, COL_SEX, COL_HEALTH],
        columns="mapped_act",
        values="duration",
        fill_value=0,
    ).reset_index()

    df_melt = pd.melt(
        df_full,
        id_vars=["unique_simulation_id", COL_SCENARIO, COL_AGE, COL_SEX, COL_HEALTH],
        value_vars=[
            c for c in SIM_TO_ACTIVITY_MAPPING.values() if c in df_full.columns
        ],
        var_name=COL_ACTIVITY,
        value_name="duration",
    )

    df_std = (
        df_melt.groupby([COL_SCENARIO, COL_AGE, COL_SEX, COL_HEALTH, COL_ACTIVITY])[
            "duration"
        ]
        .std()
        .reset_index()
    )
    df_std = df_std.rename(columns={"duration": "Std"})

    df_pivot = df_std.pivot_table(
        index=[COL_SCENARIO, COL_AGE, COL_SEX, COL_HEALTH],
        columns=COL_ACTIVITY,
        values="Std",
    )

    path = os.path.join(out_dir, "results_activities_std_minutes.csv")
    df_pivot.to_csv(path)
    print(f"  Saved {path}")


if __name__ == "__main__":
    parser = get_sim_and_out_parser("Generate activities daily std minutes table")
    args = parser.parse_args()

    generate_std_table(args.sim_dir, args.out_dir)
