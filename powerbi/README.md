# Q1 Power BI Executive Overview

## Build Status

Status: **B5 formal release complete — Q1 Portfolio Release v1.0**

The Power BI Service report is rebuilt on the frozen 21-company, 137-row, 60-field formal mart, saved in Power BI Service, exported as a `.pbix` reference file, and reconciled against `data/processed/q1_powerbi_mart.csv`. The prior six-company Pilot page is superseded; the Pilot's PBIX and screenshot survive only in git history.

## Input Boundary

Power BI consumes only:

```text
data/processed/q1_powerbi_mart.csv
```

DuPont metrics, peer medians, Shapley contributions, driver labels, H1 outcomes, evidence status, and quality warnings are all calculated in DuckDB SQL. Power BI is restricted to presentation and filtering and does not recreate those definitions in DAX.

## Single-Page Layout

### Header, Filters, and KPIs

- Title: Financial Quality and ROE Drivers
- Subtitle: `US-listed e-commerce | FY2018-FY2024 | 21 companies | Q1 analytical release`
- Company slicer: `company_name`
- Peer-group slicer: `formal_peer_group`
- Fiscal-year slicer: `fiscal_year`
- ROE: `roe`
- Net Margin: `net_margin`
- Asset Turnover: `asset_turnover`
- Equity Multiplier: `equity_multiplier`

Null SQL values remain blank. Verified with ETSY FY2023, where ROE and equity multiplier display `--` rather than 0. Mechanically unstable ROE (near-zero average equity) is left visible rather than clamped, verified with BKNG FY2023 (ROE renders as 22,573.7%, matching the mart exactly).

### Main Visuals

1. **ROE Trend: Company vs Peer Median**
   - Axis: `fiscal_year`
   - Values: `roe`, `peer_median_roe`
   - The company line retains historical context through the selected fiscal year (fiscal-year slicer highlights rather than filters this visual).

2. **DuPont ROE Change Drivers**
   - Axis: `fiscal_year`
   - Values: `contribution_margin`, `contribution_turnover`, `contribution_multiplier`
   - Data labels are visible.
   - Contributions are stored as decimals; the title states `0.10 = 10 pp`.
   - Blank for a company's first panel year (e.g. FY2018), since no prior-year transition exists to attribute — expected, not an error.

3. **Selected Company-Year Interpretation**
   - `h1_evidence_tier`
   - `dominant_driver`
   - `h1_exclusion_reason` (reads `eligible` for H1-eligible rows, or the specific exclusion reason otherwise — e.g. `turnaround_from_loss`, `next_year_not_observable`, `invalid_dupont_transition`, `no_roe_improvement`)

4. **Evidence, Quality & Comparability Notes**
   - `h1_permitted_inference`
   - `quality_warnings`
   - `comparability_note`

The interactive page prioritizes the selected-company decision path. The cohort operating-profile scatter remains available as the reproducible static chart `docs/assets/q1/05_2023_operating_profile.png`.

## Presentation Measures

Power BI uses presentation-only measures or direct column aggregation. Financial definitions remain SQL-owned.

```DAX
Selected ROE = MAX(q1_powerbi_mart[roe])
Selected Net Margin = MAX(q1_powerbi_mart[net_margin])
Selected Asset Turnover = MAX(q1_powerbi_mart[asset_turnover])
Selected Equity Multiplier = MAX(q1_powerbi_mart[equity_multiplier])
Warning Count = MAX(q1_powerbi_mart[quality_warning_count])
```

Recommended formats:

- ROE and margins: `0.0%;-0.0%;-`
- Turnover and multiplier: `0.00x`
- Contribution values: `0.0%;-0.0%;-`

## Reconciliation Checklist

Formal reconciliation completed on 2026-08-05 against the frozen mart:

- [x] AMZN FY2023 KPIs match the mart: ROE 17.5%, net margin 5.3%, asset turnover 1.16, equity multiplier 2.85.
- [x] AMZN FY2018 (panel's first year) shows a blank Selected Company-Year Interpretation row — no prior year exists for a transition.
- [x] BKNG FY2023 displays the near-zero-average-equity warning; ROE renders as the true extreme value (22,573.7%) rather than being suppressed or clamped.
- [x] BKNG FY2019 (an eligible leverage-driven transition) displays normally alongside excluded rows.
- [x] ETSY FY2023 displays invalid ROE and equity multiplier as blank rather than 0, with 3 quality warnings including "Average equity is nonpositive; ROE is invalid."
- [x] FIGS FY2024 displays `mixed_or_ambiguous` / `no_roe_improvement` correctly.
- [x] Company ROE and peer-median trend reconcile to the mart.
- [x] Shapley contribution bars reconcile to the mart and expose units in the title.
- [x] Dominant driver, H1 Evidence Tier, and exclusion reason all respond to the company and fiscal-year slicers.
- [x] Peer-group slicer (`formal_peer_group`) correctly lists all three groups; Company slicer lists all 21 formal companies (verified against `data/processed/q1_powerbi_mart.csv`, including `BYON` displaying as "Bed Bath & Beyond Inc").
- [x] H1 headline panel (21 eligible transitions, 10 unique companies, 4 leverage-driven, 17 operating-driven, +35.2% vs -11.9% median outcomes) is constant across every slicer selection, since it describes the whole frozen audit rather than one company-year.
- [x] `h1_permitted_inference` reads "Descriptive persistence patterns only; emphasize company concentration and year imbalance" throughout — Tier B wording, not upgraded to a validated-test claim.
- [x] The report is saved in Power BI Service and exported as a `.pbix` reference file (`Built in Power BI Service; .pbix exported for reference.`).
- [x] Report screenshot (`financial_health_screener_q1_powerbi.jpg`) reflects the formal mart.

Power BI Service report: [Financial Health Screener Q1 Executive Overview](https://app.powerbi.com/groups/me/reports/fb9d94b1-fc87-484a-9282-2895f48b80fa/4ffbaf6ac660aec51266?experience=power-bi)
