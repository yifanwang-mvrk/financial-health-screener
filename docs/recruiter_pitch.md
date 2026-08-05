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

- The independent unit is the company because annual transitions repeat within issuers; the audit reports both 21 transitions and 10 unique companies, and Tier A (not reached) would additionally require company-clustered bootstrap rather than treating transitions as i.i.d.
- The A3 sample audit applied Gate 1's pre-frozen thresholds (Tier A: >=15 unique companies, >=40 transitions, >=8 per driver group): the scan returned 10 companies with the leverage group at 3-4, short of Tier A on unique-company count, landing in the Tier B band.
- Margin and turnover are combined into "operating-driven" because both represent execution inside the business (pricing/cost control, asset efficiency) as opposed to a capital-structure change; this keeps the primary test binary while margin-only and turnover-only splits stay available as secondary description.
- Exact Shapley attribution handles the multiplicative DuPont identity and reconciles exactly (max gap 5.684e-14 across the formal sample) because ROE is a product of three factors, not a sum, and naive per-factor deltas leave an unallocated interaction term.
- Negative-base-ROE turnarounds remain visible but outside the main H1 sample; they are flagged `turnaround_from_loss` for case-level description only.
- XBRL tag conflicts and restatements go through an explicit `concept_map` with frozen tag priority; every disagreement is logged with winning/discarded value and relative difference, with severity thresholds frozen at Gate 1 (low <=0.5%, medium 0.5%-5%, high >5%, mandatory reconciliation above that). Version selection always takes the latest *valid* restated filing, not just the most recent filing date.
- Peer-relative change is primary because it reduces common-year shocks, though it cannot remove year-composition risk.
- A larger, balanced sample showing leverage outcomes at least as persistent as operating outcomes would fail to support H1 — and the project's actual Tier B result already points that way (+35.2pp leverage vs. -11.9pp operating), which is why it is reported as a counter-pattern rather than reframed as support.

## B5 Update (Pending Live Power BI Session)

B5 replaces the six-company Pilot page with a formal report over the frozen
21-company mart; see `docs/b5_powerbi_build_spec.md` for the field-by-field build
spec and reconciliation checklist. Once that live report is built, saved, and
reconciled, promote the CV bullet above to:

> Built a reproducible Python-DuckDB-Power BI financial-quality screener for 21
> U.S.-listed e-commerce companies; normalized filing-level XBRL facts through
> explicit mapping and restatement rules, decomposed ROE changes with exact
> Shapley attribution, and examined Tier B descriptive persistence patterns
> across leverage- and operating-driven improvements.

Do not promote this wording until the Power BI page is actually live and
reconciled — until then the current (Python-DuckDB only) bullet above remains
accurate and should stay in place.
