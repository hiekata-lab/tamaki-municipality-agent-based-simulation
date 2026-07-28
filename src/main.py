import subprocess
import sys
import os
import argparse


def run_script(script_path, args=None):
    if args is None:
        args = []
    print(f"Running {script_path}...", flush=True)
    cmd = [sys.executable, script_path] + args

    env = os.environ.copy()
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = f"{project_root}:{env['PYTHONPATH']}"
    else:
        env["PYTHONPATH"] = project_root

    result = subprocess.run(cmd, check=True, env=env)
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Run the Tamaki Town Agent-Based Simulation full experiment"
    )
    parser.add_argument(
        "--stages",
        nargs="+",
        choices=["pre_sim", "sim", "post_sim"],
        default=["pre_sim", "sim", "post_sim"],
    )
    args = parser.parse_args()

    print(f"Starting full experiment replication. Stages: {args.stages}", flush=True)
    os.makedirs("simulation_results", exist_ok=True)

    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)

    if "pre_sim" in args.stages:
        print("\n--- Running Pre-Simulation ---", flush=True)
        val_in = "data/raw/Average time spent in activities for participants by Kind of activities, Day of the week, Area classification, Sex, Usual economic activity, Usual state of health, Age (15 Years Old and Over)-Japan, Prefectures.csv"
        val_out = "data/processed/Average time spent in activities for participants by Kind of activities, Day of the week, Area classification, Sex, Usual economic activity, Usual state of health, Age (15 Years Old and Over)-Japan, Prefectures.csv"
        run_script(
            "src/pre_simulation/preprocess_validation_data.py",
            ["--in-path", val_in, "--out-path", val_out],
        )

        qa_in = "data/raw/Questionnaire A.csv"
        qa_out = "data/processed/Questionnaire A.csv"
        run_script(
            "src/pre_simulation/preprocess_questionnaire_a.py",
            ["--in-path", qa_in, "--out-path", qa_out],
        )

        se_in = "data/raw/Standard Error Ratios of Average time spent in activities for all persons by Sex, Kind of activities - Weekly average, Japan, Prefectures.csv"
        se_out = "data/processed/Standard Error Ratios of Average time spent in activities for all persons by Sex, Kind of activities - Weekly average, Japan, Prefectures.csv"
        run_script(
            "src/pre_simulation/preprocess_se_ratios.py",
            ["--in-path", se_in, "--out-path", se_out],
        )

        run_script(
            "src/pre_simulation/generate_location_graph.py",
            [
                "--input",
                "data/raw/Tamaki-Town-Locations-EPSG32654-km-scale.csv",
                "--output",
                "data/processed/locations_graph.json",
                "--connections",
                "300",
            ],
        )
        run_script(
            "src/pre_simulation/sample_agent_set.py",
            ["--num-agents", "100", "--output", "data/processed/agents.csv"],
        )

    if "sim" in args.stages or "post_sim" in args.stages:
        for model_id in ["minimax.minimax-m2.5", "zai.glm-5"]:

            print(f"\n--- Processing model: {model_id} ---", flush=True)

            raw_dir = f"simulation_results/{model_id}/raw"
            agg_dir = f"simulation_results/{model_id}/aggregated"
            tab_dir = f"simulation_results/{model_id}/tables"
            fig_dir = f"simulation_results/{model_id}/figs"

            os.makedirs(raw_dir, exist_ok=True)
            os.makedirs(agg_dir, exist_ok=True)
            os.makedirs(tab_dir, exist_ok=True)
            os.makedirs(fig_dir, exist_ok=True)

            if "sim" in args.stages:
                run_script(
                    "src/simulation/simulation.py",
                    [
                        "--output-dir",
                        raw_dir,
                        "--locations",
                        "data/processed/locations_graph.json",
                        "--travel-modes",
                        "data/raw/travel_modes.json",
                        "--activities",
                        "data/raw/activities.json",
                        "--agents",
                        "data/processed/agents.csv",
                        "--temperature",
                        "0.0",
                        "--model-id",
                        model_id,
                        "--transitions",
                        "100",
                    ],
                )

            if "post_sim" in args.stages:
                run_script(
                    "src/post_simulation/aggregate_simulation_results.py",
                    ["--results-dir", raw_dir, "--out-dir", agg_dir],
                )

                # Tables
                run_script(
                    "src/post_simulation/tables/generate_activities_daily_avg_minutes_table.py",
                    ["--sim-dir", agg_dir, "--out-dir", tab_dir],
                )
                run_script(
                    "src/post_simulation/tables/generate_activities_daily_std_minutes_table.py",
                    ["--sim-dir", agg_dir, "--out-dir", tab_dir],
                )
                run_script(
                    "src/post_simulation/tables/generate_activities_daily_majority_schedule_table.py",
                    ["--sim-dir", agg_dir, "--out-dir", tab_dir],
                )
                run_script(
                    "src/post_simulation/tables/generate_transport_mode_time_daily_avg_minutes_table.py",
                    ["--sim-dir", agg_dir, "--out-dir", tab_dir],
                )
                run_script(
                    "src/post_simulation/tables/generate_transport_mode_trips_daily_avg_count_table.py",
                    ["--sim-dir", agg_dir, "--out-dir", tab_dir],
                )
                run_script(
                    "src/post_simulation/tables/generate_transport_mode_trips_total_count_table.py",
                    ["--sim-dir", agg_dir, "--out-dir", tab_dir],
                )
                run_script(
                    "src/post_simulation/tables/generate_transport_mode_daily_avg_km_dist_table.py",
                    ["--sim-dir", agg_dir, "--out-dir", tab_dir],
                )
                run_script(
                    "src/post_simulation/tables/generate_transport_mode_total_km_dist_table.py",
                    ["--sim-dir", agg_dir, "--out-dir", tab_dir],
                )

                # Figures
                comp_csv = os.path.join(
                    tab_dir, "results_activities_average_comparison_minutes.csv"
                )
                run_script(
                    "src/post_simulation/figures/generate_activities_daily_avg_minutes_plot.py",
                    ["--comparison-csv", comp_csv, "--out-dir", fig_dir],
                )
                sched_csv = os.path.join(
                    tab_dir, "results_activities_daily_schedule.csv"
                )
                run_script(
                    "src/post_simulation/figures/generate_activities_daily_majority_schedule_plot.py",
                    ["--schedule-csv", sched_csv, "--out-dir", fig_dir],
                )

                # Transport plots
                t_time_avg_csv = os.path.join(
                    tab_dir, "results_transport_mode_time_daily_avg_minutes.csv"
                )
                run_script(
                    "src/post_simulation/figures/generate_transport_mode_time_daily_avg_minutes_plot.py",
                    ["--csv", t_time_avg_csv, "--out-dir", fig_dir],
                )

                t_trips_avg_csv = os.path.join(
                    tab_dir, "results_transport_mode_trips_daily_avg_count.csv"
                )
                run_script(
                    "src/post_simulation/figures/generate_transport_mode_trips_daily_avg_count_plot.py",
                    ["--csv", t_trips_avg_csv, "--out-dir", fig_dir],
                )

                t_trips_tot_csv = os.path.join(
                    tab_dir, "results_transport_mode_trips_total_count.csv"
                )
                run_script(
                    "src/post_simulation/figures/generate_transport_mode_trips_total_count_plot.py",
                    ["--csv", t_trips_tot_csv, "--out-dir", fig_dir],
                )

                t_dist_avg_csv = os.path.join(
                    tab_dir, "results_transport_mode_daily_avg_km_dist.csv"
                )
                run_script(
                    "src/post_simulation/figures/generate_transport_mode_daily_avg_km_dist_plot.py",
                    ["--csv", t_dist_avg_csv, "--out-dir", fig_dir],
                )

                t_dist_tot_csv = os.path.join(
                    tab_dir, "results_transport_mode_total_km_dist.csv"
                )
                run_script(
                    "src/post_simulation/figures/generate_transport_mode_total_km_dist_plot.py",
                    ["--csv", t_dist_tot_csv, "--out-dir", fig_dir],
                )

                # Trip Map
                run_script(
                    "src/post_simulation/tables/generate_agent_trips_table.py",
                    ["--sim-dir", agg_dir, "--out-dir", tab_dir],
                )
                trip_csv = os.path.join(tab_dir, "results_agent_trips.csv")
                run_script(
                    "src/post_simulation/figures/generate_agent_trips_plot.py",
                    ["--trip-csv", trip_csv, "--out-dir", fig_dir],
                )

                # Location Time Heatmap
                run_script(
                    "src/post_simulation/tables/generate_agent_location_time_table.py",
                    ["--sim-dir", agg_dir, "--out-dir", tab_dir],
                )
                time_csv = os.path.join(tab_dir, "results_agent_location_time.csv")
                run_script(
                    "src/post_simulation/figures/generate_agent_location_time_heatmap.py",
                    ["--time-csv", time_csv, "--out-dir", fig_dir],
                )

    print("Full experiment replication finished successfully.", flush=True)


if __name__ == "__main__":
    # NOTE: Overriding sys.argv to ONLY run post_sim for now. Remove this block to allow running all stages (pre_sim, sim, post_sim).
    sys.argv = [sys.argv[0], "--stages", "post_sim"]
    main()
