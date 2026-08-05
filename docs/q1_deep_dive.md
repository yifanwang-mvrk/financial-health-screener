# Q1 Deep Dive — Full Project Narrative

Purpose: a granular, step-by-step, branch-by-branch account of the whole Q1 build — what layer each piece sits in, exactly what was done, why each decision branch was taken, and what it means in business/research terms. Written so you can defend any single sentence of it in an interview without notes.

Data as of: **2026-08-05**. Frozen contract version: **Gate1-v1.0**.

---

## Part 0 — Elevator Pitches

**30 seconds:**
"I built a peer financial-quality screener for 21 U.S.-listed e-commerce companies. It explains *where* ROE comes from — margin, asset efficiency, or leverage — using SEC filing data, a Python/DuckDB/SQL pipeline, and a Power BI front end. The research question was whether leverage-driven ROE improvements are less durable than operations-driven ones a year later. The honest answer, with the sample I could build, is that the evidence isn't strong enough to say — and the descriptive pattern I did get actually runs the other way, which the project documents rather than hides."

**3 minutes:** add — the DuPont/Shapley mechanics, the sample-audit discipline (Evidence Tier A/B/C), the two-tier deliverable (B4 analytical minimum, B5 Power BI portfolio release), and the honest limitations (unbalanced panel, year concentration, non-independence of company-years).

Full CV bullet, 30-second intro, 5-minute narrative, and Q&A bank live in [`docs/recruiter_pitch.md`](recruiter_pitch.md) — this document is the *why and how* behind every line in that file.

---

## Part 1 — Project Positioning

### 1.1 The one-sentence framing

A reproducible, public-filing-based peer financial-quality screener for U.S.-listed e-commerce companies: it explains *where* ROE comes from, and tests whether leverage-driven ROE improvement is less persistent than operations-driven improvement. If evidence allows, it extends to distress-event paths and a current risk screen (Q2/Q3) — but that extension is conditional and did not happen in this build.

### 1.2 The two research questions

- **Q1-A (descriptive, always delivered):** Is ROE driven by net margin, asset turnover, or the equity multiplier, across different e-commerce business models? Can two companies with similar ROE have materially different financial quality?
- **Q1-H1 (falsifiable hypothesis, conditional on sample size):** Are ROE improvements driven mainly by rising leverage (equity multiplier) less persistent one year later than improvements driven mainly by operations (margin or turnover)?

Why this question matters commercially: two companies can print the same ROE for very different reasons. A private-equity-style leverage-up can flatter ROE without making the underlying business better; an equity/credit analyst who can't tell the two apart is mispricing risk. This project builds the instrument to tell them apart, then asks whether the leverage story actually fades faster — the kind of question a buy-side analyst or credit analyst would actually want answered before trusting a ROE trend.

### 1.3 Who this is for

- **Product-setting user:** finance / equity / risk analysts who need to quickly tell whether a company's returns are operations- or leverage-driven, and where to dig further.
- **Portfolio evaluator:** a recruiter or hiring manager — 3 minutes to understand the value, 15 minutes of follow-up questions to check data, methodology, SQL, Power BI, and limitations without the story falling apart.

### 1.4 What the project explicitly does NOT do

- No buy/sell recommendations, target prices, or return forecasts.
- Peer comparisons are descriptive, never generalized into industry-wide statistical claims.
- The retrospective persistence analysis is never described as an out-of-sample bankruptcy-prediction model.
- No "validated" language is used when the H1 or Q2 sample is thin — the wording downgrades with the evidence, never the data-quality bar.
- No black-box 0–100 risk score that hides where a number came from.

### 1.5 E-commerce scope boundary

A company had to satisfy all of: online transactions/platform commission/DTC as the core revenue engine (not a channel of a larger conglomerate); an explainable inventory/fulfillment risk ownership; a recordable revenue-recognition model (gross/net/mixed); a business narrative consistent with one of the three peer archetypes; and continuous coverage of the Q1 core annual fields. Anything that failed one of these got an explicit `exclusion_reason` — never a silent drop.

---

## Part 2 — The Full Pipeline, One Paragraph Each

```
A0E  →  A1  →  A2  →  A3  →  Gate 1  →  B1  →  B2  →  B3  →  B4  →  B5  →  Gate 2  →  (Q2/Q3, not authorized)
```

