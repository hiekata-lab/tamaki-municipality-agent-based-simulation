import argparse
import os
import textwrap
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as stats
from src.constants import (
    COL_SIMULATION,
    SURVEY_TITLE,
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

    activity_cols = [c for c in df.columns if " - " in c]
    all_activities = list(dict.fromkeys([c.split(" - ")[0] for c in activity_cols]))

    activities = [
        act
        for act in all_activities
        if act not in TRANSPORTATION_MODES
        and not act.startswith(("Riding", "Walking", "Driving"))
    ]

    sim_cols = [f"{act} - {COL_SIMULATION}" for act in activities]
    val_cols = [f"{act} - {SURVEY_TITLE}" for act in activities]
    ci95_lower_cols = [f"{act} - CI_95_Lower" for act in activities]
    ci95_upper_cols = [f"{act} - CI_95_Upper" for act in activities]
    ci90_lower_cols = [f"{act} - CI_90_Lower" for act in activities]
    ci90_upper_cols = [f"{act} - CI_90_Upper" for act in activities]

    means_sim = df[sim_cols].mean().fillna(0).values
    means_gold = df[val_cols].mean().fillna(0).values

    ci95_gold = np.nan_to_num(
        ((df[ci95_upper_cols].values - df[ci95_lower_cols].values) / 2.0).mean(
            axis=0
        )
    )
    ci90_gold = np.nan_to_num(
        ((df[ci90_upper_cols].values - df[ci90_lower_cols].values) / 2.0).mean(
            axis=0
        )
    )

    se_sim = df[sim_cols].sem().fillna(0).values
    dof = np.maximum(1, df[sim_cols].count().values - 1)
    ci95_sim = np.nan_to_num(stats.t.ppf(0.975, dof) * se_sim)
    ci90_sim = np.nan_to_num(stats.t.ppf(0.95, dof) * se_sim)

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

    ax.set_xlabel("Average Time Spent (minutes)")
    ax.set_title(
        "Average Time Spent on Activities (2021 Japanese Time Use Survey vs Simulation)",
        loc="center",
    )
    ax.set_yticks(y)
    ax.set_yticklabels([textwrap.fill(act, width=30) for act in activities])
    ax.legend()
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
