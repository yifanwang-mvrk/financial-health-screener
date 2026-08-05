# Q1 Data and Analytical Dictionary

Last updated: 2026-08-05

## Inputs

### `data/reference/company_universe.csv`

Grain: one company.

Contains the active A1 census, stable company ID, SEC CIK where available, provisional listing date, company status, operating-model classification, Q1 candidate and B1 Pilot flags, Q2 event flag, and explicit exclusion rationale. `status_group` describes issuer status; `analysis_scope_group` separately describes the project's current use of the company.

### `data/reference/events.csv`

Grain: one candidate event.

Contains the first-public event date, date basis, effective date, source, confidence, theoretical and verified pre-event coverage, provisional Q2 qualification, and exclusion reason. A3 has verified all 14 records; formal Gate 2 remains pending after B5.

### `data/reference/q1_formal_sample_v1.csv`

Grain: one formal Q1 company.

Contains the Gate1-v1.0 21-company Path A sample, frozen peer group, FY2018-FY2024 window, A3 available years, Pilot membership, conflict/review evidence, and selection basis.

### `data/reference/q1_gate1_sample_decisions.csv`

Grain: one A1 Q1 candidate.

Records the inclusion or exclusion decision and A3 evidence basis for all 40 candidates.

### `data/reference/q1_field_contract_v1.csv`

Grain: one canonical field.

Freezes formal-layer inclusion, field role, flow/stock behavior, sign, duration, and requiredness. Noncore fields remain in history but are not loaded into formal Q1 marts.

### `data/reference/q1_powerbi_mart_contract_v1.csv`

Grain: one frozen Power BI mart field.

Defines the 60 required fields and assigns all research calculations to SQL; DAX recalculation is prohibited.

### `data/raw/sec/` and `data/raw/sec/b2_formal_manifest.csv`

Contains gzip-compressed official SEC `companyfacts` and `submissions` JSON. The B2 formal manifest records ticker, CIK, artifact type, source URL, SHA-256 checksum, and fetch time for 42 artifacts covering all 21 frozen companies.

### `data/reference/a2_probe_scope.csv`

Grain: one formal A2 probe company.

Records the CHWY and EBAY probe roles, evidence-based selection reasons, and the decision not to add a third distress case at A2.

### `data/normalized/a2_annual_financial_facts_sample.csv`

Grain: one probe company x canonical field x fiscal period x filing version.

Contains the formal A2 annual sample with source tag, raw and standardized values, unit, period, duration, accession, filing date, fiscal metadata, and load timestamp.

### `data/processed/a2_field_probe.csv`

Grain: one probe company x A2 canonical field.

Audits configured and observed tags, taxonomies, units, periods, filing versions, shared-map reuse, fiscal-year issues, and potential company exceptions.

### `data/processed/a2_latest_restated_sample.csv`

Grain: one probe company x fiscal year x canonical field.

Selects the latest valid annual filing available at the A2 run date after unit and duration validation, with configured tag priority as the same-date tie-breaker.

### `data/processed/a2_concept_conflicts_sample.csv`

Grain: one discarded probe fact value.

Records the winner and discarded tags, values, accessions, filing dates, relative difference, and resolution rule. Gate 1 freezes low at no more than 0.5%, medium above 0.5% through 5%, and high above 5%.

### `data/processed/a3_coverage_company_field_year.csv`

Grain: one A1 Q1 candidate x fiscal year x core field.

Records FY2018-FY2024 availability, winner metadata, version count, conflict count, and latest-restated selectability for Revenue, Net Income, Assets, and Equity.

### `data/processed/a3_company_coverage_summary.csv`

Grain: one A1 Q1 candidate.

Summarizes complete annual years, expected-listing-window coverage, prior balances, conflicts, override need, manual review cost, failure reason, and Gate 1 sampling viability.

### `data/processed/a3_h1_transition_audit.csv`

Grain: one company x transition center year for FY2019-FY2023.

Contains the frozen H1 eligibility components, exact Shapley contributions, driver label, leverage contribution share, forward outcomes, eligibility, and exclusion reason. Gate 1 freezes Tier B on the 21-company formal sample.

