# B5 Power BI Build Spec — Executive Overview (Formal)

Status: **Spec ready; live Power BI Service authoring not yet performed.**

This is a mechanical, click-by-click spec for rebuilding the single-page Executive
Overview against the frozen formal mart. It replaces the six-company B1 Pilot page
(`powerbi/README.md`, saved 2026-08-05) with the 21-company / 137-row / 60-field
Gate1-v1.0 mart. Follow it in order; every number in the reconciliation checklist
(Section 5) was pulled directly from `data/processed/q1_powerbi_mart.csv` so it can
be checked on sight, without recomputation, once the visuals are live.

## 0. Why this file exists

Power BI Service is a browser-only, login-gated product on this Mac (no Power BI
Desktop on macOS) and is the environment the frozen charter fixes for B5 with no
downgrade path (charter v3.0 §6.1, §9). Building the report therefore requires an
authenticated Power BI Service session, which is outside automated file/terminal
tooling. This spec exists so that whoever holds that session — you directly, or an
agent driving your already-logged-in browser — can execute B5 in one pass without
re-deriving field choices, DAX, or expected values.

## 1. Data source

```text
data/processed/q1_powerbi_mart.csv
```

- Grain: one formal company x available fiscal year.
- Rows: 137. Companies: 21 (7 per peer group). Fields: 60.
- `data_as_of`: 2026-08-05 for every row (single frozen snapshot — do not mix with
  the old six-company Pilot CSV that shares a similar name).
- Import via Power Query as a fresh table (do not append to the existing Pilot
  table). Suggested table name: `q1_powerbi_mart`.
- Set data types on import: `fiscal_year` whole number; `roe`, `net_margin`,
  `asset_turnover`, `equity_multiplier`, `peer_median_*`, `*_vs_peer_median`,
  `roe_peer_percentile`, `contribution_*`, `*_share`, `*_outcome`, `*_change`,
  `*_gap` decimal number; `*_flag` boolean; everything else text. Leave blanks as
  blank (Power Query should not coerce empty ROE/equity-multiplier cells to 0).

## 2. Slicers

| Slicer | Field |
| --- | --- |
| Company | `company_name` |
| Peer group | `formal_peer_group` (values: `marketplace_platform`, `inventory_led_ecommerce`, `dtc_brand`) |
| Fiscal year | `fiscal_year` (2018–2024) |

Edit interactions: the fiscal-year slicer should **highlight**, not filter out, the
ROE Trend and Shapley visuals (Format > Edit interactions), so a company's full
multi-year line stays visible when a single year is selected for the KPI cards and
interpretation panel.

## 3. Visuals, top to bottom

### 3.1 Header

Title: `Financial Quality and ROE Drivers — E-commerce Peer Screener`
Subtitle: `Q1 Portfolio Release v1.0 · Data as of 2026-08-05 · H1 Evidence Tier B`

### 3.2 KPI cards (4, driven by presentation measures — see Section 4)

`Selected ROE` · `Selected Net Margin` · `Selected Asset Turnover` · `Selected Equity Multiplier`

Formats:
- ROE, Net Margin: `0.0%;-0.0%;-`
- Asset Turnover, Equity Multiplier: `0.00x`

### 3.3 ROE Trend: Company vs Peer Median

