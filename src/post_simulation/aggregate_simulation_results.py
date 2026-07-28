import os
import json
import argparse
import pandas as pd
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Aggregate simulation results from a directory."
    )
    parser.add_argument(
        "--results-dir",
        type=str,
        default=".",
        help="Path to the directory containing simulation folders. Defaults to current directory.",
    )
    parser.add_argument(
        "--out-dir",
        type=str,
        default="aggregated",
        help="Output directory. Defaults to 'aggregated_simulation_results'.",
    )
    args = parser.parse_args()

    results_dir = args.results_dir
    out_dir = args.out_dir

    results_path = Path(results_dir)

    # Aggregate JSON
    conf_files = list(results_path.glob("*/conf.json"))
    all_json_data = []
    for f in conf_files:
        data = json.load(open(f, "r", encoding="utf-8"))
        data["unique_simulation_id"] = f.parent.name
        all_json_data.append(data)

    out_json_path = os.path.join(out_dir, "aggregated.json")
    with open(out_json_path, "w", encoding="utf-8") as f:
        json.dump(all_json_data, f, indent=4)
    print(f"  Aggregated {len(all_json_data)} JSON files into {out_json_path}")

    # Aggregate CSV
    csv_files = list(results_path.glob("*/simulation.csv"))
    def load_csv(f):
        return pd.read_csv(f).assign(unique_simulation_id=f.parent.name)

    combined_df = pd.concat((load_csv(f) for f in csv_files), ignore_index=True)
    if not combined_df.empty:
        cols = ["unique_simulation_id"] + [
            c for c in combined_df.columns if c != "unique_simulation_id"
        ]
        combined_df = combined_df[cols]
        out_csv_path = os.path.join(out_dir, "aggregated.csv")
        combined_df.to_csv(out_csv_path, index=False)
        print(f"  Aggregated {len(csv_files)} CSV files into {out_csv_path}")


if __name__ == "__main__":
    main()
