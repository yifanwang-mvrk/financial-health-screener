# Gate 1 Decision - Frozen Q1 Construction Contract

Decision version: Gate1-v1.0

Status: **Passed**

Owner: Yifan Wang

Freeze date: 2026-08-05

Evidence base: A2 SEC Source Probe and A3 Coverage / H1 / Q2 Feasibility Audit

This document freezes the Q1 construction contract required by the Execution Charter v3.0 and the Phase A/Q1 Master Execution Checklist. The existing six-company work remains a B1 Pilot snapshot. It is not the formal sample and does not override this decision.

## 1. Data Path and Formal Sample

**Frozen decision: Path A.**

A3 found 31 viable Q1 candidates after applying the A2 unit, duration, version, conflict, and prior-balance checks. After merging the two viable Hybrid issuers into Inventory-led E-commerce, the viable pools are 12 Marketplace / Platform, 7 Inventory-led E-commerce, and 12 DTC Brand. This supports the Path A target of approximately 18-24 companies and 6-8 companies per retained group.

The formal sample is **21 companies, 7 per peer group**, stored in `data/reference/q1_formal_sample_v1.csv`. The annual analysis window is **FY2018-FY2024**. The panel is explicitly unbalanced: a company enters only when a valid annual filing exists, and FY2017 may be loaded solely to provide an opening balance for FY2018 average-balance ratios.

| Formal peer group | Frozen companies |
| --- | --- |
| Marketplace / Platform | ABNB, BKNG, CARS, DASH, EBAY, ETSY, EXPE |
| Inventory-led E-commerce | AMZN, BYON, CHWY, CVNA, QVCGA, VRM, W |
| DTC Brand | BIRD, FIGS, LOVE, PTON, RVLV, SFIX, SNBR |

All 40 A1 Q1 candidates and their inclusion or exclusion basis are recorded in `data/reference/q1_gate1_sample_decisions.csv`. The six Pilot companies AMZN, BKNG, CHWY, DASH, EBAY, and ETSY are included in the formal sample but retain `b1_pilot_member = 1`; their prior outputs remain Pilot evidence until B1 is revalidated after this Gate.

## 2. Peer Groups

The frozen groups are:

1. Marketplace / Platform
2. Inventory-led E-commerce
3. DTC Brand

The provisional Hybrid group is cancelled as a standalone peer group. AMZN and BYON move to Inventory-led E-commerce because they own inventory and recognize a material direct-commerce revenue base. GROV remains excluded as a short-history boundary case. No new peer group may be added inside Q1 v1.0.

Peer statistics are descriptive benchmarks within this selected sample. They must not be described as industry-wide statistical estimates.

## 3. H1 Evidence Tier and Eligibility

**Frozen decision: Tier B; descriptive persistence patterns only.**

Reapplying the unchanged A3 eligibility rules to the 21-company formal sample yields:

- 21 eligible company-year transitions across 10 unique companies.
- 4 leverage-driven transitions across 3 companies.
- 17 operating-driven transitions across 10 companies.
- Maximum single-company share: 14.3% of all eligible transitions.
- Largest company share inside the leverage-driven group: 50.0%.
- FY2020-FY2021 share: 47.6%.
- 75.0% of leverage-driven transitions occur in FY2019.

Tier B is required because there are fewer than 15 independent companies, fewer than 40 transitions, and fewer than 8 companies in the leverage-driven group. No inferential group-test claim is allowed.

Eligibility remains frozen exactly as follows:

- Unit of analysis: company x fiscal-year transition; independent unit: company.
- Average equity at `t-1`, `t`, and `t+1` must be positive.
- `ROE_(t-1) > 0`.
- `ROE_t - ROE_(t-1) > 0`.
- DuPont components at `t-1` and `t` must be valid.
- `ROE_(t+1)` must be observable.
- Loss turnarounds are excluded from the main sample and retained only as illustrative cases.

These rules cannot be relaxed during B1-B5.

## 4. H1 Outcomes and Driver Rules

The main outcome is frozen as:

`next_year_peer_relative_change = (ROE_(t+1) - peer_median_ROE_(t+1)) - (ROE_t - peer_median_ROE_t)`

Secondary outcomes are `next_year_roe_change`, `roe_reversal_flag`, and `rank_retention`. The raw next-year ROE change must not replace the peer-relative main outcome.

ROE is decomposed as `net_margin x asset_turnover x equity_multiplier`. Exact three-factor Shapley contributions must sum to `delta_ROE` within numeric tolerance.