- Line chart. Axis: `fiscal_year`. Values: `roe`, `peer_median_roe`.
- Filtered to the selected company only (company slicer drives this visual; do not
  let the peer-group slicer remove the company's own line).

### 3.4 DuPont ROE Change Drivers

- Clustered column chart. Axis: `fiscal_year` (transition-ending year). Values:
  `contribution_margin`, `contribution_turnover`, `contribution_multiplier`.
- Data labels on. Title note: `Values are decimal shares of ΔROE; 0.10 = 10pp`.
- Filtered to the selected company.

### 3.5 Selected Company-Year Interpretation (card / multi-row card)

Fields, in order: `dominant_driver`, `h1_driver_group`, `h1_evidence_tier`,
`h1_eligible_flag`, `h1_exclusion_reason`, `roe_peer_percentile`.

### 3.6 Evidence, Quality & Comparability Notes (card / table)

Fields, in order: `h1_permitted_inference`, `quality_warnings`,
`comparability_note`, `interpretation_note`, `limitations_note`.

`quality_warnings` and `limitations_note` are long strings — use a card or table
visual with text wrap, not a KPI tile.

### 3.7 H1 Headline Result (fixed panel — not filtered by slicers)

These six fields are constant across all 137 rows (they describe the whole frozen
audit, not a company-year), so aggregate with `MAX` or `FIRSTNONBLANK` and do not
let the company/peer-group/fiscal-year slicers clear them:

`h1_eligible_transition_count` (21) · `h1_unique_company_count` (10) ·
`h1_leverage_transition_count` (4) · `h1_operating_transition_count` (17) ·
`h1_leverage_group_median_outcome` (+35.2%) · `h1_operating_group_median_outcome`
(-11.9%) · `h1_group_median_difference` (47.1pp)

Label this panel clearly as the **overall Tier B research result**, distinct from
the per-company cards above it — this is the finding that does not support the H1
direction, and it must stay visible regardless of which company is selected.

### 3.8 Footer

One line: research question (from README) + repo link + "Built in Power BI
Service; .pbix exported for reference."

## 4. DAX (presentation-only; all research logic stays in SQL)

```DAX
Selected ROE = MAX(q1_powerbi_mart[roe])
Selected Net Margin = MAX(q1_powerbi_mart[net_margin])
Selected Asset Turnover = MAX(q1_powerbi_mart[asset_turnover])
Selected Equity Multiplier = MAX(q1_powerbi_mart[equity_multiplier])
Peer Median ROE = MAX(q1_powerbi_mart[peer_median_roe])
Warning Count = MAX(q1_powerbi_mart[quality_warning_count])
H1 Group Median Gap (pp) = MAX(q1_powerbi_mart[h1_group_median_difference]) * 100
```

Do not add any measure that recomputes ROE, margin, turnover, multiplier, Shapley
contributions, peer medians, or H1 eligibility — those are frozen SQL outputs
(charter v3.0 §9.2, checklist B5.1).

## 5. Reconciliation checklist (real values — verify on sight, no recompute needed)

Pull each row from `data/processed/q1_powerbi_mart.csv` (or query
`db/financial_health_screener.duckdb`) if you want to re-derive independently.

- [ ] **AMZN, FY2024** (inventory_led_ecommerce): ROE 24.3%, Net Margin 9.3%, Asset
      Turnover 1.11x, Equity Multiplier 2.36x, dominant driver `margin`,
      `h1_eligible_flag` = False, 1 quality warning ("No consecutive t+1 annual
      observation is available").
- [ ] **BKNG, FY2023** (marketplace_platform): ROE displays as an extreme value
      (225.7 = 22,574%) because average equity is near zero — this is expected, not
      a bug. `dominant_driver` = `multiplier`, `h1_driver_group` = `leverage_driven`,
      `h1_eligible_flag` = False (`next_year_not_observable`), warning text
      "Near-zero average equity; ROE is mechanically unstable" must be visible, not
      suppressed or clamped.
- [ ] **ETSY, FY2023** (marketplace_platform): `roe_valid_flag` = False → ROE and
      Equity Multiplier must render **blank**, not 0 or negative-looking. 3 quality
      warnings including "Average equity is nonpositive; ROE is invalid."
      `roe_peer_percentile` also blank for this row.
- [ ] **BKNG, FY2019**: a `leverage_driven` + `h1_eligible_flag = True` example —
      ROE 66.1%, dominant driver `multiplier`, part of the 4-transition leverage
      group. Confirms eligible rows render normally alongside excluded ones.
- [ ] **FIGS, FY2024** (dtc_brand): `h1_driver_group` = `mixed_or_ambiguous`,
      `h1_exclusion_reason` = `no_roe_improvement` — confirms the mixed/excluded
      path displays correctly for a non-leverage, non-eligible row.
- [ ] **H1 headline panel** (Section 3.7): 21 / 10 / 4 / 17 / +35.2% / -11.9% /
      47.1pp, and `h1_permitted_inference` reads exactly: "Descriptive persistence
      patterns only; emphasize company concentration and year imbalance." This text
      must not change when switching companies.
- [ ] Peer group counts: 7 companies each in `marketplace_platform`
      (ABNB, BKNG, CARS, DASH, EBAY, ETSY, EXPE), `inventory_led_ecommerce`
      (AMZN, BYON, CHWY, CVNA, QVCGA, VRM, W), `dtc_brand`
      (BIRD, FIGS, LOVE, PTON, RVLV, SFIX, SNBR).
- [ ] Fiscal year slicer spans 2018–2024 with no gaps in the list.
- [ ] Switching the peer-group slicer changes `peer_median_roe` for the visible
      companies but never changes the Section 3.7 headline panel.

## 6. After the visuals are built

1. Save the report in Power BI Service (this becomes the source of truth).
2. Export `.pbix` once, as a reference snapshot — same convention as the Pilot
   (`powerbi/README.md` §"固定说明": `Built in Power BI Service; .pbix exported for
   reference.`). Overwrite `powerbi/Financial_Health_Screener_Q1_Executive_Overview.pbix`.
3. Replace `powerbi/financial_health_screener_q1_powerbi.jpg` with a fresh
   screenshot of the formal page.
4. Rewrite `powerbi/README.md` to describe the formal 21-company page (the current
   file documents the six-company Pilot and must be retired, not appended to).
5. Tick every box in Section 5 above against the live page before calling B5 done.
6. Update `docs/changelog.md`, `docs/project_status.md`, and
   `docs/release_closure_audit.md` to move B5 from "Next" to "Done" — only after
   step 5 passes in full, per the project's own rule that downgrades/completions
   follow evidence, not effort spent.
