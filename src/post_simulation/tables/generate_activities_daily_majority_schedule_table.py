import argparse
import os
import pandas as pd
import numpy as np


from src.constants import (
    COL_END_TIME,
    COL_SCHEDULE_ACTIVITY,
    COL_SEGMENT_INDEX,
    COL_SIM_ACTIVITY,
    COL_STARTING_TIME,
    COL_TIME,
    COL_UNIQUE_SIMULATION_ID,
)


def generate_daily_schedule_table(sim_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)

    csv_path = os.path.join(sim_dir, "aggregated.csv")

    df = pd.read_csv(csv_path, parse_dates=[COL_STARTING_TIME, COL_END_TIME])

    # To include the final 8-hour period in resampling, add an end row for each agent
    df_last = df.groupby(COL_UNIQUE_SIMULATION_ID).last().reset_index()
    df_last[COL_STARTING_TIME] += pd.Timedelta(hours=8)
    df_last[COL_SIM_ACTIVITY] = np.nan

    df_combined = pd.concat([df, df_last]).sort_values(
        [COL_UNIQUE_SIMULATION_ID, COL_STARTING_TIME]
    )

    # Drop duplicates in case two activities have the same starting_time
    df_combined = df_combined.drop_duplicates(
        subset=[COL_UNIQUE_SIMULATION_ID, COL_STARTING_TIME], keep="last"
    )

    df_combined = df_combined.set_index(COL_STARTING_TIME)

    # Resample to 1-minute intervals and forward-fill activities
    df_min = (
        df_combined.groupby(COL_UNIQUE_SIMULATION_ID)[COL_SIM_ACTIVITY]
        .resample("1min")
        .ffill()
        .dropna()
        .reset_index()
    )

    # Calculate segment index (10-minute blocks)
    df_min[COL_SEGMENT_INDEX] = (
        df_min[COL_STARTING_TIME].dt.hour * 60 + df_min[COL_STARTING_TIME].dt.minute
    ) // 10

    # Find most common activity per segment
    df_schedule = (
        df_min.groupby(COL_SEGMENT_INDEX)[COL_SIM_ACTIVITY]
        .agg(lambda x: x.mode()[0])
        .reset_index()
    )
    df_schedule = df_schedule.rename(columns={COL_SIM_ACTIVITY: COL_SCHEDULE_ACTIVITY})

    # Format time column
    df_schedule[COL_TIME] = df_schedule[COL_SEGMENT_INDEX].apply(
        lambda x: f"{(x * 10) // 60:02d}:{(x * 10) % 60:02d}"
    )

    df_schedule = df_schedule[[COL_SEGMENT_INDEX, COL_TIME, COL_SCHEDULE_ACTIVITY]]

    path = os.path.join(out_dir, "results_activities_daily_schedule.csv")
    df_schedule.to_csv(path, index=False)
    print(f"  Saved {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate daily schedule table")

    parser.add_argument('--sim-dir', type=str, default='.', help='Path to simulation dir')

    parser.add_argument('--out-dir', type=str, default='tables', help='Output directory for tables')
    args = parser.parse_args()

    generate_daily_schedule_table(args.sim_dir, args.out_dir)
