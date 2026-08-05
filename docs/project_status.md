# Financial Health Screener Project Status

Last updated: 2026-08-05

## Current Position

Current milestone: **B4 Analytical Release passed; B5 Power BI Product Release passed. Q1 Portfolio Release v1.0 is published. Gate 2 remains pending.**

The formal minimum CV deliverable was reached at B4. B5 rebuilt the Power BI Service report on the frozen 137-row, 60-field formal mart, replacing the six-company Pilot page.

B5 was completed by connecting an authenticated Power BI Service session (via the
`claude-in-chrome` browser extension, logged in by the user) to the report already
saved in Power BI Service. Two visuals still referenced fields from the retired
Pilot schema (`analysis_peer_group`, `dominant_change_driver`, `h1_sample_status`)
after the underlying data source had already been repointed at the formal mart;
both were remapped to the frozen field names (`formal_peer_group`, `dominant_driver`,
plus `h1_exclusion_reason` in place of the retired status field), the header
subtitle was corrected from "FY2021-FY2023 | 6 companies" to
"FY2018-FY2024 | 21 companies", and the page was reconciled against six ground-truth
rows pulled directly from `data/processed/q1_powerbi_mart.csv` (see
`powerbi/README.md` for the full checklist). The report was saved in Power BI
Service, exported as `.pbix`, and a fresh screenshot was captured via a PDF export
converted locally to `powerbi/financial_health_screener_q1_powerbi.jpg`.

```text
A0E PASSED
    -> A1 DONE: 50 companies, 40 Q1 candidates, 14 event candidates
    -> A2 DONE: formal CHWY/EBAY source probe, concept map, conflict sample, report, and notebook
    -> A3 DONE: 40-company annual/H1 scan and 14-event quarterly/PIT scan
    -> Gate 1 PASSED: Path A, 21 companies, FY2018-FY2024, H1 Tier B, rules, and mart contract frozen
    -> B1 DONE: six-company raw-to-DuckDB pipeline and Pilot marts revalidated
    -> B2 DONE: unchanged pipeline expanded to 21 frozen companies and FY2018-FY2024
    -> B3 DONE: seven formal SQL marts, Tier B audit, and 60-field Power BI mart
    -> B4 DONE: standalone analytical release and CV-ready minimum deliverable
    -> B5 DONE: formal single-page Power BI report rebuilt on the frozen mart,
       reconciled, saved in Power BI Service, and exported as .pbix + screenshot
    -> Gate 2 PENDING
```

## Evidence Retained

- Completed 50-company A1 universe with 40 Q1 candidates.
- Fourteen sourced A1 event candidates with A3 verification complete; 12 provisionally qualify and two have specific exclusions.
- Formal CHWY/EBAY A2 source probe with 155 filing-level facts, 60 current winners, 38 traceable discarded-value records, and explicit A3 scan requirements.
- A3 retained 4,823 core annual fact versions, 1,046 latest winners, 945 traceable differences, and 31 coverage-viable candidates.
- Gate 1 freezes Path A and a 21-company sample with H1 Tier B from 21 transitions across 10 companies.
- Gate 1 freezes Q2 Tier A feasibility only; formal Q2 authorization remains at Gate 2 after B5.
- B1 uses 12 cached SEC artifacts, 570 filing-level mapped facts, 225 latest/derived facts, 76 explicit conflicts, 39 metric flags, and two filing-backed company override rules.
- B1 has no unresolved source conflict; DuPont and Shapley maximum reconciliation gaps are below `1e-10`.
- B2 uses 42 cached SEC artifacts, 4,780 filing-level mapped facts, 1,959 latest/derived facts, 875 explicit conflict records, and 262 metric flags.
- B2 covers all 21 frozen companies with seven companies per peer group and no missing required company-year field. All conflicts are resolved or logged, and every active exception is accession-backed.
- B3 produces 137 formal company-years, 116 candidate transition rows, 21 peer-year summaries, and a 137-row Power BI mart with exactly 60 frozen fields.
- B3 reproduces Gate 1 H1 Tier B: 21 eligible transitions across 10 companies, with 4 leverage-driven and 17 operating-driven transitions. Maximum company share is 14.3%; FY2020-FY2021 account for 47.6%.
- Maximum absolute DuPont and Shapley reconciliation gaps are `2.842e-14` and `5.684e-14`.
- B4 freezes analytical inputs with checksums and provides 14 formal EDA/research tables, eight reviewed static charts, two executed notebooks, eight AMZN/CHWY filing checks, a formal analysis report, CV bullet, and five-minute narrative.
- The Tier B descriptive result does not support the expected H1 direction: leverage-driven median peer-relative next-year change is +35.2 percentage points versus -11.9 points for operating-driven improvements.
- Six-company SEC cache, accession-level facts, latest-restated selection, conflicts, and reconciliation.
- Six-company FY2021-FY2023 DuPont, Shapley, peer, H1-audit, notebook, chart, test, and Power BI artifacts, retained as B1 Pilot evidence.
- B5 rebuilt the Power BI Service report on the formal 137-row/60-field mart: fixed the peer-group slicer and the Selected Company-Year Interpretation table (both had referenced fields retired from the Pilot schema), corrected the header subtitle, and reconciled AMZN FY2023/FY2018, BKNG FY2023/FY2019, ETSY FY2023, and FIGS FY2024 against the mart. Saved in Power BI Service; exported as `.pbix` (`powerbi/Financial_Health_Screener_Q1_Executive_Overview.pbix`) and screenshot (`powerbi/financial_health_screener_q1_powerbi.jpg`).

## Remaining Exit Conditions

- Gate 2: formally decide Tier A/B/C now that B5 is complete. A3 recommended Tier A feasibility from 12 qualified events; the actual go/no-go call has not been made and is a separate scope decision from finishing Q1's presentation layer.

## Correct Interpretation

- Zero eligible H1 transitions in the six-company Pilot is a Pilot result; Gate 1 independently freezes formal H1 Tier B at 21 transitions across 10 companies.
- Gate 1 freezes Q2 Tier A feasibility, but the formal Gate 2 decision is a distinct step that has not been made — B5 completing unblocks it but does not decide it.
- Company Deep Dive and Risk Drivers are not current Q1 requirements. Their exact form is determined only if Gate 2 and Gate 3 authorize Q2/Q3.
- The formal minimum CV deliverable was reached at B4. B5 is now complete: the Power BI report reflects the formal 21-company mart and is the Q1 Portfolio Release v1.0, not the six-company Pilot.
