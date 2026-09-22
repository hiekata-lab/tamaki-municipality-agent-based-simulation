"""Responsible for plotting the daily majority activity schedule for agents."""

import argparse
import os
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from src.constants import (
    ACTIVITY_COLOR_MAP,
    COL_SCHEDULE_ACTIVITY,
    COL_SEGMENT_INDEX,
)
from src.post_simulation.figures.utils import (
    configure_matplotlib_defaults,
    save_figure,
)

configure_matplotlib_defaults()

LONG_ENTERTAINMENT_ACTIVITY = (
    "Watching TV, listening to the radio, reading newspapers or magazines"
)


def generate_average_day_plot(csv_path: str, out_dir: str) -> None:
    df = pd.read_csv(csv_path)

    most_common_activities = df.sort_values(COL_SEGMENT_INDEX)[
        COL_SCHEDULE_ACTIVITY
    ].tolist()
    unique_activities = set(most_common_activities)

    fig, ax = plt.subplots(figsize=(20, 4))

    bar_height = 0.5
    colors = [ACTIVITY_COLOR_MAP.get(act, "#808080") for act in most_common_activities]
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
    tick_labels = [f"{h:02d}:00" for h in range(0, 25, 2)]

    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, fontsize=16)
    ax.set_yticks([])

    patches = [
        mpatches.Patch(
            color=ACTIVITY_COLOR_MAP.get(act, "#808080"),
            label="Entertainment*" if act == LONG_ENTERTAINMENT_ACTIVITY else act,
        )
        for act in sorted(unique_activities)
    ]
    ax.legend(
        handles=patches,
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
        fontsize=16,
        handlelength=2.5,
        handleheight=1.5,
    )

    if LONG_ENTERTAINMENT_ACTIVITY in unique_activities:
        ax.text(
            0.5,
            -0.35,
            f"* {LONG_ENTERTAINMENT_ACTIVITY}",
            transform=ax.transAxes,
            fontsize=14,
            horizontalalignment="center",
            verticalalignment="top",
            style="italic",
        )

    plt.tight_layout()
    output_path = os.path.join(out_dir, "average_agent_daily_schedule.png")
    save_figure(fig, output_path, bbox_inches="tight")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate activities daily majority schedule plot"
    )
    parser.add_argument(
        "--schedule-csv", type=str, required=True, help="Input CSV path"
    )
    parser.add_argument("--out-dir", type=str, required=True, help="Output directory")
    args = parser.parse_args()

    generate_average_day_plot(args.schedule_csv, args.out_dir)
