# Recruiter and Interview Pitch

## CV Bullet

Built a reproducible Python-DuckDB financial research pipeline for six public e-commerce companies and 18 company-years, engineering average-balance DuPont metrics, exact Shapley ROE decomposition, peer benchmarks, quality flags, automated tests, and a Power BI-ready analytical mart.

## 30-Second Introduction

I built a financial quality screener to show why the same ROE can mean different things across e-commerce business models. Python validates and orchestrates the data, DuckDB and SQL calculate average-balance DuPont metrics and exact Shapley contributions, and a separate audit decides whether each transition can enter a persistence test. The main finding is that Amazon and Chewy have broadly similar 2023 ROE but very different margin, turnover, and leverage profiles. The H1 sample is Tier C, so I explicitly report insufficient evidence instead of forcing a statistical result. The final output is tested, reproducible, documented, and ready for a one-page Power BI product.

## Five-Minute Story

1. **Business problem:** Headline ROE can hide whether returns come from operating economics, asset efficiency, or a thin equity base.
2. **Data judgment:** I standardized 10-K facts for six companies while preserving issuer-specific definitions, restatements, missing fields, fiscal calendars, and source URLs.
3. **Engineering:** Python validates and loads the data; seven ordered SQL files build frozen DuckDB marts; tests protect accounting identities and research rules.
4. **Analysis:** I use average assets and equity, exact three-factor Shapley decomposition, peer medians, and explicit denominator warnings.
5. **Result:** Amazon and Chewy illustrate similar ROE from different drivers. Booking is the counterexample where extreme ROE is mainly a near-zero-equity warning.
6. **Research discipline:** H1 has zero eligible transitions under the pre-set rules, so the release is Tier C and reports no group comparison.
7. **Product:** A single Power BI mart keeps research logic out of DAX and supports a one-page Executive Overview.

## Questions to Be Ready For

- Why average equity instead of year-end equity?
- Why Shapley rather than changing one factor at a time?
- Why is company the independent unit for H1?
- Why is BKNG's large ROE a warning?
- Why are FY2021 DuPont metrics unavailable?
- Why does Tier C still count as a complete B4 product?
- Why is latest-restated not point-in-time?
- Why does Power BI consume one mart instead of recreating logic in DAX?
