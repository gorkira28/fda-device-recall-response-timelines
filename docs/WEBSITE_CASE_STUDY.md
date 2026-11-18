# FDA Medical-Device Recall Response Timelines

**SAS · Python · DuckDB SQL · nonparametric statistics · regulatory data QA**

## The question

How much time elapsed between a firm's initiation of a medical-device recall and publication in an FDA Enforcement Report, and did the observed distribution differ by recall class?

## What I built

I created a reproducible pipeline that downloads the official openFDA bulk export, filters a four-year cohort, types and validates regulatory dates in DuckDB SQL, and produces publication-ready Python visualizations. A substantive SAS workflow independently performs typed import, QA, descriptive analysis, annual medians, a tie-corrected Kruskal–Wallis calculation, effect-size estimation, reporting, and export for cross-software validation.

## What I found

Among 11,005 records, median initiation-to-report time was 48 days for Class I, 50 for Class II, and 62 for Class III. The overall class difference was statistically detectable, but the effect size was small (epsilon-squared 0.011). This means recall class alone captured little of the variation—even though a large dataset produced a very small p-value.

For Class I and II records, the annual median was 43 days in 2025, compared with 56 and 54 days in 2022. The trend is descriptive and does not establish improvement caused by a specific intervention.

## Why it is useful

The project shows how to convert public regulatory data into an auditable operational measure while preserving the distinction between recall initiation, classification, public reporting, and termination. It also demonstrates a practical analytics lesson: statistical significance and operational importance are not the same thing.

## Important boundary

This is not a measure of patient harm, recall effectiveness, manufacturer performance, or the time needed to correct or remove devices. A recall number is a product-level record and multiple records can belong to one event.
