import argparse
import pandas as pd
import os
from src.constants import (
    QUESTIONNAIRE_A_COL_MAP,
    COL_REGION_JP,
    COL_REGION_EN,
    COL_SAMPLE_EDS,
    COL_SAMPLE_HOUSEHOLDS,
    COL_SAMPLE_PERSONS_LEISURE,
    COL_SAMPLE_PERSONS_TIME_USE,
    COL_SAMPLE_PERSONS_AVERAGE_TIME,
    COL_METRIC,
    COL_COUNT,
)


def preprocess_questionnaire_a(in_path, out_path):
    print(f"Preprocessing Questionnaire A: {in_path} -> {out_path}")
    # Skip 3 rows and change the columns
    df_q = pd.read_csv(in_path, skiprows=3, header=None)
    df_q.columns = [None, "地域区分", "Regions"] + list(df_q.iloc[5, 3:8])
    # Remove header rows and summary/footnote rows (keeping the 47 prefectures)
    df_q = df_q.iloc[9:56].copy()
    df_q = df_q.rename(columns=QUESTIONNAIRE_A_COL_MAP)
    df_q = df_q.dropna(subset=[COL_REGION_EN, COL_SAMPLE_EDS])
    df_q[COL_REGION_EN] = df_q[COL_REGION_EN].str.strip()
    df_q[COL_REGION_JP] = df_q[COL_REGION_JP].str.strip()
    # Gather all numeric cols of the data and replace , signs with nothing and cast to float
    numeric_cols = [
        COL_SAMPLE_EDS,
        COL_SAMPLE_HOUSEHOLDS,
        COL_SAMPLE_PERSONS_LEISURE,
        COL_SAMPLE_PERSONS_TIME_USE,
        COL_SAMPLE_PERSONS_AVERAGE_TIME,
    ]
    for col in numeric_cols:
        df_q[col] = df_q[col].astype(str).str.replace(",", "").astype(float)
    # Melt the dataframe so that the metrics are in the rows
    df_q_melt = df_q.melt(
        id_vars=[COL_REGION_JP, COL_REGION_EN],
        var_name=COL_METRIC,
        value_name=COL_COUNT,
    )
    # Create dir and save!
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    df_q_melt.to_csv(out_path, index=False)
    print(f"  Saved preprocessed Questionnaire A. Shape: {df_q_melt.shape}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preprocess Questionnaire A")
    parser.add_argument("--in-path", type=str, required=True, help="Input CSV")
    parser.add_argument("--out-path", type=str, required=True, help="Output CSV")
    args = parser.parse_args()
    preprocess_questionnaire_a(args.in_path, args.out_path)
