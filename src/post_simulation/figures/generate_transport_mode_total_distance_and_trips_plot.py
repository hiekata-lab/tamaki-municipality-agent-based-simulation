import argparse
import os
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from src.constants import (
    COL_SCENARIO,
    TRANSPORTATION_MODES,
)
from src.post_simulation.figures.utils import (
    configure_matplotlib_defaults,
    save_figure,
)

configure_matplotlib_defaults()

DEFAULT_SCENARIOS = ["Scenario 1", "Scenario 2", "Scenario 3", "Scenario 4"]


def _annotate_trip_count_on_bar(
    ax: plt.Axes,
    bar: mpatches.Rectangle,
    trips: float,
    color: str,
    threshold: float,
    stroke: pe.AbstractPathEffect,
) -> None:
    if trips <= 0:
        return
    h = float(bar.get_height())
    label_text = str(int(trips))
    x_center = float(bar.get_x() + bar.get_width() / 2.0)
    if h >= threshold:
        ax.text(
            x_center,
            h / 2.0,
            label_text,
            ha="center",
            va="center",
            rotation=90,
            fontsize=10,
            fontweight="bold",
            color="white",
            path_effects=[stroke],
        )
    else:
        ax.text(
            x_center,
            h,
            label_text,
            ha="center",
            va="bottom",
            rotation=90,
            fontsize=10,
            fontweight="bold",
            color=color,
            path_effects=[stroke],
        )


def _annotate_all_bars_in_series(
    ax: plt.Axes,
    bars: list[mpatches.Rectangle],
    trip_vals: np.ndarray,
    col_color: str,
    threshold: float,
    stroke_black: pe.AbstractPathEffect,
    stroke_white: pe.AbstractPathEffect,
) -> None:
    for i, bar in enumerate(bars):
        trips = float(trip_vals[i])
        stroke = stroke_black if bar.get_height() >= threshold else stroke_white
        _annotate_trip_count_on_bar(ax, bar, trips, col_color, threshold, stroke)


def _draw_scenario_bars_on_axes(
    ax: plt.Axes,
    scenarios: list[str],
    colors: list[str],
    d_sum: pd.DataFrame,
    t_sum: pd.DataFrame,
    x: np.ndarray,
    bar_width: float,
    offsets: np.ndarray,
    max_dist: float,
) -> None:
    stroke_black = pe.withStroke(linewidth=2, foreground="black")
    stroke_white = pe.withStroke(linewidth=2, foreground="white")
    threshold = max_dist * 0.08
    for j, scenario in enumerate(scenarios):
        col_color = colors[j]
        dist_vals = d_sum[scenario].values
        trip_vals = t_sum[scenario].values
        x_pos = x + offsets[j]
        bars = ax.bar(
            x_pos,
            dist_vals,
            width=bar_width,
            label=scenario,
            color=col_color,
            edgecolor="black",
            linewidth=0.5,
        )
        _annotate_all_bars_in_series(
            ax,
            bars,
            trip_vals,
            col_color,
            threshold,
            stroke_black,
            stroke_white,
        )


def generate_transport_mode_distance_and_trips_plot(
    distance_csv: str,
    trips_csv: str,
    out_dir: str,
) -> None:
    df_dist = pd.read_csv(distance_csv)
    df_trips = pd.read_csv(trips_csv)

    dist_grouped = df_dist.groupby(COL_SCENARIO)[TRANSPORTATION_MODES].sum()
    dist_df = dist_grouped.reindex(DEFAULT_SCENARIOS).fillna(0).T

    trips_grouped = df_trips.groupby(COL_SCENARIO)[TRANSPORTATION_MODES].sum()
    trips_df = trips_grouped.reindex(DEFAULT_SCENARIOS).fillna(0).T

    display_names = [
        mode.replace("Riding mobility-on-demand shuttle", "Riding MoD shuttle")
        for mode in TRANSPORTATION_MODES
    ]

    n_modes = len(TRANSPORTATION_MODES)
    n_scenarios = len(DEFAULT_SCENARIOS)

    fig, ax = plt.subplots(figsize=(14, 7))

    x = np.arange(n_modes)
    total_width = 0.8
    bar_width = total_width / float(n_scenarios)
    half_tw = total_width / 2.0
    half_bw = bar_width / 2.0
    offsets = np.linspace(-half_tw + half_bw, half_tw - half_bw, n_scenarios)

    prop_cycler = plt.rcParams["axes.prop_cycle"]
    colors = prop_cycler.by_key()["color"][:n_scenarios]

    max_dist = float(dist_df.values.max())

    _draw_scenario_bars_on_axes(
        ax,
        DEFAULT_SCENARIOS,
        colors,
        dist_df,
        trips_df,
        x,
        bar_width,
        offsets,
        max_dist,
    )

    ax.set_ylabel("Total Distance (km)", fontsize=20)
    ax.set_xticks(x)
    ax.set_xticklabels(display_names, rotation=35, ha="right", fontsize=16)
    ax.tick_params(axis="both", labelsize=16)
    ax.set_ylim(bottom=0, top=max_dist * 1.12)
    ax.legend(
        title="Scenario (numbers indicate trips)",
        fontsize=14,
        title_fontsize=14,
    )

    plt.tight_layout()
    output_filename = "transport_mode_total_km_dist_and_trips.png"
    output_path = os.path.join(out_dir, output_filename)
    save_figure(fig, output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate transport mode distance and trips plot"
    )
    parser.add_argument("--distance-csv", type=str, required=True, help="Input distance CSV")
    parser.add_argument("--trips-csv", type=str, required=True, help="Input trips CSV")
    parser.add_argument("--out-dir", type=str, required=True, help="Output directory")
    args = parser.parse_args()

    generate_transport_mode_distance_and_trips_plot(
        args.distance_csv,
        args.trips_csv,
        args.out_dir,
    )
