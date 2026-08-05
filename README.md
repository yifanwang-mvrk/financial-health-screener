# Financial Health Screener

A reproducible SEC-to-Power BI research project that explains how e-commerce companies produce return on equity and, if the required evidence exists, tests whether leverage-driven improvements are less persistent than operating-driven improvements.

## Research Questions

**Q1-A. Financial quality:** Is ROE driven by net margin, asset turnover, or the equity multiplier? Can similar ROE outcomes have materially different financial quality?

**Q1-H1. Persistence:** Are leverage-driven ROE improvements less persistent one year later than operating-driven improvements?

**Conditional Q2/Q3:** Only after the formal event-coverage gate, study distress event paths and determine whether any supported signals qualify for a current peer screen.

The project does not provide investment recommendations, target prices, return predictions, or a black-box risk score.

## Current Status

Status: **B4 Analytical Release is complete and is the CV-ready minimum deliverable. B5 Power BI Product Release is complete — Q1 Portfolio Release v1.0 is published. Gate 2 remains pending.**

Data as of: **2026-08-05**

The frozen execution order is:

```text
A0E -> A1 -> A2 -> A3 -> Gate 1 -> B1 -> B2 -> B3 -> B4 -> B5 -> Gate 2
```

The repository currently contains:

- A completed 50-company A1 census with 40 Q1 candidates, satisfying the approximately 30-40 stopping range.
- Fourteen sourced event candidates, all verified in A3; 12 meet the provisional Tier A feasibility criteria and two have specific exclusions.
- A completed CHWY/EBAY SEC source probe and a separate six-company accession-level Pilot cache.
- A completed 40-company FY2018-FY2024 coverage scan, 200-row H1 transition audit, and 14-event quarterly/PIT feasibility scan.
- A passed Gate 1 contract with 21 formal companies, FY2018-FY2024, three groups of seven, H1 Tier B, frozen source/version rules, and a 60-field Power BI mart contract.
- A revalidated six-company B1 pipeline that rebuilds SEC raw JSON through normalized facts, explicit conflicts/overrides, latest-restated values, metric flags, DuckDB, and Pilot marts.
- A completed B2 expansion that applies the unchanged Gate1-v1.0 rules to all 21 formal companies for FY2018-FY2024, with FY2017 loaded only for opening balances.
- A completed B3 analytical layer with all seven formal SQL marts, 137 formal company-years, exact DuPont/Shapley reconciliation, frozen-rule H1 Tier B results, and an exact 60-field Power BI mart.
- A completed B4 standalone analytical release with formal quality EDA, eight static charts, two executed notebooks, two-company filing reconciliation, a Tier B research conclusion, CV bullet, and interview narrative.
- A completed B5 Power BI Executive Overview rebuilt on the frozen 137-row, 60-field formal mart, reconciled, saved in Power BI Service, and exported as `.pbix` and screenshot. The retained FY2021-FY2023 Pilot prototype is superseded and survives only in git history.

The formal B4 release is independently presentable and may be used on a CV. B5 completes Q1 Portfolio Release v1.0.

## Pilot Scope

- Companies: AMZN, BKNG, CHWY, DASH, EBAY, ETSY
- Years: FY2021-FY2023
- Rows: 18 company-years
- Pilot peer groups:
  - Inventory-led E-commerce: AMZN, CHWY
  - Marketplace / Platform: BKNG, DASH, EBAY, ETSY
- SEC cache: 12 companyfacts/submissions artifacts
- Normalized evidence: 570 mapped accession-level facts and 225 latest/derived canonical selections

The six-company peer comparisons are descriptive examples only. The Pilot has zero eligible H1 transitions. Gate 1 freezes H1 Tier B on the formal sample: 21 eligible transitions across 10 companies, including four leverage-driven transitions across three companies.

## Gate Status

