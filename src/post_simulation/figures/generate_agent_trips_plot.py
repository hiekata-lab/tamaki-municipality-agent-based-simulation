import argparse
import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from adjustText import adjust_text


# Required to read incomplete shapefiles
os.environ["SHAPE_RESTORE_SHX"] = "YES"
# Required for IDE plotting
os.environ["MPLCONFIGDIR"] = "./.matplotlib"
# Configure Matplotlib for Japanese fonts on macOS
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = [
    "Hiragino Sans",
    "Hiragino Maru Gothic Pro",
    "AppleGothic",
    "Arial Unicode MS",
    "sans-serif",
]


def main():
    parser = argparse.ArgumentParser(description="Generate trip map.")

    parser.add_argument("--trip-csv", type=str, required=True, help='Input CSV path')

    parser.add_argument('--out-dir', type=str, required=True, help='Output directory')
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    # Load Shapefile
    shapefile_path = "data/raw/r2ka24461.shp"
    map_df = gpd.read_file(shapefile_path)
    if map_df.crs is None:
        map_df = map_df.set_crs(epsg=4326)
    map_df = map_df.to_crs(epsg=32654)
    # Scale to km to match the location graph
    map_df.geometry = map_df.geometry.scale(xfact=0.001, yfact=0.001, origin=(0, 0))

    df = pd.read_csv(args.trip_csv)

    fig, ax = plt.subplots(figsize=(24, 24))

    # Plot the background map
    map_df.plot(ax=ax, color="lightgrey", edgecolor="white", alpha=0.8)

    agents = df["unique_simulation_id"].unique()
    cmap = plt.get_cmap("tab20")

    # Gather unique locations from the newly generated legend table
    legend_csv = args.trip_csv.replace(".csv", "_legend.csv")
    legend_df = pd.read_csv(legend_csv)
    locations = (
        legend_df.set_index("Location Name")[["ID", "x", "y"]]
        .apply(tuple, axis=1)
        .to_dict()
    )

    visited_loc_ids = set()

    for i, (agent_id, agent_data) in enumerate(df.groupby("unique_simulation_id")):
        color = cmap(i % 20)

        mask = (agent_data["start_x"] != agent_data["dest_x"]) | (
            agent_data["start_y"] != agent_data["dest_y"]
        )
        valid_trips = agent_data[mask]

        if not valid_trips.empty:
            # Update visited locations
            loc_map_func = lambda x: locations.get(x, (None,))[0]
            visited_loc_ids.update(
                valid_trips["start_location"].map(loc_map_func).dropna().tolist()
            )
            visited_loc_ids.update(
                valid_trips["dest_location"].map(loc_map_func).dropna().tolist()
            )

            # Vectorized arrow plotting
            ax.quiver(
                valid_trips["start_x"],
                valid_trips["start_y"],
                valid_trips["dest_x"] - valid_trips["start_x"],
                valid_trips["dest_y"] - valid_trips["start_y"],
                angles="xy",
                scale_units="xy",
                scale=1,
                color=color,
                alpha=0.5,
                width=0.002,
                headwidth=5,
            )
            ax.scatter(
                valid_trips["start_x"],
                valid_trips["start_y"],
                color=color,
                s=9,
                alpha=0.5,
            )

    # Add location names as numbers
    texts = []
    for loc_name, (idx, x, y) in locations.items():
        if pd.notna(loc_name) and pd.notna(x) and pd.notna(y):
            if idx in visited_loc_ids:
                texts.append(
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
                        bbox=dict(
                            facecolor="white", alpha=0.7, edgecolor="none", pad=1.5
                        ),
                    )
                )

    # Adjust text to prevent overlapping
    if texts:
        adjust_text(
            texts, ax=ax, arrowprops=dict(arrowstyle="-", color="k", lw=0.5, alpha=0.5)
        )

    ax.set_title("Agent Trips")
    ax.set_xlabel("X Coordinate (km)")
    ax.set_ylabel("Y Coordinate (km)")
    ax.axis("off")

    out_file = os.path.join(args.out_dir, "agent_trips_plot.png")
    plt.tight_layout()
    plt.savefig(out_file, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  Figure saved to {out_file}")


if __name__ == "__main__":
    main()
