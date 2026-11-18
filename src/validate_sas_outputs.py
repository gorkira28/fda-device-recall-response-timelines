"""Compare SAS-exported results with independently generated Python results."""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SAS = ROOT / "outputs" / "sas_validation"
PYTHON = ROOT / "outputs" / "tables" / "python_sas_crosscheck_reference.csv"


def normalized_csv(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    frame.columns = [str(column).strip().lower() for column in frame.columns]
    return frame


def main() -> int:
    required = [SAS / "sas_summary_by_class.csv", SAS / "sas_kw_metrics.csv"]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        print("SAS outputs not present yet. Run sas/run_all.sas first.")
        print("Missing: " + ", ".join(missing))
        return 2

    reference = normalized_csv(PYTHON)
    summary = normalized_csv(required[0])
    kw = normalized_csv(required[1])
    observed_rows = []
    for row in summary.to_dict("records"):
        group = row["classification"]
        for metric in ["records", "median", "mean", "p25", "p75", "p90"]:
            observed_rows.append({"section": "class", "group": group,
                                  "metric": metric, "value": row[metric]})
    kw_row = kw.iloc[0]
    for metric in ["analysis_records", "kruskal_wallis_h", "kruskal_wallis_p", "epsilon_squared"]:
        observed_rows.append({"section": "overall", "group": "all",
                              "metric": metric, "value": kw_row[metric]})
    observed = pd.DataFrame(observed_rows)
    merged = reference.merge(observed, on=["section", "group", "metric"],
                             suffixes=("_python", "_sas"), validate="one_to_one")
    merged["absolute_difference"] = (merged["value_python"] - merged["value_sas"]).abs()
    merged["within_tolerance"] = np.isclose(
        merged["value_python"], merged["value_sas"], rtol=1e-6, atol=1e-6
    )
    merged.to_csv(SAS / "python_sas_comparison.csv", index=False)
    if not merged["within_tolerance"].all():
        print(merged.loc[~merged["within_tolerance"]].to_string(index=False))
        return 1
    print(f"PASS: {len(merged)} Python/SAS values agree within tolerance.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