### `data/processed/a3_q2_feasibility_scan.csv`

Grain: one A1 event candidate.

Records real pre-event quarter counts, three-statement metadata coverage, filing-date/PIT feasibility, YTD reconstruction need, eligible peer controls, manual cost, provisional qualification, and specific exclusions.

### `data/normalized/financial_facts.csv`

Grain: one formal company x accession x reporting period x canonical field x source tag x unit.

Retains the Gate 1 physical schema for the 21-company B2 layer, including accession number, form, filing date, period start/end, fiscal year/period, duration, canonical field, source tag, raw and standardized values, unit, source URL, and load timestamp. The three frozen noncore fields are excluded. Historical versions are retained; this table is not the analytical mart.

### `data/normalized/b1_financial_facts.csv`

Grain: one Pilot company x accession x reporting period x canonical field x source tag x unit.

Freezes the six-company B1 filing-level snapshot separately from the formal B2 main table.

### `data/normalized/b1_annual_facts_unmapped.csv`

Grain: one Pilot company x raw XBRL tag x annual filing version.

Stores the normalized pre-mapping stage so concept mapping and sign handling are independently reproducible.

### `data/reference/company_overrides.csv`

Grain: one company x fiscal year x canonical field override.

Contains only observed, accession-backed exceptions after the shared map is exhausted. The active B2 exceptions cover ABNB filing-table free cash flow values, CVNA documented operating-income derivations, and DASH/ETSY CapEx aggregations. B1 uses only its DASH/ETSY subset.

### `data/processed/b2_candidate_rejections.csv`

Grain: one rejected formal annual fact candidate.

Records unit, annual-duration, or domain failures before latest-restated selection. Rejection never substitutes a sentinel value.

### `data/processed/metric_flags.csv`

Grain: one formal company x fiscal year x metric x flag code.

Stores scripted null/sentinel, missing-prior, nonpositive-equity, zero-denominator, forward-year, source-conflict, unit, and sign/domain checks for B2.

### `data/processed/b2_company_field_year_coverage.csv` and `data/processed/b2_failures.csv`

Grain: one formal company x field x fiscal year for coverage; one failed required observation for failures.

The coverage table makes inclusion, requiredness, and availability traceable. The failure table retains the formal schema even when empty; B2 has no missing required company-year field.

### `data/processed/b2_stage_audit.json`

Grain: one B2 rebuild.

Records formal counts, quality rules, immutable Gate 1 contract hashes, scripted-generation status, and pass/fail checks.

### `data/processed/b1_candidate_rejections.csv`

Grain: one rejected annual fact candidate.

Records unit, annual-duration, or domain failures before latest-restated selection.

### `data/processed/b1_metric_flags.csv`

Grain: one company x fiscal year x metric x flag code.

Stores scripted missing-prior, nonpositive-equity, zero-denominator, forward-year, source-conflict, unit, and sign/domain flags.

### `data/processed/b1_pilot_annual_company_metrics.csv` and related B1 marts

Grain: one Pilot company x fiscal year, except peer summaries and the one-row evidence summary.

These SEC-derived marts provide Pilot DuPont metrics, peer context, exact Shapley contributions, frozen H1 eligibility, and Evidence Tier output. They prove the pipeline path only; B3 will build the formal seven marts on the 21-company B2 layer.

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

Grain: one formal company x fiscal year x canonical field.

Selects the latest valid annual filing under the frozen version rule, with source-tag priority as the deterministic tie-breaker. It preserves the winning accession and source metadata.

### `data/processed/sec_concept_conflicts.csv`

Grain: one automatically detected non-winning formal fact value.

Records the winning and discarded tags/versions, values, relative difference, severity, and resolution rule. Different values are never silently discarded.

### `data/processed/b2_sec_manual_reconciliation.csv`

Grain: one selected SEC canonical fact.

Records the formal selected fact and any explicit mapping or exception review evidence. Review records do not silently overwrite analytical outputs.

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
