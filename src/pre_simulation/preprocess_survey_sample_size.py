import argparse
import os
import pandas as pd


def preprocess_survey_sample_size(in_path: str, out_path: str) -> None:
    """Preprocesses raw survey sample sizes for Mie-ken, Both sexes, Non-working, ages 65+ on weekly average."""
    print(f"Preprocessing survey sample size: {in_path} -> {out_path}")
    if not os.path.exists(in_path):
        raise FileNotFoundError(f"Raw sample size file not found at {in_path}")

    df_raw = pd.read_csv(in_path)
    filtered = df_raw[
        (df_raw["Tabulated variable"] == "Sample size")
        & (df_raw["Area classification"] == "Mie-ken")
        & (df_raw["Day of the week"].str.contains("Weekly average"))
        & (df_raw["Sex"].str.contains("Both sexes"))
        & (df_raw["Usual economic activity"].str.contains("Not working"))
        & (
            df_raw["Age"].str.contains("65 to 74 years old")
            | df_raw["Age"].str.contains("75 years old and over")
        )
    ]
    values = pd.to_numeric(filtered["value"], errors="coerce").fillna(0)
    sample_size = int(values.sum())
    if sample_size <= 0:
        raise ValueError(f"No valid sample size entries found for specified criteria in {in_path}")

    df_out = pd.DataFrame([{"group": "Mie-ken_BothSexes_NotWorking_65Plus", "sample_size": sample_size}])
    
    if os.path.isdir(out_path) or not out_path.endswith(".csv"):
        out_path = os.path.join(out_path, "survey_sample_size.csv")
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    df_out.to_csv(out_path, index=False)
    print(f"  Saved preprocessed survey sample size: {sample_size} respondents to {out_path}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preprocess survey sample size")
    parser.add_argument("--in-path", type=str, required=True, help="Input CSV path")
    parser.add_argument("--out-path", type=str, required=True, help="Output CSV path")
    args = parser.parse_args()
    preprocess_survey_sample_size(args.in_path, args.out_path)
