import argparse
import pandas as pd
import json
import ast


def main():

    def calculate_distances(x, y, XY):
        return ((XY - [x, y]) ** 2).sum(axis=1) ** 0.5

    parser = argparse.ArgumentParser(
        description="Generate location graph from CSV EPSG32654 km scale points in  CSV format, csv must contain columns: x, y."
    )
    parser.add_argument("--input", help="Path to input CSV file")
    parser.add_argument(
        "--output", default="locations_graph.json", help="Path to output JSON file"
    )
    parser.add_argument(
        "--connections",
        type=int,
        default=10,
        help="Number of closest connections to store for each node",
    )

    args = parser.parse_args()

    df = pd.read_csv(args.input, engine="python")

    locations = {}

    XY = df[["x", "y"]].values

    NAMES = df["name"].values

    TYPES = {name: ast.literal_eval(t) for name, t in zip(NAMES, df["type"].values)}

    for i, row in df.iterrows():
        name = row["name"]
        x = float(row["x"])
        y = float(row["y"])
        types = TYPES[name]

        distances = calculate_distances(x, y, XY)
        dist_list = [
            (NAMES[j], float(distances[j])) for j in range(len(NAMES)) if j != i
        ]
        dist_list.sort(key=lambda item: item[1])

        closest = [{"name": n, "distance": d} for n, d in dist_list[: args.connections]]

        locations[name] = {"x": x, "y": y, "type": types, "closest_locations": closest}

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(locations, f, ensure_ascii=False)

    print(f"Location graph saved to {args.output}")


if __name__ == "__main__":
    main()
