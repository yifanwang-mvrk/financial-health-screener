# B4 Manual Filing Reconciliation

Analytical data as of: **2026-08-05**

This check compares the scripted latest-valid SEC selection with manually transcribed annual filing values. It does not overwrite either source. Values are USD millions; all selected rows are Form 10-K facts.

| Ticker | FY | Field | SEC latest | Manual | Relative gap | Status | Accession |
| --- | ---: | --- | ---: | ---: | ---: | --- | --- |
| AMZN | 2023 | net_income | 30,425.000 | 30,425.000 | 0.000% | match | `0001018724-26-000004` |
| AMZN | 2023 | revenue | 574,785.000 | 574,785.000 | 0.000% | match | `0001018724-26-000004` |
| AMZN | 2023 | total_assets | 527,854.000 | 527,854.000 | 0.000% | match | `0001018724-26-000004` |
| AMZN | 2023 | total_equity | 201,875.000 | 201,875.000 | 0.000% | match | `0001018724-26-000004` |
| CHWY | 2023 | net_income | 39.600 | 39.580 | 0.051% | match | `0001766502-26-000034` |
| CHWY | 2023 | revenue | 11,147.700 | 11,147.720 | 0.000% | match | `0001766502-26-000034` |
| CHWY | 2023 | total_assets | 3,186.851 | 3,186.851 | 0.000% | match | `0001766502-25-000014` |
| CHWY | 2023 | total_equity | 510.300 | 510.244 | 0.011% | match | `0001766502-26-000034` |

## Review Result

- AMZN is the clean calendar-year control; all four fields match exactly.
- CHWY is the complex 52/53-week and comparative-restatement case. Small rounded differences remain below the frozen 0.5% tolerance.
- Period end, unit conversion, reported sign, accession, filing date, and latest-restated version are retained in `data/processed/b4_filing_reconciliation.csv`.
- No processed value was manually edited during reconciliation.
