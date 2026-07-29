import argparse
import pandas as pd
import os
from src.constants import (
    SE_RATIOS_COL_MAP,
    SEX_MAP,
    ACTIVITY_MAP,
    COL_SEX_EN,
    COL_DAY_OF_WEEK_EN,
    COL_ACTIVITY,
    COL_SE_RATIO_PCT,
    COL_SE_RATIO_FRACTION,
    COL_DAY_OF_WEEK_JP,
    COL_AREA_CLASSIFICATION_JP,
    COL_AREA_CLASSIFICATION_EN,
    COL_SEX_JP,
)


def preprocess_se_ratios(in_path, out_path):
    print(f"Preprocessing SE ratios: {in_path} -> {out_path}")
    # Skip first seven rows, then construct the header from rows 0 and 1
    # Then Remove the first two rows which are now no longer needed
    df_se = pd.read_csv(in_path, skiprows=7, header=None)
    df_se.columns = list(df_se.iloc[1, 0:6]) + list(df_se.iloc[0, 6:])
    df_se = df_se.iloc[2:].copy()
    # Rename columns using the column map
    df_se = df_se.rename(columns=SE_RATIOS_COL_MAP)
    # Melt the dataframe so that the activities are in the rows
    df_melted = df_se.melt(
        id_vars=[
            COL_DAY_OF_WEEK_JP,
            COL_AREA_CLASSIFICATION_JP,
            COL_SEX_JP,
            COL_DAY_OF_WEEK_EN,
            COL_AREA_CLASSIFICATION_EN,
            COL_SEX_EN,
        ],
        var_name=COL_ACTIVITY,
        value_name=COL_SE_RATIO_PCT,
    )
    # Filter out all rows that are not Mie-ken
    df_se_mie = df_melted[
        df_melted[COL_AREA_CLASSIFICATION_EN].str.contains("Mie-ken", na=False)
    ].copy()
    # Map the sex and activity values
    df_se_mie[COL_SEX_EN] = df_se_mie[COL_SEX_EN].map(SEX_MAP)
    df_se_mie[COL_ACTIVITY] = df_se_mie[COL_ACTIVITY].map(ACTIVITY_MAP)
    df_se_mie[COL_SE_RATIO_FRACTION] = df_se_mie[COL_SE_RATIO_PCT] / 100.0
    df_final = df_se_mie[[COL_SEX_EN, COL_ACTIVITY, COL_SE_RATIO_FRACTION]]
    # Create directories and save
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    df_final.to_csv(out_path, index=False)
    print(f"  Saved preprocessed SE ratios for Mie-ken. Shape: {df_final.shape}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preprocess SE ratios")
    parser.add_argument("--in-path", type=str, required=True, help="Input CSV")
    parser.add_argument("--out-path", type=str, required=True, help="Output CSV")
    args = parser.parse_args()
    preprocess_se_ratios(args.in_path, args.out_path)
