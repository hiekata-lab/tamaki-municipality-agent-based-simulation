import argparse
import os
import pandas as pd
from src.constants import (
    COL_DEST_LOCATION,
    COL_DEST_X,
    COL_DEST_Y,
    COL_END_TIME,
    COL_ID,
    COL_LOCATION,
    COL_LOCATION_NAME,
    COL_NEXT_LOC,
    COL_STARTING_TIME,
    COL_START_LOCATION,
    COL_START_X,
    COL_START_Y,
    COL_UNIQUE_SIMULATION_ID,
    COL_X,
    COL_Y,
)


def main():
    parser = argparse.ArgumentParser(description="Generate trip map table.")

    parser.add_argument('--sim-dir', type=str, default='.', help='Path to simulation dir')

    parser.add_argument('--out-dir', type=str, default='tables', help='Output directory for tables')
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    # Load locations graph to map node IDs to coordinates
    graph_df = pd.read_json("data/processed/locations_graph.json", orient="index")
    loc_x = graph_df[COL_X]
    loc_y = graph_df[COL_Y]

    csv_path = os.path.join(args.sim_dir, "aggregated.csv")
    df = pd.read_csv(csv_path, parse_dates=[COL_STARTING_TIME, COL_END_TIME])

    # Map locations to coordinates
    df[COL_START_X] = df[COL_LOCATION].map(loc_x)
    df[COL_START_Y] = df[COL_LOCATION].map(loc_y)
    df[COL_DEST_X] = df[COL_NEXT_LOC].map(loc_x)
    df[COL_DEST_Y] = df[COL_NEXT_LOC].map(loc_y)

    agent_trips_export_cols = [
        COL_UNIQUE_SIMULATION_ID,
        COL_STARTING_TIME,
        COL_LOCATION,
        COL_NEXT_LOC,
        COL_START_X,
        COL_START_Y,
        COL_DEST_X,
        COL_DEST_Y,
    ]

    # Filter columns to export
    export_df = df[agent_trips_export_cols].copy()
    export_df = export_df.rename(
        columns={COL_LOCATION: COL_START_LOCATION, COL_NEXT_LOC: COL_DEST_LOCATION}
    )

    # Filter out trips that stay in the same location
    export_df = export_df[export_df[COL_START_LOCATION] != export_df[COL_DEST_LOCATION]]

    # Drop rows where start coordinates could not be found
    export_df = export_df.dropna(subset=[COL_START_X, COL_START_Y, COL_DEST_X, COL_DEST_Y])

    out_file = os.path.join(args.out_dir, "results_agent_trips.csv")
    export_df.to_csv(out_file, index=False)
    print(f"  Saved {out_file}")

    # Generate legend table
    unique_locs = (
        pd.concat([export_df[COL_START_LOCATION], export_df[COL_DEST_LOCATION]])
        .drop_duplicates()
        .dropna()
        .reset_index(drop=True)
    )
    legend_df = pd.DataFrame(
        {COL_ID: range(1, len(unique_locs) + 1), COL_LOCATION_NAME: unique_locs}
    )

    # Also save coords for the plot script to use the exact same IDs
    legend_df[COL_X] = legend_df[COL_LOCATION_NAME].map(loc_x)
    legend_df[COL_Y] = legend_df[COL_LOCATION_NAME].map(loc_y)

    legend_file = os.path.join(args.out_dir, "results_agent_trips_legend.csv")
    legend_df.to_csv(legend_file, index=False)
    print(f"  Saved {legend_file}")


if __name__ == "__main__":
    main()
