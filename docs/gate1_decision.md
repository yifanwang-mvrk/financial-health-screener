# Gate 1 Decision

Decision date: 2026-08-03

## Decision

Proceed with a complete Q1 B4 Analytical Release on the current verified six-company, FY2021-FY2023 dataset. Preserve the full v3 analytical method, but do not claim that the current repository contains a complete automated SEC XBRL filing-history pipeline.

## Why This Is the Correct Deadline Decision

The current data layer contains:

- 18 manually verified company-year rows.
- Detailed company-specific filing mappings.
- Source URLs and accounting notes.
- Reconciled free cash flow and balance-sheet relationships.
- Six companies spanning two broad operating-model peer groups.

It does not contain:

- FY2020 opening balances needed to calculate average-balance FY2021 DuPont metrics.
- FY2024 outcomes needed to evaluate persistence after FY2023 improvements.
- Filing accession-level version history or a raw SEC JSON fact store.
- Enough independent companies or transitions for Tier A or Tier B H1 evidence.

The v3 framework explicitly permits Tier C and defines B4 as a complete analytical product before Power BI. The correct response is therefore to finish Q1-A, keep H1 rules intact, expose the evidence shortfall, and deliver a Power BI-ready mart.

## Compatibility Path

The current release uses `manual_verified_latest_comparative_filing` as its source-selection method. It relies on the existing company source-mapping document and conflict register. It does not label the dataset point-in-time and does not infer inaccessible filing-version history.

## Frozen Scope for This Release

- Companies: AMZN, BKNG, CHWY, DASH, EBAY, ETSY.
- Years: FY2021-FY2023.
- Research product: Q1-A plus H1 eligibility and Evidence Tier audit.
- B4 deliverables: SQL marts, tests, EDA, notebooks, static charts, analysis report, data dictionary, and README.
- B5 preparation: frozen `q1_powerbi_mart` plus an Executive Overview specification.

## Deferred Work

- Expand to FY2018-FY2024 or later.
- Add more companies according to the original sample design.
- Re-evaluate H1 after sufficient next-year outcomes exist.
- Validate Q2/Q3 distress-event work under their own gates.

Deferred items are not represented as completed in this release.

## Post-Freeze Evidence Closure

Completed on 2026-08-05 without changing the frozen Q1 analytical mart:

- Added the company and event census required by A1.
- Cached official SEC companyfacts and submissions JSON for the six release companies.
- Added accession-level normalized annual facts, deterministic cutoff-based latest-restated selection, and automatic conflict logging.
- Reconciled selected SEC facts to the manually verified Q1 release; mapping differences remain explicit review items.
- Completed A3 coverage reporting and retained H1 Evidence Tier C.

The frozen six-company/FY2021-FY2023 analytical conclusions remain unchanged.
