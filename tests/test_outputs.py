from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_analysis_dataset_has_unique_recall_numbers():
    data = pd.read_csv(ROOT / "data" / "processed" / "recall_analysis.csv")
    assert data["recall_number"].is_unique


def test_required_classes_and_valid_dates():
    data = pd.read_csv(ROOT / "data" / "processed" / "recall_analysis.csv")
    assert set(data["classification"]) == {"Class I", "Class II", "Class III"}
    assert data["initiation_date"].notna().all() and data["report_date"].notna().all()


def test_required_figures_exist():
    for name in ["reporting_lag_distribution_by_class.png", "reporting_lag_ecdf_by_class.png", "median_reporting_lag_trend.png"]:
        assert (ROOT / "outputs" / "figures" / name).stat().st_size > 20_000


def test_sas_exchange_file_matches_primary_analysis():
    primary = pd.read_csv(ROOT / "data" / "processed" / "recall_analysis.csv")
    sas_input = pd.read_csv(ROOT / "data" / "processed" / "sas_analysis_input.csv")
    valid = primary[primary["initiation_to_report_days"].notna() &
                    (primary["initiation_to_report_days"] >= 0)]
    assert len(sas_input) == len(valid)
    assert sas_input["recall_number"].is_unique
    assert set(sas_input["classification"]) == {"Class I", "Class II", "Class III"}


def test_sas_program_is_substantive_and_crosscheck_is_complete():
    program = (ROOT / "sas" / "run_all.sas").read_text(encoding="utf-8").lower()
    for required in ["proc rank", "ties=mean", "tie_correction", "probchi",
                     "epsilon_squared", "proc means", "proc sgplot", "proc export"]:
        assert required in program
    reference = pd.read_csv(ROOT / "outputs" / "tables" / "python_sas_crosscheck_reference.csv")
    assert len(reference) == 22
    assert reference[["section", "group", "metric"]].duplicated().sum() == 0
