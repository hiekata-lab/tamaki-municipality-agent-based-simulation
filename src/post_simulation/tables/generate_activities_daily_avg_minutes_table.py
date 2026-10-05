import argparse
import os
import numpy as np
import pandas as pd

from src.constants import (
    COL_ACTIVITY,
    COL_AGE_GROUP,
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
    COL_VALIDATION_VALUE,
    SURVEY_MIE_TOTAL_SAMPLE_SIZE,
    TRANSPORTATION_MODES,
    VALIDATION_ACTIVITIES,
)
from src.post_simulation.tables.utils import (
    calculate_combined_standard_error,
    calculate_confidence_interval,
    calculate_margin_of_error,
    calculate_p_value,
    calculate_standard_error,
    calculate_welch_satterthwaite_dof,
    calculate_welch_t_statistic,
    load_aggregated_simulation_data,
    save_table_csv,
)


def clip_to_first_day_duration(df: pd.DataFrame) -> pd.DataFrame:
    """Clips simulation activities to the first 24-hour cycle per agent."""
    t_start = df.groupby(COL_SIMULATION_UUID)[COL_STARTING_TIME].transform("min")
    t_end = t_start + pd.Timedelta(hours=24)
    in_window = (df[COL_END_TIME] > t_start) & (df[COL_STARTING_TIME] < t_end)
    df_window = df[in_window].copy()
    clipped_start = df_window[COL_STARTING_TIME].clip(lower=t_start[in_window])
    clipped_end = df_window[COL_END_TIME].clip(upper=t_end[in_window])
    df_window[COL_DURATION] = (clipped_end - clipped_start).dt.total_seconds() / 60.0
    return df_window


def generate_comparison_table(
    sim_dir: str,
    validation_path: str,
    se_ratios_path: str,
    sample_size_path: str,
    out_dir: str,
) -> None:
    df = load_aggregated_simulation_data(sim_dir)
    df = df[df[COL_SCENARIO] == "Scenario 2"].copy()

    transit_mask = df[COL_SIM_ACTIVITY].isin(TRANSPORTATION_MODES) | df[
        COL_SIM_ACTIVITY
    ].str.startswith(("Riding", "Walking", "Driving"), na=False)
    df.loc[transit_mask, COL_SIM_ACTIVITY] = "Moving"

    df_24h = clip_to_first_day_duration(df)

    df_act = (
        df_24h.dropna(subset=[COL_SIM_ACTIVITY])
        .groupby([COL_SIMULATION_UUID, COL_SIM_ACTIVITY])[COL_DURATION]
        .sum()
        .reset_index()
    )
    df_act[COL_NORMALIZED_DURATION] = df_act[COL_DURATION]

    sim_activities = [
        act
        for act in VALIDATION_ACTIVITIES
        if act not in TRANSPORTATION_MODES
        and not act.startswith(("Riding", "Walking", "Driving"))
    ]
    if "Moving" not in sim_activities:
        sim_activities.append("Moving")

    df_meta = df[[COL_SIMULATION_UUID, COL_SCENARIO]].drop_duplicates()
    activities_df = pd.DataFrame({COL_SIM_ACTIVITY: sim_activities})

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
    df_val[COL_ACTIVITY] = df_val[COL_ACTIVITY].replace(
        {"Moving (excluding commuting)": "Moving"}
    )
    df_val_filtered = (
        df_val[
            (df_val[COL_SEX_EN] == "Both sexes")
            & (df_val[COL_HEALTH] == "Total")
            & (
                df_val[COL_AGE_GROUP].isin(
                    ["65 to 74 years old", "75 years old and over"]
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
        how="inner",
    )

    df_merged[COL_SCENARIO] = df_merged[COL_SCENARIO].fillna("Scenario 2")
    df_merged[COL_DAY_OF_WEEK_EN] = df_merged[COL_DAY_OF_WEEK_EN].fillna(
        "Weekly average"
    )
    df_merged[COL_SIMULATION] = df_merged[COL_SIMULATION].fillna(0)
    df_merged["std"] = df_merged["std"].fillna(0)
    df_merged["count"] = df_merged["count"].fillna(0)
    df_merged["se_sim"] = df_merged["se_sim"].fillna(0)
    df_merged[COL_VALIDATION_VALUE] = df_merged[COL_VALIDATION_VALUE].fillna(0)

    se_df = pd.read_csv(se_ratios_path)
    se_df[COL_ACTIVITY] = se_df[COL_ACTIVITY].replace(
        {"Moving (excluding commuting)": "Moving"}
    )
    se_ratios = se_df.set_index([COL_SEX_EN, COL_ACTIVITY])[
        COL_SE_RATIO_FRACTION
    ].to_dict()
    se_ratio_col = df_merged[COL_ACTIVITY].map(
        lambda act: se_ratios.get(("Both sexes", act), 0.0)
    )
    df_sample_size = pd.read_csv(sample_size_path)
    count_val = int(df_sample_size["sample_size"].iloc[0])
    subgroup_scale = np.sqrt(SURVEY_MIE_TOTAL_SAMPLE_SIZE / count_val)
    se_val = se_ratio_col * df_merged[COL_VALIDATION_VALUE] * subgroup_scale
    df_merged["count_val"] = count_val
    df_merged["se_val"] = se_val

    df_merged["se_combined"] = calculate_combined_standard_error(
        se1=se_val, se2=df_merged["se_sim"]
    )

    dof_welch = calculate_welch_satterthwaite_dof(
        se1=se_val,
        count1=count_val,
        se2=df_merged["se_sim"],
        count2=df_merged["count"],
    )
    df_merged["dof_welch"] = dof_welch

    val_mean = df_merged[COL_VALIDATION_VALUE]
    dof_val = np.maximum(1.0, float(count_val) - 1.0)
    dof_sim = np.maximum(1.0, df_merged["count"] - 1.0)

    df_merged["CI_90_Lower"], df_merged["CI_90_Upper"] = calculate_confidence_interval(
        mean=val_mean,
        se=se_val,
        dof=dof_val,
        confidence_level=0.90,
    )
    df_merged["CI_95_Lower"], df_merged["CI_95_Upper"] = calculate_confidence_interval(
        mean=val_mean,
        se=se_val,
        dof=dof_val,
        confidence_level=0.95,
    )

    df_merged["CI_90_Sim"] = calculate_margin_of_error(
        se=df_merged["se_sim"], dof=dof_sim, confidence_level=0.90
    )
    df_merged["CI_95_Sim"] = calculate_margin_of_error(
        se=df_merged["se_sim"], dof=dof_sim, confidence_level=0.95
    )

    t_stat = calculate_welch_t_statistic(
        mean1=df_merged[COL_SIMULATION],
        mean2=val_mean,
        se_combined=df_merged["se_combined"],
    )
    df_merged["t_stat"] = t_stat
    df_merged["p_val"] = calculate_p_value(
        t_stat=t_stat,
        dof=dof_welch,
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
    validation_path = "data/processed/Average time spent in activities for all persons by Kind of activities, Day of the week, Area classification, Sex, Usual economic activity, Usual state of health, Age (15 Years Old and Over)-Japan, Prefectures.csv"
    se_ratios_path = "data/processed/Standard Error Ratios of Average time spent in activities for all persons by Sex, Kind of activities - Weekly average, Japan, Prefectures.csv"
    sample_size_path = "data/processed/survey_sample_size.csv"
    generate_comparison_table(
        args.sim_dir,
        validation_path,
        se_ratios_path,
        sample_size_path,
        args.out_dir,
    )
