import argparse
import os
import pandas as pd
import numpy as np
import scipy.stats as stats
from src.constants import (
    COL_ACTIVITY,
    COL_AGE_GROUP,
    COL_AGENT_UUID,
    COL_DAYS_SIMULATED,
    COL_DAY_OF_WEEK_EN,
    COL_DURATION,
    COL_END_TIME,
    COL_HEALTH,
    COL_NORMALIZED_DURATION,
    COL_SCENARIO,
    COL_SE_RATIO_FRACTION,
    COL_SEX_EN,
    COL_SIM_ACTIVITY,
    COL_SIMULATION,
    COL_SIMULATION_UUID,
    COL_STARTING_TIME,
    COL_VALIDATION,
    VALIDATION_ACTIVITIES,
)


def generate_comparison_table(sim_dir, validation_path, se_ratios_path, out_dir):
    os.makedirs(out_dir, exist_ok=True)

    # Load Simulation Data
    csv_path = os.path.join(sim_dir, "aggregated.csv")
    df = pd.read_csv(csv_path, parse_dates=[COL_STARTING_TIME, COL_END_TIME])

    # Only select Scenario 2
    df = df[df[COL_SCENARIO] == "Scenario 2"].copy()

    # Sum the total amount of time spent by each agent on each activity
    df_act = (
        df.dropna(subset=[COL_SIM_ACTIVITY])
        .groupby([COL_SIMULATION_UUID, COL_DAYS_SIMULATED, COL_SIM_ACTIVITY])[
            COL_DURATION
        ]
        .sum()
        .reset_index()
    )

    # Normalize the duration by dividing it by the total days simulated
    df_act[COL_NORMALIZED_DURATION] = df_act[COL_DURATION] / df_act[COL_DAYS_SIMULATED]

    # Extract unique simulation runs and scenario metadata
    df_meta = df[[COL_SIMULATION_UUID, COL_SCENARIO]].drop_duplicates()

    # Cross join unique simulation runs with all possible activities
    activities_df = pd.DataFrame({COL_SIM_ACTIVITY: VALIDATION_ACTIVITIES})
    df_full = pd.merge(
        df_meta.merge(activities_df, how="cross"),
        df_act,
        on=[COL_SIMULATION_UUID, COL_SIM_ACTIVITY],
        how="left",
    ).fillna({COL_NORMALIZED_DURATION: 0})

    # Group by Scenario and Activity to calculate overall simulation average across all agents
    df_sim_stats = (
        df_full.groupby([COL_SCENARIO, COL_SIM_ACTIVITY])[COL_NORMALIZED_DURATION]
        .agg(["mean", "std", "count"])
        .reset_index()
        .rename(columns={COL_SIM_ACTIVITY: COL_ACTIVITY, "mean": COL_SIMULATION})
    )
    df_sim_stats["se_sim"] = df_sim_stats["std"] / np.sqrt(df_sim_stats["count"])
    df_sim_stats["se_sim"] = df_sim_stats["se_sim"].fillna(0)

    # Load Validation Data & SE Ratios for overall 65+ non-working population
    df_val = pd.read_csv(validation_path)

    # Filter validation dataset for total 65+ non-working population (Both sexes, Total health)
    df_val_filtered = (
        df_val[
            (df_val[COL_SEX_EN] == "Both sexes")
            & (df_val[COL_HEALTH] == "Total")
            & (
                df_val[COL_AGE_GROUP].isin(
                    ["65 to 74 years old", "75 years old and over", "Total"]
                )
            )
        ]
        .groupby([COL_DAY_OF_WEEK_EN, COL_ACTIVITY])[COL_VALIDATION]
        .mean()
        .reset_index()
    )

    # Merge simulation stats and validation data on activity
    df_merged = pd.merge(
        df_sim_stats,
        df_val_filtered,
        on=COL_ACTIVITY,
        how="outer",
    )

    # Load in Standard error ratios
    se_ratios = (
        pd.read_csv(se_ratios_path)
        .set_index([COL_SEX_EN, COL_ACTIVITY])[COL_SE_RATIO_FRACTION]
        .to_dict()
    )

    # Get the SE ratios
    se_ratio_col = df_merged[COL_ACTIVITY].map(
        lambda act: se_ratios.get(("Both sexes", act), 0.0)
    )

    # Create the SE values in absolute terms
    se_abs = se_ratio_col * df_merged[COL_VALIDATION]

    # Since the simulation data and survey data are independent sources of variance
    # (the simulation is merely conditioned on demographic data from the same region)
    # we can combine them using the root sum of squares formula
    df_merged["se_combined"] = np.sqrt(se_abs**2 + df_merged["se_sim"] ** 2)

    # Calculate degrees of freedom based on simulation sample count
    dof = (df_merged["count"] - 1).clip(lower=1)

    # Get t value for 0.95 and 0.975 (corresponding to 90% and 95% CIs)
    t_90 = stats.t.ppf(0.95, dof)
    t_95 = stats.t.ppf(0.975, dof)

    # Calculate the confidence intervals
    df_merged["CI_90_Lower"] = (
        df_merged[COL_VALIDATION] - t_90 * df_merged["se_combined"]
    )
    df_merged["CI_90_Upper"] = (
        df_merged[COL_VALIDATION] + t_90 * df_merged["se_combined"]
    )
    df_merged["CI_95_Lower"] = (
        df_merged[COL_VALIDATION] - t_95 * df_merged["se_combined"]
    )
    df_merged["CI_95_Upper"] = (
        df_merged[COL_VALIDATION] + t_95 * df_merged["se_combined"]
    )

    # Sort the DataFrame for better readability
    df_merged = df_merged.sort_values(
        by=[COL_SCENARIO, COL_DAY_OF_WEEK_EN, COL_ACTIVITY]
    ).reset_index(drop=True)

    path = os.path.join(out_dir, "results_activities_average_comparison_minutes.csv")
    df_merged.to_csv(path, index=False)
    print(f"  Saved {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate activities daily avg minutes table"
    )
    parser.add_argument(
        "--sim-dir", type=str, default=".", help="Path to simulation dir"
    )
    parser.add_argument(
        "--out-dir", type=str, default="tables", help="Output directory for tables"
    )
    args = parser.parse_args()

    validation_path = "data/processed/Average time spent in activities for participants by Kind of activities, Day of the week, Area classification, Sex, Usual economic activity, Usual state of health, Age (15 Years Old and Over)-Japan, Prefectures.csv"
    se_ratios_path = "data/processed/Standard Error Ratios of Average time spent in activities for all persons by Sex, Kind of activities - Weekly average, Japan, Prefectures.csv"

    generate_comparison_table(
        args.sim_dir, validation_path, se_ratios_path, args.out_dir
    )
