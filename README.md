# Financial Health Screener

A reproducible SEC-to-Power BI research project that explains how e-commerce companies produce return on equity and, if the required evidence exists, tests whether leverage-driven improvements are less persistent than operating-driven improvements.

## Research Questions

**Q1-A. Financial quality:** Is ROE driven by net margin, asset turnover, or the equity multiplier? Can similar ROE outcomes have materially different financial quality?

**Q1-H1. Persistence:** Are leverage-driven ROE improvements less persistent one year later than operating-driven improvements?

**Conditional Q2/Q3:** Only after the formal event-coverage gate, study distress event paths and determine whether any supported signals qualify for a current peer screen.

The project does not provide investment recommendations, target prices, return predictions, or a black-box risk score.

## Current Status

Status: **Gate 1, B1, and B2 passed. B3 formal analytical SQL marts are next; Gate 2 remains pending after B5.**

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
- A retained FY2021-FY2023 Pilot visualization prototype, which remains separate from the future B5 formal release.

The six-company analytical artifacts are retained as Pilot evidence. They are not the formal B4 minimum CV deliverable or the B5 Portfolio Release v1.0.

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
- **B3: next.** Build and validate the seven formal analytical SQL marts without changing the frozen H1, peer, source, or version rules.
- **Gate 2: pending after B5.** A3 recommends Tier A feasibility from 12 qualified events, but no Q2 work is authorized until the formal Gate 2 decision.

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

## Pilot Findings

- 11 of 18 Pilot company-years have valid average-balance DuPont metrics.
- Five Pilot transitions have valid Shapley decompositions.
- AMZN and CHWY illustrate that similar ROE can come from very different margin, turnover, and leverage profiles.
- BKNG illustrates why near-zero average equity can make ROE mechanically extreme and economically unstable.
- The Pilot cannot test H1 because it has zero eligible forward transitions.

Pilot analysis: [`docs/q1_analysis_report.md`](docs/q1_analysis_report.md)

![Pilot DuPont profiles](docs/assets/q1/02_2023_dupont_profiles.png)

## Power BI Pilot Prototype

The existing one-page Executive Overview consumes only `data/processed/q1_powerbi_mart.csv`. It demonstrates the required B5 interaction pattern but is not the formal B5 release because it uses the Pilot sample.

The page includes company, peer-group, and fiscal-year slicers; four DuPont KPIs; company versus peer-median ROE trend; Shapley change contributions; selected-year interpretation; and quality/comparability notes.

![Q1 Power BI Pilot Executive Overview](powerbi/financial_health_screener_q1_powerbi.jpg)

Reference Pilot export: [`powerbi/Financial_Health_Screener_Q1_Executive_Overview.pbix`](powerbi/Financial_Health_Screener_Q1_Executive_Overview.pbix)

Power BI Service Pilot report: [Financial Health Screener Q1 Executive Overview](https://app.powerbi.com/groups/me/reports/fb9d94b1-fc87-484a-9282-2895f48b80fa/4ffbaf6ac660aec51266?experience=power-bi)

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
| `data/reference/company_overrides.csv` | Filing-backed exceptions used only when the shared concept map fails |
| `src/build_b1_pilot.py` | Rebuilds the current six-company Pilot evidence layer |
| `src/build_b2_formal_sample.py` | Rebuilds the frozen 21-company B2 data layer |
| `src/q1_annual_pipeline.py` | Gate 1-compliant staged SEC annual pipeline used by B1 and B2 |
| `src/q1_formal_pipeline.py` | B2 formal-sample orchestration, coverage, QA, and audit outputs |
| `src/phase_a_evidence.py` | Retained A1-A3 and earlier Pilot evidence helpers |
| `src/build_q1_v3_pipeline.py` | Rebuilds Pilot SQL marts |
| `sql/01_core_tables.sql` to `sql/07_q1_powerbi_mart.sql` | Pilot implementation of the frozen analytical method |
| `tests/` | Pilot accounting, evidence, and method contracts |
| `powerbi/` | Pilot report export, screenshot, notes, and reconciliation |

Legacy composite risk-ranking files remain labelled learning artifacts and are not part of the v3 method.

## Rebuild B1 and B2

```bash
.venv/bin/python src/build_b1_pilot.py
.venv/bin/python src/build_b2_formal_sample.py
.venv/bin/python -m unittest discover -s tests -p 'test_*.py' -v
```

## Rebuild Completed Phase A Stages

```bash
.venv/bin/python src/build_a1_census.py
.venv/bin/python src/build_a2_source_probe.py
.venv/bin/python src/build_a3_coverage_audit.py
```

## Formal Completion Criteria

- **B4 minimum CV deliverable:** only after the completed B2 formal expansion and the B3 formal marts pass their documented DoD.
- **B5 Portfolio Release v1.0:** formal B4 plus the reconciled single-page Power BI report, frozen PBIX reference, screenshot, README, CV bullet, and five-minute narrative.
- **Q2/Q3:** conditional; their existence and form are determined only by Gate 2 and Gate 3 evidence.

See [`docs/project_status.md`](docs/project_status.md), [`docs/release_closure_audit.md`](docs/release_closure_audit.md), and [`docs/limitations.md`](docs/limitations.md) for the current execution boundary.
