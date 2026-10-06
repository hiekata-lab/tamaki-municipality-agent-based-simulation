import argparse
import os
import pandas as pd
from src.constants import (
    COL_ACTIVITY,
    COL_AGE_GROUP,
    COL_AGENT_UUID,
    COL_DURATION,
    COL_HEALTH,
    COL_NORMALIZED_DURATION,
    COL_SCENARIO,
    COL_SEX_EN,
    COL_SIM_ACTIVITY,
    COL_SIMULATION_UUID,
    TRANSPORTATION_MODES,
    VALIDATION_ACTIVITIES,
)
from src.post_simulation.tables.utils import (
    clip_to_first_day_duration,
    export_grouped_pivot_table,
    load_aggregated_simulation_data,
)

DEMOGRAPHIC_COLS = [COL_SCENARIO, COL_AGE_GROUP, COL_SEX_EN, COL_HEALTH]


def generate_std_table(sim_dir: str, out_dir: str) -> None:
    df = load_aggregated_simulation_data(sim_dir)

    # Harmonize normalization with average table: map transit modes and Arriving to Moving
    transit_mask = (
        df[COL_SIM_ACTIVITY].isin(TRANSPORTATION_MODES)
        | df[COL_SIM_ACTIVITY].str.startswith(
            ("Riding", "Walking", "Driving"), na=False
        )
        | (df[COL_SIM_ACTIVITY] == "Arriving")
    )
    df.loc[transit_mask, COL_SIM_ACTIVITY] = "Moving"

    # Harmonize normalization: clip to first 24-hour cycle per agent
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

    df_meta = df[
        [
            COL_SIMULATION_UUID,
            COL_AGENT_UUID,
            COL_SCENARIO,
            COL_AGE_GROUP,
            COL_SEX_EN,
            COL_HEALTH,
        ]
    ].drop_duplicates()

    activities_df = pd.DataFrame({COL_SIM_ACTIVITY: sim_activities})
    df_full = pd.merge(
        df_meta.merge(activities_df, how="cross"),
        df_act,
        on=[COL_SIMULATION_UUID, COL_SIM_ACTIVITY],
        how="left",
    ).fillna({COL_NORMALIZED_DURATION: 0})

    out_file = os.path.join(out_dir, "results_activities_std_minutes.csv")
    export_grouped_pivot_table(
        df=df_full,
        group_cols=DEMOGRAPHIC_COLS,
        val_col=COL_NORMALIZED_DURATION,
        agg_func="std",
        output_path=out_file,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate activities daily std minutes table"
    )
    parser.add_argument(
        "--sim-dir", type=str, default=".", help="Path to simulation dir"
    )
    parser.add_argument(
        "--out-dir", type=str, default="tables", help="Output directory for tables"
    )
    args = parser.parse_args()
    generate_std_table(args.sim_dir, args.out_dir)
