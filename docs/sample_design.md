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

A3 has scanned all A1 candidates for FY2018-FY2024 annual coverage, prior balances, tag conflicts, latest-restated feasibility, and override cost. It recommends Path A because 31 companies are coverage-viable and the proposed Marketplace / Inventory-led / DTC groups contain 12 / 7 / 12 viable candidates after merging viable Hybrid issuers into Inventory-led. Gate 1 will now select:

- Path A when coverage is high and mappings are reusable: approximately 18-24 companies, approximately 6-8 per retained group.
- Path B when tags are heterogeneous and manual review cost is high: approximately 12 companies, approximately 4 per retained group.

Data Path and H1 Evidence Tier are separate decisions.

## Event Census

Events are stored separately from companies. `event_date` is the first public availability date of qualifying distress evidence; `event_effective_date` separately records legal or transaction effectiveness.

During A1, `estimated_pre_event_quarters` was only a theoretical listing-to-event upper bound. A3 has now filled `coverage_verified`, real `verified_pre_event_quarters`, and provisional Q2 qualification for every event.

A3 recommends Tier A feasibility from 12 qualified events. This does not authorize Q2; formal Gate 2 remains after B5.
