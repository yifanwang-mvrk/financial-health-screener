# Changelog

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
