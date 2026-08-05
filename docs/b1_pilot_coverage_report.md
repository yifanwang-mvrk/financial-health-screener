# B1 Pilot Pipeline Report

Generated: 2026-08-05

Status: **Done - revalidated against Gate1-v1.0**

The six companies remain the Pilot. They do not define the 21-company formal sample.

## Selection Coverage

- AMZN and CHWY: Inventory-led E-commerce; CHWY tests a 52/53-week fiscal year.
- BKNG, DASH, EBAY, and ETSY: Marketplace / Platform.
- CHWY and EBAY provide restatement/concept-conflict cases.
- BKNG and ETSY provide near-zero or nonpositive-equity metric-invalid cases.
- AMZN and CHWY provide filing reconciliation cases.

## Pipeline Evidence

| Ticker | Complete extracted fields | Extracted fields | Medium/high conflicts | Metric flags | Reconciliation reviews |
| --- | ---: | ---: | ---: | ---: | ---: |
| AMZN | 12 | 13 | 0 | 2 | 0 |
| BKNG | 11 | 13 | 0 | 2 | 0 |
| CHWY | 12 | 13 | 13 | 11 | 1 |
| DASH | 11 | 13 | 14 | 10 | 0 |
| EBAY | 12 | 13 | 3 | 5 | 0 |
| ETSY | 11 | 13 | 9 | 9 | 0 |

The scripted order is Extract -> Normalize -> Map & Sign -> Conflicts -> Latest-restated -> Validate -> DuckDB -> Pilot marts. Extraction and validation errors have dedicated CSV logs. DASH and ETSY use documented CapEx aggregation overrides after the shared single-tag rule failed filing reconciliation.

DuPont identity and Shapley reconciliation are tested automatically. The Pilot H1 result does not determine the frozen formal Tier B conclusion.
