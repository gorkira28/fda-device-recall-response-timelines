# Data dictionary

| Field | Type | Role |
|---|---|---|
| `recall_number` | text | FDA product-level recall identifier; analytic key |
| `event_id` | text | FDA recall-event identifier; may link multiple recall numbers |
| `classification` | text | FDA hazard class I, II, or III |
| `enforcement_status` | text | Status as published in the enforcement record; not used as a lifecycle outcome |
| `voluntary_mandated` | text | How the recall was initiated |
| `initial_firm_notification` | text | First notification mode recorded by FDA |
| `recalling_firm` | text | Public name of recalling firm |
| `state`, `country` | text | Public firm location fields |
| `product_description` | text | FDA product description |
| `reason_for_recall` | text | FDA narrative reason |
| `initiation_date` | date | Date the firm initiated the recall |
| `classification_date` | date | FDA center classification date |
| `report_date` | date | FDA Enforcement Report date |
| `initiation_to_classification_days` | integer | Classification date minus initiation date |
| `initiation_to_report_days` | integer | Report date minus initiation date; primary outcome |
| `classification_to_report_days` | integer | Report date minus classification date |
| `reason_group` | text | Keyword-derived descriptive category; not an FDA ontology |