- **A0E — Power BI environment check.** Verified once (2026-07-22) that CSV/Power Query import, semantic modeling, DAX, slicers, Report save, and `.pbix` export all worked in Power BI Service on this Mac. Passed; never repeated.
- **A1 — Unified Company & Event Census.** Light-research pass (memory, company sites, exchange filings, light search — explicitly *not* SEC XBRL yet) to build a deduplicated candidate pool of companies and a separate pool of distress-event candidates, each with an inclusion/exclusion reason.
- **A2 — Two-company Source Probe.** Picked one Marketplace company (EBAY) and one Inventory-led company (CHWY), ran them through one real SEC-extraction pipeline, and used the friction discovered there — tag variance, unit/duration issues, restatements — to design the rules the full-candidate scan would need.
- **A3 — Coverage Verification + H1 Sample Audit.** Applied A2's rules to *all* 40 Q1 candidates and all 14 event candidates. This produced the real numbers — not estimates — behind the Path A/B and H1 Tier A/B/C recommendations.
- **Gate 1 — Freeze Scope.** Converted A3's evidence into a signed, versioned contract (`Gate1-v1.0`): final company list, peer groups, canonical fields, source/version rules, H1 Tier, and the Power BI mart's field contract. Nothing downstream is allowed to renegotiate this without a new, evidenced Gate decision.
- **B1 — Pilot Pipeline.** Built and revalidated the entire raw→normalized→DuckDB→marts pipeline on 6 companies chosen to include multiple business models, a complex fiscal year, a conflict/restatement case, and a metric-failure case — proving the pipeline works before spending it on all 21 companies.
- **B2 — Q1 Sample Expansion.** Ran the *same, unmodified* B1 pipeline across the frozen 21-company sample and FY2018–FY2024 window. Any company-specific exception had to be an explicit, filing-backed override — never a silent patch.
- **B3 — SQL Analytical Marts.** Seven ordered SQL files turn the normalized facts into DuPont metrics, exact Shapley ROE-change attribution, persistence outcomes, the H1 sample audit, peer summaries, and the single 60-field Power BI mart.
- **B4 — Analytical Release.** Freezes the analytical inputs, runs the full EDA/QA/research narrative, performs manual filing reconciliation, and packages README/data-dictionary/limitations/tests — a complete, presentable product with *zero* dependency on Power BI.
- **B5 — Power BI Product Release.** Rebuilds the single-page Executive Overview on the frozen B3 mart, reconciles every visual against it, and ships `.pbix` + screenshot — turning the already-complete B4 analysis into a 3-minute recruiter-facing artifact.
- **Gate 2 — Q2/Q3 Go/No-Go (unresolved).** A3 supports a Tier A feasibility *recommendation* for Q2, but the actual go/no-go decision has deliberately not been made — Q1's completion does not depend on it.

---

## Part 3 — Stage-by-Stage Deep Dive

Each subsection follows the same shape: **layer → what was actually done, in order, including the branch decisions → business/research meaning → real output numbers.**

### 3.1 A1 — Unified Company & Event Census

**Layer:** research/data scoping (not yet financial-data engineering).

**What was done, in order:**
1. Set a provisional year window (FY2018–FY2024) and three provisional peer groups (Marketplace/Platform, Inventory-led E-commerce, DTC Brand), explicitly flagged as changeable at Gate 1.
2. For each candidate company, walked a fixed decision order: (a) is e-commerce the *core* revenue engine, not a channel of a conglomerate? → if not, excluded outright; (b) can inventory/fulfillment risk ownership be explained? → ambiguous cases flagged `boundary`, not forced into a bucket; (c) what's the revenue-recognition model (gross/net/mixed/unknown)? → recorded provisionally, verified later in A2/A3; (d) assign `peer_group` and a `classification_confidence` (high/medium/low) — low confidence was left low rather than faked to make the three groups look balanced.
3. Built the company table in batches (5 → 15 → 30–40) to calibrate the schema before chasing volume, and stopped once ~30–40 Q1 candidates were reached with all three business models and boundary/delisted/distressed cases represented — a deliberate **stopping rule**, not exhaustive search.
4. Built a parallel, independent `events.csv` for distress candidates (Chapter 11, going-concern opinions, covenant breaches, debt restructuring, emergency financing, asset exit/liquidation), each dated at **t=0 = the first date the evidence was public** (not fiscal year-end, not deal-close date), stopping at ~10–15 candidates.
5. Audited the census: no duplicate `company_id`, every company has an inclusion/exclusion call with a real reason (never "not suitable"), every event links to a valid company and has date/basis/source/confidence.

**Business meaning:** this is the sampling-frame decision — before you can say anything about "e-commerce financial quality," you have to define, defensibly, what counts as an e-commerce company and why some plausible candidates don't count. Getting this wrong invalidates everything downstream regardless of how good the SQL is later.

**Real output:** 50 total companies scoped, 40 Q1 candidates, 14 event candidates across four provisional peer groups (including a temporary Hybrid/Boundary bucket later resolved at Gate 1).

### 3.2 A2 — Two-Company Source Probe

**Layer:** data engineering — first real contact with SEC XBRL.