- `dominant_driver`: component with the largest absolute Shapley contribution; deterministic tie order is margin, turnover, multiplier.
- `leverage_driven`: multiplier contribution is positive and strictly greater than both operating contributions.
- `operating_driven`: margin or turnover contribution is positive and strictly greatest.
- `mixed_or_ambiguous`: no unique positive largest contribution or materially mixed direction.
- `leverage_contribution_share`: positive multiplier contribution divided by the sum of all positive contributions; null when the denominator is zero.

Driver labels and the continuous share must both be retained.

## 5. Canonical Fields

The field contract is versioned in `data/reference/q1_field_contract_v1.csv`.

Frozen extracted fields are:

- DuPont core: revenue, net income, total assets, total equity.
- Direct quality fields: operating income, total liabilities, current assets, current liabilities, cash and equivalents, inventory, total debt, operating cash flow, and capital expenditure.
- Derived field: free cash flow = operating cash flow - capital expenditure.

Gross profit, duplicate long-term debt, and shares outstanding are noncore for formal Q1 and are not loaded into the formal analytical layer. Their prior Pilot data and concept-map rows are retained for traceability; nothing is deleted from history.

## 6. Source, Version, Sign, and Duration Rules

**Canonical source:** SEC Companyfacts with accession-level history retained.

**Fallback:** the exact SEC filing/XBRL instance may be used only when Companyfacts is missing, conceptually ambiguous, or cannot reconcile to the consolidated annual filing. Every fallback must record accession, URL, source tag or filing line, value, reason, reviewer, and review date. Unaudited aggregators are not valid fallbacks.

**Latest-restated:** retain every valid filing version. For each company-period-field, validate unit, concept, domain, and flow/stock period first; then select the latest valid filing as of the project run date, using configured tag priority only to break otherwise valid ties. A same-filing unresolved ambiguity blocks that metric rather than choosing mechanically by filing date.

**Signs and missing values:** income and OCF preserve reported signs; CapEx is stored as a positive cash outflow; free cash flow is OCF minus CapEx; balance-sheet stocks preserve deficits where conceptually valid; inventory and debt are nonnegative; missing is never converted to zero without filing evidence.

**Duration:** annual flow facts must span 330-385 days. Stock facts must be instant facts at the issuer fiscal-year end. Fiscal year is assigned from the reporting period and issuer calendar, not calendar year or filing date. A 52/53-week year is valid inside the duration band.

**Conflict severity:**

`relative_difference = abs(discarded_value - winning_value) / max(abs(winning_value), 1e-9)`

- Low: at most 0.5%; log only after validation.
- Medium: above 0.5% and at most 5%; review and retain resolution evidence.
- High: above 5%; mandatory reconciliation before release.

A high difference is not automatically invalid when it is explained by a later comparative restatement. A conflict is blocking when a same-filing ambiguity, unit/domain/duration error, or unresolved filing reconciliation remains.

## 7. Company Overrides

A company override is allowed only when the shared concept map fails on an observed formal-sample filing and the consolidated filing supports one unambiguous treatment. It must be narrow, company/field-specific, version controlled, and contain accession-level evidence and rationale.

Overrides are not allowed to fill missing values from assumption, convert blank to zero, conceal a conflict, or improve a result. B2 may add overrides only for observed failures and must rerun conflict and quality reports after each addition.

## 8. Frozen Physical Schema

### `financial_facts`

Grain: one company x accession x reporting period x canonical field x source tag x unit.

Required columns: `company_id VARCHAR`, `ticker VARCHAR`, `accession_number VARCHAR`, `form VARCHAR`, `filing_date DATE`, `period_start DATE`, `period_end DATE`, `fiscal_year INTEGER`, `fiscal_period VARCHAR`, `duration_days INTEGER`, `canonical_field VARCHAR`, `taxonomy VARCHAR`, `source_tag VARCHAR`, `value_raw DOUBLE`, `value_standardized DOUBLE`, `unit VARCHAR`, `flow_or_stock VARCHAR`, `source_priority INTEGER`, `source_url VARCHAR`, `loaded_at TIMESTAMP`.

### `concept_conflicts`

Grain: one winning fact x one discarded fact.

Required columns: `company_id VARCHAR`, `fiscal_year INTEGER`, `canonical_field VARCHAR`, `winning_accession VARCHAR`, `winning_filing_date DATE`, `winning_source_tag VARCHAR`, `winning_value DOUBLE`, `discarded_accession VARCHAR`, `discarded_filing_date DATE`, `discarded_source_tag VARCHAR`, `discarded_value DOUBLE`, `relative_difference DOUBLE`, `conflict_severity VARCHAR`, `resolution_rule VARCHAR`, `resolution_status VARCHAR`, `review_note VARCHAR`, `created_at TIMESTAMP`.

