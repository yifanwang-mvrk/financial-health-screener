# Recruiter and Interview Pitch

## CV Bullet

Built a reproducible SEC-Python-DuckDB financial research pipeline and interactive Power BI report for six public e-commerce companies and 18 company-years, retaining accession-level evidence and engineering average-balance DuPont metrics, exact Shapley ROE decomposition, peer benchmarks, quality flags, and automated tests.

## 30-Second Introduction

I built a financial quality screener to show why the same ROE can mean different things across e-commerce business models. The pipeline caches official SEC evidence and keeps accession history, Python validates and orchestrates it, and DuckDB SQL calculates average-balance DuPont metrics and exact Shapley contributions. Amazon and Chewy have broadly similar 2023 ROE but very different operating profiles. The H1 sample is Tier C, so I report insufficient evidence instead of forcing a result. The finished product is tested, documented, and presented in an interactive one-page Power BI report.

## Five-Minute Story

1. **Business problem:** Headline ROE can hide whether returns come from operating economics, asset efficiency, or a thin equity base.
2. **Data judgment:** I cached official SEC companyfacts and submissions JSON, retained accession-level annual facts, and reconciled them to six companies' issuer-specific filing mappings.
3. **Engineering:** Python handles extraction, normalization, reconciliation, and validation; seven ordered SQL files build frozen DuckDB marts; tests protect source and analytical contracts.
4. **Analysis:** I use average assets and equity, exact three-factor Shapley decomposition, peer medians, and explicit denominator warnings.
5. **Result:** Amazon and Chewy illustrate similar ROE from different drivers. Booking is the counterexample where extreme ROE is mainly a near-zero-equity warning.
6. **Research discipline:** H1 has zero eligible transitions under the pre-set rules, so the release is Tier C and reports no group comparison.
7. **Product:** A single Power BI mart keeps research logic out of DAX and supports the completed one-page Executive Overview.
8. **Scope decision:** A separate event census fails Gate 2 because point-in-time quarterly coverage is unverified, so I close the project at Q1 instead of presenting an unsupported risk model.

## Questions to Be Ready For

- Why average equity instead of year-end equity?
- Why Shapley rather than changing one factor at a time?
- Why is company the independent unit for H1?
- Why is BKNG's large ROE a warning?
- Why are FY2021 DuPont metrics unavailable?
- Why does Tier C still count as a complete B4 product?
- Why is latest-restated not point-in-time?
- Why does Power BI consume one mart instead of recreating logic in DAX?
- Why did Gate 2 stop Q2/Q3, and why is that a successful project outcome?
