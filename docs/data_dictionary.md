# Q1 Pilot Analytical Data Dictionary

Last updated: 2026-08-05

## Inputs

### `data/reference/company_universe.csv`

Grain: one company.

Contains the active A1 census, stable company ID, SEC CIK where available, provisional listing date, company status, operating-model classification, Q1 candidate and B1 Pilot flags, Q2 event flag, and explicit exclusion rationale. `status_group` describes issuer status; `analysis_scope_group` separately describes the project's current use of the company.

### `data/reference/events.csv`

Grain: one candidate event.

Contains the first-public event date, date basis, effective date, source, confidence, theoretical and verified pre-event coverage, Q2 qualification, and exclusion reason. The 14 records complete the A1 event census. Their unverified quarterly coverage leaves Gate 2 pending until A3.

### `data/raw/sec/`

Contains gzip-compressed official SEC `companyfacts` and `submissions` JSON for the six Pilot companies. `manifest.csv` records ticker, CIK, artifact type, source URL, SHA-256 checksum, and fetch time.

### `data/normalized/financial_facts.csv`

Grain: one company x canonical field x reported annual fact version.

Retains taxonomy, source tag, priority, accession, filing date, form, period, duration, reported value, standardized value, unit, source URL, and load timestamp. Historical versions are retained; this table is not the analytical mart.

### `data/raw/financial_statements_raw.csv`

Grain: one company x fiscal year.

Contains standardized income-statement, balance-sheet, and cash-flow fields in USD millions, plus the fiscal period end, source type, URL, and company-year notes. Optional blanks represent unavailable or non-applicable fields; they are not silently converted to zero.

### `data/raw/sample_companies_master.csv`

Grain: one company.

Contains issuer identity, detailed business-model classification, scope flags, and original peer groups.

### `data/reference/q1_analysis_scope.csv`

Grain: one B1 Pilot company.

Adds the broader `analysis_peer_group` used for descriptive Q1 peer comparisons and records the comparability boundary.

### `data/reference/concept_map.csv`

Grain: one canonical financial concept.

Records canonical definitions, candidate SEC tags in priority order, statement type, flow/stock behavior, expected unit, sign treatment, duration rule, Q1 requirement status, applicability, and compatibility policy.

### `data/reference/concept_conflicts.csv`

Grain: one documented source or interpretation conflict.

Records severity, resolution status, and analytical effect for restatements, nonpositive equity, source gaps, boundary differences, and structural breaks.

### `data/processed/sec_latest_restated_long.csv`

Grain: one company x fiscal year x canonical field.

Selects the latest annual filing available by 2024-04-30, with source-tag priority as the deterministic tie-breaker. It preserves the winning accession and source metadata.

### `data/processed/sec_concept_conflicts.csv`

Grain: one automatically detected non-winning fact value.

Records the winning and discarded tags/versions, values, relative difference, severity, and resolution rule. Different values are never silently discarded.

### `data/processed/sec_manual_reconciliation.csv`

Grain: one selected SEC canonical fact.

Compares the SEC selection with the manually verified Pilot analytical value and labels each row `match`, `review_company_mapping`, or `manual_value_unavailable`. Review rows do not overwrite the Pilot mart.

### `data/processed/b1_pilot_coverage.csv`

Grain: one Pilot company x required canonical field.

Records FY2021-FY2023 Pilot year coverage and reconciliation counts. It is not the A3 all-candidate coverage report.

## SQL Marts

### `q1_latest_restated`

Grain: one company x fiscal year.

Purpose: selects the single manually verified latest comparative source row and documents the selection method. In this release, there is only one input version per company-year.

### `q1_annual_company_metrics`

Grain: one company x fiscal year.

Purpose: calculates average balances, DuPont components, profitability, liquidity, leverage, cash-flow metrics, growth, validity flags, and quality warnings.

Key fields:

