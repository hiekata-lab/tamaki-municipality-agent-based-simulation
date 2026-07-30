import argparse
import os
from adjustText import adjust_text
import matplotlib.pyplot as plt
import pandas as pd
from src.constants import (
    COL_DEST_LOCATION,
    COL_DEST_X,
    COL_DEST_Y,
    COL_SIMULATION_UUID,
    COL_START_LOCATION,
    COL_START_X,
    COL_START_Y,
)
from src.post_simulation.figures.utils import (
    configure_matplotlib_defaults,
    load_projected_shapefile,
    parse_legend_location_coordinates,
    save_figure,
)

configure_matplotlib_defaults()


def generate_trips_plot(trip_csv: str, out_dir: str) -> None:
    map_df = load_projected_shapefile("data/raw/r2ka24461.shp")
    df = pd.read_csv(trip_csv)

    legend_csv = trip_csv.replace(".csv", "_legend.csv")
    locations = parse_legend_location_coordinates(legend_csv)

    fig, ax = plt.subplots(figsize=(24, 24))
    map_df.plot(ax=ax, color="lightgrey", edgecolor="white", alpha=0.8)

    cmap = plt.get_cmap("tab20")
    visited_loc_ids = set()

    for i, (_, agent_data) in enumerate(df.groupby(COL_SIMULATION_UUID)):
        color = cmap(i % 20)
        mask = (agent_data[COL_START_X] != agent_data[COL_DEST_X]) | (
            agent_data[COL_START_Y] != agent_data[COL_DEST_Y]
        )
        valid_trips = agent_data[mask]

        if not valid_trips.empty:
            for start_loc in valid_trips[COL_START_LOCATION].dropna():
                if start_loc in locations:
                    visited_loc_ids.add(locations[start_loc][0])
            for dest_loc in valid_trips[COL_DEST_LOCATION].dropna():
                if dest_loc in locations:
                    visited_loc_ids.add(locations[dest_loc][0])

            ax.quiver(
                valid_trips[COL_START_X],
                valid_trips[COL_START_Y],
                valid_trips[COL_DEST_X] - valid_trips[COL_START_X],
                valid_trips[COL_DEST_Y] - valid_trips[COL_START_Y],
                angles="xy",
                scale_units="xy",
                scale=1,
                color=color,
                alpha=0.5,
                width=0.002,
                headwidth=5,
            )
            ax.scatter(
                valid_trips[COL_START_X],
                valid_trips[COL_START_Y],
                color=color,
                s=9,
                alpha=0.5,
            )

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

    ax.set_title("Agent Trips")
    ax.set_xlabel("X Coordinate (km)")
    ax.set_ylabel("Y Coordinate (km)")
    ax.axis("off")

    out_file = os.path.join(out_dir, "agent_trips_plot.png")
    save_figure(fig, out_file, bbox_inches="tight")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate trip map.")
    parser.add_argument("--trip-csv", type=str, required=True, help="Input CSV path")
    parser.add_argument("--out-dir", type=str, required=True, help="Output directory")
    args = parser.parse_args()

    generate_trips_plot(args.trip_csv, args.out_dir)
