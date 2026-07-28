import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from adjustText import adjust_text
from src.tools import get_csv_and_out_parser

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
    parser = get_csv_and_out_parser("Generate agent location time heatmap.", "--time-csv")
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

    df = pd.read_csv(args.time_csv)

    fig, ax = plt.subplots(figsize=(24, 24))

    # Plot the background map
    map_df.plot(ax=ax, color="lightgrey", edgecolor="white", alpha=0.8)

    # Gather unique locations from the newly generated legend table
    legend_csv = args.time_csv.replace(".csv", "_legend.csv")
    legend_df = pd.read_csv(legend_csv)
    locations = (
        legend_df.set_index("Location Name")[["ID", "x", "y"]]
        .apply(tuple, axis=1)
        .to_dict()
    )

    # Aggregate duration by location across all agents to create a heatmap
    loc_durations = df.groupby(["location", "x", "y"])["duration"].sum().reset_index()

    vmin = loc_durations["duration"].min()
    vmax = loc_durations["duration"].max()

    import seaborn as sns

    # Plot the KDE heatmap for the "bleed" effect
    sns.kdeplot(
        data=loc_durations,
        x="x",
        y="y",
        weights="duration",
        fill=True,
        cmap="YlOrRd",
        alpha=0.4, # Slightly lower alpha
        levels=50,
        thresh=0.15, # Higher threshold makes it bleed less outwards
        ax=ax,
        bw_adjust=0.6, # Lower bandwidth makes it tighter to the points
    )

    # Plot the actual circles
    sc = ax.scatter(
        loc_durations["x"],
        loc_durations["y"],
        c=loc_durations["duration"],
        cmap="YlOrRd",
        s=150,
        alpha=0.9,
        edgecolors="black",
        linewidth=0.5,
        vmin=vmin,
        vmax=vmax,
    )
    
    # Add a colorbar
    cbar = plt.colorbar(sc, ax=ax, shrink=0.5, pad=0.02)
    cbar.set_label("Total Time Spent (minutes)", fontsize=14)
    cbar.ax.tick_params(labelsize=12)

    visited_loc_names = set(loc_durations["location"].unique())
    visited_loc_ids = set()
    for loc_name in visited_loc_names:
        if loc_name in locations:
            visited_loc_ids.add(locations[loc_name][0])

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

    ax.set_title("Agent Location Time Heatmap", fontsize=20)
    ax.set_xlabel("X Coordinate (km)", fontsize=14)
    ax.set_ylabel("Y Coordinate (km)", fontsize=14)
    ax.tick_params(axis="both", which="major", labelsize=12)
    ax.axis("off")

    out_file = os.path.join(args.out_dir, "agent_location_time_heatmap.png")
    plt.tight_layout()
    plt.savefig(out_file, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  Figure saved to {out_file}")


if __name__ == "__main__":
    main()
