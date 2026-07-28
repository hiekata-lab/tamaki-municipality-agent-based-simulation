import random
from pprint import pprint
import json

import pandas as pd

random.seed(20011108)

# Statistical data
average_time_spent_path = "data/raw/Average time spent in activities for participants by Kind of activities, Day of the week, Area classification, Sex, Usual economic activity, Usual state of health, Age (15 Years Old and Over)-Japan, Prefectures.csv"
AVERAGE_TIME_SPENT_DF = pd.read_csv(
    average_time_spent_path, engine="python", skiprows=13
)
print("Loaded average time spent data...")

household_size_path = "data/raw/Household size (15 years and older), health awareness, gender, age (5-year age groups), and education level.csv"
HOUSEHOLD_SIZE_DF = pd.read_csv(
    household_size_path, engine="python", thousands=",", encoding="shift_jis"
).fillna(0)
print("Loaded household size data...")

population_path = "data/raw/Population by Sex, Age (single years) and All nationality or Japanese - Japan, Prefectures, Municipalities (including Municipalities as of 2000).csv"
POPULATION_DF = pd.read_csv(population_path, engine="python")
print("Loaded population data...")

locations_path = "data/processed/locations_graph.json"
with open(locations_path, "r", encoding="utf-8") as f:
    LOCATIONS = json.load(f)
print("Loaded locations graph data...")

# Distributions


# Pick all locations that has the type Home from the locations_grapj.json
def sample_home_distribution(n):
    HOMES = [
        home_name
        for home_name in LOCATIONS.keys()
        if "home" in LOCATIONS[home_name]["type"]
    ]
    print(
        f"\nSampling home distribution... (Uniform probability: {1/len(HOMES):.4f} for each of {len(HOMES)} homes)"
    )
    return random.choices(HOMES, k=n)


# Everyone in this simulation is Japanese
def sample_nationality_distribution(n):
    print("\nSampling nationality distribution... ({'Japanese': 1.0})")
    return ["Japanese"] * n


# Everyone in this simulation is from Mie-prefecture
def sample_regionality_distribution(n):
    print("\nSampling regionality distribution... ({'Mie-prefecture': 1.0})")
    return ["Mie-prefecture"] * n


# Everyone in this simulation is from Tamaki-town
def sample_town_distribution(n):
    print("\nSampling town distribution... ({'Tamaki-town': 1.0})")
    return ["Tamaki-town"] * n


# Everyone in this simulation is retired
def sample_work_distribution(n):
    WORK_CLASSES = ["Not working", "Working"]
    WORK_WEIGHTS = [1, 0]
    print(f"\nSampling work distribution... ({dict(zip(WORK_CLASSES, WORK_WEIGHTS))})")
    return random.choices(WORK_CLASSES, weights=WORK_WEIGHTS, k=n)


# Sample ages from the tamaki-town census data
def sample_age_distribution(n):
    t = POPULATION_DF[POPULATION_DF["Sex"] == "Total"].copy()
    t["value"] = pd.to_numeric(t["value"], errors="coerce").fillna(0)
    t = t[t["Age"].str.contains("years old", na=False)]

    total = t["value"].sum()
    weights = (t["value"] / total).tolist()
    age_cols = t["Age"].tolist()

    print(f"\nSampling age distribution... Weights:")
    for k, v in zip(age_cols, weights):
        print({k: v})
    return [random.choices(age_cols, weights=weights, k=1)[0] for _ in range(n)]


# Sample gender conditionally based on the tamaki-town census data
def sample_gender_distribution(ages):
    df_t = POPULATION_DF[POPULATION_DF["Sex"] == "Total"].set_index("Age")
    df_m = POPULATION_DF[POPULATION_DF["Sex"] == "Male"].set_index("Age")
    df_f = POPULATION_DF[POPULATION_DF["Sex"] == "Female"].set_index("Age")

    t = pd.to_numeric(df_t["value"], errors="coerce").fillna(0)
    m = pd.to_numeric(df_m["value"], errors="coerce").fillna(0)
    f = pd.to_numeric(df_f["value"], errors="coerce").fillna(0)

    unique_ages = set(ages)
    age_probs = {
        c: {"Male": m.get(c, 0) / t.get(c, 1), "Female": f.get(c, 0) / t.get(c, 1)}
        for c in unique_ages
        if c in t.index and t[c] > 0
    }

    print(f"\nSampling gender distribution... Probabilities by age:")
    for k, v in age_probs.items():
        print({k: v})

    weights = [(m.get(c, 0) / t.get(c, 1), f.get(c, 0) / t.get(c, 1)) for c in ages]
    # Fallback if division is zero
    weights = [w if sum(w) > 0 else (0.5, 0.5) for w in weights]

    return [random.choices(["Male", "Female"], weights=w, k=1)[0] for w in weights]


