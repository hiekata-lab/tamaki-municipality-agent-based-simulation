import pandas as pd
import os
from src.constants import QUESTIONNAIRE_A_COLS, QUESTIONNAIRE_A_NUMERIC_COLS
from src.tools import get_io_parser


def preprocess_questionnaire_a(in_path, out_path):
    print(f"Preprocessing Questionnaire A: {in_path} -> {out_path}")
    df_q_raw = pd.read_csv(in_path, header=None, skiprows=12, encoding="utf-8")

    df_q_clean = df_q_raw[[1, 2, 3, 4, 5, 6, 7]].copy()
    df_q_clean.columns = QUESTIONNAIRE_A_COLS

    df_q_clean = df_q_clean.dropna(subset=["Region_EN", "Sample_EDs"])
    df_q_clean["Region_EN"] = df_q_clean["Region_EN"].str.strip()
    df_q_clean["Region_JP"] = df_q_clean["Region_JP"].str.strip()

    for col in QUESTIONNAIRE_A_NUMERIC_COLS:
        df_q_clean[col] = df_q_clean[col].astype(str).str.replace(",", "").astype(float)

    df_q_melt = df_q_clean.melt(
        id_vars=["Region_JP", "Region_EN"], var_name="Metric", value_name="Count"
    )
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    df_q_melt.to_csv(out_path, index=False)
    print(f"  Saved preprocessed Questionnaire A. Shape: {df_q_melt.shape}")


if __name__ == "__main__":
    parser = get_io_parser("Preprocess Questionnaire A")
    args = parser.parse_args()
    preprocess_questionnaire_a(args.in_path, args.out_path)
