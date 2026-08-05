# Changelog

## 2026-08-05 - Complete B4 Analytical Release

- Froze the formal analytical inputs with SHA-256 hashes and recorded an analytical data-as-of date of 2026-08-05.
- Generated formal coverage, missingness, conflict, latest-selection, metric-flag, H1 exclusion, company concentration, peer distribution, fiscal-year distribution, peer metric, case, and research-finding outputs.
- Produced and visually reviewed eight static charts covering formal coverage, peer DuPont distributions, similar-ROE/different-driver cases, H1 exclusions, Tier B outcomes, quality warnings, year imbalance, and denominator instability.
- Executed and saved the formal data-quality and Q1 analysis notebooks with embedded outputs.
- Completed eight AMZN/CHWY filing reconciliation checks across Revenue, Net Income, Assets, and Equity; all match within tolerance and no processed value was manually edited.
- Documented that the Tier B pattern does not support H1: leverage-driven median next-year peer-relative change is +35.2 percentage points versus -11.9 points for operating-driven improvements, with material sample and year limitations.
- Completed the CV bullet, 30-second introduction, five-minute narrative, formal README, limitations, and release audit. B4 is now the CV-ready minimum deliverable; B5 is next.

## 2026-08-05 - Build Q1 Analytical SQL Marts

- Replaced the legacy six-company/manual-wide-table SQL with the formal 21-company B2 fact layer and `company_id`-based joins and windows.
- Rebuilt all seven mandatory marts in the frozen `01` through `07` order, producing 137 formal company-years, 116 candidate transition rows, and 21 peer-year summaries.
- Implemented latest-valid restated selection, consecutive-year average balances, valid-observation peer medians/quartiles/sample sizes, exact three-factor Shapley attribution, and LEAD-based persistence outcomes.
- Reproduced the Gate 1 H1 Tier B audit exactly: 21 eligible transitions across 10 companies, including four leverage-driven and 17 operating-driven transitions.
- Added company and fiscal-year concentration fields, enforced the frozen 20% Tier A company threshold, and retained peer-relative change as the primary persistence outcome.
- Matched the Power BI mart to all 60 Gate1-v1.0 fields with no DAX-owned research logic and exported a field-level schema dictionary with grain and descriptions.
- Reconciled maximum absolute DuPont and Shapley gaps to `2.842e-14` and `5.684e-14`; B4 is the next mandatory stage.

## 2026-08-05 - Expand Q1 Pipeline to Frozen Sample

- Applied the unchanged Gate1-v1.0 field, source, version, sign, duration, peer-group, and year rules to all 21 formal companies, with FY2017 retained only for opening balances.
- Rebuilt 42 checksummed SEC artifacts into 5,439 normalized pre-map records, 4,780 mapped filing-level facts, and 1,959 latest/derived canonical facts.
- Recorded 212 rejected candidates, 875 explicit winner/discarded conflicts, and 262 metric-quality flags; no source conflict is unresolved.
- Closed all required company-year coverage gaps without sentinels. The formal failure list is empty and the three frozen peer groups each contain seven companies.
- Added accession-backed observed exceptions for ABNB free cash flow table values, CVNA operating-income derivations, and DASH/ETSY CapEx aggregations without changing the shared mapping rules.
- Preserved the Gate 1 sample and field-contract hashes, added reproducible B2 stage auditing and tests, and marked B3 formal analytical marts as the next mandatory stage.

## 2026-08-05 - Build Reproducible Q1 Pilot Pipeline

