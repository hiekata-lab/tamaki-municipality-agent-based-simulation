import argparse
import os
import numpy as np
import pandas as pd
from src.constants import (
    COL_SCHEDULE_ACTIVITY,
    COL_SEGMENT_INDEX,
    COL_SIM_ACTIVITY,
    COL_SIMULATION_UUID,
    COL_STARTING_TIME,
    COL_TIME,
    TRANSPORTATION_MODES,
)
from src.post_simulation.tables.utils import (
    load_aggregated_simulation_data,
    save_table_csv,
)


def generate_daily_schedule_table(sim_dir: str, out_dir: str) -> None:
    df = load_aggregated_simulation_data(sim_dir)

    # Harmonize transit modes to Moving without dropping them,
    # preserving transit events during 1-minute forward-fill resampling to prevent activity leaks.
    transit_mask = (
        df[COL_SIM_ACTIVITY].isin(TRANSPORTATION_MODES)
        | df[COL_SIM_ACTIVITY].str.startswith(
            ("Riding", "Walking", "Driving"), na=False
        )
        | (df[COL_SIM_ACTIVITY] == "Arriving")
    )
    df.loc[transit_mask, COL_SIM_ACTIVITY] = "Moving"

    df_last = df.groupby(COL_SIMULATION_UUID).last().reset_index()
    df_last[COL_STARTING_TIME] += pd.Timedelta(hours=8)
    df_last[COL_SIM_ACTIVITY] = np.nan

    df_combined = (
        pd.concat([df, df_last])
        .sort_values([COL_SIMULATION_UUID, COL_STARTING_TIME])
        .drop_duplicates(subset=[COL_SIMULATION_UUID, COL_STARTING_TIME], keep="last")
        .set_index(COL_STARTING_TIME)
    )

    df_min = (
        df_combined.groupby(COL_SIMULATION_UUID)[COL_SIM_ACTIVITY]
        .resample("1min")
        .ffill()
        .dropna()
        .reset_index()
    )

    df_min[COL_SEGMENT_INDEX] = (
        df_min[COL_STARTING_TIME].dt.hour * 60 + df_min[COL_STARTING_TIME].dt.minute
    ) // 10

    df_schedule = (
        df_min.groupby(COL_SEGMENT_INDEX)[COL_SIM_ACTIVITY]
        .agg(lambda x: x.mode().iloc[0] if not x.mode().empty else "Unknown")
        .reset_index()
        .rename(columns={COL_SIM_ACTIVITY: COL_SCHEDULE_ACTIVITY})
    )

    df_schedule[COL_TIME] = df_schedule[COL_SEGMENT_INDEX].apply(
        lambda x: f"{(x * 10) // 60:02d}:{(x * 10) % 60:02d}"
    )
    df_schedule = df_schedule[[COL_SEGMENT_INDEX, COL_TIME, COL_SCHEDULE_ACTIVITY]]

    path = os.path.join(out_dir, "results_activities_daily_schedule.csv")
    save_table_csv(df_schedule, path, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate daily schedule table")
    parser.add_argument(
        "--sim-dir", type=str, default=".", help="Path to simulation dir"
    )
    parser.add_argument(
        "--out-dir", type=str, default="tables", help="Output directory for tables"
    )
    args = parser.parse_args()
    generate_daily_schedule_table(args.sim_dir, args.out_dir)
