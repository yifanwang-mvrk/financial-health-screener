# Financial Health Screener

A reproducible SEC-to-Power BI research pipeline that explains how e-commerce companies produce return on equity and whether ROE improvements appear operationally or leverage driven.

## Research Questions

**Q1-A. Financial quality:** Is a company's ROE driven by net margin, asset turnover, or the equity multiplier? Can similar ROE outcomes have materially different quality?

**H1. Persistence:** Are leverage-driven ROE improvements less persistent one year later than operating-driven improvements?

This release does not produce an investment recommendation or a black-box risk score.

## Current Release

Status: **Phase A and Q1 Portfolio Release v1.0 complete; Gate 2 closed as Tier C / No-Go**

Data scope:

- 6 public e-commerce or platform companies
- Fiscal years 2021-2023
- 18 company-year financial statement rows
- 26-company census and 5-event candidate census
- 12 cached official SEC JSON artifacts for the six-company release
- 599 accession-level normalized SEC facts and 222 cutoff-eligible canonical selections
- USD millions, with company-specific filing mappings
- Latest fiscal period end in the dataset: 2024-01-28

Analysis peer groups:

- Inventory-led E-commerce: AMZN, CHWY
- Marketplace / Platform: BKNG, DASH, EBAY, ETSY

The peer groups are analytical operating-model categories. With only six companies, peer comparisons are descriptive rather than industry estimates.

Release verification: the end-to-end rebuild completes successfully and all 16 automated tests pass.

Gate 2 result: none of the five event candidates has a verified point-in-time pre-event quarterly panel. Under the v3 downgrade rule, Q2 and Q3 are not started and the project ends successfully with the complete Q1 product.

## Method

The core DuPont identity is:

```text
ROE = Net Margin x Asset Turnover x Equity Multiplier

Net Margin        = Net Income / Revenue
Asset Turnover    = Revenue / Average Assets
Equity Multiplier = Average Assets / Average Equity
ROE               = Net Income / Average Equity
```

Average assets and average equity use consecutive fiscal-year-end balances. If prior-year balances are unavailable or average equity is nonpositive, the affected metric is explicitly invalidated.

Exact three-factor Shapley decomposition attributes each valid annual change in ROE to:

- Margin contribution
- Asset-turnover contribution
- Equity-multiplier contribution

The three contributions reconcile to the observed change in ROE. H1 eligibility then requires positive average equity at `t-1`, `t`, and `t+1`; positive prior ROE; an ROE improvement; valid DuPont components; and an observable next-year outcome.

## Results

- 11 of 18 company-years have valid average-balance DuPont metrics.
- 5 annual transitions have valid Shapley decompositions.
- AMZN and CHWY show the central Q1-A result: their 2023 ROE is broadly comparable, but AMZN relies on a 5.3% net margin and moderate turnover/leverage, while CHWY combines a 0.4% margin with 3.91x turnover and an 8.51x equity multiplier.
- BKNG is the principal counterexample: its extreme 2023 ROE is mathematically reconciled but driven by a near-zero average equity base, so it is treated as a denominator warning rather than superior operating quality.
- H1 is **Evidence Tier C** with zero eligible transitions. No persistence group test is reported. Valid improvements either begin from nonpositive ROE or lack an observable next-year outcome.

Full findings: [`docs/q1_analysis_report.md`](docs/q1_analysis_report.md)

![2023 DuPont profiles](docs/assets/q1/02_2023_dupont_profiles.png)

## Power BI Executive Overview

The B5 release adds a single-page interactive report built from `data/processed/q1_powerbi_mart.csv` only. Power BI is used for presentation and filtering; it does not recalculate the SQL-owned financial definitions.

The page includes:

- company, peer-group, and fiscal-year slicers
- ROE, net margin, asset turnover, and equity multiplier KPIs
- company ROE versus peer-median trend
- exact Shapley DuPont contributions, with `0.10 = 10 percentage points`
- dominant ROE driver, H1 Evidence Tier, and H1 sample status
- permitted-inference, quality-warning, and comparability notes

The page was reconciled to the mart for the default AMZN FY2023 view and tested against two edge cases: BKNG FY2023 exposes the near-zero-equity warning, while ETSY FY2023 keeps invalid ROE blank rather than displaying zero.

![Q1 Power BI Executive Overview](powerbi/financial_health_screener_q1_powerbi.jpg)

Reference export: [`powerbi/Financial_Health_Screener_Q1_Executive_Overview.pbix`](powerbi/Financial_Health_Screener_Q1_Executive_Overview.pbix)

