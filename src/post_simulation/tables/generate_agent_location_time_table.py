import argparse
import os
import pandas as pd


def main():
    parser = argparse.ArgumentParser(description="Generate agent location time table.")

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

    # Group by agent and location
    df_loc = (
        df.groupby(["unique_simulation_id", "location"])
        .agg({"duration": "sum"})
        .reset_index()
    )

    # Map locations to coordinates
    df_loc["x"] = df_loc["location"].map(loc_x)
    df_loc["y"] = df_loc["location"].map(loc_y)

    # Drop rows where coordinates could not be found
    df_loc = df_loc.dropna(subset=["x", "y"])

    out_file = os.path.join(args.out_dir, "results_agent_location_time.csv")
    df_loc.to_csv(out_file, index=False)
    print(f"  Saved {out_file}")

    # Generate legend table
    unique_locs = df_loc["location"].drop_duplicates().dropna().reset_index(drop=True)
    legend_df = pd.DataFrame(
        {"ID": range(1, len(unique_locs) + 1), "Location Name": unique_locs}
    )

    # Also save coords for the plot script to use the exact same IDs
    legend_df["x"] = legend_df["Location Name"].map(loc_x)
    legend_df["y"] = legend_df["Location Name"].map(loc_y)

    legend_file = os.path.join(
        args.out_dir, "results_agent_location_time_legend.csv"
    )
    legend_df.to_csv(legend_file, index=False)
    print(f"  Saved {legend_file}")


if __name__ == "__main__":
    main()
