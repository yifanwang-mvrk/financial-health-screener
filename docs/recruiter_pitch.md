# Recruiter and Interview Pitch

## CV Bullet

Built a reproducible six-company Pilot for an SEC-Python-DuckDB-Power BI financial research pipeline, retaining accession-level evidence and implementing average-balance DuPont metrics, exact Shapley ROE decomposition, peer benchmarks, quality flags, and automated tests; formal sample expansion is in progress under a pre-specified gate process.

## 30-Second Introduction

I built a six-company Pilot for a financial quality screener that shows why the same ROE can mean different things across e-commerce business models. The pipeline caches official SEC evidence and keeps accession history, Python validates and orchestrates it, and DuckDB SQL calculates average-balance DuPont metrics and exact Shapley contributions. Amazon and Chewy have broadly similar 2023 ROE but very different operating profiles. The Pilot has no eligible H1 transitions, so I do not force a persistence result. The next stage expands and audits the formal candidate pool before the portfolio release is claimed.

## Five-Minute Story

1. **Business problem:** Headline ROE can hide whether returns come from operating economics, asset efficiency, or a thin equity base.
2. **Data judgment:** I cached official SEC companyfacts and submissions JSON, retained accession-level annual facts, and reconciled them to six companies' issuer-specific filing mappings.
3. **Engineering:** Python handles extraction, normalization, reconciliation, and validation; seven ordered SQL files build frozen DuckDB marts; tests protect source and analytical contracts.
4. **Analysis:** I use average assets and equity, exact three-factor Shapley decomposition, peer medians, and explicit denominator warnings.
5. **Result:** Amazon and Chewy illustrate similar ROE from different drivers. Booking is the counterexample where extreme ROE is mainly a near-zero-equity warning.
6. **Research discipline:** H1 has zero eligible transitions under the pre-set rules, so the release is Tier C and reports no group comparison.
7. **Product prototype:** A single Power BI mart keeps research logic out of DAX and supports the Pilot one-page Executive Overview.
8. **Scope discipline:** Gate 2 remains pending because point-in-time quarterly coverage has not yet been verified; no unsupported risk model is presented.

## Questions to Be Ready For

- Why average equity instead of year-end equity?
- Why Shapley rather than changing one factor at a time?
- Why is company the independent unit for H1?
- Why is BKNG's large ROE a warning?
- Why are FY2021 DuPont metrics unavailable?
- Why does the six-company Pilot not determine the formal H1 Tier?
- Why is latest-restated not point-in-time?
- Why does Power BI consume one mart instead of recreating logic in DAX?
- What evidence must A3 collect before Gate 2 can decide Q2/Q3?
