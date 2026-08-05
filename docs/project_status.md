# Financial Health Screener Project Status

Last updated: 2026-08-05

## Current Position

Current milestone: **B1 passed; B2 formal sample expansion is next.**

The six-company analytical and Power BI work remains a **B1 Pilot snapshot**. Its SEC-to-DuckDB pipeline has now been rebuilt against Gate1-v1.0. It proves the common path but does not replace the 21-company B2 expansion.

```text
A0E PASSED
    -> A1 DONE: 50 companies, 40 Q1 candidates, 14 event candidates
    -> A2 DONE: formal CHWY/EBAY source probe, concept map, conflict sample, report, and notebook
    -> A3 DONE: 40-company annual/H1 scan and 14-event quarterly/PIT scan
    -> Gate 1 PASSED: Path A, 21 companies, FY2018-FY2024, H1 Tier B, rules, and mart contract frozen
    -> B1 DONE: six-company raw-to-DuckDB pipeline and Pilot marts revalidated
    -> B2 NEXT: expand unchanged rules to 21 frozen companies and FY2018-FY2024
    -> B3-B5 formal releases PENDING
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
- Six-company SEC cache, accession-level facts, latest-restated selection, conflicts, and reconciliation.
- Six-company FY2021-FY2023 DuPont, Shapley, peer, H1-audit, notebook, chart, test, and Power BI artifacts.
- A saved one-page Power BI Pilot prototype and PBIX reference snapshot.

## Remaining Exit Conditions

- B2-B5: formal-sample data, marts, analysis, and Power BI release.
- Gate 2: refresh and formally decide Tier A/B/C after B5.

## Correct Interpretation

- Zero eligible H1 transitions in the six-company Pilot is a Pilot result; Gate 1 independently freezes formal H1 Tier B at 21 transitions across 10 companies.
- Gate 1 freezes Q2 Tier A feasibility, but formal Gate 2 still occurs after B5 and no Q2 technology is authorized yet.
- Company Deep Dive and Risk Drivers are not current Q1 requirements. Their exact form is determined only if Gate 2 and Gate 3 authorize Q2/Q3.
- The formal minimum CV deliverable has not yet been reached; the existing Pilot is a strong prototype, not the completed portfolio release.
