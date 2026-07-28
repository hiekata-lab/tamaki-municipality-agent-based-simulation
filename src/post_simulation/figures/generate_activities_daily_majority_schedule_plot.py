import pandas as pd
import os
from src.tools import get_csv_and_out_parser

os.environ["MPLCONFIGDIR"] = "./.matplotlib"

import matplotlib.pyplot as plt
import numpy as np
import argparse
import matplotlib.patches as mpatches
from src.constants import ACTIVITY_COLORS


def generate_average_day_plot(csv_path, out_dir):
    df = pd.read_csv(csv_path)

    most_common_activities = df.sort_values("Segment Index")["Activity"].tolist()
    unique_activities = set(most_common_activities)

    fig, ax = plt.subplots(figsize=(15, 3))

    bar_height = 0.5
    # Vectorize barh by passing arrays
    acts_series = pd.Series(most_common_activities)
    colors = acts_series.map(ACTIVITY_COLORS).fillna("#808080").tolist()
    starts = np.arange(len(most_common_activities)) * 10
    widths = np.full(len(most_common_activities), 10)
    ax.barh(
        np.zeros(len(most_common_activities)),
        widths,
        left=starts,
        height=bar_height,
        color=colors,
    )

    ax.set_xlim(0, 24 * 60)
    ax.set_ylim(-0.5, 0.5)

    tick_positions = np.arange(0, 24 * 60 + 1, 120)
    time_map = df.set_index("Segment Index")["Time"].to_dict()
    tick_labels = [time_map.get(pos // 10, "24:00") for pos in tick_positions]

    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels)

    ax.set_yticks([])
    ax.set_xlabel("Time of Day")
    ax.set_title("Average Agent Daily Schedule (Majority of Every 10-min Segment)")

    patches = [
        mpatches.Patch(color=ACTIVITY_COLORS.get(act, "#808080"), label=act)
        for act in unique_activities
    ]
    ax.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc="upper left")

    plt.tight_layout()
    os.makedirs(out_dir, exist_ok=True)
    output_path = os.path.join(out_dir, "average_agent_daily_schedule.png")
    plt.savefig(output_path, dpi=300)
    print(f"  Figure saved to {output_path}")


if __name__ == "__main__":
    parser = get_csv_and_out_parser("Generate activities daily majority schedule plot", "--schedule-csv")
    args = parser.parse_args()

    generate_average_day_plot(args.schedule_csv, args.out_dir)
