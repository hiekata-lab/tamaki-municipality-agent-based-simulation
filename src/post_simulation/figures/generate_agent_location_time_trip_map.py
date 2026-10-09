"""Responsible for plotting agent time spent and trips across geographic locations."""

import argparse
import os
from typing import Optional, Tuple
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import matplotlib.path as mpath
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from src.constants import (
    COL_DEST_X,
    COL_DEST_Y,
    COL_DURATION,
    COL_LOCATION,
    COL_SIMULATION_UUID,
    COL_START_X,
    COL_START_Y,
    COL_X,
    COL_Y,
)
from src.post_simulation.figures.utils import (
    configure_matplotlib_defaults,
    load_projected_shapefile,
    save_figure,
)

configure_matplotlib_defaults()


def _create_house_marker_path() -> mpath.Path:
    verts = [
        (-0.5, -0.5),
        (0.5, -0.5),
        (0.5, 0.1),
        (0.65, 0.1),
        (0.0, 0.7),
        (-0.65, 0.1),
        (-0.5, 0.1),
        (-0.5, -0.5),
    ]
    codes = [
        mpath.Path.MOVETO,
        mpath.Path.LINETO,
        mpath.Path.LINETO,
        mpath.Path.LINETO,
        mpath.Path.LINETO,
        mpath.Path.LINETO,
        mpath.Path.LINETO,
        mpath.Path.CLOSEPOLY,
    ]
    return mpath.Path(verts, codes)


def _resolve_trip_csv_path_from_time_csv(
    time_csv: str, trip_csv: Optional[str]
) -> Optional[str]:
    if trip_csv and os.path.exists(trip_csv):
        return trip_csv
    fallback = time_csv.replace(
        "results_agent_location_time.csv", "results_agent_trips.csv"
    )
    if os.path.exists(fallback):
        return fallback
    return None


def _resolve_agents_csv_path(agents_csv: Optional[str]) -> Optional[str]:
    if agents_csv and os.path.exists(agents_csv):
        return agents_csv
    default_path = "data/processed/agents.csv"
    if os.path.exists(default_path):
        return default_path
    return None


def _load_home_counts_from_agents_csv(
    agents_csv_path: Optional[str],
) -> dict[str, int]:
    if not agents_csv_path or not os.path.exists(agents_csv_path):
        return {}
    df_agents = pd.read_csv(agents_csv_path)
    if "home" not in df_agents.columns:
        return {}
    return df_agents["home"].value_counts().to_dict()


def _calculate_duration_range_from_time_data(
    df_time: pd.DataFrame,
) -> Tuple[float, float]:
    durs = (
        df_time.groupby([COL_LOCATION, COL_X, COL_Y])[COL_DURATION].sum().reset_index()
    )
    if durs.empty:
        return 0.0, 1.0
    durs_hours = durs[COL_DURATION] / 60.0
    return float(durs_hours.min()), float(durs_hours.max())



def _draw_outside_home_durations_on_axes(
    ax: plt.Axes, df_outside: pd.DataFrame, vmin: float, vmax: float
) -> Optional[plt.Artist]:
    if df_outside.empty:
        return None
    out_durations = (
        df_outside.groupby([COL_LOCATION, COL_X, COL_Y])[COL_DURATION]
        .sum()
        .reset_index()
    )
    out_durations[COL_DURATION] = out_durations[COL_DURATION] / 60.0
    return ax.scatter(
        out_durations[COL_X],
        out_durations[COL_Y],
        c=out_durations[COL_DURATION],
        cmap="YlOrRd",
        vmin=vmin,
        vmax=vmax,
        s=120,
        alpha=0.9,
        edgecolors="black",
        linewidth=0.5,
        zorder=4,
    )


def _draw_home_durations_on_axes(
    ax: plt.Axes,
    df_home: pd.DataFrame,
    marker: mpath.Path,
    vmin: float,
    vmax: float,
) -> Optional[plt.Artist]:
    if df_home.empty:
        return None
    home_durations = (
        df_home.groupby([COL_LOCATION, COL_X, COL_Y])[COL_DURATION].sum().reset_index()
    )
    home_durations[COL_DURATION] = home_durations[COL_DURATION] / 60.0
    return ax.scatter(
        home_durations[COL_X],
        home_durations[COL_Y],
        c=home_durations[COL_DURATION],
        cmap="YlOrRd",
        vmin=vmin,
        vmax=vmax,
        marker=marker,
        s=480,
        alpha=0.9,
        edgecolors="black",
        linewidth=0.8,
        zorder=5,
    )


def _annotate_count_under_home_on_axes(
    ax: plt.Axes,
    x: float,
    y: float,
    count: int,
    stroke_effect: pe.AbstractPathEffect,
) -> None:
    ax.annotate(
        str(count),
        xy=(x, y),
        xytext=(0, -13),
        textcoords="offset points",
        ha="center",
        va="top",
        fontsize=14,
        fontweight="bold",
        color="black",
        path_effects=[stroke_effect],
        zorder=6,
    )


def _draw_counts_under_homes_on_axes(
    ax: plt.Axes,
    df_home: pd.DataFrame,
    home_counts: dict[str, int],
) -> None:
    if df_home.empty or not home_counts:
        return
    home_coords = df_home[[COL_LOCATION, COL_X, COL_Y]].drop_duplicates(
        subset=[COL_LOCATION]
    )
    stroke_effect = pe.withStroke(linewidth=3, foreground="white")
    for row in home_coords.itertuples():
        count = home_counts.get(getattr(row, COL_LOCATION), 0)
        x = float(getattr(row, COL_X))
        y = float(getattr(row, COL_Y))
        _annotate_count_under_home_on_axes(ax, x, y, count, stroke_effect)


