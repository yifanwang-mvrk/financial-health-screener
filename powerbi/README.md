# Q1 Power BI Executive Overview

## Input Boundary

Power BI must consume only:

```text
data/processed/q1_powerbi_mart.csv
```

DuPont metrics, peer medians, Shapley contributions, driver labels, H1 outcomes, Evidence Tier, and quality warnings are already calculated in DuckDB SQL. DAX must not recreate or override those definitions.

## Single-Page Layout

### Header and Filters

- Title: Financial Quality and ROE Drivers
- Company slicer: `ticker` or `company_name`
- Peer-group slicer: `analysis_peer_group`
- Fiscal-year slicer: `fiscal_year`
- Evidence badge: `h1_evidence_tier`

### KPI Row

- ROE: `roe`
- Net Margin: `net_margin`
- Asset Turnover: `asset_turnover`
- Equity Multiplier: `equity_multiplier`

Each KPI must show blank rather than zero when the SQL mart returns null. A warning icon or conditional label should appear when `roe_valid_flag` is false or `near_zero_average_equity_flag` is true.

### Main Visuals

1. **ROE Driver Contribution**
   - Stacked or clustered bar.
   - Values: `contribution_margin`, `contribution_turnover`, `contribution_multiplier`.
   - Category: company or fiscal year, depending on slicer context.

2. **Company vs Peer**
   - Dot or variance bars for `roe_vs_peer_median`, `net_margin_vs_peer_median`, `asset_turnover_vs_peer_median`, and `equity_multiplier_vs_peer_median`.

3. **Operating Profile**
   - Scatter: x = `net_margin`, y = `asset_turnover`, bubble size = capped/log presentation of `equity_multiplier`, color = `analysis_peer_group`.

4. **H1 Status**
   - Text value for `h1_sample_status` and `h1_permitted_inference`.
   - The current release must visibly state Tier C and no group test.

### Warning Area

- `quality_warnings`
- `comparability_note`
- `source_selection_note`

Do not hide the warning area when a KPI is visually strong.

## Basic Measures

Presentation-only examples:

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

- Selected company-year KPIs match the CSV exactly.
- Peer medians match the CSV exactly.
- Dominant driver and H1 group match the CSV exactly.
- Null ROE remains blank.
- BKNG FY2023 displays the near-zero-equity warning.
- ETSY FY2023 displays invalid ROE rather than zero.
- Slicer combinations do not silently aggregate incompatible company-years.

## Build Status

The analytical mart and design specification are complete. The interactive Power BI page and `.pbix` reference export are the next collaborative B5 step.
