import pandas as pd
import os
from src.constants import SE_RATIOS_ID_COLS, SE_RATIOS_ACTIVITIES
from src.tools import get_io_parser


def preprocess_se_ratios(in_path, out_path):
    print(f"Preprocessing SE ratios: {in_path} -> {out_path}")
    df_se = pd.read_csv(in_path, skiprows=9, header=None)

    df_se = df_se.dropna(subset=[0, 1, 2, 3, 4, 5])
    df_se = df_se[df_se[3].str.contains(r"Weekly", na=False)]

    id_cols = df_se.iloc[:, 0:6]
    id_cols.columns = SE_RATIOS_ID_COLS

    val_cols = df_se.iloc[:, 6:29]
    val_cols.columns = SE_RATIOS_ACTIVITIES

    combined = pd.concat(
        [id_cols.reset_index(drop=True), val_cols.reset_index(drop=True)], axis=1
    )

    df_melted = combined.melt(
        id_vars=[
            "Day_of_week_JP",
            "Area_classification_JP",
            "Sex_JP",
            "Day_of_week_EN",
            "Area_classification_EN",
            "Sex_EN",
        ],
        var_name="Activity",
        value_name="Standard_Error_Ratio_Pct",
    )

    df_se_mie = df_melted[
        df_melted["Area_classification_EN"].str.contains("Mie-ken", na=False)
    ].copy()

    sex_map = {"0_Both sexes": "Both sexes", "1_Male": "Male", "2_Female": "Female"}
    df_se_mie["Sex"] = df_se_mie["Sex_EN"].map(sex_map)
    df_se_mie["Activity_clean"] = df_se_mie["Activity"].str.split("_", n=1).str[-1]

    df_se_mie["SE_Ratio_Fraction"] = df_se_mie["Standard_Error_Ratio_Pct"] / 100.0

    df_final = df_se_mie[["Sex", "Activity_clean", "SE_Ratio_Fraction"]].rename(
        columns={"Activity_clean": "Activity"}
    )

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    df_final.to_csv(out_path, index=False)
    print(f"  Saved preprocessed SE ratios for Mie-ken. Shape: {df_final.shape}")


if __name__ == "__main__":
    parser = get_io_parser("Preprocess SE ratios")
    args = parser.parse_args()
    preprocess_se_ratios(args.in_path, args.out_path)
