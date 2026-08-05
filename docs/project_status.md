# Financial Health Screener Project Status

Last updated: 2026-08-05

## Current Position

Current milestone: **Phase A and Q1 Portfolio Release v1.0 complete. Gate 2 is Tier C / No-Go.**

```text
A1 company and event census
    -> A2 official SEC source probe
    -> A3 coverage and H1 sample audit
    -> Gate 1 frozen six-company release
    -> B1-B4 reproducible Q1 analytical product
    -> B5 single-page Power BI Executive Overview
    -> Gate 2 Tier C / No-Go
    -> project closes with Q1; Q2/Q3 are not built
```

The No-Go decision is a valid completion state under both project guides. It prevents latest-restated annual data from being misrepresented as a point-in-time distress model.

## Completed Scope

- A 26-company census with stable IDs, listing status, provisional listing dates, operating-model fields, Q1 scope, and event flags.
- A five-record event census with first-public dates, primary SEC sources, confidence, coverage status, and exclusion reasons.
- Twelve cached SEC companyfacts/submissions artifacts for the six release companies, each with a manifest checksum.
- 599 normalized annual filing facts retaining accession, filing date, source tag, unit, duration, and source URL.
- 222 latest-restated canonical facts available by the frozen 2024-04-30 source cutoff.
- Explicit automated concept conflicts and reconciliation against the manually verified analytical table.
- 18 company-year Q1 rows for AMZN, BKNG, CHWY, DASH, EBAY, and ETSY across FY2021-FY2023.
- Average-balance DuPont metrics, exact Shapley attribution, peer comparisons, H1 eligibility, and Evidence Tier logic.
- Six static charts, three executed notebooks, analytical report, data dictionary, limitations, risk register, and interview pitch.
- A tested single-page Power BI report, saved in Power BI Service and exported as a reference `.pbix`.
- Sixteen passing automated tests covering the SEC evidence layer and Q1 analytical contracts.

## Findings

- 11 company-years have valid average-balance DuPont metrics.
- Five annual transitions have valid exact Shapley decompositions.
- AMZN and CHWY demonstrate that broadly similar ROE can come from very different margin, turnover, and leverage profiles.
- BKNG demonstrates why an extreme ROE can be a near-zero-equity denominator warning.
- H1 is Evidence Tier C with zero eligible persistence transitions.
- Gate 2 is Tier C / No-Go because no event candidate has verified point-in-time quarterly coverage.

## Display Layer

The final display product is the one-page `Executive Overview` required by B5. It includes three slicers, four KPI cards, company-versus-peer ROE trend, DuPont change contributions, selected-year interpretation, and evidence/quality/comparability notes.

Company Deep Dive and Risk Drivers pages are not missing deliverables. The framework makes them optional only after Q2/Q3 evidence gates; Gate 2 prevents them in this release.

## Release Boundary

The old composite risk-ranking files remain as labelled legacy learning artifacts. They are not the methodology, input, or display layer of the v3 release.
