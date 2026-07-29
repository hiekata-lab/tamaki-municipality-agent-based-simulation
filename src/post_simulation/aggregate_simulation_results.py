import os
import json
import argparse
import pandas as pd
from pathlib import Path
from src.constants import COL_UNIQUE_SIMULATION_ID

def aggregate_simulation_dirs(in_dir: str, out_dir: str):
    # Create output dir
    os.makedirs(out_dir, exist_ok=True)
    # Aggregate result folders
    results_path = Path(in_dir)
    conf_files = list(results_path.glob("*/conf.json"))

    # NOTE: Aggregate JSON metadata files
    all_json_data = []
    for f in conf_files:
        data = json.load(open(f, "r", encoding="utf-8"))
        data[COL_UNIQUE_SIMULATION_ID] = f.parent.name
        all_json_data.append(data)
    out_json_path = os.path.join(out_dir, "aggregated.json")
    with open(out_json_path, "w", encoding="utf-8") as f:
        json.dump(all_json_data, f, indent=4)
    print(f"  Aggregated {len(all_json_data)} JSON files into {out_json_path}")

    # NOTE: Aggregate CSV time series files
    csv_files = list(results_path.glob("*/simulation.csv"))
    def load_csv(f):
        return pd.read_csv(f).assign(**{COL_UNIQUE_SIMULATION_ID: f.parent.name})
    # Concat all files
    combined_df = pd.concat((load_csv(f) for f in csv_files), ignore_index=True)
    if not combined_df.empty:
        # Re-order columns
        cols = [COL_UNIQUE_SIMULATION_ID] + [
            c for c in combined_df.columns if c != COL_UNIQUE_SIMULATION_ID
        ]
        # Save aggregated raw data
        combined_df = combined_df[cols]
        out_csv_path = os.path.join(out_dir, "aggregated_raw.csv")
        combined_df.to_csv(out_csv_path, index=False)
        print(f"  Aggregated {len(csv_files)} CSV files into {out_csv_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aggregate simulation results from a directory.")
    parser.add_argument("--in-dir", type=str, default=".", help="Path to the directory containing simulation folders. Defaults to current directory.")
    parser.add_argument("--out-dir", type=str, default="aggregated", help="Output directory. Defaults to 'aggregated'.")
    args = parser.parse_args()
    aggregate_simulation_dirs(args.in_dir, args.out_dir)
