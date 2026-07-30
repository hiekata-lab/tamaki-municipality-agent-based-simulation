import argparse
import os
import pandas as pd
from src.constants import (
    COL_ACTIVITY,
    COL_AGE_GROUP,
    COL_DAYS_SIMULATED,
    COL_DAY_OF_WEEK_EN,
    COL_DURATION,
    COL_HEALTH,
    COL_NORMALIZED_DURATION,
    COL_SCENARIO,
    COL_SE_RATIO_FRACTION,
    COL_SEX_EN,
    COL_SIM_ACTIVITY,
    COL_SIMULATION,
    COL_SIMULATION_UUID,
    COL_VALIDATION_VALUE,
    VALIDATION_ACTIVITIES,
)
from src.post_simulation.tables.utils import (
    calculate_combined_standard_error,
    calculate_confidence_interval,
    calculate_margin_of_error,
    calculate_standard_error,
    load_aggregated_simulation_data,
    save_table_csv,
)


def generate_comparison_table(
    sim_dir: str, validation_path: str, se_ratios_path: str, out_dir: str
) -> None:
    df = load_aggregated_simulation_data(sim_dir)
    df = df[df[COL_SCENARIO] == "Scenario 2"].copy()

    df_act = (
        df.dropna(subset=[COL_SIM_ACTIVITY])
        .groupby([COL_SIMULATION_UUID, COL_DAYS_SIMULATED, COL_SIM_ACTIVITY])[
            COL_DURATION
        ]
        .sum()
        .reset_index()
    )
    df_act[COL_NORMALIZED_DURATION] = df_act[COL_DURATION] / df_act[COL_DAYS_SIMULATED]

    df_meta = df[[COL_SIMULATION_UUID, COL_SCENARIO]].drop_duplicates()
    activities_df = pd.DataFrame({COL_SIM_ACTIVITY: VALIDATION_ACTIVITIES})

    df_full = pd.merge(
        df_meta.merge(activities_df, how="cross"),
        df_act,
        on=[COL_SIMULATION_UUID, COL_SIM_ACTIVITY],
        how="left",
    ).fillna({COL_NORMALIZED_DURATION: 0})

    df_sim_stats = (
        df_full.groupby([COL_SCENARIO, COL_SIM_ACTIVITY])[COL_NORMALIZED_DURATION]
        .agg(["mean", "std", "count"])
        .reset_index()
        .rename(columns={COL_SIM_ACTIVITY: COL_ACTIVITY, "mean": COL_SIMULATION})
    )
    df_sim_stats["se_sim"] = calculate_standard_error(
        std=df_sim_stats["std"], count=df_sim_stats["count"]
    )

    df_val = pd.read_csv(validation_path)
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
        .groupby([COL_DAY_OF_WEEK_EN, COL_ACTIVITY])[COL_VALIDATION_VALUE]
        .mean()
        .reset_index()
    )

    df_merged = pd.merge(
        df_sim_stats,
        df_val_filtered,
        on=COL_ACTIVITY,
        how="outer",
    )

    df_merged[COL_SCENARIO] = df_merged[COL_SCENARIO].fillna("Scenario 2")
    df_merged[COL_DAY_OF_WEEK_EN] = df_merged[COL_DAY_OF_WEEK_EN].fillna("Weekday")
    df_merged[COL_SIMULATION] = df_merged[COL_SIMULATION].fillna(0)
    df_merged["std"] = df_merged["std"].fillna(0)
    df_merged["count"] = df_merged["count"].fillna(0)
    df_merged["se_sim"] = df_merged["se_sim"].fillna(0)
    df_merged[COL_VALIDATION_VALUE] = df_merged[COL_VALIDATION_VALUE].fillna(0)

    se_ratios = (
        pd.read_csv(se_ratios_path)
        .set_index([COL_SEX_EN, COL_ACTIVITY])[COL_SE_RATIO_FRACTION]
        .to_dict()
    )
    se_ratio_col = df_merged[COL_ACTIVITY].map(
        lambda act: se_ratios.get(("Both sexes", act), 0.0)
    )
    se_val = se_ratio_col * df_merged[COL_VALIDATION_VALUE]

    df_merged["se_combined"] = calculate_combined_standard_error(
        se1=se_val, se2=df_merged["se_sim"]
    )

    val_mean = df_merged[COL_VALIDATION_VALUE]
    count = df_merged["count"].replace(0, 1)

    df_merged["CI_90_Lower"], df_merged["CI_90_Upper"] = (
        calculate_confidence_interval(
            mean=val_mean,
            se=df_merged["se_combined"],
            count=count,
            confidence_level=0.90,
        )
    )
    df_merged["CI_95_Lower"], df_merged["CI_95_Upper"] = (
        calculate_confidence_interval(
            mean=val_mean,
            se=df_merged["se_combined"],
            count=count,
            confidence_level=0.95,
        )
    )

    df_merged["CI_90_Sim"] = calculate_margin_of_error(
        se=df_merged["se_sim"], count=count, confidence_level=0.90
    )
    df_merged["CI_95_Sim"] = calculate_margin_of_error(
        se=df_merged["se_sim"], count=count, confidence_level=0.95
    )

    df_merged = df_merged.fillna(0)
    df_merged = df_merged.sort_values(
        by=[COL_SCENARIO, COL_DAY_OF_WEEK_EN, COL_ACTIVITY]
    ).reset_index(drop=True)

    path = os.path.join(out_dir, "results_activities_average_comparison_minutes.csv")
    save_table_csv(df_merged, path, index=False)


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
