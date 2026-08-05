# A1 Unified Company & Event Census Report

Generated: 2026-08-05

Status: **Done**

## Stopping Rules

- Total company universe: 50
- Q1 candidates: 40 (required stopping range: approximately 30-40)
- Event candidates: 14 (required stopping range: approximately 10-15)

## Q1 Candidate Structure

| Peer group | Companies |
| --- | ---: |
| dtc_brand | 15 |
| hybrid | 3 |
| inventory_led_ecommerce | 8 |
| marketplace_platform | 14 |

| Status | Companies |
| --- | ---: |
| acquired | 2 |
| active | 30 |
| bankrupt | 6 |
| delisted | 2 |

## Event Structure

| Event type | Candidates |
| --- | ---: |
| Asset exit / liquidation | 2 |
| Chapter 11 | 5 |
| Debt restructuring | 3 |
| Emergency financing | 1 |
| Going concern | 3 |

## Missing Fields for A2/A3 Verification

- Missing CIK among Q1 candidates: None
- Missing fiscal-year end among Q1 candidates: ABNB, AKA, APRN, BARK, BBBY, BIRD, BOXD, BYON, CARG, CARS, CVNA, EXPE, FIGS, FTCH, GROV, GRPN, HNST, LOVE, ME, POSH, PRPL, PTON, QVCGA, REAL, RENT, RVLV, SDC, SFIX, SNBR, TDUP, VRM, W, WISH, WRBY
- Missing listing date: None

CIK and fiscal-year-end gaps are allowed at A1 and are explicitly carried into A2/A3. Listing dates and theoretical pre-event quarters remain provisional until verified.

## DoD Result

- [x] company_schema_complete
- [x] event_schema_complete
- [x] company_ids_unique
- [x] tickers_unique
- [x] event_ids_unique
- [x] event_company_links_valid
- [x] q1_candidate_stopping_rule_met
- [x] event_candidate_stopping_rule_met
- [x] candidate_groups_valid
- [x] excluded_companies_have_specific_reason
- [x] listing_dates_valid
- [x] listing_sources_present
- [x] event_types_valid
- [x] event_required_text_complete
- [x] event_dates_valid
- [x] event_sources_present
- [x] theoretical_quarters_plausible
- [x] a3_fields_remain_provisional

A1 stops here. No Companyfacts mapping, real quarterly coverage, or formal sample decision was performed in this stage.
