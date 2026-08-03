# Financial Health Screener

A reproducible Python, DuckDB, SQL, and Power BI-ready research pipeline that explains how e-commerce companies produce return on equity and whether ROE improvements appear operationally or leverage driven.

## Research Questions

**Q1-A. Financial quality:** Is a company's ROE driven by net margin, asset turnover, or the equity multiplier? Can similar ROE outcomes have materially different quality?

**H1. Persistence:** Are leverage-driven ROE improvements less persistent one year later than operating-driven improvements?

This release does not produce an investment recommendation or a black-box risk score.

## Current Release

Status: **B4 Analytical Release**

Data scope:

- 6 public e-commerce or platform companies
- Fiscal years 2021-2023
- 18 company-year financial statement rows
- USD millions, with company-specific filing mappings
- Latest fiscal period end in the dataset: 2024-01-28

Analysis peer groups:

- Inventory-led E-commerce: AMZN, CHWY
- Marketplace / Platform: BKNG, DASH, EBAY, ETSY

The peer groups are analytical operating-model categories. With only six companies, peer comparisons are descriptive rather than industry estimates.

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

## Architecture

```text
manually verified 10-K mappings
        -> raw financial statements
        -> Python validation and normalization
        -> DuckDB core tables
        -> SQL average-balance metrics
        -> exact Shapley contributions
        -> H1 eligibility and evidence-tier audit
        -> frozen analytical marts
        -> notebooks, static charts, Power BI mart
```

Python orchestrates file loading, validation, database execution, exports, EDA, and charts. SQL owns the financial definitions, peer comparisons, driver labels, persistence outcomes, and sample audit. Power BI is restricted to presentation logic and consumes only `data/processed/q1_powerbi_mart.csv`.

## Repository Guide

| Path | Role |
| --- | --- |
| `data/raw/financial_statements_raw.csv` | Manually verified company-year financial facts and source notes |
| `data/reference/` | Q1 scope, canonical concept definitions, and conflict register |
| `src/build_q1_v3_pipeline.py` | Validates inputs, executes SQL, and exports marts |
| `src/build_q1_analysis_outputs.py` | Builds EDA tables, static charts, and notebooks |
| `sql/01_core_tables.sql` to `sql/07_q1_powerbi_mart.sql` | Rebuildable research logic |
| `data/processed/q1_powerbi_mart.csv` | Sole Power BI input table |
| `notebooks/` | Executed source, quality, and Q1 analysis notebooks |
| `tests/test_q1_v3_pipeline.py` | Minimum accounting and research-logic test suite |
| `docs/` | Research design, data dictionary, limitations, analysis report, and reconciliation |

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
- Latest-restated manual selection is not point-in-time financial data.
- Fiscal calendars, revenue recognition, acquisitions, buybacks, non-operating gains, and issuer-specific definitions limit direct comparability.
- The project is analytical decision support, not investment advice.

See [`docs/limitations.md`](docs/limitations.md) and [`docs/research_design.md`](docs/research_design.md) for the full boundary.
