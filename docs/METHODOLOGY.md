# Methodology

## Study design and unit of analysis

This is a retrospective descriptive analysis of medical-device recall records in the openFDA Device Enforcement Reports dataset. The unit is an FDA `recall_number`, not a unique firm, patient, device unit, or recall event. One event may contain multiple recalled products and therefore multiple recall numbers.

## Cohort

- Inclusion: product type `Devices`; recall initiation date from 2022-01-01 through 2025-12-31; classification Class I, II, or III.
- Primary analytic records: 11,005.
- Source snapshot: openFDA bulk export dated 2026-11-10.

The completed calendar-year window reduces partial-year selection. It does not remove the possibility that FDA may later correct historical records.

## Measures

- `initiation_to_report_days`: report date minus recall initiation date; primary outcome.
- `initiation_to_classification_days`: center classification date minus initiation date.
- `classification_to_report_days`: report date minus center classification date.

FDA explains that a report posting/classification date does not necessarily indicate a new recall because firms may have initiated and communicated the action earlier. That distinction is the analytical focus here.

## Statistical analysis

Delay distributions were summarized using median, 25th and 75th percentiles, mean, and 90th percentile. The Kruskal–Wallis rank test assessed whether the three class distributions differed. Epsilon-squared was calculated as `(H - k + 1) / (n - k)` and bounded at zero. The small effect size is emphasized because the large cohort can make modest distributional differences statistically detectable.

No multiplicity-adjusted pairwise tests were conducted because the portfolio question concerns the overall class pattern. No causal model was fitted.

## SAS validation workflow

`sas/run_all.sas` independently reads a narrow six-field CSV created from the validated cohort. It does not consume Python summary tables. The program repeats identifier/date QA, class-specific descriptive statistics, annual medians, visualization, and reporting.

For the Kruskal–Wallis test, SAS assigns mean ranks with `PROC RANK`, aggregates rank sums by recall class, applies the standard tie correction, calculates the chi-square probability, and derives epsilon-squared. The formula was independently reproduced against `scipy.stats.kruskal`; the H statistic agreed exactly in the development environment. After SAS execution, `src/validate_sas_outputs.py` compares 22 exported values with the Python reference at a 1e-6 numerical tolerance.

SAS was not available locally, so the current release distinguishes formula validation and static code review from actual SAS execution. The repository does not include fabricated SAS output.

## Narrative categories

Reason-for-recall text was grouped with documented, ordered keywords: software/firmware; labeling/instructions; sterility/contamination; power/battery; packaging/seal; design; other/unspecified. These groups are descriptive convenience labels, not validated ontologies or FDA root-cause fields. A record matching more than one group receives the first matching category.

## Quality assurance

DuckDB SQL writes checks for identifier uniqueness, missing identifiers, missing classification dates, classification before initiation, and report before initiation. Pytest verifies unique recall numbers, required classes and dates, and non-empty visual outputs.

## Sensitivity and limitations

The 99th percentile restriction applies only to the boxen-plot display; all valid values remain in summaries and tests. Class III has a much smaller sample. Results describe enforcement-report records and should not be generalized to the effectiveness, clinical severity, or completion time of recalls.
