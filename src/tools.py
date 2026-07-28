import os
import argparse
import pandas as pd
import numpy as np

from src.constants import (
    COL_AGE,
    COL_HEALTH,
    COL_SCENARIO,
    COL_SEX,
    SCENARIO_MAPPING,
)


def load_and_preprocess_simulation_data(sim_dir: str) -> pd.DataFrame:
    """
    Loads aggregated.csv from sim_dir, parses dates, calculates durations,
    and determines the next location. Also calculates the number of simulated days
    and attaches it to the dataframe.
    """
    csv_path = os.path.join(sim_dir, "aggregated.csv")
    df = pd.read_csv(csv_path)
    
    df["starting_time"] = pd.to_datetime(df["starting_time"], format="%Y-%m-%d %H.%M")
    df = df.sort_values(["unique_simulation_id", "starting_time"])

    df["end_time"] = df.groupby("unique_simulation_id")["starting_time"].shift(-1)
    df["end_time"] = df["end_time"].fillna(df["starting_time"] + pd.Timedelta(hours=8))
    df["duration"] = (df["end_time"] - df["starting_time"]).dt.total_seconds() / 60.0

    df["next_loc"] = df.groupby("unique_simulation_id")["location"].shift(-1)
    df["next_loc"] = df["next_loc"].fillna(df["location"])

    # Calculate days simulated per simulation id
    days_sim = df.groupby("unique_simulation_id")["duration"].sum() / (24 * 60)
    days_sim = days_sim.clip(lower=1).reset_index(name="days_simulated")
    
    df = pd.merge(df, days_sim, on="unique_simulation_id", how="left")
    return df


def load_simulation_metadata(sim_dir: str) -> pd.DataFrame:
    """
    Loads aggregated.json from sim_dir and parses agent demographics
    and scenario policies into a standardized DataFrame.
    """
    df_meta_raw = pd.read_json(os.path.join(sim_dir, "aggregated.json"))
    df_meta = pd.DataFrame()
    df_meta["unique_simulation_id"] = df_meta_raw["unique_simulation_id"]
    agent_params = pd.json_normalize(df_meta_raw["extra_params"].tolist())
    
    df_meta[COL_SCENARIO] = agent_params["agent_params.mod_policy"].map(SCENARIO_MAPPING)
    
    age_series = agent_params["agent_params.age"].str.extract(r"(\d+)").astype(int)[0]
    df_meta[COL_AGE] = np.where(
        age_series <= 74, "65 to 74 years old", "75 years old and over"
    )
    df_meta[COL_SEX] = agent_params["agent_params.gender"]
    df_meta[COL_HEALTH] = agent_params["agent_params.health"]
    
    return df_meta


def load_locations_coordinates(graph_path: str = "data/processed/locations_graph.json") -> tuple:
    """
    Loads locations_graph.json and returns Series mapping locations to X and Y coordinates.
    Returns: (loc_x, loc_y)
    """
    graph_df = pd.read_json(graph_path, orient="index")
    return graph_df["x"], graph_df["y"]


def get_sim_and_out_parser(description: str) -> argparse.ArgumentParser:
    """
    Returns an ArgumentParser configured with --sim-dir and --out-dir.
    Commonly used by post_simulation table scripts.
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--sim-dir", type=str, default=".", help="Path to simulation dir"
    )
    parser.add_argument(
        "--out-dir", type=str, default="tables", help="Output directory for tables"
    )
    return parser


def get_csv_and_out_parser(description: str, csv_arg: str = "--csv") -> argparse.ArgumentParser:
    """
    Returns an ArgumentParser configured with --csv (or --comparison-csv) and --out-dir.
    Commonly used by post_simulation figure scripts.
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(csv_arg, type=str, required=True, help="Input CSV path")
    parser.add_argument("--out-dir", type=str, required=True, help="Output directory")
    return parser


def get_io_parser(description: str) -> argparse.ArgumentParser:
    """
    Returns an ArgumentParser configured with --in-path and --out-path.
    Commonly used by pre_simulation scripts.
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--in-path", type=str, required=True, help="Input CSV")
    parser.add_argument("--out-path", type=str, required=True, help="Output CSV")
    return parser
