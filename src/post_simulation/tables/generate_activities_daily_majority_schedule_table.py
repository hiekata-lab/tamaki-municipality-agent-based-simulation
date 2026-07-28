import argparse
import os
import pandas as pd
import numpy as np


def generate_daily_schedule_table(sim_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)

    csv_path = os.path.join(sim_dir, "aggregated.csv")

    df = pd.read_csv(csv_path, parse_dates=["starting_time", "end_time"])

    # To include the final 8-hour period in resampling, add an end row for each agent
    df_last = df.groupby("unique_simulation_id").last().reset_index()
    df_last["starting_time"] += pd.Timedelta(hours=8)
    df_last["activity"] = np.nan

    df_combined = pd.concat([df, df_last]).sort_values(
        ["unique_simulation_id", "starting_time"]
    )

    # Drop duplicates in case two activities have the same starting_time
    df_combined = df_combined.drop_duplicates(
        subset=["unique_simulation_id", "starting_time"], keep="last"
    )

    df_combined = df_combined.set_index("starting_time")

    # Resample to 1-minute intervals and forward-fill activities
    df_min = (
        df_combined.groupby("unique_simulation_id")["activity"]
        .resample("1min")
        .ffill()
        .dropna()
        .reset_index()
    )

    # Calculate segment index (10-minute blocks)
    df_min["Segment Index"] = (
        df_min["starting_time"].dt.hour * 60 + df_min["starting_time"].dt.minute
    ) // 10

    # Find most common activity per segment
    df_schedule = (
        df_min.groupby("Segment Index")["activity"]
        .agg(lambda x: x.mode()[0])
        .reset_index()
    )
    df_schedule = df_schedule.rename(columns={"activity": "Activity"})

    # Format time column
    df_schedule["Time"] = df_schedule["Segment Index"].apply(
        lambda x: f"{(x * 10) // 60:02d}:{(x * 10) % 60:02d}"
    )

    df_schedule = df_schedule[["Segment Index", "Time", "Activity"]]

    path = os.path.join(out_dir, "results_activities_daily_schedule.csv")
    df_schedule.to_csv(path, index=False)
    print(f"  Saved {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate daily schedule table")

    parser.add_argument('--sim-dir', type=str, default='.', help='Path to simulation dir')

    parser.add_argument('--out-dir', type=str, default='tables', help='Output directory for tables')
    args = parser.parse_args()

    generate_daily_schedule_table(args.sim_dir, args.out_dir)