### `metric_flags`

Grain: one company x fiscal year x metric x flag code.

Required columns: `company_id VARCHAR`, `fiscal_year INTEGER`, `metric_name VARCHAR`, `flag_code VARCHAR`, `flag_value BOOLEAN`, `severity VARCHAR`, `reason VARCHAR`, `source_fields VARCHAR`, `generated_at TIMESTAMP`.

The normalized tables retain all versions; `q1_latest_restated` is a separate selected-value layer. Processed CSVs may mirror these tables, but DuckDB is the analytical source of truth.

## 9. Frozen Power BI Mart Contract

Power BI consumes only `q1_powerbi_mart` at one company x fiscal year grain. The field-level contract is stored in `data/reference/q1_powerbi_mart_contract_v1.csv`.

The mart must contain:

- Identity and context: company ID, ticker, company name, formal peer group, fiscal year, period end, company status, sample status, data-as-of date, and comparability note.
- Four DuPont KPIs: ROE, net margin, asset turnover, equity multiplier, plus validity reasons.
- Peer context: peer medians, company-minus-peer differences, ROE percentile, and valid peer counts.
- Driver evidence: ROE change, all three Shapley contributions, contribution sum/gap, dominant driver, H1 driver group, and continuous leverage share.
- Persistence evidence: H1 eligibility/exclusion, primary and secondary outcomes, reversal/rank-retention flags, Tier, permitted language, and frozen sample counts/group summaries.
- Quality: metric flags, unresolved conflict counts, warnings, source-selection method/note, interpretation note, and limitation note.

SQL/DuckDB must calculate financial ratios, average balances, peer statistics, percentiles, Shapley contributions, driver labels, leverage share, H1 eligibility, outcomes, Evidence Tier, and quality flags. These calculations are forbidden in DAX. DAX is limited to simple display measures, filter context, selected labels, and formatting that do not recreate analytical logic.

The required page remains one Executive Overview with Company, Peer Group, and Fiscal Year slicers. Because peer medians are precomputed by peer-year in SQL, selecting a company must not recalculate the peer benchmark from the selected company alone.

## 10. Q2 Feasibility

**Frozen Gate 1 feasibility: Tier A candidate; authorization pending formal Gate 2 after B5.**

A3 verified 14 event candidates. Twelve have at least eight verified pre-event quarters, three-statement metadata, eligible peer controls, point-in-time filing metadata, and acceptable reconstruction cost. BOXD and FTCH have explicit coverage exclusions.

This conclusion authorizes no quarterly panel, TTM/YTD reconstruction, controls, false-positive analysis, or current risk screen. Formal Gate 2 is executed only after Q1 Portfolio Release v1.0 and may confirm or downgrade the Tier using refreshed event evidence.

## 11. Frozen Limitations Language

- Results are descriptive peer benchmarks for a selected 21-company sample, not industry-wide inference or investment advice.
- The FY2018-FY2024 panel is unbalanced because public history and filing availability differ.
- H1 is Tier B: only 10 independent companies, 4 leverage-driven transitions, and 3 leverage-group companies are eligible.
- Leverage evidence is concentrated: one company contributes 50% of leverage transitions and FY2019 contributes 75%.
- FY2020-FY2021 account for 47.6% of eligible transitions; peer-relative outcomes reduce but do not eliminate year effects.
- Latest-restated annual facts are retrospective and are not point-in-time observations.
- Negative or nonpositive average equity invalidates ROE; loss turnarounds are not part of the main H1 sample.
- Fiscal calendars, revenue-recognition models, restatements, acquisitions, and issuer status changes limit comparability.
- Missing fields are not zeros; unresolved conflicts or invalid denominators suppress the affected metric.
- Q2 remains a feasibility finding until formal Gate 2 and cannot be described as completed early-warning validation.

## 12. Change Control and Exit

Gate 1 is passed because Path, formal sample, years, peer groups, H1 Tier and rules, canonical fields, source/version rules, overrides, schema, Power BI mart, Q2 feasibility, and limitations are all frozen with A2/A3 evidence.

Any new Q1 idea after this freeze goes to backlog and cannot enter Q1 v1.0. The required next sequence is B1 revalidation, B2 sample expansion, B3 SQL marts, B4 Analytical Release, B5 Portfolio Release, then formal Gate 2.
