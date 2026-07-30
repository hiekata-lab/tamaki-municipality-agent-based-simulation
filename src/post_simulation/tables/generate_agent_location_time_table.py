import argparse
import os
import pandas as pd
from src.constants import (
    COL_DURATION,
    COL_LOCATION,
    COL_SIMULATION_UUID,
    COL_START_X,
    COL_START_Y,
    COL_X,
    COL_Y,
)
from src.post_simulation.tables.utils import (
    generate_location_legend_table,
    load_aggregated_simulation_data,
    save_table_csv,
)


def generate_agent_location_time_table(sim_dir: str, out_dir: str) -> None:
    df = load_aggregated_simulation_data(sim_dir)

    df_loc = (
        df.groupby([COL_SIMULATION_UUID, COL_LOCATION])
        .agg({COL_DURATION: "sum", COL_START_X: "first", COL_START_Y: "first"})
        .reset_index()
        .rename(columns={COL_START_X: COL_X, COL_START_Y: COL_Y})
    )
    df_loc = df_loc.dropna(subset=[COL_X, COL_Y])

    out_file = os.path.join(out_dir, "results_agent_location_time.csv")
    save_table_csv(df_loc, out_file, index=False)

    legend_file = os.path.join(out_dir, "results_agent_location_time_legend.csv")
    generate_location_legend_table(df_loc[COL_LOCATION], legend_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate agent location time table."
    )
    parser.add_argument(
        "--sim-dir", type=str, default=".", help="Path to simulation dir"
    )
    parser.add_argument(
        "--out-dir", type=str, default="tables", help="Output directory for tables"
    )
    args = parser.parse_args()
    generate_agent_location_time_table(args.sim_dir, args.out_dir)
