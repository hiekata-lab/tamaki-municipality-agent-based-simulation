import os
import argparse
import pandas as pd
import numpy as np
from src.constants import (
    ACTIVITIES,
    COL_AGE_GROUP,
    COL_AGE_YEAR,
    COL_AGENT_UUID,
    COL_DAYS_SIMULATED,
    COL_DEST_X,
    COL_DEST_Y,
    COL_DIST,
    COL_DURATION,
    COL_END_TIME,
    COL_HEALTH,
    COL_LOCATION,
    COL_NEXT_LOC,
    COL_SCENARIO,
    COL_SEX_EN,
    COL_SIM_ACTIVITY,
    COL_SIMULATION_UUID,
    COL_STARTING_TIME,
    COL_START_X,
    COL_START_Y,
    COL_X,
    COL_Y,
    KEY_EXTRA_PARAMS,
    PARAM_AGE,
    PARAM_GENDER,
    PARAM_HEALTH,
    PARAM_MOD_POLICY,
    SIM_ACTIVITY_TO_VAL_ACTIVIY_MAP,
    SIM_SCENARIO_TO_VAL_SCENARIO_MAP,
)


def preprocess_aggregated_data(in_dir: str, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)

    # Load aggregated raw data
    csv_path = os.path.join(in_dir, "raw_activities.csv")
    if not os.path.exists(csv_path):
        print(f"  No raw csv data found at {csv_path}")
        return
    # Read into pandas
    df_sim = pd.read_csv(csv_path)
    # Cast starting times to datetime objects
    df_sim[COL_STARTING_TIME] = pd.to_datetime(
        df_sim[COL_STARTING_TIME], format="%Y-%m-%d %H.%M"
    )
    # Sort values in the dataframe by simulation UUID and starting time
    df_sim = df_sim.sort_values([COL_SIMULATION_UUID, COL_STARTING_TIME])

    # NOTE: Create Utility columns from the aggregated simulation data file
    # Create the end time column by shifting up the start time of the next state
    df_sim[COL_END_TIME] = df_sim.groupby(COL_SIMULATION_UUID)[
        COL_STARTING_TIME
    ].shift(-1)
    # Create a map for the time each activity takes using the time delta
    # Use this to assign the duration of the state when no next state is available
    activity_durations = {
        act: pd.Timedelta(minutes=data[COL_DURATION])
        for act, data in ACTIVITIES.items()
    }
    df_sim[COL_END_TIME] = df_sim[COL_END_TIME].fillna(
        df_sim[COL_STARTING_TIME] + df_sim[COL_SIM_ACTIVITY].map(activity_durations)
    )
    # Convert the duration to minutes
    df_sim[COL_DURATION] = (
        df_sim[COL_END_TIME] - df_sim[COL_STARTING_TIME]
    ).dt.total_seconds() / 60.0
    # Create the next location column by shifting up the location of the next state
    df_sim[COL_NEXT_LOC] = df_sim.groupby(COL_SIMULATION_UUID)[COL_LOCATION].shift(
        -1
    )
    df_sim[COL_NEXT_LOC] = df_sim[COL_NEXT_LOC].fillna(df_sim[COL_LOCATION])
    # Create a column for the number of days simulated by dividing the total duration by the number of minutes in a day
    df_sim[COL_DAYS_SIMULATED] = (
        df_sim.groupby(COL_SIMULATION_UUID)[COL_DURATION].transform("sum")
        / (24 * 60)
    ).clip(lower=1)
    # Create a column for current loc x,y and next loc x,y
    graph_df = pd.read_json("data/processed/locations_graph.json", orient="index")
    loc_x = graph_df[COL_X]
    loc_y = graph_df[COL_Y]
    df_sim[COL_START_X] = df_sim[COL_LOCATION].map(loc_x)
    df_sim[COL_START_Y] = df_sim[COL_LOCATION].map(loc_y)
    df_sim[COL_DEST_X] = df_sim[COL_NEXT_LOC].map(loc_x)
    df_sim[COL_DEST_Y] = df_sim[COL_NEXT_LOC].map(loc_y)
    # Create a column for the distance between start and dest locations
    df_sim[COL_DIST] = np.sqrt(
        (df_sim[COL_START_X] - df_sim[COL_DEST_X]) ** 2
        + (df_sim[COL_START_Y] - df_sim[COL_DEST_Y]) ** 2
    )
    # Map simulation activity to validation survey activity format
    df_sim[COL_SIM_ACTIVITY] = df_sim[COL_SIM_ACTIVITY].map(
        SIM_ACTIVITY_TO_VAL_ACTIVIY_MAP
    )

    # NOTE: Create Metadata columns from the aggregated json metadata file
    json_path = os.path.join(in_dir, "agent_parameters.json")
    df_meta_raw = pd.read_json(json_path)
    # Create a fresh df for the metadata columns
    df_meta = pd.DataFrame()
    df_meta[COL_SIMULATION_UUID] = df_meta_raw[COL_SIMULATION_UUID]
    df_meta[COL_AGENT_UUID] = df_meta_raw[COL_AGENT_UUID]
    # Parse the agent parameters from the raw JSON DF into a new separate DF
    agent_params = pd.json_normalize(df_meta_raw[KEY_EXTRA_PARAMS].tolist())
    # Set the scenario columns by mapping from agent params
    df_meta[COL_SCENARIO] = agent_params[PARAM_MOD_POLICY].map(
        SIM_SCENARIO_TO_VAL_SCENARIO_MAP
    )
    # Create a series of ages by extracting the numerical age from the natural language age
    age_series = agent_params[PARAM_AGE].str.extract(r"(\d+)").astype(int)[0]
    df_meta[COL_AGE_YEAR] = age_series
    # Set age groups and create the respective groups
    df_meta[COL_AGE_GROUP] = np.where(
        age_series <= 74, "65 to 74 years old", "75 years old and over"
    )
    # Set genders by taking them directly from the agents
    df_meta[COL_SEX_EN] = agent_params[PARAM_GENDER]
    # Same for health
    df_meta[COL_HEALTH] = agent_params[PARAM_HEALTH]
    # Merge the metadata frame with the simulation data frame
    df_sim = pd.merge(
        df_sim, df_meta, on=[COL_SIMULATION_UUID, COL_AGENT_UUID], how="left"
    )
    # Export
    out_csv_path = os.path.join(out_dir, "processed_activities.csv")
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
        help="Input directory containing raw_activities.csv and agent_parameters.json.",
    )
    parser.add_argument(
        "--out-dir",
        type=str,
        required=True,
        help="Output directory for processed_activities.csv.",
    )
    args = parser.parse_args()
    preprocess_aggregated_data(args.in_dir, args.out_dir)
