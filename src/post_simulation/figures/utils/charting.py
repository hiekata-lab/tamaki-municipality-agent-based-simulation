"""Responsible for providing shared charting and plotting utilities."""

import os
from typing import Dict, List, Optional, Tuple
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import pandas as pd


def plot_grouped_category_bars(
    df: pd.DataFrame,
    group_col: str,
    category_order: List[str],
    value_cols: List[str],
    ylabel: str,
    title: Optional[str] = None,
    agg_func: str = "mean",
    integer_y_ticks: bool = False,
    figsize: Tuple[int, int] = (14, 7),
    rot: int = 45,
    width: float = 0.8,
) -> Tuple[plt.Figure, plt.Axes]:
    """Renders a grouped bar chart comparing numeric metrics across categorical groups."""
    grouped = df.groupby(group_col).agg(agg_func, numeric_only=True)
    plot_df = grouped.reindex(category_order).fillna(0)[value_cols].T
    plot_df = plot_df.rename(
        index={"Riding mobility-on-demand shuttle": "Riding MoD shuttle"}
    )

    fig, ax = plt.subplots(figsize=figsize)
    plot_df.plot.bar(ax=ax, width=width, rot=rot)

    ax.set_ylabel(ylabel, fontsize=20)
    ax.tick_params(axis="both", labelsize=20)
    if title:
        ax.set_title(title, fontweight="bold", fontsize=24)
    if integer_y_ticks:
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.legend()
    plt.tight_layout()

    return fig, ax


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
