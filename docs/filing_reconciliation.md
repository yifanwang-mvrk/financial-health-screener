# Manual Filing Reconciliation

Last updated: 2026-08-03

This document records the minimum B4 manual reconciliation for two issuers. Detailed source labels, URLs, issuer-specific definitions, and restatement notes remain in `docs/a2_financial_data/financial_source_mapping.md`.

All monetary values below are USD millions.

## AMZN

Source basis: annual SEC Form 10-K comparative financial statements.

| Fiscal year | Revenue | Net income | Assets | Liabilities | Equity | OCF | CapEx | Project FCF |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2021 | 469,822 | 33,364 | 420,549 | 282,304 | 138,245 | 46,327 | 61,053 | -14,726 |
| 2022 | 513,983 | -2,722 | 462,675 | 316,632 | 146,043 | 46,752 | 63,645 | -16,893 |
| 2023 | 574,785 | 30,425 | 527,854 | 325,979 | 201,875 | 84,946 | 52,729 | 32,217 |

Reconciliation:

- Assets equal liabilities plus equity in each year with zero stored difference.
- Project FCF equals OCF less sign-normalized CapEx in each year with zero stored difference.
- Gross profit is project-derived as total net sales less cost of sales because Amazon does not report a consolidated gross-profit line.
- Project FCF uses gross purchases of property and equipment and can differ from Amazon's issuer-defined non-GAAP FCF.
- Fiscal-year-end shares are not weighted-average EPS shares.

## CHWY

Source basis: Chewy 2024 Form 10-K latest restated comparative series, supplemented by earlier balance-sheet disclosure where required.

| Fiscal year | Period end | Revenue | Net income | Assets | Liabilities | Equity | OCF | CapEx | Project FCF |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2021 | 2022-01-30 | 8,967.407 | -75.207 | 2,086.281 | 2,071.545 | 14.736 | 191.743 | 183.186 | 8.557 |
| 2022 | 2023-01-29 | 10,119.000 | 49.899 | 2,519.818 | 2,359.550 | 160.268 | 349.777 | 230.310 | 119.467 |
| 2023 | 2024-01-28 | 11,147.720 | 39.580 | 3,186.851 | 2,676.607 | 510.244 | 486.211 | 143.282 | 342.929 |

Reconciliation:

- Source values reported in USD thousands are divided by 1,000 for the project unit.
- Floating-point balance-equation and FCF gaps are below `1e-10` after unit conversion.
- The 52/53-week fiscal-year label is stored separately from the actual period-end date.
- Latest restated income-statement and cash-flow values take priority over earlier versions.
- Cash excludes marketable securities, so the cash ratio understates broader liquid assets.
- Long-term debt is recorded as zero only for years where the filing confirms no outstanding ABL borrowing; lease liabilities remain separate.

## Resolution Record

No stored numeric correction was required during this reconciliation. The remaining issues are interpretation and comparability warnings retained in the concept-conflict register and analytical mart.
