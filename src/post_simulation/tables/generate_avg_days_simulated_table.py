import argparse
import os
import pandas as pd
from src.constants import (
    COL_DAYS_SIMULATED,
    COL_SIMULATION_UUID,
)
from src.post_simulation.tables.utils import (
    load_aggregated_simulation_data,
    save_table_csv,
)


def generate_avg_days_simulated_table(sim_dir: str, out_dir: str) -> None:
    df = load_aggregated_simulation_data(sim_dir, parse_dates=[])

    avg_days = df.groupby(COL_SIMULATION_UUID)[COL_DAYS_SIMULATED].first().mean()
    result = pd.DataFrame(
        [
            {
                "Metric": "Average number of days simulated per agent",
                "Value": round(avg_days, 4),
            }
        ]
    )

    out_file = os.path.join(out_dir, "results_avg_days_simulated.csv")
    save_table_csv(result, out_file, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate average days simulated table."
    )
    parser.add_argument(
        "--sim-dir", type=str, default=".", help="Path to simulation dir"
    )
    parser.add_argument(
        "--out-dir", type=str, default="tables", help="Output directory for tables"
    )
    args = parser.parse_args()
    generate_avg_days_simulated_table(args.sim_dir, args.out_dir)
