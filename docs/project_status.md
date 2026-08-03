# Financial Health Screener Project Status

Last updated: 2026-08-03

## Current Position

The original v3 Q1 plan is active again.

Current milestone: **B4 Analytical Release complete; B5 Power BI product build next.**

```text
sample and source mapping
    -> verified financial data
    -> Python validation
    -> DuckDB core tables
    -> SQL metrics and peer benchmarks
    -> exact Shapley decomposition
    -> H1 sample and Evidence Tier audit
    -> B4 analysis, notebooks, charts, and documentation
    -> B5 single-page Power BI Executive Overview (next)
```

The current release uses six companies and FY2021-FY2023, but the analytical method has not been reduced to the earlier simple risk score.

## Scope

Companies:

- AMZN
- BKNG
- CHWY
- DASH
- EBAY
- ETSY

Years: FY2021-FY2023.

Research:

- Q1-A DuPont financial-quality analysis.
- H1 leverage-driven versus operating-driven persistence design.
- Evidence-tier decision based on the actual eligible sample.

## Completed

### Data and Governance

- 18 company-year financial statement rows populated and validated.
- Detailed company source mappings retained.
- Q1 analytical scope and peer groups frozen.
- Canonical concept map and conflict register added.
- Latest-restated manual compatibility path documented.

### SQL Analysis

- Average assets and average equity.
- ROE, ROA, net margin, asset turnover, and equity multiplier.
- Profitability, liquidity, leverage, cash-flow, and growth metrics.
- Exact three-factor Shapley contributions.
- Driver classification and leverage contribution share.
- Peer medians and company-versus-peer positions.
- Next-year persistence outcomes.
- H1 eligibility, exclusion waterfall, concentration, and Evidence Tier.
- Frozen Power BI mart.

### Python and QA

- Rebuildable Q1 pipeline.
- Rebuildable EDA, charts, and notebooks.
- Seven automated accounting and research-logic tests.
- DuPont and Shapley reconciliation tolerances verified below `1e-10`.

### B4 Deliverables

- Ten exported Q1 analytical tables.
- Six inspected static charts.
- Three executed notebooks.
- Research design and analysis report.
- Data dictionary and limitations.
- Manual reconciliation for AMZN and CHWY.
- Risk register, changelog, README, and recruiter pitch.

## Current Findings

- 11 valid DuPont company-years.
- 5 valid Shapley transitions.
- AMZN and CHWY demonstrate similar ROE from different margin, turnover, and multiplier combinations.
- BKNG demonstrates why extreme ROE can be a near-zero-equity denominator warning.
- H1 is Evidence Tier C with zero eligible transitions.
- No H1 group test is permitted or reported.

## Next Step

Build the B5 single-page Power BI Executive Overview using only `data/processed/q1_powerbi_mart.csv`, then reconcile each visual back to DuckDB and export the reference `.pbix` and screenshots.

## Legacy Files

The earlier MVP risk-score pipeline remains for learning history:

- `sql/financial_health_screener_mvp.sql`
- `src/build_mvp_pipeline.py`
- `data/processed/risk_ranking.csv`
- `sql/mvp_analysis_rebuild.sql`
- `src/run_analysis_rebuild.py`

These files are not part of the active v3 Q1 research product and must not be described as the final methodology.
