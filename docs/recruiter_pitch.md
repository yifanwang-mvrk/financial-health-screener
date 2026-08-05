# Q1 Recruiter and Interview Narrative

## CV Bullet

Built a reproducible Python-DuckDB financial-quality screener for 21 U.S.-listed e-commerce companies; normalized filing-level XBRL facts through explicit mapping and restatement rules, decomposed ROE changes with exact Shapley attribution, and examined Tier B descriptive persistence patterns across leverage- and operating-driven improvements.

## 30-Second Introduction

I built a reproducible financial-quality screener for 21 U.S.-listed e-commerce companies. It converts SEC filing facts into average-balance DuPont metrics, peer benchmarks, and exact Shapley explanations of ROE changes. The project also tests a pre-registered persistence idea. The available panel reached Tier B rather than a validation sample, and the descriptive result did not support the expected leverage-is-less-persistent direction. That evidence boundary is part of the product, not something hidden after the analysis.

## Five-Minute Narrative

1. **Question.** Similar ROE can come from margin, asset efficiency, or leverage, so I wanted a product that separates those drivers and tests whether leverage-led improvements fade faster.
2. **Data discipline.** I began with 40 Q1 candidates, probed two issuers, audited full coverage, and froze a 21-company Path A sample before engineering the formal release.
3. **Engineering.** The pipeline retains filing-level accessions, explicit concept conflicts, latest-valid restatements, sign rules, nulls, metric flags, and accession-backed exceptions. Seven ordered DuckDB SQL files produce the analytical marts.
4. **Q1-A result.** ABNB and LOVE both generated roughly 36% FY2022 ROE, but ABNB relied on margin while LOVE relied much more on turnover. BKNG shows why near-zero equity can make correct ROE economically unstable.
5. **H1 result.** The frozen sample has 21 eligible transitions across 10 companies, but only four leverage-driven transitions across three companies. The leverage group median peer-relative next-year outcome is 35.2%, versus -11.9% for the operating group, so the observed direction does not support H1.
6. **Limits.** This is Tier B descriptive evidence. Years are imbalanced, latest-restated is not point-in-time, company-years are not independent companies, and no investment or distress-prediction claim is made.
7. **Product boundary.** B4 is a complete standalone analytical release. B5 adds the single-page Power BI presentation without moving research logic into DAX.

## Interview Checks

- The independent unit is the company because annual transitions repeat within issuers.
- Exact Shapley attribution handles the multiplicative DuPont identity and reconciles exactly.
- Negative-base-ROE turnarounds remain visible but outside the main H1 sample.
- Peer-relative change is primary because it reduces common-year shocks, though it cannot remove year-composition risk.
- A larger, balanced sample showing leverage outcomes at least as persistent as operating outcomes would fail to support H1.
