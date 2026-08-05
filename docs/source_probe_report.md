# A2 Two-Company SEC Source Probe

Probe date: 2026-08-05

The probe uses Amazon (inventory-led/hybrid) and eBay (marketplace) to test the official SEC companyfacts source, accession-level version retention, annual-duration filtering, source-tag priority, sign handling, and latest-restated selection.

## Probe Results

| Ticker | Normalized facts | Latest canonical facts | Manual matches | Review mappings |
| --- | ---: | ---: | ---: | ---: |
| AMZN | 104 | 39 | 39 | 0 |
| EBAY | 101 | 39 | 39 | 0 |

## Interpretation

- SEC raw JSON is cached without replacing the manually reconciled Pilot mart.
- Comparative annual facts retain accession and filing date, so restatements are visible rather than silently overwritten.
- Differences are routed to `sec_manual_reconciliation.csv`; they are not auto-forced into the Pilot mart.
- The Pilot source cutoff is 2024-04-30, matching the filing vintage used for the FY2021-FY2023 snapshot.

This is reusable A2 probe evidence. A2 is formally closed only after A1 reaches its stopping rules and the probe is revalidated against that candidate pool.
