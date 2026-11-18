/*
  FDA medical-device recall reporting timeline validation
  Compatible with SAS 9.4 / SAS Studio. Update PROJECT_ROOT before running.
*/

%let project_root=/home/YOUR_USERNAME/fda-device-recall-response-timelines;
%let input_csv=&project_root./data/processed/sas_analysis_input.csv;
%let output_dir=&project_root./outputs/sas_validation;

options validvarname=v7 nodate nonumber;

/* 1. Typed import and analytic inclusion rules. */
filename recallcsv "&input_csv." encoding='utf-8';

data work.recall;
    infile recallcsv dsd dlm=',' firstobs=2 truncover lrecl=32767;
    length recall_number $20 classification $10 reason_group $40;
    informat initiation_date report_date yymmdd10.;
    format initiation_date report_date yymmdd10.;
    input recall_number :$20.
          classification :$10.
          initiation_date :yymmdd10.
          report_date :yymmdd10.
          initiation_to_report_days
          reason_group :$40.;
    initiation_year = year(initiation_date);
    if not missing(initiation_to_report_days)
       and initiation_to_report_days >= 0
       and classification in ('Class I', 'Class II', 'Class III');
run;

/* 2. Identifier and date QA. */
proc sort data=work.recall out=work.recall_sorted nodupkey dupout=work.duplicates;
    by recall_number;
run;

proc sql noprint;
    select count(*) into :analysis_n trimmed from work.recall;
    select count(*) into :duplicate_n trimmed from work.duplicates;
    select sum(missing(recall_number)) into :missing_id_n trimmed from work.recall;
    select sum(missing(initiation_date)) into :missing_initiation_n trimmed from work.recall;
    select sum(missing(report_date)) into :missing_report_n trimmed from work.recall;
    select sum(report_date < initiation_date) into :negative_lag_n trimmed from work.recall;
quit;

data work.sas_qa_checks;
    length check_name $40;
    check_name='analysis_records'; check_value=&analysis_n.; output;
    check_name='duplicate_recall_numbers'; check_value=&duplicate_n.; output;
    check_name='missing_recall_number'; check_value=&missing_id_n.; output;
    check_name='missing_initiation_date'; check_value=&missing_initiation_n.; output;
    check_name='missing_report_date'; check_value=&missing_report_n.; output;
    check_name='report_before_initiation'; check_value=&negative_lag_n.; output;
run;

/* 3. Descriptive statistics matching the Python workflow. */
proc means data=work.recall nway noprint;
    class classification;
    var initiation_to_report_days;
    output out=work.sas_summary_by_class(drop=_type_ _freq_)
        n=records median=median mean=mean q1=p25 q3=p75 p90=p90;
run;

proc means data=work.recall nway noprint;
    class initiation_year classification;
    var initiation_to_report_days;
    output out=work.sas_annual_medians(drop=_type_ _freq_) median=median_days;
run;

/* 4. Kruskal-Wallis test computed transparently from mean ranks.
      The tie correction is applied explicitly to match scipy.stats.kruskal. */
proc rank data=work.recall out=work.ranked ties=mean;
    var initiation_to_report_days;
    ranks lag_rank;
run;

proc sql noprint;
    create table work.group_ranks as
    select classification, count(*) as n_i, sum(lag_rank) as r_i
    from work.ranked
    group by classification;

    create table work.tie_counts as
    select initiation_to_report_days, count(*) as t
    from work.recall
    group by initiation_to_report_days
    having calculated t > 1;

    select count(*), count(distinct classification)
        into :n_total trimmed, :k_groups trimmed
    from work.recall;
    select sum((r_i*r_i)/n_i) into :rank_term trimmed from work.group_ranks;
    select coalesce(sum(t**3-t),0) into :tie_sum trimmed from work.tie_counts;
quit;

data work.sas_kw_metrics;
    analysis_records=&n_total.;
    groups=&k_groups.;
    h_uncorrected=(12/(&n_total.*(&n_total.+1)))*&rank_term.-3*(&n_total.+1);
    tie_correction=1-(&tie_sum./((&n_total.**3)-&n_total.));
    kruskal_wallis_h=h_uncorrected/tie_correction;
    degrees_freedom=&k_groups.-1;
    kruskal_wallis_p=1-probchi(kruskal_wallis_h,degrees_freedom);
    epsilon_squared=max(0,(kruskal_wallis_h-&k_groups.+1)/(&n_total.-&k_groups.));
run;

/* 5. Reviewer-friendly report and portable CSV outputs. */
ods html5 path="&output_dir." file="sas_validation_report.html"
    options(bitmap_mode='inline') style=htmlblue;
ods graphics / reset width=9in height=5.5in imagename='sas_reporting_lag_by_class';

title "FDA Medical-Device Recall Reporting Lag by Class";
proc sgplot data=work.recall;
    vbox initiation_to_report_days / category=classification;
    yaxis label='Days from initiation to enforcement report' max=500;
    xaxis label='FDA recall class';
run;

title "SAS validation summary";
proc print data=work.sas_summary_by_class noobs; run;
proc print data=work.sas_kw_metrics noobs; run;
proc print data=work.sas_qa_checks noobs; run;
title;
ods html5 close;

proc export data=work.sas_summary_by_class
    outfile="&output_dir./sas_summary_by_class.csv" dbms=csv replace;
run;
proc export data=work.sas_annual_medians
    outfile="&output_dir./sas_annual_medians.csv" dbms=csv replace;
run;
proc export data=work.sas_kw_metrics
    outfile="&output_dir./sas_kw_metrics.csv" dbms=csv replace;
run;
proc export data=work.sas_qa_checks
    outfile="&output_dir./sas_qa_checks.csv" dbms=csv replace;
run;

%put NOTE: Analysis records=&analysis_n.;
%put NOTE: Duplicate recall numbers=&duplicate_n.;
%put NOTE: SAS validation outputs written to &output_dir.;
