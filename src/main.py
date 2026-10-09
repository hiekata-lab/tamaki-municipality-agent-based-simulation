import subprocess
import sys
import os
import argparse


def run_script(script_path, args=None):
    print(f"Running {script_path}...", flush=True)
    # Create command
    cmd = [sys.executable, script_path] + args or []
    # Copy environment variables
    env = os.environ.copy()
    # Set the project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    # If there is a pythonpath in env replace it otherwise dont
    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = f"{project_root}:{env['PYTHONPATH']}"
    else:
        env["PYTHONPATH"] = project_root
    #
    result = subprocess.run(cmd, check=True, env=env)
    return result


# Script Paths
PREPROCESS_VALIDATION_DATA_SCRIPT = "src/pre_simulation/preprocess_validation_data.py"
PREPROCESS_QUESTIONNAIRE_A_SCRIPT = "src/pre_simulation/preprocess_questionnaire_a.py"
PREPROCESS_SE_RATIOS_SCRIPT = "src/pre_simulation/preprocess_se_ratios.py"
PREPROCESS_SURVEY_SAMPLE_SIZE_SCRIPT = (
    "src/pre_simulation/preprocess_survey_sample_size.py"
)
GENERATE_LOCATION_GRAPH_SCRIPT = "src/pre_simulation/generate_location_graph.py"
SAMPLE_AGENT_SET_SCRIPT = "src/pre_simulation/sample_agent_set.py"
SIMULATION_SCRIPT = "src/simulation/simulation.py"
AGGREGATE_SIMULATION_RESULTS_SCRIPT = (
    "src/post_simulation/aggregate_simulation_results.py"
)
PREPROCESS_AGGREGATED_DATA_SCRIPT = "src/post_simulation/preprocess_aggregated_data.py"
GENERATE_ACTIVITIES_DAILY_AVG_MINUTES_TABLE_SCRIPT = (
    "src/post_simulation/tables/generate_activities_daily_avg_minutes_table.py"
)
GENERATE_ACTIVITIES_DAILY_STD_MINUTES_TABLE_SCRIPT = (
    "src/post_simulation/tables/generate_activities_daily_std_minutes_table.py"
)
GENERATE_ACTIVITIES_DAILY_MAJORITY_SCHEDULE_TABLE_SCRIPT = (
    "src/post_simulation/tables/generate_activities_daily_majority_schedule_table.py"
)
GENERATE_TRANSPORT_MODE_TRIPS_TOTAL_COUNT_TABLE_SCRIPT = (
    "src/post_simulation/tables/generate_transport_mode_trips_total_count_table.py"
)
GENERATE_TRANSPORT_MODE_TOTAL_KM_DIST_TABLE_SCRIPT = (
    "src/post_simulation/tables/generate_transport_mode_total_km_dist_table.py"
)
GENERATE_AGENT_TRIPS_TABLE_SCRIPT = (
    "src/post_simulation/tables/generate_agent_trips_table.py"
)
GENERATE_AGENT_LOCATION_TIME_TABLE_SCRIPT = (
    "src/post_simulation/tables/generate_agent_location_time_table.py"
)
GENERATE_AVG_DAYS_SIMULATED_TABLE_SCRIPT = (
    "src/post_simulation/tables/generate_avg_days_simulated_table.py"
)
GENERATE_ACTIVITIES_DAILY_AVG_MINUTES_PLOT_SCRIPT = (
    "src/post_simulation/figures/generate_activities_daily_avg_minutes_plot.py"
)
GENERATE_ACTIVITIES_DAILY_MAJORITY_SCHEDULE_PLOT_SCRIPT = (
    "src/post_simulation/figures/generate_activities_daily_majority_schedule_plot.py"
)
GENERATE_TRANSPORT_MODE_TOTAL_DISTANCE_AND_TRIPS_PLOT_SCRIPT = (
    "src/post_simulation/figures/generate_transport_mode_total_distance_and_trips_plot.py"
)
GENERATE_AGENT_LOCATION_TIME_TRIP_MAP_SCRIPT = (
    "src/post_simulation/figures/generate_agent_location_time_trip_map.py"
)


