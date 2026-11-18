# LinkedIn post

11,005 medical-device recall records changed how I read a small p-value.

For my latest healthcare analytics project, I analyzed FDA enforcement records for recalls initiated from 2022 through 2025.

I focused on one operational interval: the time between a firm initiating a recall and publication in an FDA Enforcement Report.

The median was 48 days for Class I records, 50 days for Class II, and 62 days for Class III.

At first glance, the difference looked decisive. The Kruskal–Wallis test returned p < 0.001.

But the effect size was only 0.011.

That was the more useful finding. With a large dataset, a difference can be statistically detectable while explaining very little of the overall variation.

I built the workflow with Python and DuckDB SQL, then wrote a substantive SAS validation program for typed import, QA, grouped summaries, mean-rank construction, tie correction, effect-size calculation, reporting, and cross-software comparison.

I also kept the interpretation narrow. This analysis does not measure patient harm, recall effectiveness, or manufacturer or FDA performance. It measures one public reporting interval in the enforcement dataset.

When you review analytical work, what helps you distinguish statistical significance from practical importance?

#HealthcareAnalytics #Epidemiology
