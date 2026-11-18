-- Build a recall-record cohort and operational timeline measures.
CREATE OR REPLACE TABLE enforcement AS
SELECT
    recall_number, event_id, classification, status AS enforcement_status,
    voluntary_mandated, initial_firm_notification, recalling_firm, state, country,
    product_description, reason_for_recall,
    strptime(recall_initiation_date, '%Y%m%d')::DATE AS initiation_date,
    try_strptime(center_classification_date, '%Y%m%d')::DATE AS classification_date,
    strptime(report_date, '%Y%m%d')::DATE AS report_date
FROM read_json_auto('data/raw/openfda_enforcement_2022_2025.jsonl', format='newline_delimited');

COPY (
    SELECT *,
        date_diff('day', initiation_date, classification_date) AS initiation_to_classification_days,
        date_diff('day', initiation_date, report_date) AS initiation_to_report_days,
        date_diff('day', classification_date, report_date) AS classification_to_report_days,
        CASE
            WHEN reason_for_recall IS NULL OR trim(reason_for_recall) = '' THEN 'Not reported'
            WHEN lower(reason_for_recall) LIKE '%software%' OR lower(reason_for_recall) LIKE '%firmware%' THEN 'Software/firmware'
            WHEN lower(reason_for_recall) LIKE '%label%' OR lower(reason_for_recall) LIKE '%instruction%' THEN 'Labeling/instructions'
            WHEN lower(reason_for_recall) LIKE '%steril%' OR lower(reason_for_recall) LIKE '%contamin%' THEN 'Sterility/contamination'
            WHEN lower(reason_for_recall) LIKE '%battery%' OR lower(reason_for_recall) LIKE '%power%' THEN 'Power/battery'
            WHEN lower(reason_for_recall) LIKE '%packag%' OR lower(reason_for_recall) LIKE '%seal%' THEN 'Packaging/seal'
            WHEN lower(reason_for_recall) LIKE '%design%' THEN 'Design'
            ELSE 'Other/unspecified'
        END AS reason_group
    FROM enforcement
    WHERE initiation_date BETWEEN DATE '2022-01-01' AND DATE '2025-12-31'
      AND classification IN ('Class I', 'Class II', 'Class III')
) TO 'data/processed/recall_analysis.csv' (HEADER, DELIMITER ',');

COPY (
    SELECT 'source_rows' AS check_name, count(*)::VARCHAR AS check_value FROM enforcement
    UNION ALL
    SELECT 'duplicate_recall_numbers', count(*)::VARCHAR FROM (SELECT recall_number FROM enforcement GROUP BY 1 HAVING count(*) > 1)
    UNION ALL
    SELECT 'missing_recall_number', count(*)::VARCHAR FROM enforcement WHERE recall_number IS NULL
    UNION ALL
    SELECT 'missing_classification_date', count(*)::VARCHAR FROM enforcement WHERE classification_date IS NULL
    UNION ALL
    SELECT 'classification_before_initiation', count(*)::VARCHAR FROM enforcement WHERE classification_date < initiation_date
    UNION ALL
    SELECT 'report_before_initiation', count(*)::VARCHAR FROM enforcement WHERE report_date < initiation_date
) TO 'outputs/tables/qa_checks.csv' (HEADER, DELIMITER ',');
