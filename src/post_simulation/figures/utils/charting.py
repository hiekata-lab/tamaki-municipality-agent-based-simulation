"""Responsible for providing shared charting and plotting utilities."""

import os
from typing import Dict, Optional, Tuple
import matplotlib.pyplot as plt
import pandas as pd


def parse_legend_location_coordinates(
    legend_csv_path: str,
    name_col: str = "Location Name",
    id_col: str = "ID",
    x_col: str = "x",
    y_col: str = "y",
) -> Dict[str, Tuple[int, float, float]]:
    """Parses location metadata CSV into a dictionary mapping location name to (id, x, y)."""
    df = pd.read_csv(legend_csv_path)
    locations = {}
    for row in df.itertuples():
        loc_name = getattr(row, name_col, None)
        loc_id = getattr(row, id_col, None)
        loc_x = getattr(row, x_col, None)
        loc_y = getattr(row, y_col, None)
        if pd.notna(loc_name):
            locations[loc_name] = (loc_id, loc_x, loc_y)
    return locations


def save_figure(
    fig: plt.Figure,
    output_path: str,
    dpi: int = 300,
    bbox_inches: Optional[str] = "tight",
) -> None:
    """Saves a Matplotlib figure to the specified file path,
    creating parent directories if needed."""
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    fig.savefig(output_path, dpi=dpi, bbox_inches=bbox_inches)
    plt.close(fig)
    print(f"  Figure saved to {output_path}")
