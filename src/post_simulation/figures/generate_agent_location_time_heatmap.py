import argparse
import os
from adjustText import adjust_text
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from src.constants import (
    COL_DURATION,
    COL_LOCATION,
    COL_X,
    COL_Y,
)
from src.post_simulation.figures.utils import (
    configure_matplotlib_defaults,
    load_projected_shapefile,
    parse_legend_location_coordinates,
    save_figure,
)

configure_matplotlib_defaults()


def generate_location_time_heatmap(time_csv: str, out_dir: str) -> None:
    map_df = load_projected_shapefile("data/raw/r2ka24461.shp")
    df = pd.read_csv(time_csv)

    legend_csv = time_csv.replace(".csv", "_legend.csv")
    locations = parse_legend_location_coordinates(legend_csv)

    fig, ax = plt.subplots(figsize=(24, 24))
    map_df.plot(ax=ax, color="lightgrey", edgecolor="white", alpha=0.8)

    loc_durations = (
        df.groupby([COL_LOCATION, COL_X, COL_Y])[COL_DURATION].sum().reset_index()
    )
    vmin = loc_durations[COL_DURATION].min()
    vmax = loc_durations[COL_DURATION].max()

    sns.kdeplot(
        data=loc_durations,
        x=COL_X,
        y=COL_Y,
        weights=COL_DURATION,
        fill=True,
        cmap="YlOrRd",
        alpha=0.4,
        levels=50,
        thresh=0.15,
        ax=ax,
        bw_adjust=0.6,
    )

    sc = ax.scatter(
        loc_durations[COL_X],
        loc_durations[COL_Y],
        c=loc_durations[COL_DURATION],
        cmap="YlOrRd",
        s=150,
        alpha=0.9,
        edgecolors="black",
        linewidth=0.5,
        vmin=vmin,
        vmax=vmax,
    )

    cbar = plt.colorbar(sc, ax=ax, shrink=0.5, pad=0.02)
    cbar.set_label("Total Time Spent (minutes)", fontsize=14)
    cbar.ax.tick_params(labelsize=12)

    visited_loc_ids = {
        locations[loc][0]
        for loc in loc_durations[COL_LOCATION].unique()
        if loc in locations
    }

    texts = [
        ax.text(
            x,
            y,
            str(idx),
            fontsize=10,
            alpha=0.9,
            ha="center",
            va="center",
            fontweight="bold",
            color="black",
            bbox=dict(facecolor="white", alpha=0.7, edgecolor="none", pad=1.5),
        )
        for loc_name, (idx, x, y) in locations.items()
        if pd.notna(loc_name)
        and pd.notna(x)
        and pd.notna(y)
        and idx in visited_loc_ids
    ]

    if texts:
        adjust_text(
            texts, ax=ax, arrowprops=dict(arrowstyle="-", color="k", lw=0.5, alpha=0.5)
        )

    ax.set_title("Agent Location Time Heatmap", fontsize=20)
    ax.set_xlabel("X Coordinate (km)", fontsize=14)
    ax.set_ylabel("Y Coordinate (km)", fontsize=14)
    ax.tick_params(axis="both", which="major", labelsize=12)
    ax.axis("off")

    out_file = os.path.join(out_dir, "agent_location_time_heatmap.png")
    save_figure(fig, out_file, bbox_inches="tight")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate agent location time heatmap.")
    parser.add_argument("--time-csv", type=str, required=True, help="Input CSV path")
    parser.add_argument("--out-dir", type=str, required=True, help="Output directory")
    args = parser.parse_args()

    generate_location_time_heatmap(args.time_csv, args.out_dir)