- **Gate 1: passed.** Path A is frozen at 21 companies, FY2018-FY2024, seven companies per retained group, H1 Tier B, and the versioned data/schema/Power BI contracts.
- **B1: passed.** All six companies run through one SEC-to-DuckDB entry; DASH/ETSY CapEx overrides are filing-backed, error logs are clear, and DuPont/Shapley reconcile.
- **B2: passed.** The formal layer rebuilds 42 SEC artifacts into 4,780 filing-level facts and 1,959 latest/derived facts; all 21 companies are covered and no required company-year field is missing.
- **B3: passed.** Seven formal marts rebuild 137 company-years; DuPont and Shapley gaps remain below `1e-10`, H1 matches the frozen 21-transition/10-company Tier B audit, and the Power BI mart matches all 60 contracted fields.
- **B4: passed.** Formal analytical inputs are checksummed; quality EDA, Q1-A profiles, Tier B persistence analysis, company cases, eight static charts, two executed notebooks, two-company filing reconciliation, and release narrative are complete.
- **B5: passed.** The single-page Power BI Executive Overview was rebuilt on the frozen 137-row mart, every visual reconciled against the mart, and the Service report saved and exported as reference `.pbix` and screenshot. Q1 Portfolio Release v1.0 is published.
- **Gate 2: pending.** A3 recommends Tier A feasibility from 12 qualified events, but no Q2 work is authorized until the formal Gate 2 decision is made.

## Method

```text
ROE = Net Margin x Asset Turnover x Equity Multiplier

Net Margin        = Net Income / Revenue
Asset Turnover    = Revenue / Average Assets
Equity Multiplier = Average Assets / Average Equity
ROE               = Net Income / Average Equity
```

Average assets and equity use consecutive fiscal-year-end balances. Metrics are invalidated when required balances are missing or average equity is nonpositive.

Exact three-factor Shapley decomposition attributes each valid annual ROE change to margin, asset turnover, and equity multiplier. The contributions reconcile exactly to the observed change. H1 eligibility retains the frozen positive-equity, positive-base-ROE, positive-improvement, valid-components, and observable-forward-year rules.

## Formal Findings

- 104 of 137 formal company-years have valid average-balance DuPont metrics.
- ABNB and LOVE both produced roughly 36% FY2022 ROE, but ABNB relied on a 22.5% margin and 0.56x turnover while LOVE relied on a 9.5% margin and 1.84x turnover.
- BKNG shows why positive but near-zero average equity can make mathematically correct ROE mechanically extreme and economically unstable.
- H1 remains Tier B: 21 eligible transitions across 10 companies, including only four leverage-driven transitions across three companies.
- The descriptive direction does **not support H1**. Median next-year peer-relative ROE change is +35.2 percentage points for leverage-driven improvements versus -11.9 points for operating-driven improvements.
- This is not validation or a balanced-panel rejection: FY2020-FY2021 contain 47.6% of eligible transitions, and leverage cases occur only in FY2019 and FY2021.

Formal analysis: [`docs/q1_analysis_report.md`](docs/q1_analysis_report.md)

![Formal peer-group DuPont distributions](docs/assets/q1/02_peer_group_dupont_distributions.png)

![Tier B persistence outcomes](docs/assets/q1/05_h1_peer_relative_outcomes.png)

## Power BI Executive Overview (B5)

The one-page Executive Overview is built on the frozen 137-row, 60-field formal `q1_powerbi_mart` — the same 21-company sample as the rest of Q1, not the earlier six-company Pilot snapshot.

The page includes company, peer-group (`formal_peer_group`), and fiscal-year slicers; four DuPont KPIs; company versus peer-median ROE trend; Shapley change contributions; selected-year interpretation (H1 Evidence Tier, dominant driver, exclusion reason); and quality/comparability notes. All research logic (DuPont, peer medians, Shapley, driver labels, H1 outcomes) is computed in SQL; Power BI only presents and filters it. See [`powerbi/README.md`](powerbi/README.md) for the full field mapping and reconciliation checklist.