**What was done, in order:**
1. Picked **CHWY** (Inventory-led) and **EBAY** (Marketplace/Platform) — chosen to maximize contrast in revenue-recognition model and asset structure, and recorded *why*, not just "well-known companies."
2. Built `src/extract_sec.py` once: calls SEC Companyfacts by CIK with a compliant User-Agent, saves the *entire* raw JSON (not pre-filtered fields), names files deterministically by `company_id`, logs `loaded_at`, and never silently overwrites a prior raw pull.
3. Probed a first-round mandatory field set (Revenue, Net Income, Total Assets, Stockholders' Equity) and a second-round conditional set (Cash, Inventory, Current Assets/Liabilities, Total Debt, OCF, CapEx) for: which XBRL tags exist, taxonomy consistency, unit consistency, plausible `period_start`/`period_end`/`duration_days`, reliable `fiscal_year`/`fiscal_period`, usable `filing_date`/`accession_number`, and — critically — whether the *same period* had multiple conflicting values across tags or restatements.
4. From that friction, built the first `concept_map.csv`: one row per (`canonical_field`, `source_tag`) pair with an explicit `priority` (which tag wins when both exist), `flow_or_stock` (controls whether it needs a duration check or a point-in-time balance), `sign_multiplier` (e.g. CapEx is always stored as a positive outflow, OCF keeps its true sign, inventory must be non-negative), and `duration_rule`.
5. Generated a small `concept_conflicts` sample: every time two tags disagreed for the same company-period, logged `winning_tag`, `discarded_tag`, `winning_value`, `discarded_value`, `relative_difference`, and the `resolution_rule` applied — the conflict *threshold itself* (low/medium/high) was deliberately left unfrozen at this stage, to be set from the *distribution* observed once A3 ran at full scale, not guessed in advance.
6. Verified a `latest-restated` selection rule could run deterministically: keep the most recent filing that is *valid*, not simply the row with the latest `filing_date` (a later filing can still be the wrong one if it fails validity checks).

**Business meaning:** this is the step that turns "SEC data exists" into "SEC data can be trusted and combined across companies." Two issuers rarely tag the same concept identically — Amazon and eBay might report "Revenue" under different XBRL tags, different units, different fiscal calendars. Without an explicit, auditable priority rule, any downstream ratio is silently comparing apples to a slightly different fruit.

**Real output:** 155 filing-level annual facts, 60 latest-restated winners, 38 traceable discarded-value records, a 22-row field audit, and — crucially — the exact list of scan metrics A3 would need to run at scale.

### 3.3 A3 — Coverage Verification + H1 Sample Audit

**Layer:** data engineering at scale + the project's most important research-design gate.

**Why this step has to exist:** ROE uses *average* equity (mean of consecutive year-end balances), and H1 needs three consecutive fiscal years (t−1, t, t+1) per transition. On a 7-year annual panel, that ceiling means each company can contribute at most ~4 H1 transitions — not 5, not "however many years the company has." You cannot know the real H1 sample size until you've actually scanned every candidate's real field coverage; guessing from theoretical panel length overstates it.

**What was done, in order:**
1. **Q1 coverage scan** (all 40 candidates): counted full annual years available in FY2018–FY2024, checked coverage of Revenue/Net Income/Assets/Equity, checked whether *prior-year* balances existed (needed for averages), counted tag conflicts and severity, flagged whether a company needed an override, and recorded the primary failure reason per company.
2. **H1 transition audit** (built the full table: `company_id`, `peer_group`, `fiscal_year_t`, `roe_t_minus_1`, `roe_t`, `roe_t_plus_1`, `average_equity_valid`, `components_valid`, `positive_roe_base`, `positive_roe_change`, `forward_year_available`, `dominant_driver`, `eligible_h1`, `exclusion_reason`), applying the **frozen main-sample rule without relaxing it for sample size**:
   - `average_equity` positive at t−1, t, and t+1
   - `ROE(t−1) > 0`
   - `ROE_t − ROE(t−1) > 0`
   - DuPont components valid at both t−1 and t
   - `ROE(t+1)` observable
   - A company improving from −30% to −10% ROE does **not** qualify for the main sample — it's separately tagged `turnaround_from_loss` for case-level description only, never merged into the group comparison.
3. **Driver classification via exact Shapley decomposition** of every valid ΔROE into margin/turnover/multiplier contributions (see §4.2 for the math): `leverage_driven` if the multiplier contribution is the largest *positive* one, `operating_driven` if margin or turnover is, `mixed_or_ambiguous` otherwise.
4. **Mandatory sample-audit reporting**, not just a pass/fail: total eligible transitions, unique eligible companies, leverage-driven vs. operating-driven counts (both transitions *and* unique companies — these are different denominators and both matter), per-company transition share (to catch concentration), distribution by peer group, distribution by fiscal year (to catch a single crisis year dominating the sample), and a full exclusion-reason breakdown.
5. **Q2 event verification** in parallel: real `verified_pre_event_quarters`, three-statement coverage, filing-date availability, point-in-time feasibility, and manual-review cost per event candidate — turning A1's *theoretical* event window into a *verified* one.
6. Produced the **Data Path recommendation** (A vs. B) and the **H1 Evidence Tier recommendation** (A/B/C) as evidence-backed proposals for Gate 1 — not decisions; A3 recommends, Gate 1 freezes.

**Business meaning:** this is the step that keeps the whole project honest. It would have been easy to relax "positive ROE base" or "3 consecutive years" to manufacture a bigger, cleaner-looking H1 sample. A3's discipline is exactly what makes the eventual Tier B (not Tier A) result *credible* rather than cherry-picked — the thresholds were set before the scan, applied mechanically, and the resulting sample size is reported honestly even though it's smaller than hoped.

**Real output:** 4,823 core annual fact versions scanned, 1,046 latest-restated winners, 945 traceable differences, 200 potential H1 transitions scanned, all 14 events verified (12 qualify; BOXD and FTCH excluded for specific documented coverage reasons), 31 coverage-viable candidates supporting **Path A**, and a recommendation of **H1 Tier B**.

### 3.4 Gate 1 — Freeze Scope

**Layer:** governance / contract-freezing, not engineering.

**What was done:** every A3 recommendation was converted into a signed, dated decision in `docs/gate1_decision.md` (version `Gate1-v1.0`, frozen 2026-08-05, owner Yifan Wang), each with the frozen result *and* the evidence summary that justified it:

| Decision | Frozen result | Evidence |
| --- | --- | --- |
| Data Path | **Path A** | 31 viable candidates; merged pools 12 Marketplace / 7 Inventory-led / 12 DTC |
| Formal sample | **21 companies**, FY2018–FY2024 unbalanced panel | 7 companies per retained group; all 40 candidate decisions versioned |
| Peer groups | Retain Marketplace, Inventory-led, DTC; **cancel standalone Hybrid** | AMZN, BYON viable and merged into Inventory-led; GROV stays a short-history boundary exclusion |
| Six-company scope | Demoted to **B1 Pilot membership only** | All six remain in the formal 21, but the Pilot doesn't define formal sample size or period |
| H1 Tier | **Tier B**, descriptive patterns only | 21 eligible transitions / 10 companies; leverage group only 4 transitions / 3 companies |
| H1 outcome/driver rules | Peer-relative next-year change as primary; exact Shapley; label + continuous share | Retained without relaxation from A3 |
| Canonical fields | 13 extracted fields + derived FCF; 3 noncore fields excluded | A2/A3 coverage supports the DuPont core + directly used quality fields |
| Source/version policy | SEC Companyfacts canonical; filing-level documented fallback; latest *valid* restated version | A2: 60 winners/38 discarded; A3: 1,046 winners/945 differences |
| Conflict thresholds | Low ≤0.5%; medium 0.5–5%; high >5% (mandatory reconciliation) | Frozen from the observed A2/A3 distribution |
| Q2 feasibility | **Tier A candidate**, formal authorization pending Gate 2 after B5 | A3 verified 12/14 event candidates |

**Business meaning:** this is the point where the project stops being exploratory and becomes a fixed-scope engineering build. Every subsequent stage (B1–B5) is *forbidden* from renegotiating these numbers — if B2 discovers a company doesn't fit cleanly, the fix is an explicit, filing-backed override, never a quiet change to the frozen sample. This discipline is what makes the final research claim defensible: nothing was tuned after seeing results.

### 3.5 B1 — Pilot Pipeline

**Layer:** data engineering, proof-of-pipeline before proof-of-scale.

**What was done, in order:**
1. Selected 4–6 pilot companies (AMZN, BKNG, CHWY, DASH, EBAY, ETSY) specifically because together they cover ≥2 business models, one complex fiscal year, one conflict/restatement case, and one metric-failure case — not because they're the biggest names.
2. Built the fixed pipeline sequence behind **one entry point**: Extract → Normalize annual facts → Apply concept map & sign convention → Log conflicts → Select latest-restated → Validate → Load DuckDB → Build Pilot marts. No company was ever hand-patched outside this sequence.
3. Discovered during reconciliation that the shared single-tag CapEx rule silently omitted capitalized-software cash outflows for **DASH** and **ETSY** — added a *filing-backed*, explicit override for those two companies rather than loosening the shared rule for everyone.
4. Verified the DuPont identity and the exact Shapley contribution sum both reconcile to floating-point precision, and ran one company (CHWY) through a manual filing comparison to catch a comparative-equity restatement issue before it could propagate.

**Business meaning:** proving the pipeline is *correct and reproducible* on a small, deliberately-hard subset is far cheaper than discovering a systemic bug after running all 21 companies. The B1→B2 split is a classic engineering risk-reduction move: fail fast and cheap, not slow and expensive.

**Real output:** 12 cached SEC artifacts → 570 mapped filing-level facts → 225 latest/derived facts → 76 explicit conflict records → 39 metric flags → 18 Pilot company-year mart rows; DuPont/Shapley reconciliation gaps below `1e-10`.

### 3.6 B2 — Q1 Sample Expansion

**Layer:** data engineering at full scale.

**What was done, in order:**
1. Applied the **exact same, unmodified** B1 pipeline to the frozen 21-company Gate 1 sample and FY2018–FY2024 window (with FY2017 loaded only to supply opening balances for FY2018 averages).
2. Extended `concept_map.csv` only where a *real, observed* problem appeared — never speculatively. Three accession-backed exceptions were added: ABNB's free-cash-flow table values, CVNA's operating-income derivation, and generalizing the DASH/ETSY CapEx aggregation fix discovered in B1.
3. Re-ran conflict and quality reports after every expansion batch, closing all required company-year coverage gaps **without sentinel values** — a missing field stays `NULL`, it is never filled with 0 or a placeholder.

**Business meaning:** this is where "does the method work on one company" becomes "does the method work as a *system* across 21 companies with genuinely different accounting choices" — the real test of whether the concept-mapping approach generalizes, or whether it was accidentally tuned to the Pilot six.

**Real output:** 42 checksummed SEC artifacts → 5,439 normalized pre-map records → 4,780 mapped filing-level facts → 1,959 latest/derived canonical facts; 212 rejected candidates; 875 explicit winner/discarded conflicts; 262 metric-quality flags; zero required company-year fields missing; all 21 companies covered, 7 per peer group.

### 3.7 B3 — SQL Analytical Marts

**Layer:** analytical engineering — where "raw facts" becomes "research-ready metrics." This is the layer most likely to get a deep technical follow-up question, so each mart is broken out individually.

Executed in this exact, frozen order:

1. **`01_core_tables.sql`** — loads the B2 output into DuckDB core tables. No calculation, just the entry point.
2. **`02_q1_latest_restated.sql`** — implements the latest-*valid*-restated selection per (company, fiscal year, canonical field): picks the most recent filing that passes validity checks, not simply `MAX(filing_date)`. Produces `source_selection_method` and a human-readable `source_selection_note` for every row, so every number is traceable to *why* it was chosen.
3. **`03_q1_metrics.sql`** — computes average-balance DuPont metrics: `average_assets`/`average_equity` as the mean of consecutive fiscal-year-end balances, then `net_margin = NI/Revenue`, `asset_turnover = Revenue/AvgAssets`, `equity_multiplier = AvgAssets/AvgEquity`, `roe = NI/AvgEquity`, all protected with `NULLIF` on every denominator (never a division-by-zero crash, never a fabricated 0). Also emits `roe_valid_flag`/`dupont_valid_flag` and the reason when invalid (e.g. `nonpositive_average_equity`, `missing_prior_balance`).
4. **`04_q1_shapley_contributions.sql`** — the exact three-factor Shapley decomposition of ΔROE into margin/turnover/multiplier contributions (math in §4.2), plus the `dominant_driver` label and the continuous `leverage_contribution_share`.
5. **`05_q1_persistence.sql`** — `LEAD`-based next-year outcomes: `next_year_roe_change`, `roe_reversal_flag`, `peer_relative_roe_t`, and the **primary outcome** `next_year_peer_relative_change` (peer-relative, specifically to net out common-year macro shocks — see §4.3 for why this is primary and not the raw ROE change).
6. **`06_q1_h1_sample_audit.sql`** — reproduces the frozen Gate 1 H1 eligibility/exclusion/concentration audit directly from the live formal data, as a running check that nothing has drifted from the frozen contract.
7. **`07_q1_powerbi_mart.sql`** — the single 60-field consumption table (`q1_powerbi_mart`) joining company metrics, peer benchmarks, Shapley labels, H1 outcomes, and quality warnings into one row per (company, fiscal year) — engineered so Power BI never needs to recreate any research logic in DAX.

**Business meaning:** this layer is the actual "product" in a data sense — it's what turns a pile of normalized SEC facts into the specific numbers a peer-benchmarking tool would show an analyst. Keeping every calculation in SQL (not Python, not DAX) means the logic is inspectable, testable, and has exactly one source of truth.

**Real output:** 137 formal company-years, 116 candidate transition rows, 21 peer-year summaries, a 137-row/60-field Power BI mart; reproduces the frozen H1 Tier B audit exactly (21 eligible transitions / 10 companies / 4 leverage / 17 operating); maximum absolute DuPont identity gap `2.842e-14`, maximum absolute Shapley reconciliation gap `5.684e-14`.

### 3.8 B4 — Analytical Release

**Layer:** research synthesis + quality assurance. This is the **CV-ready minimum deliverable** — complete and presentable with zero Power BI dependency.

**What was done, in order:**
1. **Froze the analytical inputs**: recorded a `data_as_of` date and SHA-256 hashes of every input, and treated the mart outputs as read-only during analysis — any fix had to go back to the Python/SQL source and rerun, never a direct edit to a processed file.
2. **Quality EDA**: coverage maps, missingness rates, concept-conflict severity, latest-restated version-selection distribution, metric-flag distribution, the H1 exclusion waterfall, per-company transition share, per-peer-group distribution, and per-fiscal-year distribution (specifically to check whether leverage-driven and operating-driven transitions are *year-balanced* — they are not, see §6).
3. **Q1-A financial-quality analysis**: compared ROE/margin/turnover/multiplier across peer groups, surfaced same-ROE-different-driver company pairs (ABNB vs. LOVE, §3.9 findings below), and showed companies' positions relative to peer medians.
4. **H1 analysis, executed strictly at Tier B rules**: descriptive persistence patterns, company trajectories, case-level detail, and cautious descriptive group differences — explicitly *not* a validated group-comparison claim, and explicitly *not* company-clustered bootstrap (that's Tier A-only machinery, not reached here).
5. **Mandatory honesty checks**: at least one genuine counter-example was surfaced rather than cherry-picked away; the project states in writing what result *would* have rejected H1 (see §5); the FY2020–2021 and FY2019 year-concentration risk is disclosed; the fact that latest-restated data is not point-in-time is disclosed; negative-equity/negative-ROE handling is disclosed; no investment language appears anywhere.
6. **Manual filing reconciliation**: 8 checks across Revenue/Net Income/Assets/Equity for **AMZN** (clean calendar-year control — all four fields matched exactly) and **CHWY** (the deliberately messy 52/53-week fiscal calendar plus a comparative-restatement case — small rounded differences, all below the frozen 0.5% tolerance).
7. **Minimum automated test set** (7 conceptual tests, expanded to 59 total test cases across the whole repo): concept-mapping priority, sign standardization, latest-restated selection, DuPont identity, exact Shapley contribution sum, H1 eligibility, metric flags.
8. Packaged the formal README, data dictionary, limitations, reproduction steps, static charts, executed notebooks, CV bullet, and interview narrative.

**Business meaning:** B4 is the point where the project can be judged entirely on its research and engineering merits, independent of any presentation layer. It answers the question "did you actually find something, and can you show your work" — which is what a technical interviewer probes first, before ever looking at a dashboard.

**Real output:** frozen input manifest with checksums; 14 formal EDA/research tables; 8 reviewed static charts; 2 executed notebooks with embedded outputs; 8 filing-reconciliation checks (0 discrepancies beyond tolerance); a formal analysis report; the Tier B result documented as **not supporting H1** (see §5).

### 3.9 B5 — Power BI Product Release

**Layer:** presentation — the only layer allowed to touch a BI tool, and even here, only for display.

**What was done, in order (including this session's completion work):**
1. **Input boundary enforced**: Power BI Service consumes only `data/processed/q1_powerbi_mart.csv` — every DuPont number, peer median, Shapley contribution, driver label, H1 outcome, and quality warning is pre-computed in SQL. DAX is restricted to presentation-only measures (`MAX()` aggregations on the currently-selected row) and formatting — never a recomputation of research logic.
2. **Single-page layout**: header + subtitle stating scope (`US-listed e-commerce | FY2018-FY2024 | 21 companies | Q1 analytical release`); three slicers (Company, `formal_peer_group`, Fiscal Year); four KPI cards (ROE, Net Margin, Asset Turnover, Equity Multiplier); a company-vs-peer-median ROE trend line; a DuPont Shapley-contribution bar chart; a "Selected Company-Year Interpretation" table (`h1_evidence_tier`, `dominant_driver`, `h1_exclusion_reason`); and an "Evidence, Quality & Comparability Notes" panel (`h1_permitted_inference`, `quality_warnings`, `comparability_note`).
3. **This session's repair work**: the underlying Power Query source had already been repointed at the formal 21-company mart, but two visuals still referenced fields retired from the six-company Pilot schema (`analysis_peer_group`, `dominant_change_driver`, `h1_sample_status`) — remapped to the frozen field names (`formal_peer_group`, `dominant_driver`, `h1_exclusion_reason`), and corrected a stale header subtitle still reading "FY2021-FY2023 | 6 companies."
4. **Reconciliation, not assumption**: verified six ground-truth company-years directly against the mart CSV — AMZN FY2023 (clean values), AMZN FY2018 (correctly blank at the panel's first year, since no prior-year transition exists), BKNG FY2023 (an extreme 22,573.7% ROE from near-zero average equity, deliberately left unclamped rather than hidden), BKNG FY2019 (a normal eligible leverage-driven transition), ETSY FY2023 (invalid ROE correctly rendered blank, not zero), and FIGS FY2024 (a `mixed_or_ambiguous`/`no_roe_improvement` case).
5. **Shipped the release**: saved in Power BI Service, exported `.pbix` and a PDF (converted locally to the repository screenshot), and updated every status document from "B5 next" to "B5 done."

**Business meaning:** B5 exists purely to compress an already-complete, already-defensible analysis into something a recruiter can absorb in three minutes without reading SQL. The discipline of *not* letting research logic leak into DAX is what keeps the presentation layer from becoming "a second, less-tested source of truth" — a common failure mode in real BI teams that this project deliberately avoids.

---

## Part 4 — Core Methodology, Deep Enough to Survive Follow-Ups

### 4.1 DuPont identity and average balances

```
ROE = Net Margin × Asset Turnover × Equity Multiplier
    = (Net Income / Revenue) × (Revenue / Average Assets) × (Average Assets / Average Equity)
    = Net Income / Average Equity
```

**Why average, not year-end, balances:** a flow measure (net income, earned *across* the year) divided by a point-in-time stock measure (year-end equity) mismatches the denominator's timing — a company that raised a lot of new equity in December would show an artificially low ROE for income earned when equity was much smaller all year. Averaging consecutive fiscal-year-end balances is the standard fix, and it's why H1 needs *three* consecutive years of valid balances (t−1, t, t+1) rather than one.

**Why metrics get invalidated rather than computed anyway:** if average equity is zero or negative, ROE is mathematically undefined or economically meaningless (a company can show a huge *positive* ROE purely because equity is a tiny denominator, as BKNG FY2023 demonstrates at 22,573.7% — see §3.9). The project's rule is to flag and null these out (`nonpositive_average_equity`), never to compute and silently trust a number that means nothing.

### 4.2 Exact three-factor Shapley decomposition

**The problem it solves:** ROE is a *product* of three factors, not a sum. A naive attribution — "margin changed by X, so margin's contribution is X times the *old* turnover and multiplier" — leaves an unallocated interaction term, because moving all three factors simultaneously creates cross-terms that a simple before/after subtraction can't cleanly assign. The naive approach also breaks down when net margin is negative (a common real case in this project, e.g. the `turnaround_from_loss` companies), because negative bases distort naive percentage contributions.

**The fix:** exact Shapley value attribution treats the three factors as "players" in a cooperative game where the "payout" is ΔROE, and averages each factor's contribution across all possible orderings of applying the three changes. For three factors this is a closed-form calculation, not simulation, and it has one property that matters enormously for credibility: **the three contributions sum exactly to the observed ΔROE** — verified in this project to a maximum absolute gap of `5.684e-14` across all 116 candidate transitions. That reconciliation number is a direct, checkable claim you can make in an interview: "the math isn't approximate, and I can prove it."

```
ΔROE = contribution_margin + contribution_turnover + contribution_multiplier   (exactly, by construction)
```

- `dominant_driver = leverage` if the multiplier's contribution is the single largest **positive** contribution.
- `dominant_driver = operating` if margin's or turnover's contribution is the largest positive one.
- `dominant_driver = mixed_or_ambiguous` if ΔROE ≤ 0, or the contributions point in conflicting directions with no clear largest positive term.
- The continuous `leverage_contribution_share` is retained separately for robustness checks that don't want a hard binary label.

### 4.3 H1 eligibility rules and the Evidence Tier system

**Main-sample rule (all must hold):** `average_equity(t-1,t,t+1) > 0`; `ROE(t-1) > 0`; `ROE_t - ROE(t-1) > 0`; DuPont components valid at t-1 and t; `ROE(t+1)` observable. A company recovering from a *loss* (negative base ROE) is excluded from this comparison by construction and separately flagged `turnaround_from_loss` — mixing "loss turning into a small profit" with "already-profitable company getting more profitable" would confound two different economic stories.

**Why the primary outcome is peer-relative, not raw ROE change:** `next_year_peer_relative_change = (ROE_(t+1) - peer_median_(t+1)) - (ROE_t - peer_median_t)`. Raw `next_year_roe_change` is kept as a secondary outcome, but the *primary* claim uses the peer-relative version specifically because e-commerce had genuine sector-wide shocks (2020–2021 account for 47.6% of eligible transitions in this panel) — a common macro shock would move every company's raw ROE in the same direction in the same year, and a naive before/after comparison could mistake "everyone got hit by the same thing" for "leverage-driven companies specifically reverted." Netting out the peer median in the same year for the same peer group removes that shared-shock contamination (though it cannot remove *year-composition* risk — see §6).

**Why the project reports both transitions and unique companies:** the analysis unit is *company × fiscal-year transition*, but the independent entity for inference purposes is the *company*, because transitions from the same company across different years are not independent draws — a company with a persistently leveraged balance sheet will tend to generate several similar-looking transitions, which is not the same evidentiary weight as five different companies each showing the pattern once. Reporting "21 transitions across 10 companies" (not "21 independent observations") is the honest framing.

**Evidence Tier thresholds (frozen *before* the scan, not fit to the result):**

| Tier | Threshold | Permitted framing |
| --- | --- | --- |
| A | ≥15 unique eligible companies; ≥40 eligible transitions; ≥8 unique companies in *each* driver group; no single company >20% of transitions | "exploratory comparative panel evidence"; permits company-clustered bootstrap |
| B | 8–14 unique companies, OR 20–39 transitions, OR either driver group has <8 companies, OR one company is over-concentrated | "descriptive persistence patterns"; distributions, trajectories, cases, cautious differences |
| C | <8 unique companies, OR <20 eligible transitions | no group comparison at all; "evidence insufficient," illustrative cases only |

The formal sample landed at **10 unique companies / 21 transitions**, with the leverage-driven group specifically thin (**3 unique companies / 4 transitions**) — short of Tier A purely on the unique-company count, which is why the project reports Tier B language throughout rather than a validated test, and why company-clustered bootstrap (a Tier A-only tool) was never run.

### 4.4 XBRL conflict handling and latest-restated selection

Every canonical field has an explicit `priority`-ordered list of acceptable source tags in `concept_map.csv`. When two tags disagree for the same company-period, the conflict is *logged*, never silently dropped: `winning_tag`, `discarded_tag`, `winning_value`, `discarded_value`, `relative_difference`, and a `resolution_rule`. Severity thresholds (frozen at Gate 1 from the observed A2/A3 distribution) are **low ≤0.5%, medium 0.5–5%, high >5%**, with mandatory manual reconciliation required above the high threshold. Version selection ("latest-restated") always means the most recent filing that is *valid* — a later filing that fails a validity check does not automatically win over an earlier valid one.

### 4.5 Data-quality flag system

Metric flags are automatically derived from the SQL/view layer, never hand-maintained: `non_positive_average_equity`, `zero_denominator`, `missing_prior_balance`, `insufficient_forward_year`, `source_conflict`, `unit_mismatch`, `invalid_sign`. Every denominator in every ratio calculation is protected with `NULLIF` — a missing or invalid value becomes `NULL`, never `0` or a sentinel like `-999`, because a fake zero would silently corrupt every downstream average, peer median, and chart.

---

## Part 5 — Findings and Counterfactual Reasoning

### 5.1 Q1-A: same ROE, different quality

104 of 137 formal company-years have valid average-balance DuPont metrics. Concretely: **ABNB and LOVE both produced roughly 36% FY2022 ROE**, but ABNB got there with a 22.5% net margin and 0.56x asset turnover (margin-led, asset-light platform economics), while LOVE got there with a 9.5% margin and 1.84x turnover (volume/efficiency-led, asset-heavier retail economics). Same headline number, structurally different businesses — exactly the ambiguity the DuPont decomposition exists to resolve.

**BKNG** is the cautionary example: positive but *near-zero* average equity makes a mathematically correct ROE calculation mechanically extreme and economically meaningless (22,573.7% in FY2023) — the project's answer is to flag it loudly (`quality_warnings`), never to hide it or clamp it to look more presentable.

### 5.2 H1: the result that doesn't support the hypothesis

Median next-year peer-relative ROE change: **+35.2 percentage points for leverage-driven improvements** vs. **−11.9 points for operating-driven improvements** — the *opposite* direction from what H1 predicted. This is reported directly, not reframed, alongside the caveats that make it inconclusive rather than a confident rejection: the leverage group is only 3–4 companies, 75% of leverage transitions cluster in FY2019 (the remainder in FY2021), and FY2020–2021 alone account for 47.6% of all eligible transitions.

### 5.3 What would make you reject H1 outright?

This project's own Tier B result *is* that case in miniature: a clean, well-powered (Tier A), *year-balanced* sample showing leverage-driven outcomes at least as persistent as operating-driven outcomes would be a genuine rejection. What's missing here isn't the direction of the signal — it's statistical power and year balance. A future Q2-scale expansion of the annual panel (more companies, more years, less concentration in 2019–2021) is exactly what would upgrade this from "inconclusive counter-pattern" to "a real answer, in either direction."

### 5.4 If the sample had been larger and balanced?

Two honest possibilities, both worth saying out loud in an interview: (1) the pattern could reverse toward H1's prediction once the 2019/2020–2021 concentration is diluted by more ordinary years — the current result may partly be an artifact of measuring leverage-driven transitions almost entirely from one unusual pre-pandemic cohort; or (2) the counter-pattern could hold up, which would be a genuinely interesting finding worth a dedicated write-up — leverage-driven ROE gains being *more* persistent than commonly assumed, at least in this e-commerce cohort. The project doesn't know which, and says so.

---

## Part 6 — Limitations, Stated Proactively

- **Not point-in-time.** Every metric uses the *latest-restated* value as of the `data_as_of` date, not what was known at the time. This is a peer-benchmarking tool, not a trading signal — using it for anything that requires knowing what an analyst could have known in real time would be a category error.
- **Unbalanced, concentrated panel.** FY2020–2021 alone hold 47.6% of eligible H1 transitions; leverage-driven transitions are almost entirely FY2019/FY2021. Any year-specific macro effect (pandemic e-commerce demand shock, in particular) is a live confound the peer-relative outcome only partially controls.
- **Company-years are not independent companies.** 21 transitions come from only 10 unique companies — repeatedly emphasized throughout the project specifically to prevent overstating statistical power.
- **No investment or distress-prediction claim.** The retrospective, descriptive persistence analysis is never described as forward-looking or predictive.
- **Company concentration.** Maximum single-company share of transitions is 14.3% in the formal sample — below the Tier A 20% threshold, but still worth disclosing given the small group sizes.

---

## Part 7 — Interview Question Bank (by topic)

**Sampling & scope**
- *Why e-commerce specifically?* — narrow enough to make peer comparison meaningful (shared revenue-recognition and inventory-risk questions), broad enough to have real business-model variation (platform vs. inventory-led vs. DTC) worth decomposing.
- *Why did you stop at ~40 candidates instead of scanning every possible company?* — a deliberate stopping rule (§3.1): once three business models, boundary cases, and distressed cases were represented and new companies stopped changing the structure, further search had diminishing research value relative to engineering time.

**Method**
- *Why the company as the independent unit, not the company-year?* — annual transitions repeat within the same issuer and are not independent draws; the audit reports both the transition count and the unique-company count for exactly this reason (§4.3).
- *How did A3 decide Tier A vs. B vs. C?* — pre-frozen thresholds applied mechanically to the real scan result, not chosen after seeing the outcome (§4.3 table).
- *Why combine margin and turnover into "operating-driven"?* — both represent execution *inside* the business (pricing/cost control, asset efficiency) as opposed to a capital-structure decision; this keeps the primary H1 test binary while preserving margin-only/turnover-only splits as secondary description.
- *Why Shapley instead of a simpler attribution?* — ROE is multiplicative, not additive; naive per-factor deltas leave an unallocated interaction term and break down with negative margins. Exact Shapley sums to ΔROE by construction, verified to `5.684e-14` (§4.2).
- *How did you handle negative ROE improvements and non-positive equity?* — excluded from the main H1 sample by construction; negative-to-less-negative cases are separately flagged `turnaround_from_loss`, never merged in (§4.3).
- *How were XBRL conflicts and restatements handled?* — explicit tag-priority concept map, every disagreement logged with a resolution rule, frozen severity thresholds with mandatory reconciliation above 5% (§4.4).

**Results**
- *What did you actually find?* — Q1-A: same ROE can come from structurally different sources (ABNB vs. LOVE); H1: the Tier B descriptive pattern runs opposite to the hypothesis, but the sample is too thin and year-concentrated to call it a rejection (§5.1–§5.2).
- *What result would make you reject H1?* — a Tier A, year-balanced sample still showing leverage-driven persistence at least equal to operating-driven persistence (§5.3).
- *Why is the primary outcome peer-relative rather than raw ROE change?* — to net out common-year macro shocks, given 47.6% of transitions cluster in 2020–2021 (§4.3).

**Engineering / product**
- *Why is B4 a complete product before touching Power BI?* — every research computation lives in tested, documented SQL/DuckDB; Power BI in B5 only presents numbers that already exist, introducing zero new logic (§3.8, §3.9).
- *What's the single-source-of-truth boundary between SQL and Power BI?* — DAX is restricted to `MAX()`-style presentation measures and formatting; every DuPont number, peer median, Shapley contribution, driver label, and H1 outcome is computed in SQL, never recreated in DAX (§3.9, §4).
- *How do you know the pipeline is actually reproducible?* — 59 automated tests spanning concept mapping, sign conventions, latest-restated selection, DuPont/Shapley identities, H1 eligibility, and metric flags all pass from a clean rebuild.

---

## Part 8 — Business Value, Restated

This is not a technical showcase bolted onto a dataset — it's built the way an actual financial-quality screening tool would need to be built for someone to trust it: a defensible sampling frame, an auditable data-conflict resolution process, a pre-registered and honestly-reported hypothesis test, and a presentation layer that cannot silently diverge from the underlying logic. The differentiator versus a typical student project isn't the DuPont formula (that's table stakes) — it's the sample-audit discipline (Evidence Tier A/B/C), the willingness to report and explain a result that didn't support the hypothesis, and the strict separation between "what SQL computed" and "what the dashboard shows," which is exactly the discipline a real analytics team would expect from day one.

---

## Appendix — Numbers Cheat Sheet

**Census:** 50 companies scoped → 40 Q1 candidates, 14 event candidates.

**A2 probe:** CHWY + EBAY → 155 filing-level facts, 60 latest-restated winners, 38 discarded records.

**A3 scan:** 40 candidates → 4,823 core fact versions, 1,046 latest winners, 945 differences, 200 potential H1 transitions scanned, 14/14 events verified (12 qualify).

**Gate 1 (`Gate1-v1.0`, frozen 2026-08-05):** Path A · 21 companies · FY2018–FY2024 · 7/7/7 peer-group split (Marketplace/Platform, Inventory-led, DTC Brand) · H1 Tier B · conflict thresholds 0.5%/5%.

**B1 Pilot:** 6 companies · 570 mapped facts · 225 latest/derived facts · DuPont/Shapley gaps < `1e-10`.

**B2 expansion:** 42 SEC artifacts · 4,780 mapped facts · 1,959 latest/derived facts · 875 conflicts · 262 flags · 0 missing required fields.

**B3 marts:** 137 company-years · 116 transition rows · 21 peer-year summaries · 60-field mart · DuPont gap `2.842e-14` · Shapley gap `5.684e-14`.

**H1 result:** 21 eligible transitions / 10 unique companies · 4 leverage-driven (3 companies) / 17 operating-driven · max company share 14.3% · FY2020–2021 = 47.6% of transitions · leverage transitions concentrated in FY2019/FY2021 · **+35.2pp leverage vs. −11.9pp operating** (does not support H1).

**B4:** 8 filing-reconciliation checks (AMZN, CHWY) · 8 static charts · 2 executed notebooks · 59 automated tests passing.

**B5:** Power BI Executive Overview rebuilt on the formal mart, 6 ground-truth rows reconciled, `.pbix` + screenshot shipped. Q1 Portfolio Release v1.0 published.

**Q2 feasibility (unresolved go/no-go):** 12 of 14 event candidates qualify → Tier A candidate recommendation; formal Gate 2 decision not yet made.
