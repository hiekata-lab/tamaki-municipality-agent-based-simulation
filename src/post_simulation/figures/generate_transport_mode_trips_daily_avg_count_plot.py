import pandas as pd
import os


os.environ["MPLCONFIGDIR"] = "./.matplotlib"
from matplotlib.ticker import MaxNLocator
import matplotlib.pyplot as plt
import numpy as np
import argparse
from src.constants import COL_SCENARIO, TRANSPORTATION_MODES


def plot_transport_metric(csv_path, out_dir):
    df = pd.read_csv(csv_path)
    scenarios = ["Scenario 1", "Scenario 2", "Scenario 3", "Scenario 4"]

    df_agg = df.groupby(COL_SCENARIO).mean(numeric_only=True)

    fig, ax = plt.subplots(figsize=(12, 6))
    df_plot = df_agg.reindex(scenarios).fillna(0)[TRANSPORTATION_MODES].T
    df_plot.plot.bar(ax=ax, width=0.8, rot=15)

    # keep x for compatibility with following code
    x = np.arange(len(TRANSPORTATION_MODES))

    ax.set_ylabel("Daily Average Number of Trips")
    ax.set_title("Daily Average Number of Trips per Transportation Mode per Scenario")

    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    # ax ticks handled by pandas
    ax.legend()

    plt.tight_layout()
    os.makedirs(out_dir, exist_ok=True)
    output_path = os.path.join(out_dir, "transport_trips_daily_avg_count.png")
    plt.savefig(output_path, dpi=300)
    print(f"  Figure saved to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate transport mode trips daily avg count plot")

    parser.add_argument("--csv", type=str, required=True, help='Input CSV path')

    parser.add_argument('--out-dir', type=str, required=True, help='Output directory')
    args = parser.parse_args()

    plot_transport_metric(args.csv, args.out_dir)
