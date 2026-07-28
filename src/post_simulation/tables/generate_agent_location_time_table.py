import os
import pandas as pd
from src.tools import (
    load_and_preprocess_simulation_data,
    load_locations_coordinates,
    get_sim_and_out_parser,
)

def main():
    parser = get_sim_and_out_parser("Generate agent location time table.")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    # Load locations graph to map node IDs to coordinates
    loc_x, loc_y = load_locations_coordinates()

    df = load_and_preprocess_simulation_data(args.sim_dir)

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
