# Limitations and Evidence Boundary

Last updated: 2026-08-03

## Sample and Time Coverage

- The current sample contains six companies and 18 company-years.
- The two analytical peer groups contain only two and four companies.
- Fiscal years 2021-2023 do not represent a full business cycle.
- FY2021 lacks FY2020 opening balances, so its average-balance DuPont metrics are unavailable.
- FY2023 lacks FY2024 outcomes, preventing a one-year persistence test for 2023 improvements.

The results are company-specific and descriptive. They are not estimates of the e-commerce industry.

## Source Architecture

- The release uses manually verified wide financial facts and company-specific source mappings.
- It does not include a complete raw SEC JSON fact store or filing accession history.
- `latest_restated` indicates the manually selected latest comparative series, not point-in-time information available to investors on the original fiscal-year end.
- CHWY comparative values incorporate the documented latest restated series.

## Accounting Comparability

- Revenue represents different economics across first-party retailers and platforms.
- Gross profit is unavailable for BKNG and currently missing from the raw DASH rows.
- Inventory blanks for platform companies do not mean zero.
- Cash and equivalents exclude material marketable securities for some issuers.
- Lease liabilities are not automatically classified as long-term debt.
- EBAY net income includes non-operating and one-off effects.
- DASH's Wolt acquisition creates a structural break.
- BKNG and ETSY have thin or negative equity periods that destabilize or invalidate ROE.
- Fiscal calendars differ, especially CHWY's 52/53-week year.

## Metric Interpretation

- A mathematically valid ratio can still be economically unstable when its denominator is close to zero.
- ROE is null when average equity is nonpositive, but a separate near-zero-equity flag is needed before the denominator becomes negative.
- Peer medians can move materially when only a few valid companies are available.
- Shapley decomposition explains arithmetic attribution, not causality.

## H1 Boundary

The current release is Evidence Tier C with zero eligible transitions. It reports no group test, p-value, bootstrap interval, or validated persistence claim. Illustrative driver cases do not support H1.

## Product Boundary

- No investment recommendation.
- No bankruptcy prediction claim.
- No black-box financial health score.
- No inference that a quality warning implies imminent distress.
- Power BI is a presentation layer for SQL outputs, not an independent research engine.
