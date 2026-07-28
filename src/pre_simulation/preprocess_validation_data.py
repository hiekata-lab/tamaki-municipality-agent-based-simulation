import pandas as pd
import os
from src.constants import COL_HEALTH, COL_VALIDATION
from src.tools import get_io_parser


def preprocess_validation_data(in_path, out_path):
    print(f"Preprocessing validation data: {in_path} -> {out_path}")
    df_val = pd.read_csv(in_path)
    df_val = df_val[df_val["Usual economic activity"] == "2_Not working"]

    for col in ["Day of the week", "Sex", "Age", "Kind of activities"]:
        df_val[col] = df_val[col].str.split("_", n=1).str[-1]

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

    df_val["value"] = pd.to_numeric(df_val["value"], errors="coerce")
    df_val = df_val.dropna(subset=["value", COL_HEALTH])

    df_val = df_val.rename(columns={"value": COL_VALIDATION})

    keep_cols = [
        "Day of the week",
        "Age",
        "Sex",
        COL_HEALTH,
        "Kind of activities",
        COL_VALIDATION,
    ]
    df_val = df_val[keep_cols]

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df_val.to_csv(out_path, index=False)
    print(f"  Saved preprocessed validation data. Shape: {df_val.shape}")


if __name__ == "__main__":
    parser = get_io_parser("Preprocess validation data")
    args = parser.parse_args()
    preprocess_validation_data(args.in_path, args.out_path)
