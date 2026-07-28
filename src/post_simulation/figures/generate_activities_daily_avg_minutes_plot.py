import pandas as pd
import os
from src.tools import get_csv_and_out_parser

os.environ["MPLCONFIGDIR"] = "./.matplotlib"

import matplotlib.pyplot as plt
import numpy as np
import textwrap
import argparse
import scipy.stats as stats


def generate_activity_time_comparison_plot(comparison_csv, out_dir):
    df = pd.read_csv(comparison_csv, header=[0, 1])

    # Vectorize column parsing
    lvl0 = (
        pd.Series([c[0] for c in df.columns])
        .replace(regex="^Unnamed.*", value=np.nan)
        .ffill()
    )
    lvl0.iloc[:5] = df.iloc[0, :5].values

    lvl1 = pd.Series([c[1] for c in df.columns]).fillna("")
    lvl1.iloc[:5] = ""

    df.columns = pd.MultiIndex.from_arrays([lvl0, lvl1])
    df = df.iloc[1:].reset_index(drop=True)

    df_scen2 = df[
        (df[("Scenario", "")] == "Scenario 2")
        & (df[("Day of the week", "")] == "Weekday")
    ].copy()

    activities = lvl0[5:].unique().tolist()

    df_g = df_scen2.xs(
        "Survey on Time Use and Leisure Activities 2021", level=1, axis=1
    ).apply(pd.to_numeric, errors="coerce")
    df_s = df_scen2.xs("Simulation", level=1, axis=1).apply(
        pd.to_numeric, errors="coerce"
    )

    # Vectorized means, se, degrees of freedom, and t-scores
    means_gold = df_g.mean().fillna(0).values
    means_sim = df_s.mean().fillna(0).values

    se_g = df_g.sem().fillna(0)
    se_s = df_s.sem().fillna(0)

    df_g_count = np.maximum(1, df_g.count() - 1)
    df_s_count = np.maximum(1, df_s.count() - 1)

    t95_g = stats.t.ppf(0.975, df_g_count)
    t95_s = stats.t.ppf(0.975, df_s_count)
    t90_g = stats.t.ppf(0.95, df_g_count)
    t90_s = stats.t.ppf(0.95, df_s_count)

    ci95_gold = np.nan_to_num(t95_g * se_g)
    ci95_sim = np.nan_to_num(t95_s * se_s)
    ci90_gold = np.nan_to_num(t90_g * se_g)
    ci90_sim = np.nan_to_num(t90_s * se_s)

    y = np.arange(len(activities))
    height = 0.35

    _, ax = plt.subplots(figsize=(12, 10))

    # Plot bars
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

    # Plot 95% CI (thin line with caps)
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

    # Plot 90% CI (thick line without caps)
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
        "Average Time Spent on Activities (2021 Japanese Time Use Survey vs Scenario 2)",
        loc="center",
    )
    ax.set_yticks(y)
    ax.set_yticklabels([textwrap.fill(act, width=30) for act in activities])
    ax.legend()
    ax.invert_yaxis()

    plt.tight_layout()
    os.makedirs(out_dir, exist_ok=True)
    output_path = os.path.join(out_dir, "activity_time_comparison_minutes.png")
    plt.savefig(output_path, dpi=300)
    print(f"  Figure saved to {output_path}")


if __name__ == "__main__":
    parser = get_csv_and_out_parser("Generate activities daily avg minutes plot", "--comparison-csv")
    args = parser.parse_args()

    generate_activity_time_comparison_plot(args.comparison_csv, args.out_dir)