- Revalidated AMZN, BKNG, CHWY, DASH, EBAY, and ETSY as the six-company B1 Pilot after Gate 1; all six remain members of the formal sample but do not define it.
- Implemented the required Extract -> Normalize -> Map & Sign -> Conflicts -> Latest-restated -> Validate -> DuckDB -> Pilot marts sequence behind one entry.
- Rebuilt 12 cached SEC artifacts into 570 mapped filing-level facts, 225 latest/derived facts, 76 explicit conflict records, 39 metric flags, and 18 Pilot company-year mart rows.
- Added filing-backed CapEx aggregation overrides for DASH and ETSY after reconciliation proved that the shared single-tag rule omitted capitalized software cash outflows.
- Reduced manual reconciliation reviews to one explicit CHWY comparative-equity restatement; no processed value is manually overwritten.
- Added dedicated extraction, candidate-rejection, and validation error logs; extraction and validation logs are clear and no source conflict remains unresolved.
- Reconciled DuPont and exact Shapley identities below `1e-10`, generated the Pilot H1 audit, and retained the formal H1 Tier B conclusion as independent Gate 1 evidence.
- Marked B1 Done and B2 as the next mandatory stage. No formal sample expansion, Power BI release, or Q2 technology was performed in B1.

## 2026-08-05 - Freeze Gate 1 Scope and Evidence Tiers

Decision version: Gate1-v1.0

Owner: Yifan Wang

Freeze date: 2026-08-05

| Decision differing from or resolving a v3.0 provisional value | Frozen result | Evidence and data summary |
| --- | --- | --- |
| Data Path | Path A | A3 found 31 viable candidates; post-merge pools are 12 Marketplace / 7 Inventory-led / 12 DTC. |
| Formal sample | 21 companies; FY2018-FY2024 unbalanced panel | Seven companies per retained group; all 40 candidate decisions are versioned. |
| Peer groups | Retain Marketplace, Inventory-led, DTC; cancel standalone Hybrid | AMZN and BYON are viable and merge into Inventory-led; GROV remains a short-history boundary exclusion. |
| Six-company scope | Retain only as B1 Pilot membership | All six remain in the formal 21-company sample, but the Pilot does not define formal sample size or period. |
| H1 Tier | Tier B; descriptive patterns only | Formal sample has 21 eligible transitions across 10 companies; leverage group has 4 transitions across 3 companies. |
| H1 outcomes and drivers | Peer-relative next-year change; exact Shapley; label plus continuous share | A3 eligibility and contribution reconciliation were retained without relaxation. |
| Canonical fields | 13 extracted fields plus derived FCF; 3 noncore fields excluded from the formal analytical layer | A2/A3 coverage supports the DuPont core and directly used quality fields; prior rows remain for history. |
| Source and version policy | SEC Companyfacts canonical; filing-level documented fallback; latest valid restated version | A2 produced 60 winners and 38 discarded records; A3 produced 1,046 winners and 945 differences. |
| Conflict thresholds | Low <=0.5%; medium >0.5%-5%; high >5% | A2/A3 exploratory distribution is now frozen with mandatory reconciliation for high conflicts. |
| Physical schemas and Power BI contract | Frozen in Gate 1 decision and versioned mart field contract | Research logic remains in SQL/DuckDB; DAX is display-only. |
| Q2 feasibility | Tier A candidate only; formal authorization pending Gate 2 after B5 | A3 verified 12 of 14 event candidates; no quarterly signal panel was built. |
| Limitations | Frozen descriptive, concentration, year-effect, unbalanced-panel, and non-PIT wording | Formal H1 has 47.6% of transitions in FY2020-FY2021 and 75% of leverage transitions in FY2019. |

Gate 1 is passed. New Q1 ideas now go to backlog. The mandatory next stage is B1 revalidation, not B2, Power BI, or Q2.

## 2026-08-05 - Complete A3 Coverage and H1 Sample Audit

- Cached complete Companyfacts and submissions JSON for all 40 Q1 candidates with an 80-row checksum manifest and zero extraction errors.
- Scanned FY2018-FY2024 core annual coverage using 4,823 filing-level versions, 1,046 latest-restated winners, and 945 explicit winner/discarded differences.
- Audited 200 potential H1 transitions without relaxing eligibility; 22 transitions across 11 companies support a Tier B recommendation, with a material driver/year imbalance.
- Verified all 14 event candidates; 12 satisfy the provisional Tier A metadata criteria, while BOXD and FTCH have specific quarterly/PIT coverage exclusions.
- Recommended Path A after merging viable Hybrid issuers into Inventory-led, producing viable group pools of 12 Marketplace / 7 Inventory-led / 12 DTC.
- Preserved Gate 1 and formal Gate 2 as pending decisions; no Q2 signal panel or current screen was built.