| Field | Definition |
| --- | --- |
| `average_assets` | Mean of prior and current fiscal-year-end total assets |
| `average_equity` | Mean of prior and current fiscal-year-end total equity |
| `roe` | Net income divided by positive average equity; otherwise null |
| `net_margin` | Net income divided by revenue |
| `asset_turnover` | Revenue divided by average assets |
| `equity_multiplier` | Average assets divided by positive average equity |
| `dupont_roe` | Product of net margin, turnover, and multiplier |
| `dupont_identity_gap` | Reported ROE minus DuPont product; expected near zero |
| `current_ratio` | Current assets divided by current liabilities |
| `quick_ratio` | Current assets less inventory, divided by current liabilities; null when inventory is unavailable |
| `cash_ratio` | Cash and equivalents divided by current liabilities |
| `liabilities_to_assets` | Total liabilities divided by total assets |
| `operating_cash_flow_margin` | Operating cash flow divided by revenue |
| `free_cash_flow_margin` | Project free cash flow divided by revenue |
| `near_zero_average_equity_flag` | Absolute average equity below 2% of average assets |
| `quality_warnings` | Semicolon-delimited, human-readable metric and comparability warnings |

### `q1_dupont_contributions`

Grain: one company x transition-ending fiscal year.

Purpose: calculates exact three-factor Shapley contributions and driver labels.

Key fields:

| Field | Definition |
| --- | --- |
| `roe_change` | Current ROE less prior-year ROE |
| `contribution_margin` | Exact Shapley attribution to net-margin change |
| `contribution_turnover` | Exact Shapley attribution to asset-turnover change |
| `contribution_multiplier` | Exact Shapley attribution to equity-multiplier change |
| `contribution_sum` | Sum of the three Shapley contributions |
| `shapley_reconciliation_gap` | ROE change less contribution sum; expected near zero |
| `dominant_change_driver` | Largest absolute contribution for descriptive use |
| `h1_driver_group` | `leverage_driven`, `operating_driven`, `mixed_or_ambiguous`, or `not_improvement` |
| `leverage_contribution_share` | Positive multiplier contribution divided by total positive contributions |

### `q1_driver_persistence`

Grain: one company x transition-ending fiscal year.

Purpose: joins the current driver classification to next-year absolute and peer-relative outcomes.

Key fields: `next_year_roe_change`, `next_year_peer_relative_change`, `roe_reversal_flag`, and `rank_retention`.

### `q1_h1_sample_audit`

Grain: one company x candidate transition.

Purpose: applies every H1 eligibility rule and retains one exclusion reason per transition.

Key fields: `h1_eligible_flag`, `turnaround_from_loss`, `h1_sample_status`, prior/current/next average equity, prior/current/next ROE, and driver group.

### `q1_h1_exclusion_waterfall`

Grain: one H1 sample status.

Purpose: counts transitions and unique companies by final eligibility or exclusion reason.

### `q1_h1_evidence_summary`

Grain: one Pilot snapshot.

Purpose: calculates eligible transition and company counts, group counts, concentration, Evidence Tier, and permitted inference.

### `q1_peer_summary`

Grain: one analysis peer group x fiscal year.

Purpose: supplies peer medians for ROE, DuPont components, profitability, liquidity, leverage, and free cash flow.

### `q1_company_vs_peer`

Grain: one company x fiscal year.

Purpose: joins company metrics to peer medians and calculates differences and ROE percentile position.

### `q1_powerbi_mart`

Grain: one company x fiscal year.

Purpose: Pilot single-table input for the Executive Overview prototype. It contains research outputs already calculated in SQL so Power BI does not become a second financial-logic layer.

## EDA Outputs

- `q1_coverage_summary.csv`
- `q1_missingness_summary.csv`
- `q1_metric_flag_summary.csv`
- `q1_research_findings.csv`
- `b1_pilot_summary.json`

These files summarize the Pilot snapshot; the SQL marts remain the source of analytical truth for that snapshot.
