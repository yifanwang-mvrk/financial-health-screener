# B1 Filing Reconciliation

Revalidated: 2026-08-05

This B1 check compares the scripted latest-valid SEC selection with the existing manually transcribed annual filing values. It does not overwrite either source.

| Ticker | FY | Field | SEC latest | Manual | Status | Accession |
| --- | ---: | --- | ---: | ---: | --- | --- |
| AMZN | 2023 | net_income | 30,425.000 | 30,425.000 | match | 0001018724-26-000004 |
| AMZN | 2023 | revenue | 574,785.000 | 574,785.000 | match | 0001018724-26-000004 |
| AMZN | 2023 | total_assets | 527,854.000 | 527,854.000 | match | 0001018724-26-000004 |
| AMZN | 2023 | total_equity | 201,875.000 | 201,875.000 | match | 0001018724-26-000004 |
| CHWY | 2023 | net_income | 39.600 | 39.580 | match | 0001766502-26-000034 |
| CHWY | 2023 | revenue | 11,147.700 | 11,147.720 | match | 0001766502-26-000034 |
| CHWY | 2023 | total_assets | 3,186.851 | 3,186.851 | match | 0001766502-25-000014 |
| CHWY | 2023 | total_equity | 510.300 | 510.244 | match | 0001766502-26-000034 |

AMZN supplies the clean filing check. CHWY supplies the complex 52/53-week and comparative-restatement check. Review differences remain explicit in `sec_manual_reconciliation.csv`; no processed value is hand-edited.
