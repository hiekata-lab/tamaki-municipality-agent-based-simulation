import argparse
import os
import pandas as pd
import numpy as np
import scipy.stats as stats
from src.constants import (
    COL_ACTIVITY,
    COL_AGE,
    COL_DAY_OF_WEEK_EN,
    COL_HEALTH,
    COL_SCENARIO,
    COL_SEX_EN,
    COL_SIMULATION,
    COL_VALIDATION,
    SIM_TO_ACTIVITY_MAPPING,
)


def generate_comparison_table(sim_dir, validation_path, se_ratios_path, out_dir):
    os.makedirs(out_dir, exist_ok=True)

    # 1. Load Simulation Data
    csv_path = os.path.join(sim_dir, "aggregated.csv")
    df = pd.read_csv(csv_path, parse_dates=["starting_time", "end_time"])

    # Filter and group activities
    df["mapped_act"] = df["activity"].map(SIM_TO_ACTIVITY_MAPPING)
    df_act = (
        df.dropna(subset=["mapped_act"])
        .groupby(["unique_simulation_id", "mapped_act"])["duration"]
        .sum()
        .reset_index()
    )

    # Normalize to daily average
    # days_simulated is already joined in load_and_preprocess_simulation_data
    df_act = pd.merge(
        df_act,
        df[["unique_simulation_id", "days_simulated"]].drop_duplicates(),
        on="unique_simulation_id",
        how="left",
    )
    df_act["duration"] /= df_act["days_simulated"]

    # 2. Extract Demographics
    df_meta = df[
        ["unique_simulation_id", COL_SCENARIO, COL_AGE, COL_SEX_EN, COL_HEALTH]
    ].drop_duplicates()

    # Cross demographics with all activities (fill 0 for missing activities)
    df_full = pd.merge(df_meta, df_act, on="unique_simulation_id", how="left")
    df_full = df_full.pivot_table(
        index=["unique_simulation_id", COL_SCENARIO, COL_AGE, COL_SEX_EN, COL_HEALTH],
        columns="mapped_act",
        values="duration",
        fill_value=0,
    ).reset_index()

    # Melt and average across demographics
    df_melt = pd.melt(
        df_full,
        id_vars=["unique_simulation_id", COL_SCENARIO, COL_AGE, COL_SEX_EN, COL_HEALTH],
        value_vars=[
            c for c in SIM_TO_ACTIVITY_MAPPING.values() if c in df_full.columns
        ],
        var_name=COL_ACTIVITY,
        value_name="duration",
    )
    df_sim_stats = (
        df_melt.groupby([COL_SCENARIO, COL_AGE, COL_SEX_EN, COL_HEALTH, COL_ACTIVITY])[
            "duration"
        ]
        .agg(["mean", "std", "count"])
        .reset_index()
    )
    df_sim_stats["se_sim"] = df_sim_stats["std"] / np.sqrt(df_sim_stats["count"])
    df_sim_stats["se_sim"] = df_sim_stats["se_sim"].fillna(0)
    df_sim_avg = df_sim_stats.rename(columns={"mean": COL_SIMULATION})

    # 3. Load Validation Data & SE Ratios
    df_val = pd.read_csv(validation_path)
    se_ratios = (
        pd.read_csv(se_ratios_path)
        .set_index(["Sex", "Activity"])["SE_Ratio_Fraction"]
        .to_dict()
    )

    scenarios = pd.DataFrame({COL_SCENARIO: df_sim_avg[COL_SCENARIO].unique()})
    day_types = pd.DataFrame({COL_DAY_OF_WEEK_EN: df_val[COL_DAY_OF_WEEK_EN].unique()})

    df_sim_avg = df_sim_avg.merge(day_types, how="cross")
    df_val = df_val.merge(scenarios, how="cross")

    df_merged = pd.merge(
        df_sim_avg,
        df_val,
        on=[
            COL_SCENARIO,
            COL_DAY_OF_WEEK_EN,
            COL_AGE,
            COL_SEX_EN,
            COL_HEALTH,
            COL_ACTIVITY,
        ],
        how="outer",
    )

    # 4. Calculate Confidence Intervals (Vectorized)
    def get_se(row):
        return se_ratios.get(
            (row[COL_SEX_EN], row[COL_ACTIVITY]),
            se_ratios.get(("Both sexes", row[COL_ACTIVITY]), np.nan),
        )

    se_ratio_col = df_merged.apply(get_se, axis=1)
    se_abs = se_ratio_col * df_merged[COL_VALIDATION]

    df_merged["se_combined"] = np.sqrt(se_abs**2 + df_merged["se_sim"] ** 2)

    # Calculate degrees of freedom based on simulation sample count
    dof = (df_merged["count"] - 1).clip(lower=1)

    t_90 = stats.t.ppf(0.95, dof)
    t_95 = stats.t.ppf(0.975, dof)

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

    # 5. Pivot and Save
    val_cols = [
        COL_SIMULATION,
        COL_VALIDATION,
        "CI_90_Lower",
        "CI_90_Upper",
        "CI_95_Lower",
        "CI_95_Upper",
    ]
    df_pivot = df_merged.pivot_table(
        index=[COL_SCENARIO, COL_DAY_OF_WEEK_EN, COL_AGE, COL_SEX_EN, COL_HEALTH],
        columns=COL_ACTIVITY,
        values=val_cols,
    ).swaplevel(axis=1)

    # Order columns
    activities_sorted = sorted(df_merged[COL_ACTIVITY].dropna().unique())
    ordered_cols = [(act, src) for act in activities_sorted for src in val_cols]
    df_pivot = df_pivot.reindex(columns=ordered_cols)

    path = os.path.join(out_dir, "results_activities_average_comparison_minutes.csv")
    df_pivot.to_csv(path)
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