def main():
    # Create a CLI arg parser
    parser = argparse.ArgumentParser(
        description="Run the Tamaki Town Agent-Based Simulation full experiment"
    )

    # Add arguments for running different stages of the simulation pipeline
    parser.add_argument(
        "--stages",
        nargs="+",
        choices=["pre_sim", "sim", "post_sim"],
        default=["pre_sim", "sim", "post_sim"],
    )

    # Parse arguments
    args = parser.parse_args()

    # Print arguments
    print(f"Starting full experiment replication. Stages: {args.stages}", flush=True)

    # Pre-sim Paths
    VAL_DIR = (
        "data/raw/70-1-2 Average time spent in activities for all persons by Kind of "
        "activities, Day of the week, Area classification, Sex, Usual economic activity, "
        "Usual state of health, Age (15 Years Old and Over)-Japan, Prefectures.csv"
    )
    QA_DIR = (
        "data/raw/Appendix Table A Number of Sample EDs, Households and Persons "
        "by Prefectures (Questionnaire A).csv"
    )
    SE_FILE = (
        "data/raw/13 Standard Error Ratios of Average time spent in activities for "
        "all persons by Sex, Kind of activities - Weekly average, Japan, Prefectures.csv"
    )
    SAMPLE_SIZE_RAW_FILE = (
        "data/raw/70-1-1 Average time spent in activities for all persons by Kind of "
        "activities, Day of the week, Area classification, Sex, Usual economic activity, "
        "Usual state of health, Age (15 Years Old and Over)-Japan, Prefectures.csv"
    )
    PRO_DIR = "data/processed"
    GEO_FILE = "data/raw/Tamaki-Town-Locations-EPSG32654-km-scale.csv"
    LOCG_FILE = "data/processed/locations_graph.json"
    AGN_FILE = "data/processed/agents.csv"

    # Make dirs for results
    os.makedirs("simulation_results", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)

    # Executes pre simulation steps
    # Preprocesses validation data, SE ratios, generates location graphs, and samples agents.
    if "pre_sim" in args.stages:
        print("\n--- Running Pre-Simulation ---", flush=True)
        run_script(
            PREPROCESS_VALIDATION_DATA_SCRIPT,
            ["--in-path", VAL_DIR, "--out-path", PRO_DIR],
        )

        run_script(
            PREPROCESS_QUESTIONNAIRE_A_SCRIPT,
            ["--in-path", QA_DIR, "--out-path", PRO_DIR],
        )

        run_script(
            PREPROCESS_SE_RATIOS_SCRIPT,
            ["--in-path", SE_FILE, "--out-path", PRO_DIR],
        )

        sample_size_args = ["--out-path", PRO_DIR]
        if os.path.exists(SAMPLE_SIZE_RAW_FILE):
            sample_size_args.extend(["--in-path", SAMPLE_SIZE_RAW_FILE])

        run_script(
            PREPROCESS_SURVEY_SAMPLE_SIZE_SCRIPT,
            sample_size_args,
        )

        run_script(
            GENERATE_LOCATION_GRAPH_SCRIPT,
            [
                "--input",
                GEO_FILE,
                "--output",
                LOCG_FILE,
                "--connections",
                "300",
            ],
        )
        run_script(
            SAMPLE_AGENT_SET_SCRIPT,
            ["--num-agents", "100", "--output", AGN_FILE],
        )

    # Exectues the simulation and post simulation steps
    # Runs the actual simulation, aggregates the individual simulations results, produces output tables and figures.
    if "sim" in args.stages or "post_sim" in args.stages:
        for model_id in ["minimax.minimax-m2.5", "zai.glm-5"]:
            print(f"\n--- Processing model: {model_id} ---", flush=True)

            # Sim-step and post-sim paths
            raw_dir = f"simulation_results/{model_id}/raw"
            agg_dir = f"simulation_results/{model_id}/aggregated"
            tab_dir = f"simulation_results/{model_id}/tables"
            fig_dir = f"simulation_results/{model_id}/figs"
            locations_path = "data/processed/locations_graph.json"
            agents_path = "data/processed/agents.csv"
            comp_csv = os.path.join(
                tab_dir, "results_activities_average_comparison_minutes.csv"
            )
            sched_csv = os.path.join(tab_dir, "results_activities_daily_schedule.csv")
            t_trips_tot_csv = os.path.join(
                tab_dir, "results_transport_mode_trips_total_count.csv"
            )
            t_dist_tot_csv = os.path.join(
                tab_dir, "results_transport_mode_total_km_dist.csv"
            )
            trip_csv = os.path.join(tab_dir, "results_agent_trips.csv")
            time_csv = os.path.join(tab_dir, "results_agent_location_time.csv")

            # Make dirs for results
            os.makedirs(raw_dir, exist_ok=True)
            os.makedirs(agg_dir, exist_ok=True)
            os.makedirs(tab_dir, exist_ok=True)
            os.makedirs(fig_dir, exist_ok=True)

            # Executes the simulation step
            if "sim" in args.stages:
                run_script(
                    SIMULATION_SCRIPT,
                    [
                        "--output-dir",
                        raw_dir,
                        "--locations",
                        locations_path,
                        "--agents",
                        agents_path,
                        "--temperature",
                        "0.0",
                        "--model-id",
                        model_id,
                        "--transitions",
                        "100",
                    ],
                )

            # Executes the post simulation step
            if "post_sim" in args.stages:
                run_script(
                    AGGREGATE_SIMULATION_RESULTS_SCRIPT,
                    ["--in-dir", raw_dir, "--out-dir", agg_dir],
                )
                run_script(
                    PREPROCESS_AGGREGATED_DATA_SCRIPT,
                    ["--in-dir", agg_dir, "--out-dir", agg_dir],
                )

                # Executes all the Table generation scripts
                run_script(
                    GENERATE_ACTIVITIES_DAILY_AVG_MINUTES_TABLE_SCRIPT,
                    ["--sim-dir", agg_dir, "--out-dir", tab_dir],
                )
                run_script(
                    GENERATE_ACTIVITIES_DAILY_STD_MINUTES_TABLE_SCRIPT,
                    ["--sim-dir", agg_dir, "--out-dir", tab_dir],
                )
                run_script(
                    GENERATE_ACTIVITIES_DAILY_MAJORITY_SCHEDULE_TABLE_SCRIPT,
                    ["--sim-dir", agg_dir, "--out-dir", tab_dir],
                )

                run_script(
                    GENERATE_TRANSPORT_MODE_TOTAL_KM_DIST_TABLE_SCRIPT,
                    ["--sim-dir", agg_dir, "--out-dir", tab_dir],
                )
                run_script(
                    GENERATE_AGENT_TRIPS_TABLE_SCRIPT,
                    ["--sim-dir", agg_dir, "--out-dir", tab_dir],
                )
                run_script(
                    GENERATE_AGENT_LOCATION_TIME_TABLE_SCRIPT,
                    ["--sim-dir", agg_dir, "--out-dir", tab_dir],
                )
                run_script(
                    GENERATE_AVG_DAYS_SIMULATED_TABLE_SCRIPT,
                    ["--sim-dir", agg_dir, "--out-dir", tab_dir],
                )

                # Exectues all the Figure generation scripts
                run_script(
                    GENERATE_ACTIVITIES_DAILY_AVG_MINUTES_PLOT_SCRIPT,
                    ["--comparison-csv", comp_csv, "--out-dir", fig_dir],
                )
                run_script(
                    GENERATE_ACTIVITIES_DAILY_MAJORITY_SCHEDULE_PLOT_SCRIPT,
                    ["--schedule-csv", sched_csv, "--out-dir", fig_dir],
                )
                run_script(
                    GENERATE_TRANSPORT_MODE_TOTAL_DISTANCE_AND_TRIPS_PLOT_SCRIPT,
                    [
                        "--distance-csv",
                        t_dist_tot_csv,
                        "--trips-csv",
                        t_trips_tot_csv,
                        "--out-dir",
                        fig_dir,
                    ],
                )
                run_script(
                    GENERATE_AGENT_LOCATION_TIME_TRIP_MAP_SCRIPT,
                    [
                        "--time-csv",
                        time_csv,
                        "--trip-csv",
                        trip_csv,
                        "--agents-csv",
                        agents_path,
                        "--out-dir",
                        fig_dir,
                    ],
                )

    print("Full experiment replication finished successfully.", flush=True)


if __name__ == "__main__":
    main()
