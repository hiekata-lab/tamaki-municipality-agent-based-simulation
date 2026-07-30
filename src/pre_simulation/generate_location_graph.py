import argparse
import pandas as pd
import json
import ast
import os


def generate_location_graph(in_path, out_path, connections=10):
    print(f"Generating location graph: {in_path} -> {out_path}")
    # Helper for distance calculations
    def calculate_distances(x, y, XY):
        return ((XY - [x, y]) ** 2).sum(axis=1) ** 0.5
    # Read in locations
    df = pd.read_csv(in_path, engine="python")
    # Initialize graph
    locations = {}
    # Collect Location coordinate, name and associated types
    XY = df[["x", "y"]].values
    NAMES = df["name"].values
    TYPES = {name: ast.literal_eval(t) for name, t in zip(NAMES, df["type"].values)}
    # iterate through each location to build the locations dict
    for i, row in df.iterrows():
        name = row["name"]
        x = float(row["x"])
        y = float(row["y"])
        types = TYPES[name]
        # Calculate distance from current to all other locations
        distances = calculate_distances(x, y, XY)
        # Create a list of (name, distance) tuples excluding the current location
        dist_list = [
            (NAMES[j], float(distances[j])) for j in range(len(NAMES)) if j != i
        ]
        # Sort by distance
        dist_list.sort(key=lambda item: item[1])
        # Select closest
        closest = [{"name": n, "distance": d} for n, d in dist_list[:connections]]
        # Build dictionary for each location
        locations[name] = {"x": x, "y": y, "type": types, "closest_locations": closest}

    # Export
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(locations, f, ensure_ascii=False)

    print(f"  Location graph saved to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate location graph from CSV EPSG32654 km scale points in CSV format, csv must contain columns: x, y."
    )
    parser.add_argument(
        "--input",
        "--in-path",
        dest="in_path",
        required=True,
        help="Path to input CSV file",
    )
    parser.add_argument(
        "--output",
        "--out-path",
        dest="out_path",
        required=True,
        help="Path to output JSON file",
    )
    parser.add_argument(
        "--connections",
        type=int,
        default=10,
        help="Number of closest connections to store for each node",
    )
    args = parser.parse_args()
    generate_location_graph(args.in_path, args.out_path, args.connections)
