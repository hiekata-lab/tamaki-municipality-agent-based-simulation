import argparse
import pandas as pd
import os
from src.constants import COL_HEALTH, COL_VALIDATION


def preprocess_validation_data(in_path, out_path):
    print(f"Preprocessing validation data: {in_path} -> {out_path}")
    df_val = pd.read_csv(in_path)
    # Only select data from the non-working population
    df_val = df_val[df_val["Usual economic activity"] == "2_Not working"]
    # Strip _ prefix from col values
    for col in ["Day of the week", "Sex", "Age", "Kind of activities"]:
        df_val[col] = df_val[col].str.split("_", n=1).str[-1]
    # Map the health values from the 5-class validation data format to the unified 3-class format for the project
    df_val[COL_HEALTH] = df_val[COL_HEALTH].map(
        {
            "0_Total": None,
            "1_Excellent": "Good",
            "2_Good": "Good",
            "3_Fair": "Normal",
            "4_Not good": "Poor",
            "5_Poor": "Poor",
        }
    )
    # Convert the value column to numeric, coercing any errors to NaN
    df_val["value"] = pd.to_numeric(df_val["value"], errors="coerce")
    # Drop any rows that have NaN in the value or health columns
    df_val = df_val.dropna(subset=["value", COL_HEALTH])
    # Rename the value column to validation_value
    df_val = df_val.rename(columns={"value": COL_VALIDATION})
    # Keep only the columns that are needed for the simulation
    df_val = df_val[
        [
            "Day of the week",
            "Age",
            "Sex",
            COL_HEALTH,
            "Kind of activities",
            COL_VALIDATION,
        ]
    ]
    # Save the preprocessed validation data
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    df_val.to_csv(out_path, index=False)
    print(f"  Saved preprocessed validation data. Shape: {df_val.shape}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preprocess validation data")
    parser.add_argument("--in-path", type=str, required=True, help="Input CSV")
    parser.add_argument("--out-path", type=str, required=True, help="Output CSV")
    args = parser.parse_args()
    preprocess_validation_data(args.in_path, args.out_path)
