import os
from typing import Optional, List
import pandas as pd
from src.constants import COL_END_TIME, COL_STARTING_TIME


def load_aggregated_simulation_data(
    sim_dir: str,
    filename: str = "aggregated.csv",
    parse_dates: Optional[List[str]] = None,
) -> pd.DataFrame:
    """Loads aggregated simulation data CSV from simulation directory."""
    csv_path = os.path.join(sim_dir, filename)
    if parse_dates is None:
        parse_dates = [COL_STARTING_TIME, COL_END_TIME]
    return pd.read_csv(csv_path, parse_dates=parse_dates)


def save_table_csv(
    df: pd.DataFrame, output_path: str, index: bool = False
) -> None:
    """Saves a pandas DataFrame to CSV, ensuring parent directories exist and logging progress."""
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    df.to_csv(output_path, index=index)
    print(f"  Saved {output_path}")
