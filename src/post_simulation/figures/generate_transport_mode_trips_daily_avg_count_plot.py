import argparse
import os
import pandas as pd
from src.constants import COL_SCENARIO, TRANSPORTATION_MODES
from src.post_simulation.figures.utils import (
    configure_matplotlib_defaults,
    plot_grouped_category_bars,
    save_figure,
)

configure_matplotlib_defaults()

DEFAULT_SCENARIOS = ["Scenario 1", "Scenario 2", "Scenario 3", "Scenario 4"]


def plot_transport_metric(csv_path: str, out_dir: str) -> None:
    df = pd.read_csv(csv_path)
    fig, _ = plot_grouped_category_bars(
        df=df,
        group_col=COL_SCENARIO,
        category_order=DEFAULT_SCENARIOS,
        value_cols=TRANSPORTATION_MODES,
        ylabel="Daily Average Number of Trips",
        agg_func="mean",
        integer_y_ticks=True,
    )
    save_figure(fig, os.path.join(out_dir, "transport_trips_daily_avg_count.png"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate transport mode trips daily avg count plot"
    )
    parser.add_argument("--csv", type=str, required=True, help="Input CSV path")
    parser.add_argument("--out-dir", type=str, required=True, help="Output directory")
    args = parser.parse_args()

    plot_transport_metric(args.csv, args.out_dir)
