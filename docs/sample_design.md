# Sample Design

Last updated: 2026-08-05

## A1 Census Boundary

A1 Unified Company & Event Census is complete. The provisional annual window is FY2018-FY2024 and is not frozen until Gate 1.

Company eligibility starts with US-listed or historically US-listed businesses where online transactions, platform commissions, or DTC commerce are a core business engine. Each company must retain an explicit online-core judgment, inventory-risk judgment, revenue-recognition model, peer or boundary classification, confidence, status, and inclusion/exclusion rationale.

The A1 stopping ranges are:

- Approximately 30-40 Q1 candidates, after the operating-model, boundary, delisted, and distress structures are adequately represented.
- Approximately 10-15 event candidates, without deep SEC or quarterly verification at A1.

The current tables contain 40 Q1 candidates and 14 event candidates, so both A1 stopping ranges are satisfied.

## Six-Company Pilot Snapshot

The existing analytical work contains six Pilot companies with three manually verified fiscal years each:

| Pilot analysis peer group | Companies |
| --- | --- |
| Inventory-led E-commerce | AMZN, CHWY |
| Marketplace / Platform | BKNG, DASH, EBAY, ETSY |

The Pilot is retained to test the common data path, accounting identities, Shapley method, quality flags, and Power BI interaction. It is not the formal Q1 sample and does not freeze the peer-group design.

## Formal Sample Selection

A3 must first scan all A1 candidates for FY2018-FY2024 annual coverage, prior balances, tag conflicts, latest-restated feasibility, and override cost. Gate 1 will then select:

- Path A when coverage is high and mappings are reusable: approximately 18-24 companies, approximately 6-8 per retained group.
- Path B when tags are heterogeneous and manual review cost is high: approximately 12 companies, approximately 4 per retained group.

Data Path and H1 Evidence Tier are separate decisions.

## Event Census

Events are stored separately from companies. `event_date` is the first public availability date of qualifying distress evidence; `event_effective_date` separately records legal or transaction effectiveness.

During A1, `estimated_pre_event_quarters` is only a theoretical listing-to-event upper bound. `coverage_verified` remains false, `verified_pre_event_quarters` remains blank, and Q2 qualification remains provisional until A3.

No Gate 2 tier can be inferred from the 14 A1 event candidates until A3 verifies their real quarterly and point-in-time coverage.
