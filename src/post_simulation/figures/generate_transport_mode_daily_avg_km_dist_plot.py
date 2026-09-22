"""Responsible for plotting daily average distance traveled by transport mode."""

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
    df[TRANSPORTATION_MODES] = df[TRANSPORTATION_MODES] * 1000.0
    fig, _ = plot_grouped_category_bars(
        df=df,
        group_col=COL_SCENARIO,
        category_order=DEFAULT_SCENARIOS,
        value_cols=TRANSPORTATION_MODES,
        ylabel="Daily Average Distance (m)",
        agg_func="mean",
    )
    save_figure(fig, os.path.join(out_dir, "transport_mode_daily_avg_km_dist.png"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate transport mode daily avg km dist plot"
    )
    parser.add_argument("--csv", type=str, required=True, help="Input CSV path")
    parser.add_argument("--out-dir", type=str, required=True, help="Output directory")
    args = parser.parse_args()

    plot_transport_metric(args.csv, args.out_dir)