![Q1 Power BI Executive Overview](powerbi/financial_health_screener_q1_powerbi.jpg)

Reference export: [`powerbi/Financial_Health_Screener_Q1_Executive_Overview.pbix`](powerbi/Financial_Health_Screener_Q1_Executive_Overview.pbix)

Power BI Service report: [Financial Health Screener Q1 Executive Overview](https://app.powerbi.com/groups/me/reports/fb9d94b1-fc87-484a-9282-2895f48b80fa/4ffbaf6ac660aec51266?experience=power-bi)

## Repository Guide

| Path | Role |
| --- | --- |
| `data/reference/company_universe.csv` | Active A1 company census and Pilot flag |
| `data/reference/events.csv` | Active A1 event candidate census |
| `data/reference/a2_probe_scope.csv` | Formal CHWY/EBAY A2 probe selection and reasons |
| `data/reference/a3_scan_requirements.csv` | Frozen A2 output describing the required A3 scan metrics |
| `data/reference/q1_analysis_scope.csv` | Six-company B1 Pilot scope only |
| `data/reference/q1_formal_sample_v1.csv` | Gate1-v1.0 formal 21-company sample and frozen FY2018-FY2024 window |
| `data/reference/q1_gate1_sample_decisions.csv` | Inclusion/exclusion evidence for all 40 Q1 candidates |
| `data/reference/q1_field_contract_v1.csv` | Frozen canonical and noncore field contract |
| `data/reference/q1_powerbi_mart_contract_v1.csv` | Frozen one-page mart fields and SQL/DAX ownership |
| `data/raw/sec/` | Cached SEC companyfacts/submissions JSON |
| `data/raw/sec/b2_formal_manifest.csv` | Checksummed 42-artifact manifest for the formal 21-company layer |
| `data/normalized/a2_annual_financial_facts_sample.csv` | Formal A2 two-company filing-level annual facts sample |
| `data/normalized/b1_financial_facts.csv` | Frozen six-company Pilot filing-level fact snapshot |
| `data/normalized/financial_facts.csv` | Formal B2 annual accession-level SEC fact history |
| `data/processed/a2_field_probe.csv` | Formal A2 field/tag/unit/period/version audit |
| `data/processed/a2_concept_conflicts_sample.csv` | Formal A2 winner/discarded conflict sample |
| `data/processed/a3_company_coverage_summary.csv` | All-candidate FY2018-FY2024 coverage, prior-balance, conflict, override, and cost summary |
| `data/processed/a3_h1_transition_audit.csv` | Frozen-rule A3 H1 eligibility, Shapley, outcomes, and exclusions |
| `data/processed/a3_q2_feasibility_scan.csv` | Event-quarter, cash-flow, PIT, control, cost, and qualification evidence |
| `data/processed/a3_recommendation.json` | A3 evidence input retained beneath the formal Gate 1 decision |
| `data/processed/b1_pilot_coverage.csv` | Six-company coverage snapshot; not the A3 full-candidate report |
| `data/processed/b1_metric_flags.csv` | Scripted Pilot metric-quality flags |
| `data/processed/b1_pilot_*` | SEC-derived Pilot metrics, peer, Shapley, H1, and stage audit outputs |
| `data/processed/sec_latest_restated_long.csv` | Formal B2 latest-restated canonical facts |
| `data/processed/sec_concept_conflicts.csv` | Formal B2 winner/discarded value evidence |
| `data/processed/metric_flags.csv` | Formal B2 metric-quality flags |
| `data/processed/b2_company_field_year_coverage.csv` | Formal company/field/year coverage and requiredness audit |
| `data/processed/b2_failures.csv` | Formal required-field failure list; currently empty |
| `data/processed/q1_annual_company_metrics.csv` | Formal 137-row annual DuPont and financial-quality mart |
| `data/processed/q1_dupont_contributions.csv` | Formal exact Shapley transition mart |
| `data/processed/q1_driver_persistence.csv` | Formal next-year raw and peer-relative outcome mart |
| `data/processed/q1_h1_sample_audit.csv` | Frozen-rule eligibility, exclusion, year, and concentration audit |
| `data/processed/q1_peer_summary.csv` | Formal peer-year medians, quartiles, and valid sample sizes |
| `data/processed/q1_company_vs_peer.csv` | Formal company positions relative to peer benchmarks |
| `data/processed/q1_powerbi_mart.csv` | Formal 137-row, 60-field B5 consumption table |
| `data/processed/b3_mart_schema.csv` | Field-level grain, type, and description for B3 outputs |
| `data/processed/b4_release_manifest.csv` | Checksummed frozen inputs for the analytical release |
| `data/processed/b4_stage_audit.json` | B4 DoD, chart, notebook, reconciliation, and narrative audit |
| `data/processed/q1_research_findings.csv` | Formal Q1-A, H1, counterexample, and falsification findings |
| `data/processed/b4_filing_reconciliation.csv` | AMZN/CHWY filing-to-pipeline reconciliation evidence |
| `data/reference/company_overrides.csv` | Filing-backed exceptions used only when the shared concept map fails |
| `src/build_b1_pilot.py` | Rebuilds the current six-company Pilot evidence layer |
| `src/build_b2_formal_sample.py` | Rebuilds the frozen 21-company B2 data layer |
| `src/q1_annual_pipeline.py` | Gate 1-compliant staged SEC annual pipeline used by B1 and B2 |
| `src/q1_formal_pipeline.py` | B2 formal-sample orchestration, coverage, QA, and audit outputs |
| `src/phase_a_evidence.py` | Retained A1-A3 and earlier Pilot evidence helpers |
| `src/build_b3_analytical_marts.py` | Rebuilds B2 and all formal B3 SQL marts in frozen order |
| `src/build_q1_v3_pipeline.py` | Formal B3 orchestration, export, schema dictionary, and DoD audit |
| `src/build_b4_analytical_release.py` | Rebuilds the complete standalone analytical release |
| `src/build_q1_analysis_outputs.py` | Formal EDA, charts, notebooks, reports, reconciliation, and B4 audit |
| `sql/01_core_tables.sql` to `sql/07_q1_powerbi_mart.sql` | Formal implementation of the frozen analytical method |
| `tests/` | Pilot, formal data, accounting, evidence, and method contracts |
| `powerbi/` | Formal B5 report export, screenshot, notes, and reconciliation |

Legacy composite risk-ranking files remain labelled learning artifacts and are not part of the v3 method.

## Rebuild B1-B4

```bash
.venv/bin/python src/build_b1_pilot.py
.venv/bin/python src/build_b2_formal_sample.py
.venv/bin/python src/build_b3_analytical_marts.py
.venv/bin/python src/build_b4_analytical_release.py
.venv/bin/python -m unittest discover -s tests -p 'test_*.py' -v
```

## Rebuild Completed Phase A Stages

```bash
.venv/bin/python src/build_a1_census.py
.venv/bin/python src/build_a2_source_probe.py
.venv/bin/python src/build_a3_coverage_audit.py
```

## Formal Completion Criteria

- **B4 minimum CV deliverable:** achieved. The formal analysis, QA, static outputs, executed notebooks, reconciliation, README, CV bullet, and interview narrative are complete.
- **B5 Portfolio Release v1.0:** achieved. Formal B4 plus the reconciled single-page Power BI report, frozen PBIX reference, screenshot, README, CV bullet, and five-minute narrative are complete.
- **Q2/Q3:** conditional; their existence and form are determined only by Gate 2 and Gate 3 evidence.

See [`docs/project_status.md`](docs/project_status.md), [`docs/release_closure_audit.md`](docs/release_closure_audit.md), and [`docs/limitations.md`](docs/limitations.md) for the current execution boundary.