## 2026-08-05 - Complete A2 SEC Source Probe

- Selected CHWY as the Inventory-led probe and EBAY as the Marketplace / Platform probe through one SEC extraction entry.
- Added refresh-safe raw version retention, checksum manifests, and an explicit extraction error log.
- Produced 155 filing-level annual facts, 60 latest-restated winners, 38 traceable discarded-value records, and a 22-row field audit.
- Verified shared tag, unit, duration, sign, filing metadata, and fiscal-year rules; recorded Total Debt as a company-review boundary rather than assuming missing values are zero.
- Rebuilt and executed the A2 notebook, documented incremental review cost, and wrote the full A3 scan requirements. Gate 1 remains pending A3.

## 2026-08-05 - Complete A1 Company and Event Census

- Expanded the light-research universe to 50 companies and 40 Q1 candidates across four provisional peer groups.
- Expanded the sourced event census to 14 candidates while keeping quarterly coverage and Q2 qualification fields provisional for A3.
- Recorded stable issuer IDs, historical CIK fallbacks, listing-date provenance, status changes, and ticker-history notes, including legacy/current BBBY separation.
- Added reproducible A1 census generation, stopping-rule audits, and tests; Gate 1 and Gate 2 remain pending.

## 2026-08-05 - Restore Six-Company Work to B1 Pilot

- Re-read Execution Charter v3.0 and the Phase A/Q1 Master Execution Checklist as the sole execution contract.
- Withdrew the prior formal Gate 1 and Gate 2 labels because A1 stopping rules and A3 all-candidate verification had not been completed.
- Restored AMZN, BKNG, CHWY, DASH, EBAY, and ETSY to a six-company B1 Pilot snapshot.
- Renamed the active inclusion flag to `b1_pilot_included` and separated Pilot coverage outputs from the future A3 report.
- Set the active stage to A1: expand to approximately 30-40 Q1 candidates and 10-15 event candidates before proceeding.
- Preserved the existing SEC cache, analytical marts, notebooks, tests, Power BI prototype, and Git history as Pilot evidence.

## 2026-08-05 - Phase A Evidence and Q1 Portfolio Release v1.0

- Added a 26-company universe and five-event census with explicit scope and Gate 2 fields.
- Cached official SEC companyfacts and submissions JSON for all six Q1 release companies with SHA-256 manifests.
- Added 599 accession-level normalized facts, deterministic latest-restated selection, automatic conflict logging, and SEC-to-manual reconciliation.
- Added A2 source-probe, A3 coverage, Gate 2 No-Go, project-status, and release-closure documentation.
- Loaded Phase A evidence tables into DuckDB and added manual step entry points plus one-command release orchestration.
- Expanded the automated suite from 8 to 16 passing tests.
- Confirmed the existing one-page Power BI Executive Overview as the final display layer; Q2/Q3 risk pages are excluded by Gate 2.

## 2026-08-03 - Q1 B4 Analytical Release

- Restored the original v3 Q1 research scope while retaining the six-company current dataset.
- Added explicit Q1 analytical peer groups, canonical concepts, and a conflict register.
- Added seven ordered SQL modules for core tables, source selection, metrics, Shapley decomposition, persistence, H1 audit, and the Power BI mart.
- Added a Python pipeline that rebuilds DuckDB and exports ten analytical tables.
- Added exact average-balance DuPont metrics and three-factor Shapley attribution.
- Added H1 eligibility, exclusion waterfall, concentration checks, and Evidence Tier logic.
- Added denominator, one-off, structural-break, liquidity-scope, restatement, and missingness warnings.
- Added seven automated accounting and research-logic tests.
- Added EDA summaries, six static charts, and three executed notebooks.
- Added research design, gate decision, data dictionary, manual reconciliation, limitations, risk register, analysis report, and Power BI specification.
- Replaced the short in-progress README with a recruiter-ready analytical release README.

## Legacy MVP

The earlier simple financial-ratio risk score and ranking remain in the repository as learning artifacts. They are not used by the Q1 v3 analytical release.
