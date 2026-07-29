import argparse
import pandas as pd
import os
from src.constants import (
    COL_HEALTH,
    COL_VALIDATION,
    HEALTH_MAP,
    VALIDATION_COL_MAP,
    DAY_OF_WEEK_MAP,
    SEX_MAP,
    AGE_MAP,
    ACTIVITY_MAP,
    COL_DAY_OF_WEEK_EN,
    COL_SEX_EN,
    COL_AGE_GROUP,
    COL_ACTIVITY,
)


def preprocess_validation_data(in_path, out_path):
    print(f"Preprocessing validation data: {in_path} -> {out_path}")
    df_val = pd.read_csv(in_path)
    # Only select data from the non-working population
    df_val = df_val[df_val["Usual economic activity"] == "2_Not working"]
    # Rename columns using the map
    df_val = df_val.rename(columns=VALIDATION_COL_MAP)
    # Map column values using the defined dictionaries
    df_val[COL_DAY_OF_WEEK_EN] = df_val[COL_DAY_OF_WEEK_EN].map(DAY_OF_WEEK_MAP)
    df_val[COL_SEX_EN] = df_val[COL_SEX_EN].map(SEX_MAP)
    df_val[COL_AGE_GROUP] = df_val[COL_AGE_GROUP].map(AGE_MAP)
    df_val[COL_ACTIVITY] = df_val[COL_ACTIVITY].map(ACTIVITY_MAP)
    df_val[COL_HEALTH] = df_val[COL_HEALTH].map(HEALTH_MAP)
    # Convert the value column to numeric, coercing any errors to NaN
    df_val[COL_VALIDATION] = pd.to_numeric(df_val[COL_VALIDATION], errors="coerce")
    # Drop any rows that have NaN in the value or health columns
    df_val = df_val.dropna(subset=[COL_VALIDATION, COL_HEALTH])
    # Keep only the columns that are needed for the simulation
    df_val = df_val[
        [
            COL_DAY_OF_WEEK_EN,
            COL_AGE_GROUP,
            COL_SEX_EN,
            COL_HEALTH,
            COL_ACTIVITY,
            COL_VALIDATION,
        ]
    ]
    # Save the preprocessed validation data
    if os.path.isdir(out_path) or not out_path.endswith(".csv"):
        out_path = os.path.join(out_path, os.path.basename(in_path))
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    df_val.to_csv(out_path, index=False)
    print(f"  Saved preprocessed validation data. Shape: {df_val.shape}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preprocess validation data")
    parser.add_argument("--in-path", type=str, required=True, help="Input CSV")
    parser.add_argument("--out-path", type=str, required=True, help="Output CSV")
    args = parser.parse_args()
    preprocess_validation_data(args.in_path, args.out_path)
