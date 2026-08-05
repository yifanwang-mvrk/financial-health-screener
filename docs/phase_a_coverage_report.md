# Phase A Coverage Verification

Generated: 2026-08-05

The strict evidence layer caches official SEC JSON for the six frozen Q1 companies, retains accession-level annual facts, and compares latest-restated canonical selections with the manually reconciled release table.

| Ticker | Complete required fields | Required fields | Review mappings |
| --- | ---: | ---: | ---: |
| AMZN | 8 | 8 | 0 |
| BKNG | 8 | 8 | 0 |
| CHWY | 8 | 8 | 1 |
| DASH | 8 | 8 | 3 |
| EBAY | 8 | 8 | 0 |
| ETSY | 8 | 8 | 3 |

## Decision Use

- Missing or mismatched SEC facts do not overwrite manually reconciled analytical values.
- Mapping reviews are explicit evidence tasks, not silent pipeline failures.
- H1 remains Tier C because the annual window still has no eligible forward transitions.
