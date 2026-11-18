"""Create descriptive and nonparametric analyses of FDA recall timelines."""
from __future__ import annotations
import json
from pathlib import Path
import duckdb
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import kruskal

ROOT = Path(__file__).resolve().parents[1]
FIG, TAB = ROOT / "outputs" / "figures", ROOT / "outputs" / "tables"
ORDER = ["Class I", "Class II", "Class III"]
PALETTE = {"Class I": "#B42318", "Class II": "#175CD3", "Class III": "#027A48"}


def run_sql() -> None:
    sql = (ROOT / "sql" / "01_build_analysis.sql").read_text(encoding="utf-8")
    con = duckdb.connect(str(ROOT / "data" / "processed" / "recalls.duckdb"))
    try:
        con.execute(sql)
    finally:
        con.close()


def summarize(frame: pd.DataFrame, field: str) -> pd.DataFrame:
    return (frame.groupby("classification")[field]
            .agg(records="size", median="median", mean="mean",
                 p25=lambda x: x.quantile(.25), p75=lambda x: x.quantile(.75),
                 p90=lambda x: x.quantile(.90))
            .reindex(ORDER).round(1).reset_index())


def main() -> None:
    FIG.mkdir(parents=True, exist_ok=True); TAB.mkdir(parents=True, exist_ok=True)
    run_sql()
    data = pd.read_csv(ROOT / "data" / "processed" / "recall_analysis.csv")
    valid = data[data["initiation_to_report_days"].notna() & (data["initiation_to_report_days"] >= 0)].copy()
    valid["initiation_year"] = pd.to_datetime(valid["initiation_date"]).dt.year
    class_summary = summarize(valid, "initiation_to_report_days")
    class_summary.to_csv(TAB / "reporting_lag_summary_by_class.csv", index=False)

    # Deliberately narrow, typed exchange file for independent SAS validation.
    sas_input = valid[["recall_number", "classification", "initiation_date", "report_date",
                       "initiation_to_report_days", "reason_group"]].copy()
    sas_input.to_csv(ROOT / "data" / "processed" / "sas_analysis_input.csv", index=False)

    groups = [valid.loc[valid["classification"] == label, "initiation_to_report_days"] for label in ORDER]
    test = kruskal(*groups); n, k = len(valid), len(groups)
    epsilon_squared = max(0.0, (test.statistic - k + 1) / (n - k))

    cap = valid["initiation_to_report_days"].quantile(.99)
    fig, ax = plt.subplots(figsize=(10, 5.8))
    sns.boxenplot(data=valid[valid["initiation_to_report_days"] <= cap], x="classification",
                  y="initiation_to_report_days", order=ORDER, palette=PALETTE,
                  hue="classification", legend=False, ax=ax)
    ax.set(title="Time from firm recall initiation to FDA enforcement report",
           xlabel="FDA recall class", ylabel="Days (visualized through the 99th percentile)")
    ax.grid(axis="y", alpha=.2); sns.despine(); fig.tight_layout()
    fig.savefig(FIG / "reporting_lag_distribution_by_class.png", dpi=180); plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 5.8))
    for label in ORDER:
        values = np.sort(valid.loc[valid["classification"] == label, "initiation_to_report_days"].to_numpy())
        ax.step(values, np.arange(1, len(values) + 1) / len(values), where="post",
                label=label, color=PALETTE[label], linewidth=2)
    ax.set(title="Cumulative distribution of recall reporting lag",
           xlabel="Days from initiation to enforcement report", ylabel="Share of recall records reported")
    ax.set_xlim(0, min(750, cap)); ax.set_ylim(0, 1.01); ax.grid(alpha=.2); ax.legend(frameon=False)
    sns.despine(); fig.tight_layout(); fig.savefig(FIG / "reporting_lag_ecdf_by_class.png", dpi=180); plt.close(fig)

    trend = (valid.groupby(["initiation_year", "classification"])["initiation_to_report_days"]
             .median().unstack().reindex(columns=ORDER))
    fig, ax = plt.subplots(figsize=(10, 5.5))
    for label in ORDER:
        ax.plot(trend.index, trend[label], marker="o", linewidth=2.5, label=label, color=PALETTE[label])
    ax.set(title="Median initiation-to-report time by recall year",
           xlabel="Recall initiation year", ylabel="Median days")
    ax.set_xticks([2022, 2023, 2024, 2025]); ax.grid(axis="y", alpha=.2); ax.legend(frameon=False)
    sns.despine(); fig.tight_layout(); fig.savefig(FIG / "median_reporting_lag_trend.png", dpi=180); plt.close(fig)
    trend.reset_index().to_csv(TAB / "median_reporting_lag_by_year.csv", index=False)

    reasons = (valid.groupby("reason_group", as_index=False)
               .agg(records=("recall_number", "size"), median_reporting_lag_days=("initiation_to_report_days", "median"))
               .sort_values("records", ascending=False))
    reasons.to_csv(TAB / "reason_group_summary.csv", index=False)
    metrics = {"source_records": int(len(data)), "analysis_records": int(len(valid)),
               "excluded_negative_or_missing_lag": int(len(data) - len(valid)),
               "kruskal_wallis_h": round(float(test.statistic), 2), "kruskal_wallis_p": float(test.pvalue),
               "epsilon_squared": round(float(epsilon_squared), 4), "source_export_date": "2026-11-10"}
    (TAB / "key_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    # Long-format reference values make cross-software comparison unambiguous.
    reference_rows = [
        {"section": "overall", "group": "all", "metric": "analysis_records", "value": len(valid)},
        {"section": "overall", "group": "all", "metric": "kruskal_wallis_h", "value": test.statistic},
        {"section": "overall", "group": "all", "metric": "kruskal_wallis_p", "value": test.pvalue},
        {"section": "overall", "group": "all", "metric": "epsilon_squared", "value": epsilon_squared},
    ]
    for row in class_summary.to_dict("records"):
        for metric in ["records", "median", "mean", "p25", "p75", "p90"]:
            reference_rows.append({"section": "class", "group": row["classification"],
                                   "metric": metric, "value": row[metric]})
    pd.DataFrame(reference_rows).to_csv(TAB / "python_sas_crosscheck_reference.csv", index=False)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__": main()
