# Changelog

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
