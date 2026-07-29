import os
import argparse
import pandas as pd
import numpy as np
from src.constants import (
    ACTIVITIES,
    COL_SCENARIO,
    SCENARIO_MAPPING,
    COL_AGE,
    COL_SEX_EN,
    COL_HEALTH,
)


def preprocess_aggregated_data(in_dir: str, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)

    csv_path = os.path.join(in_dir, "aggregated_raw.csv")
    if not os.path.exists(csv_path):
        print(f"  No raw csv data found at {csv_path}")
        return

    df_sim = pd.read_csv(csv_path)
    df_sim["starting_time"] = pd.to_datetime(
        df_sim["starting_time"], format="%Y-%m-%d %H.%M"
    )
    df_sim = df_sim.sort_values(["unique_simulation_id", "starting_time"])

    df_sim["end_time"] = df_sim.groupby("unique_simulation_id")["starting_time"].shift(
        -1
    )

    activity_durations = {
        act: pd.Timedelta(minutes=data["duration"]) for act, data in ACTIVITIES.items()
    }
    df_sim["end_time"] = df_sim["end_time"].fillna(
        df_sim["starting_time"] + df_sim["activity"].map(activity_durations)
    )

    df_sim["duration"] = (
        df_sim["end_time"] - df_sim["starting_time"]
    ).dt.total_seconds() / 60.0

    df_sim["next_loc"] = df_sim.groupby("unique_simulation_id")["location"].shift(-1)
    df_sim["next_loc"] = df_sim["next_loc"].fillna(df_sim["location"])

    df_sim["days_simulated"] = (
        df_sim.groupby("unique_simulation_id")["duration"].transform("sum") / (24 * 60)
    ).clip(lower=1)

    # Process metadata
    json_path = os.path.join(in_dir, "aggregated.json")

    df_meta_raw = pd.read_json(json_path)
    df_meta = pd.DataFrame()
    df_meta["unique_simulation_id"] = df_meta_raw["unique_simulation_id"]
    agent_params = pd.json_normalize(df_meta_raw["extra_params"].tolist())

    df_meta[COL_SCENARIO] = agent_params["agent_params.mod_policy"].map(
        SCENARIO_MAPPING
    )
    age_series = agent_params["agent_params.age"].str.extract(r"(\d+)").astype(int)[0]
    df_meta["Age_Years"] = age_series
    df_meta[COL_AGE] = np.where(
        age_series <= 74, "65 to 74 years old", "75 years old and over"
    )
    df_meta[COL_SEX_EN] = agent_params["agent_params.gender"]
    df_meta[COL_HEALTH] = agent_params["agent_params.health"]

    df_sim = pd.merge(df_sim, df_meta, on="unique_simulation_id", how="left")

    out_csv_path = os.path.join(out_dir, "aggregated.csv")
    df_sim.to_csv(out_csv_path, index=False)
    print(f"  Preprocessed data and output to {out_csv_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Preprocess aggregated simulation results."
    )
    parser.add_argument(
        "--in-dir",
        type=str,
        required=True,
        help="Input directory containing aggregated_raw.csv and aggregated.json.",
    )
    parser.add_argument(
        "--out-dir",
        type=str,
        required=True,
        help="Output directory for aggregated.csv.",
    )
    args = parser.parse_args()

    preprocess_aggregated_data(args.in_dir, args.out_dir)
