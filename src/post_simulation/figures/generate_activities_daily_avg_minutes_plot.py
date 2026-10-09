import argparse
import os
import textwrap
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from src.constants import (
    COL_ACTIVITY,
    COL_SIMULATION,
    COL_VALIDATION_VALUE,
    TRANSPORTATION_MODES,
)
from src.post_simulation.figures.utils import (
    configure_matplotlib_defaults,
    save_figure,
)

configure_matplotlib_defaults()


def generate_activity_time_comparison_plot(
    comparison_csv: str, out_dir: str
) -> None:
    df = pd.read_csv(comparison_csv)

    df_plot = df[
        ~df[COL_ACTIVITY].isin(TRANSPORTATION_MODES)
        & ~df[COL_ACTIVITY].str.startswith(("Riding", "Walking", "Driving"))
    ].copy()

    activities = df_plot[COL_ACTIVITY].tolist()
    means_sim = df_plot[COL_SIMULATION].values
    means_gold = df_plot[COL_VALIDATION_VALUE].values

    # Validation confidence interval half-widths using standardized bounds or fallback
    if "CI_95_Val_Upper" in df_plot.columns and "CI_95_Val_Lower" in df_plot.columns:
        ci95_gold = (
            df_plot["CI_95_Val_Upper"].values - df_plot["CI_95_Val_Lower"].values
        ) / 2.0
        ci90_gold = (
            df_plot["CI_90_Val_Upper"].values - df_plot["CI_90_Val_Lower"].values
        ) / 2.0
    else:
        ci95_gold = (
            df_plot["CI_95_Upper"].values - df_plot["CI_95_Lower"].values
        ) / 2.0
        ci90_gold = (
            df_plot["CI_90_Upper"].values - df_plot["CI_90_Lower"].values
        ) / 2.0

    # Simulation confidence interval half-widths using standardized bounds or fallback
    if "CI_95_Sim_Upper" in df_plot.columns and "CI_95_Sim_Lower" in df_plot.columns:
        ci95_sim = (
            df_plot["CI_95_Sim_Upper"].values - df_plot["CI_95_Sim_Lower"].values
        ) / 2.0
        ci90_sim = (
            df_plot["CI_90_Sim_Upper"].values - df_plot["CI_90_Sim_Lower"].values
        ) / 2.0
    else:
        ci95_sim = df_plot["CI_95_Sim"].values
        ci90_sim = df_plot["CI_90_Sim"].values

    y = np.arange(len(activities))
    height = 0.35

    fig, ax = plt.subplots(figsize=(12, 10))

    ax.barh(
        y - height / 2,
        means_gold,
        height,
        label="2021 Japanese Time Use Survey (Mie Prefecture, Weekly Average)",
        color="skyblue",
    )
    ax.barh(
        y + height / 2,
        means_sim,
        height,
        label="Simulation (Scenario 2)",
        color="salmon",
    )

    ax.errorbar(
        means_gold,
        y - height / 2,
        xerr=ci95_gold,
        fmt="none",
        ecolor="black",
        capsize=3,
        elinewidth=1,
        label="95% Confidence Interval",
    )
    ax.errorbar(
        means_sim,
        y + height / 2,
        xerr=ci95_sim,
        fmt="none",
        ecolor="black",
        capsize=3,
        elinewidth=1,
    )

    ax.errorbar(
        means_gold,
        y - height / 2,
        xerr=ci90_gold,
        fmt="none",
        ecolor="black",
        elinewidth=3,
        label="90% Confidence Interval",
    )
    ax.errorbar(
        means_sim,
        y + height / 2,
        xerr=ci90_sim,
        fmt="none",
        ecolor="black",
        elinewidth=3,
    )

    ax.set_xlabel("Mean Minutes Spent Across All Agents", fontsize=12)
    ax.set_yticks(y)
    ytick_labels = [textwrap.fill(act, width=30) for act in activities]
    ax.set_yticklabels(ytick_labels)
    ax.text(
        -0.02,
        1.02,
        "Activity",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=12,
        fontweight="bold",
    )
    ax.legend(fontsize=11)
    ax.invert_yaxis()

    plt.tight_layout()
    output_path = os.path.join(out_dir, "activity_time_comparison_minutes.png")
    save_figure(fig, output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate activities daily avg minutes plot"
    )
    parser.add_argument(
        "--comparison-csv", type=str, required=True, help="Input CSV path"
    )
    parser.add_argument("--out-dir", type=str, required=True, help="Output directory")
    args = parser.parse_args()

    generate_activity_time_comparison_plot(args.comparison_csv, args.out_dir)
