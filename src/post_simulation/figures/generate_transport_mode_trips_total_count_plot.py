import pandas as pd
import os
from src.tools import get_csv_and_out_parser

os.environ["MPLCONFIGDIR"] = "./.matplotlib"
from matplotlib.ticker import MaxNLocator
import matplotlib.pyplot as plt
import numpy as np
import argparse
from src.constants import TRANSPORTATION_MODES


def plot_transport_metric(csv_path, out_dir):
    df = pd.read_csv(csv_path)
    scenarios = ["Scenario 1", "Scenario 2", "Scenario 3", "Scenario 4"]

    df_agg = df.groupby("Scenario").sum(numeric_only=True)

    fig, ax = plt.subplots(figsize=(12, 6))
    df_plot = df_agg.reindex(scenarios).fillna(0)[TRANSPORTATION_MODES].T
    df_plot.plot.bar(ax=ax, width=0.8, rot=15)

    # keep x for compatibility with following code
    x = np.arange(len(TRANSPORTATION_MODES))

    ax.set_ylabel("Total Number of Trips")
    ax.set_title("Total Number of Trips per Transportation Mode per Scenario")

    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    # ax ticks handled by pandas
    ax.legend()

    plt.tight_layout()
    os.makedirs(out_dir, exist_ok=True)
    output_path = os.path.join(out_dir, "transport_trips_total_count.png")
    plt.savefig(output_path, dpi=300)
    print(f"  Figure saved to {output_path}")


if __name__ == "__main__":
    parser = get_csv_and_out_parser("Generate transport mode trips total count plot")
    args = parser.parse_args()

    plot_transport_metric(args.csv, args.out_dir)
