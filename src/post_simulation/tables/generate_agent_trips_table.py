import argparse
import os
import pandas as pd
from src.constants import AGENT_TRIPS_EXPORT_COLS


def main():
    parser = argparse.ArgumentParser(description="Generate trip map table.")

    parser.add_argument('--sim-dir', type=str, default='.', help='Path to simulation dir')

    parser.add_argument('--out-dir', type=str, default='tables', help='Output directory for tables')
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    # Load locations graph to map node IDs to coordinates
    graph_df = pd.read_json("data/processed/locations_graph.json", orient="index")
    loc_x = graph_df["x"]
    loc_y = graph_df["y"]

    csv_path = os.path.join(args.sim_dir, "aggregated.csv")
    df = pd.read_csv(csv_path, parse_dates=["starting_time", "end_time"])

    # Map locations to coordinates
    df["start_x"] = df["location"].map(loc_x)
    df["start_y"] = df["location"].map(loc_y)
    df["dest_x"] = df["next_loc"].map(loc_x)
    df["dest_y"] = df["next_loc"].map(loc_y)

    # Filter columns to export
    export_df = df[AGENT_TRIPS_EXPORT_COLS].copy()
    export_df = export_df.rename(
        columns={"location": "start_location", "next_loc": "dest_location"}
    )

    # Filter out trips that stay in the same location
    export_df = export_df[export_df["start_location"] != export_df["dest_location"]]

    # Drop rows where start coordinates could not be found
    export_df = export_df.dropna(subset=["start_x", "start_y", "dest_x", "dest_y"])

    out_file = os.path.join(args.out_dir, "results_agent_trips.csv")
    export_df.to_csv(out_file, index=False)
    print(f"  Saved {out_file}")

    # Generate legend table
    unique_locs = (
        pd.concat([export_df["start_location"], export_df["dest_location"]])
        .drop_duplicates()
        .dropna()
        .reset_index(drop=True)
    )
    legend_df = pd.DataFrame(
        {"ID": range(1, len(unique_locs) + 1), "Location Name": unique_locs}
    )

    # Also save coords for the plot script to use the exact same IDs
    legend_df["x"] = legend_df["Location Name"].map(loc_x)
    legend_df["y"] = legend_df["Location Name"].map(loc_y)

    legend_file = os.path.join(args.out_dir, "results_agent_trips_legend.csv")
    legend_df.to_csv(legend_file, index=False)
    print(f"  Saved {legend_file}")


if __name__ == "__main__":
    main()
