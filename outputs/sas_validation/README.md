# SAS output destination

Run `sas/run_all.sas` to populate this folder with:

- `sas_summary_by_class.csv`
- `sas_annual_medians.csv`
- `sas_kw_metrics.csv`
- `sas_qa_checks.csv`
- `sas_validation_report.html`

These generated files are intentionally not fabricated in an environment without SAS. After SAS execution, `python src/validate_sas_outputs.py` performs the documented cross-software comparison.
