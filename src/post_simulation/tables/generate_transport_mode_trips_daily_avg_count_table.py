import argparse
import os
from src.constants import (
    COL_AGE_GROUP,
    COL_HEALTH,
    COL_SCENARIO,
    COL_SEX_EN,
)
from src.post_simulation.tables.utils import (
    export_grouped_pivot_table,
    load_normalized_transport_data,
)

DEMOGRAPHIC_COLS = [COL_SCENARIO, COL_AGE_GROUP, COL_SEX_EN, COL_HEALTH]


def generate_transport_tables(sim_dir: str, out_dir: str) -> None:
    df_full = load_normalized_transport_data(sim_dir)
    export_grouped_pivot_table(
        df=df_full,
        group_cols=DEMOGRAPHIC_COLS,
        val_col="avg_trips",
        agg_func="mean",
        output_path=os.path.join(
            out_dir, "results_transport_mode_trips_daily_avg_count.csv"
        ),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate transport mode trips daily average count table"
    )
    parser.add_argument(
        "--sim-dir", type=str, default=".", help="Path to simulation dir"
    )
    parser.add_argument(
        "--out-dir", type=str, default="tables", help="Output directory for tables"
    )
    args = parser.parse_args()
    generate_transport_tables(args.sim_dir, args.out_dir)