Power BI Service report: [Financial Health Screener Q1 Executive Overview](https://app.powerbi.com/groups/me/reports/fb9d94b1-fc87-484a-9282-2895f48b80fa/4ffbaf6ac660aec51266?experience=power-bi)

The operating-profile scatter and other cohort views remain available as reproducible static charts under `docs/assets/q1/`; the interactive page intentionally stays focused on the selected company-year decision path.

## CV-Ready Summary

> Built a reproducible SEC-Python-DuckDB financial research pipeline and interactive Power BI report for six public e-commerce companies and 18 company-years, retaining accession-level evidence and engineering average-balance DuPont metrics, exact Shapley ROE decomposition, peer benchmarks, evidence-tier controls, quality flags, and automated tests.

## Architecture

```text
26-company and event census
        -> cached SEC companyfacts and submissions JSON
        -> accession-level normalized annual facts
        -> latest-restated selection and reconciliation
        -> frozen manually verified Q1 financial statements
        -> Python validation
        -> DuckDB core tables
        -> SQL average-balance metrics
        -> exact Shapley contributions
        -> H1 eligibility and evidence-tier audit
        -> frozen analytical marts
        -> notebooks, static charts, Power BI mart
```

Python orchestrates SEC extraction, normalization, reconciliation, validation, database execution, exports, EDA, and charts. SQL owns the financial definitions, peer comparisons, driver labels, persistence outcomes, and sample audit. Power BI is restricted to presentation logic and consumes only `data/processed/q1_powerbi_mart.csv`.

## Repository Guide

| Path | Role |
| --- | --- |
| `data/reference/company_universe.csv` | Auditable 26-company census, status, model, and scope flags |
| `data/reference/events.csv` | Candidate distress-event census and Gate 2 eligibility evidence |
| `data/raw/sec/` | Cached official SEC companyfacts and submissions JSON plus manifest |
| `data/normalized/financial_facts.csv` | Annual accession-level SEC fact history with tags, units, and filing dates |
| `data/raw/financial_statements_raw.csv` | Manually verified company-year financial facts and source notes |
| `src/build_phase_a_release.py` | Rebuilds the census, SEC evidence, restatement selection, coverage, and Gate 2 record |
| `src/build_q1_v3_pipeline.py` | Validates inputs, executes SQL, and exports marts |
| `src/build_q1_analysis_outputs.py` | Builds EDA tables, static charts, and notebooks |
| `sql/01_core_tables.sql` to `sql/07_q1_powerbi_mart.sql` | Rebuildable research logic |
| `data/processed/q1_powerbi_mart.csv` | Sole Power BI input table |
| `notebooks/` | Executed source, quality, and Q1 analysis notebooks |
| `tests/` | SEC evidence, accounting identity, research-rule, and release-contract tests |
| `docs/` | Research design, data dictionary, limitations, analysis report, and reconciliation |
| `powerbi/` | B5 report export, final screenshot, build notes, and reconciliation record |

The earlier `financial_health_screener_mvp.sql`, `build_mvp_pipeline.py`, and risk-ranking outputs are retained as legacy learning artifacts. They are not the v3 research product.

## Reproduce

Run from the repository root:

```bash
.venv/bin/python src/check_financial_statements.py
.venv/bin/python src/build_q1_release.py
.venv/bin/python -m unittest discover -s tests -p 'test_*.py' -v
```

Optional notebook execution:

```bash
.venv/bin/jupyter nbconvert --to notebook --execute --inplace notebooks/01_source_probe.ipynb
.venv/bin/jupyter nbconvert --to notebook --execute --inplace notebooks/02_data_quality.ipynb
.venv/bin/jupyter nbconvert --to notebook --execute --inplace notebooks/03_q1_analysis.ipynb
```

To intentionally regenerate notebook source before execution, run `src/build_q1_analysis_outputs.py --refresh-notebooks`.

## Evidence Boundary

- Six companies and three fiscal years do not support industry-wide inference.
- FY2021 lacks prior-year balances, so average-balance DuPont metrics begin in FY2022.
- FY2023 lacks a next-year outcome, which prevents evaluation of otherwise valid improvements.
- The SEC evidence layer uses a 2024-04-30 source cutoff and is not point-in-time investor information.
- Seven SEC-to-manual differences remain explicit company-mapping reviews; they do not overwrite the frozen Q1 release.
- Fiscal calendars, revenue recognition, acquisitions, buybacks, non-operating gains, and issuer-specific definitions limit direct comparability.
- Q2/Q3 are cancelled for this release because no event has verified point-in-time quarterly coverage.
- The project is analytical decision support, not investment advice.

See [`docs/limitations.md`](docs/limitations.md) and [`docs/research_design.md`](docs/research_design.md) for the full boundary.
