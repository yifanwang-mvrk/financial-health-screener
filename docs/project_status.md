# Financial Health Screener Project Status

Last updated: 2026-08-05

## Current Position

Current milestone: **B4 Analytical Release passed; B5 Power BI Product Release is in progress — spec and materials ready, live Service authoring pending.**

The formal minimum CV deliverable is complete. The six-company Power BI work remains a **Pilot snapshot** until B5 refreshes the page from the frozen 137-row, 60-field formal mart.

B5 preparation is done: `docs/b5_powerbi_build_spec.md` gives a field-by-field,
DAX-verbatim build spec plus a reconciliation checklist populated with real values
from the formal mart, and `docs/recruiter_pitch.md` (extended this session with a
fuller Interview Checks section and a pending Power BI CV-bullet update) carries
the Tier B CV bullet, 30-second intro, 5-minute narrative, and anticipated Q&A.
What remains is
the live Power BI Service session itself: Power BI Service is browser/login-gated
(no Power BI Desktop on macOS) and no authenticated session is currently reachable
by either browser tool, so the visual/DAX authoring, Service save, `.pbix` export,
and screenshot capture have not been performed yet.

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
    -> B5 IN PROGRESS: build spec and recruiter materials ready; live Power BI
       Service authoring, reconciliation, Service save, and .pbix export pending
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
- Six-company FY2021-FY2023 DuPont, Shapley, peer, H1-audit, notebook, chart, test, and Power BI artifacts.
- A saved one-page Power BI Pilot prototype and PBIX reference snapshot.

## Remaining Exit Conditions

- B5: build spec (`docs/b5_powerbi_build_spec.md`) and recruiter materials
  (`docs/recruiter_pitch.md`) are ready. Still open: live Power BI Service
  visual/DAX authoring against the formal mart, visual reconciliation against the
  Section 5 checklist, Service save, PBIX reference export, screenshot refresh, and
  `powerbi/README.md` rewrite — blocked on an authenticated Power BI Service
  session (see Correct Interpretation below).
- Gate 2: refresh and formally decide Tier A/B/C after B5.

## Correct Interpretation

- Zero eligible H1 transitions in the six-company Pilot is a Pilot result; Gate 1 independently freezes formal H1 Tier B at 21 transitions across 10 companies.
- Gate 1 freezes Q2 Tier A feasibility, but formal Gate 2 still occurs after B5 and no Q2 technology is authorized yet.
- Company Deep Dive and Risk Drivers are not current Q1 requirements. Their exact form is determined only if Gate 2 and Gate 3 authorize Q2/Q3.
- The formal minimum CV deliverable has been reached at B4. The existing Power BI report remains a Pilot and must not be described as the formal portfolio release until B5 passes.
- B5's remaining work is a live, authenticated Power BI Service session (visual and DAX authoring, Service save, `.pbix` export). This cannot be completed by file/terminal automation or by an unauthenticated browser, and credentials must never be entered on the user's behalf. Treat `docs/b5_powerbi_build_spec.md` as the authoritative to-do list for whoever holds that session, and do not mark B5 Done until its Section 5 reconciliation checklist has actually been verified against the live report.
