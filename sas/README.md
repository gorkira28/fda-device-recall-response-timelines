# Running the SAS validation

The SAS program is designed for SAS 9.4 or SAS Studio, including an academic SAS Studio environment when available.

1. Upload or clone this repository into your SAS-accessible files area.
2. Open `sas/run_all.sas`.
3. Change `project_root` on line 7 to the repository's absolute SAS path.
4. Run the complete program.
5. Confirm that four CSV files and `sas_validation_report.html` appear in `outputs/sas_validation/`.
6. From the repository root, run `python src/validate_sas_outputs.py` to compare 22 SAS results with the independent Python reference.

The program performs typed CSV import, analytic inclusion, duplicate and date QA, class-specific descriptive statistics, annual medians, a tie-corrected Kruskal–Wallis calculation, effect-size calculation, reporting, visualization, and output export. It does not require paid desktop SAS-specific paths or proprietary data.
