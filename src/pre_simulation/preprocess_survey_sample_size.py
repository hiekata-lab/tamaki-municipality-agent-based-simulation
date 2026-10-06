import argparse
import os
import pandas as pd

DEFAULT_ALL_HOUSEHOLDS_SAMPLE_SIZE = 800


def preprocess_survey_sample_size(
    in_path: str = None,
    out_path: str = "data/processed",
    sample_size: int = DEFAULT_ALL_HOUSEHOLDS_SAMPLE_SIZE,
) -> None:
    """Preprocesses survey sample sizes for Mie-ken, Both sexes, Non-working, ages 65+ on weekly average.

    Reflects the true all-household elderly non-working sample size from Table 70-1-1 (~800 respondents).
    """
    print(f"Preprocessing survey sample size: {in_path} -> {out_path}")
    final_sample_size = sample_size

    if in_path and os.path.exists(in_path):
        df_raw = pd.read_csv(in_path)
        if "Tabulated variable" in df_raw.columns:
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
            extracted_size = int(values.sum())
            if extracted_size > 0:
                final_sample_size = extracted_size

    df_out = pd.DataFrame(
        [{"group": "Mie-ken_BothSexes_NotWorking_65Plus", "sample_size": final_sample_size}]
    )

    if os.path.isdir(out_path) or not out_path.endswith(".csv"):
        out_path = os.path.join(out_path, "survey_sample_size.csv")
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    df_out.to_csv(out_path, index=False)
    print(f"  Saved preprocessed survey sample size: {final_sample_size} respondents to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preprocess survey sample size")
    parser.add_argument("--in-path", type=str, default=None, help="Input CSV path (optional)")
    parser.add_argument("--out-path", type=str, required=True, help="Output CSV path")
    parser.add_argument(
        "--sample-size",
        type=int,
        default=DEFAULT_ALL_HOUSEHOLDS_SAMPLE_SIZE,
        help="Sample size override (default: 800 from Table 70-1-1)",
    )
    args = parser.parse_args()
    preprocess_survey_sample_size(args.in_path, args.out_path, args.sample_size)
