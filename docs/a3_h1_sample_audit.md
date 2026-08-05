# A3 H1 Sample Audit

Generated: 2026-08-05

Recommended Evidence Tier: **B**

- Eligible transitions: 22
- Unique eligible companies: 11
- Leverage-driven: 4 transitions across 3 companies
- Operating-driven: 18 transitions across 11 companies
- Maximum one-company transition share: 13.6%
- FY2020-FY2021 share: 50.0%
- Maximum single-year share by driver: {'leverage_driven': 0.75, 'operating_driven': 0.2777777777777778}
- Year/driver imbalance risk: True
- Permitted language: descriptive persistence patterns only

## Year Distribution

| fiscal_year_t | leverage_driven | operating_driven | total |
| --- | --- | --- | --- |
| 2019 | 3 | 1 | 4 |
| 2020 | 0 | 5 | 5 |
| 2021 | 1 | 5 | 6 |
| 2022 | 0 | 4 | 4 |
| 2023 | 0 | 3 | 3 |

## Peer and Driver Distribution

| peer_group | dominant_driver | transition_count | unique_company_count |
| --- | --- | --- | --- |
| dtc_brand | operating_driven | 3 | 2 |
| hybrid | operating_driven | 3 | 2 |
| marketplace_platform | leverage_driven | 4 | 3 |
| marketplace_platform | operating_driven | 12 | 7 |

## Company Concentration

| company_id | ticker | eligible_transition_count | transition_share |
| --- | --- | --- | --- |
| abnb | ABNB | 1 | 0.045454545454545456 |
| amzn | AMZN | 2 | 0.09090909090909091 |
| bkng | BKNG | 3 | 0.13636363636363635 |
| byon | BYON | 1 | 0.045454545454545456 |
| carg | CARG | 1 | 0.045454545454545456 |
| cars | CARS | 2 | 0.09090909090909091 |
| ebay | EBAY | 3 | 0.13636363636363635 |
| etsy | ETSY | 3 | 0.13636363636363635 |
| expe | EXPE | 3 | 0.13636363636363635 |
| love | LOVE | 1 | 0.045454545454545456 |
| rvlv | RVLV | 2 | 0.09090909090909091 |

## Exclusion Waterfall

| exclusion_reason | transition_count | unique_company_count |
| --- | --- | --- |
| invalid_dupont_transition | 96 | 31 |
| turnaround_from_loss | 30 | 25 |
| nonpositive_prior_roe | 27 | 18 |
| no_roe_improvement | 24 | 16 |
| eligible | 22 | 11 |
| next_year_not_observable | 1 | 1 |

Eligibility rules were not relaxed. Loss turnarounds remain separate, exact Shapley contributions reconcile to delta ROE, and the main outcome is next-year peer-relative change.
