import argparse
import os
import pandas as pd
from src.constants import (
    COL_DEST_LOCATION,
    COL_DEST_X,
    COL_DEST_Y,
    COL_LOCATION,
    COL_NEXT_LOC,
    COL_SIMULATION_UUID,
    COL_STARTING_TIME,
    COL_START_LOCATION,
    COL_START_X,
    COL_START_Y,
)
from src.post_simulation.tables.utils import (
    generate_location_legend_table,
    load_aggregated_simulation_data,
    save_table_csv,
)


def generate_agent_trips_table(sim_dir: str, out_dir: str) -> None:
    df = load_aggregated_simulation_data(sim_dir)

    agent_trips_export_cols = [
        COL_SIMULATION_UUID,
        COL_STARTING_TIME,
        COL_LOCATION,
        COL_NEXT_LOC,
        COL_START_X,
        COL_START_Y,
        COL_DEST_X,
        COL_DEST_Y,
    ]

    export_df = df[agent_trips_export_cols].rename(
        columns={COL_LOCATION: COL_START_LOCATION, COL_NEXT_LOC: COL_DEST_LOCATION}
    )
    export_df = export_df[
        export_df[COL_START_LOCATION] != export_df[COL_DEST_LOCATION]
    ].dropna(subset=[COL_START_X, COL_START_Y, COL_DEST_X, COL_DEST_Y])

    out_file = os.path.join(out_dir, "results_agent_trips.csv")
    save_table_csv(export_df, out_file, index=False)

    legend_file = os.path.join(out_dir, "results_agent_trips_legend.csv")
    all_trip_locs = pd.concat(
        [export_df[COL_START_LOCATION], export_df[COL_DEST_LOCATION]]
    )
    generate_location_legend_table(all_trip_locs, legend_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate trip map table.")
    parser.add_argument(
        "--sim-dir", type=str, default=".", help="Path to simulation dir"
    )
    parser.add_argument(
        "--out-dir", type=str, default="tables", help="Output directory for tables"
    )
    args = parser.parse_args()
    generate_agent_trips_table(args.sim_dir, args.out_dir)