def _draw_single_trip_on_axes(
    ax: plt.Axes,
    pos_a: Tuple[float, float],
    pos_b: Tuple[float, float],
    cstyle: mpatches.ConnectionStyle.Arc3,
    color: tuple,
) -> None:
    arc = FancyArrowPatch(
        pos_a,
        pos_b,
        connectionstyle=cstyle,
        arrowstyle="-",
        linewidth=0.8,
        color=color,
        alpha=0.75,
        zorder=3,
    )
    ax.add_patch(arc)
    p0, p1, p2 = cstyle.connect(pos_a, pos_b).vertices
    mid = 0.25 * p0 + 0.5 * p1 + 0.25 * p2
    tangent = p2 - p0
    norm = float(np.linalg.norm(tangent))
    if norm <= 1e-6:
        return
    unit_t = tangent / norm
    head = FancyArrowPatch(
        mid - unit_t * 0.001,
        mid + unit_t * 0.001,
        arrowstyle="-|>",
        mutation_scale=10,
        linewidth=0.8,
        color=color,
        alpha=0.75,
        zorder=3,
    )
    ax.add_patch(head)


def _draw_agent_trips_on_axes(
    ax: plt.Axes,
    agent_data: pd.DataFrame,
    cstyle: mpatches.ConnectionStyle.Arc3,
    color: tuple,
) -> None:
    mask = (agent_data[COL_START_X] != agent_data[COL_DEST_X]) | (
        agent_data[COL_START_Y] != agent_data[COL_DEST_Y]
    )
    valid_trips = agent_data[mask]
    for row in valid_trips.itertuples():
        pos_a = (float(getattr(row, COL_START_X)), float(getattr(row, COL_START_Y)))
        pos_b = (float(getattr(row, COL_DEST_X)), float(getattr(row, COL_DEST_Y)))
        _draw_single_trip_on_axes(ax, pos_a, pos_b, cstyle, color)


def _draw_all_trips_on_axes(ax: plt.Axes, trip_csv_path: Optional[str]) -> None:
    if not trip_csv_path:
        return
    df_trips = pd.read_csv(trip_csv_path)
    cmap = plt.get_cmap("tab20")
    cstyle = mpatches.ConnectionStyle.Arc3(rad=0.15)
    for i, (_, agent_data) in enumerate(df_trips.groupby(COL_SIMULATION_UUID)):
        _draw_agent_trips_on_axes(ax, agent_data, cstyle, cmap(i % 20))


def _add_shared_colorbar_to_axes(ax: plt.Axes, mappable: Optional[plt.Artist]) -> None:
    if mappable is None:
        return
    cbar = plt.colorbar(
        mappable,
        ax=ax,
        orientation="horizontal",
        shrink=0.45,
        pad=0.03,
        aspect=25,
    )
    cbar.set_label("Time Spent (hours)", fontsize=20, fontweight="bold", labelpad=12)
    cbar.ax.tick_params(labelsize=18)


def generate_agent_location_time_trip_map(
    time_csv: str,
    out_dir: str,
    trip_csv: Optional[str] = None,
    agents_csv: Optional[str] = "data/processed/agents.csv",
) -> None:
    if load_projected_shapefile is None:
        print("  Warning: geopandas is not available; skipping geographic trip map regeneration.")
        return
    map_df = load_projected_shapefile("data/raw/r2ka24461.shp")
    df_time = pd.read_csv(time_csv)

    resolved_trip_csv = _resolve_trip_csv_path_from_time_csv(time_csv, trip_csv)
    resolved_agents_csv = _resolve_agents_csv_path(agents_csv)
    home_counts = _load_home_counts_from_agents_csv(resolved_agents_csv)
    vmin, vmax = _calculate_duration_range_from_time_data(df_time)

    fig, ax = plt.subplots(figsize=(24, 24))
    map_df.plot(ax=ax, color="lightgrey", edgecolor="white", alpha=0.8, zorder=1)
    _draw_all_trips_on_axes(ax, resolved_trip_csv)

    is_home = df_time[COL_LOCATION].str.startswith("Home")
    sc_out = _draw_outside_home_durations_on_axes(ax, df_time[~is_home], vmin, vmax)

    house_marker = _create_house_marker_path()
    sc_home = _draw_home_durations_on_axes(
        ax, df_time[is_home], house_marker, vmin, vmax
    )
    _draw_counts_under_homes_on_axes(ax, df_time[is_home], home_counts)

    _add_shared_colorbar_to_axes(ax, sc_home or sc_out)

    minx, miny, maxx, maxy = map_df.total_bounds
    pad = 0.05
    ax.set_xlim(minx - pad, maxx + pad)
    ax.set_ylim(miny - pad, maxy + pad)
    ax.axis("off")

    plt.tight_layout()
    out_file = os.path.join(out_dir, "agent_location_time_trip_map.png")
    save_figure(fig, out_file, bbox_inches="tight")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate agent location time trip map."
    )
    parser.add_argument("--time-csv", type=str, required=True, help="Input CSV path")
    parser.add_argument(
        "--trip-csv", type=str, default=None, help="Optional input trip CSV path"
    )
    parser.add_argument(
        "--agents-csv",
        type=str,
        default="data/processed/agents.csv",
        help="Optional input agents CSV path",
    )
    parser.add_argument("--out-dir", type=str, required=True, help="Output directory")
    args = parser.parse_args()

    generate_agent_location_time_trip_map(
        args.time_csv, args.out_dir, args.trip_csv, args.agents_csv
    )
