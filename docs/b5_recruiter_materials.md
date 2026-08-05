# B5 Recruiter Materials — Tier B

Status: **Draft ready from final B4 numbers.** Finalize wording only if the live
Power BI page (see `b5_powerbi_build_spec.md`) changes any headline figure.

All figures below are the frozen Gate1-v1.0 formal results (21 companies,
FY2018–2024, H1 Evidence Tier B), matching `docs/changelog.md` and
`docs/project_status.md` as of 2026-08-05. Wording follows charter v3.0 §14.2's
Tier B guidance: descriptive persistence patterns, not a validated test.

## CV bullet

> Built a reproducible Python–DuckDB–Power BI financial-quality screener for 21
> U.S.-listed e-commerce companies across three business-model peer groups;
> normalized filing-level XBRL facts through an explicit concept map, decomposed
> ROE changes into margin, asset-turnover, and leverage contributions using exact
> three-factor Shapley attribution, and examined descriptive one-year persistence
> patterns across leverage- and operating-driven ROE improvements (H1 Evidence Tier
> B: 21 eligible transitions, 10 unique companies).

## 30-second introduction

> "I built a peer financial-quality screener for U.S.-listed e-commerce companies
> that explains *where* ROE comes from — margin, asset efficiency, or leverage —
> using SEC filing data, DuckDB/SQL, and a Power BI front end. The research
> question was whether ROE improvements driven by leverage are less durable than
> ones driven by operations. The honest answer, with the sample I could build, is
> that the evidence isn't strong enough to say — and the descriptive pattern I did
> get actually runs the other way, which the project documents rather than hides."

## Five-minute narrative

1. **Question.** Two companies can show the same ROE for very different reasons —
   thin margins with fast asset turns, or fat margins with heavy leverage. Q1-A
   decomposes ROE via DuPont (margin × turnover × equity multiplier) across three
   e-commerce peer groups (Marketplace/Platform, Inventory-led, DTC Brand; 7
   companies each). Q1-H1 asks whether leverage-driven ROE improvements persist
   one year out as well as operating-driven ones do.
2. **Method.** SEC Companyfacts XBRL, normalized through an explicit concept map
   with documented tag priority and a logged conflict-resolution rule (60 winners /
   38 discarded at the two-company probe stage; 1,046 winners / 945 differences at
   full-sample scale). ΔROE is attributed to margin, turnover, and leverage with an
   exact three-factor Shapley decomposition — contributions sum to ΔROE to within
   `5.684e-14`, not an approximation. Persistence uses `next_year_peer_relative_change`
   as the primary outcome, specifically to net out common-year shocks (2020–2021
   account for 47.6% of eligible transitions in this panel).
3. **Sample honesty.** The frozen sample audit found 21 eligible H1 transitions
   across 10 unique companies — 4 leverage-driven, 17 operating-driven, with the
   leverage group concentrated in just 3–4 companies and 75% of leverage
   transitions falling in FY2019. Against the project's own pre-registered
   thresholds, that's Evidence Tier B: enough for descriptive patterns, not enough
   for a group-comparison claim, and nowhere near enough for a causal one.
4. **Finding.** The Tier B pattern doesn't support the hypothesis: the
   leverage-driven group's median next-year peer-relative ROE change is **+35.2
   percentage points**, versus **-11.9 points** for the operating-driven group —
   the opposite direction from what H1 predicted. I report that directly rather
   than reframing it, along with the concentration and year-imbalance caveats that
   explain why it isn't strong evidence either way.
5. **What it demonstrates.** SQL window functions and CTEs for peer/versioned
   data; Python for XBRL parsing, cleaning, and reshaping; research discipline —
   a falsifiable hypothesis, a pre-frozen evidence-tier threshold, and a documented
   negative/inconclusive result instead of a curve-fit narrative; and a Power BI
   layer that only presents SQL-owned numbers, with zero research logic re-derived
   in DAX.

## Anticipated interview questions (charter v3.0 §14.4)

**Why is the independent unit a company rather than a company-year?**
Because ROE trajectories within one company are autocorrelated across years — five
clean transitions from one company are not five independent data points. The audit
reports both: 21 eligible transitions *and* 10 unique companies, and Tier A (not
reached here) would additionally require company-clustered bootstrap rather than
treating transitions as i.i.d.

**How did the A3 sample audit determine H1 Tier A/B/C?**
Thresholds were frozen before the scan ran: Tier A needs ≥15 unique companies, ≥40
transitions, ≥8 companies in each driver group, and no company over 20% of
transitions. The full-candidate scan returned 21 transitions across 10 companies
with the leverage group at 3–4 companies — short of Tier A on unique-company count,
landing in the Tier B band (8–14 companies, or a driver group under 8).

**Why combine margin and turnover into "operating-driven" for the main
comparison?**
Both represent execution inside the business (pricing/cost control and
asset-efficiency) as opposed to a capital-structure change. Collapsing them keeps
the primary test binary — capital-structure-driven vs. operations-driven — while
margin-only and turnover-only splits remain available as secondary description.

**How did you handle negative ROE improvements and non-positive equity?**
Both are excluded from the H1 main sample by construction: the eligibility rule
requires `ROE_(t-1) > 0`, `ΔROE > 0`, and positive average equity at t-1, t, and
t+1. A company improving from -30% to -10% ROE is not merged into that sample; it's
separately flagged `turnaround_from_loss` for case-level description only.

**Why Shapley rather than raw component changes?**
ROE is a product of three factors, not a sum, so naive per-factor deltas leave an
unallocated interaction term and don't reconstruct ΔROE exactly. The exact
three-factor Shapley decomposition allocates that interaction term so contributions
sum to ΔROE precisely (verified to `5.684e-14` across the formal sample) and stays
well-defined when net margin is negative.

**How were XBRL conflicts and restatements handled?**
An explicit `concept_map` sets tag priority per canonical field; every case where
tags disagree is logged with winning value, discarded value, and relative
difference (`concept_conflicts`), with severity thresholds frozen at Gate 1 (low
≤0.5%, medium 0.5–5%, high >5%, mandatory reconciliation above that). Version
selection always takes the latest *valid* restated filing, not simply the most
recent `filing_date`.

**Why is B4 a complete product before Power BI?**
Every research computation — DuPont, Shapley, peer medians, H1 outcomes, quality
flags — lives in SQL/DuckDB, is covered by 9 automated tests, and is documented in
two executed notebooks plus a full README. None of that depends on a BI tool.
Power BI in B5 only adds a single-page, slicer-driven presentation of numbers that
already exist; it introduces no new logic.

**What result would make you reject H1?**
This project's actual Tier B result *is* that case: the leverage-driven group's
next-year peer-relative ROE change is positive (+35.2pp) while the operating-driven
group's is negative (-11.9pp) — the opposite of what H1 predicts. It's disclosed as
a genuine counter-pattern, with the caveat that a 3–4 company leverage group,
concentrated 75% in FY2019, is too thin and unbalanced to treat as a confident
rejection rather than an inconclusive, direction-reversing signal.

## Notes for whoever finalizes B5

- If the live Power BI page surfaces a materially different headline number than
  the ones above (it shouldn't — same frozen CSV), fix the CSV/SQL first and
  re-derive these materials; never edit a number here to match a report without
  tracing it back to the mart.
- Keep the Tier B wording ("descriptive", "examined", "pattern") throughout. Do not
  upgrade to Tier A language ("tested", "validated") anywhere these materials are
  reused (README, LinkedIn, resume, cover letters).