# Sample the distribution of subjective health statuses using the census data from Mie-prefecture
def sample_health_distribution(age, gender):

    AGE_MAP = {
        **{f"{i} years old": "６５〜６９歳" for i in range(65, 70)},
        **{f"{i} years old": "７０〜７４歳" for i in range(70, 75)},
        **{f"{i} years old": "７５〜７９歳" for i in range(75, 80)},
        **{f"{i} years old": "８０〜８４歳" for i in range(80, 85)},
        **{f"{i} years old": "８５歳以上" for i in range(85, 100)},
        "100 years old and over": "８５歳以上",
    }

    HEALTH_MAP = {
        "Good": ["よい", "まあよい"],
        "Normal": ["ふつう"],
        "Poor": ["あまりよくない", "よくない", "不詳"],
    }

    GENDER_MAP = {"Male": "男", "Female": "女"}

    weights_map = {}

    # Process the melted dataframe
    df = HOUSEHOLD_SIZE_DF.copy()
    df["value"] = pd.to_numeric(df["value"], errors="coerce").fillna(0)
    grouped = (
        df.groupby(["性_002", "年齢(5歳階級別)_2015", "健康意識_2015"])["value"]
        .sum()
        .reset_index()
    )

    for gender_v in GENDER_MAP.values():
        for age_v in set(AGE_MAP.values()):
            df_sub = grouped[
                (grouped["性_002"] == gender_v)
                & (grouped["年齢(5歳階級別)_2015"] == age_v)
            ]

            counts = {}
            for k, statuses in HEALTH_MAP.items():
                counts[k] = df_sub[df_sub["健康意識_2015"].isin(statuses)][
                    "value"
                ].sum()

            total = sum(counts.values())
            if total > 0:
                weights_map[(gender_v, age_v)] = [
                    counts["Good"] / total,
                    counts["Normal"] / total,
                    counts["Poor"] / total,
                ]
            else:
                weights_map[(gender_v, age_v)] = [1 / 3, 1 / 3, 1 / 3]

    print(f"\nSampling health distribution... Probabilities by gender and age group:")
    for k, v in weights_map.items():
        print({k: dict(zip(["Good", "Normal", "Poor"], v))})

    sampled_health = []
    for a, g in zip(age, gender):
        conditional_weights = weights_map[(GENDER_MAP[g], AGE_MAP[a])]
        choice = random.choices(
            ["Good", "Normal", "Poor"], weights=conditional_weights, k=1
        )[0]
        sampled_health.append(choice)

    return sampled_health


# Sample the agents
def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--num-agents", type=int, default=100, help="Number of agents to generate"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/processed/agents.csv",
        help="Output path for agents CSV",
    )
    args = parser.parse_args()

    NR_OF_AGENTS = args.num_agents
    print(f"Number of agents is {NR_OF_AGENTS}")
    age = sample_age_distribution(NR_OF_AGENTS)
    gender = sample_gender_distribution(age)
    personas_dict = {
        "home": sample_home_distribution(NR_OF_AGENTS),
        "nationality": sample_nationality_distribution(NR_OF_AGENTS),
        "regionality": sample_regionality_distribution(NR_OF_AGENTS),
        "town": sample_town_distribution(NR_OF_AGENTS),
        "age": age,
        "gender": gender,
        "working": sample_work_distribution(NR_OF_AGENTS),
        "health": sample_health_distribution(age, gender),
    }

    AGENTS_DF = pd.DataFrame(personas_dict)
    print("Agent attributes sampled...")
    pprint(AGENTS_DF.head())

    output_path = args.output
    AGENTS_DF.to_csv(output_path, index=False)
    print(f"Agents saved to {output_path}")


if __name__ == "__main__":
    main()
