# B3 SQL Analytical Marts Report

Generated: 2026-08-05

Status: **Done**

The seven SQL files run in the frozen order from formal B2 DuckDB core tables. No Gate 1 field, sample, peer, H1, source, or version rule is changed.

## Mandatory Marts

| Mart | Grain | Rows | Purpose |
| --- | --- | ---: | --- |
| `q1_annual_company_metrics` | one formal company x available fiscal year | 137 | Average-balance DuPont, liquidity, leverage, cash-flow, validity, and quality metrics. |
| `q1_dupont_contributions` | one formal company x consecutive annual transition ending year | 116 | Exact three-factor Shapley ROE-change attribution and frozen driver classification. |
| `q1_driver_persistence` | one formal company x consecutive annual transition ending year | 116 | Consecutive-year LEAD outcomes, including the peer-relative primary result. |
| `q1_h1_sample_audit` | one formal company x candidate H1 transition ending year | 116 | Frozen H1 eligibility, exclusions, year distribution, and company concentration. |
| `q1_peer_summary` | one formal peer group x fiscal year | 21 | Valid-observation peer-year medians, quartiles, and sample sizes. |
| `q1_company_vs_peer` | one formal company x available fiscal year | 137 | Company metrics joined to peer benchmarks and ROE percentile position. |
| `q1_powerbi_mart` | one formal company x available fiscal year | 137 | Exact Gate1-v1.0 60-field single-table Power BI consumption layer. |

## H1 Frozen-Rule Result

- Evidence Tier: B
- Eligible transitions: 21
- Unique eligible companies: 10
- Leverage-driven transitions: 4
- Operating-driven transitions: 17
- Maximum company transition share: 14.3%
- FY2020-FY2021 transition share: 47.6%
- Permitted inference: Descriptive persistence patterns only; emphasize company concentration and year imbalance.

## Reconciliation

- Maximum absolute DuPont identity gap: 2.842e-14
- Maximum absolute Shapley reconciliation gap: 5.684e-14
- Power BI fields: 60 of 60 frozen contract fields
- Complete field-level schema and descriptions: `data/processed/b3_mart_schema.csv`
