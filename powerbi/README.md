# Q1 Power BI Executive Overview

## Build Status

Status: **Complete as a six-company B1 Pilot display prototype; formal B5 is pending**

The Power BI Service Pilot report is saved, a `.pbix` Pilot reference export is stored in this directory, and the page screenshot is stored as `financial_health_screener_q1_powerbi.jpg`. The formal B5 report must be rebuilt and reconciled after Gate 1, B2, B3, and B4 are complete.

## Input Boundary

Power BI consumes only:

```text
data/processed/q1_powerbi_mart.csv
```

Pilot DuPont metrics, peer medians, Shapley contributions, driver labels, H1 outcomes, evidence status, and quality warnings are calculated in DuckDB SQL. Power BI is restricted to presentation and filtering and does not recreate those definitions in DAX.

## Single-Page Layout

### Header, Filters, and KPIs

- Title: Financial Quality and ROE Drivers
- Company slicer: `company_name`
- Peer-group slicer: `analysis_peer_group`
- Fiscal-year slicer: `fiscal_year`
- ROE: `roe`
- Net Margin: `net_margin`
- Asset Turnover: `asset_turnover`
- Equity Multiplier: `equity_multiplier`

Null SQL values remain blank. This is verified with ETSY FY2023, where ROE and equity multiplier display `--` rather than zero.

### Main Visuals

1. **ROE Trend: Company vs Peer Median**
   - Axis: `fiscal_year`
   - Values: `roe`, `peer_median_roe`
   - The company line retains historical context through the selected fiscal year.

2. **DuPont ROE Change Drivers**
   - Axis: `fiscal_year`
   - Values: `contribution_margin`, `contribution_turnover`, `contribution_multiplier`
   - Data labels are visible.
   - Contributions are stored as decimals; the title states `0.10 = 10 pp`.

3. **Selected Company-Year Interpretation**
   - `dominant_change_driver`
   - `h1_evidence_tier`
   - `h1_sample_status`

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

Pilot reconciliation completed on 2026-08-05:

- [x] AMZN FY2023 KPIs match the mart: ROE 17.5%, net margin 5.3%, asset turnover 1.16, and equity multiplier 2.85.
- [x] Company ROE and peer-median trend reconcile to the mart.
- [x] Shapley contribution bars reconcile to the mart and expose units in the title.
- [x] Dominant driver, Evidence Tier, and H1 sample status respond to slicers.
- [x] BKNG FY2023 displays the near-zero-average-equity warning and mechanically unstable ROE note.
- [x] ETSY FY2023 displays invalid ROE as blank rather than zero.
- [x] The Pilot has zero eligible H1 transitions and explicitly forbids group-level inference.
- [x] The Pilot report is saved in Power BI Service and exported as a `.pbix` reference file.

These checks validate the Pilot page only. They do not constitute the formal B5 DoD.

Power BI Service report: [Financial Health Screener Q1 Executive Overview](https://app.powerbi.com/groups/me/reports/fb9d94b1-fc87-484a-9282-2895f48b80fa/4ffbaf6ac660aec51266?experience=power-bi)
