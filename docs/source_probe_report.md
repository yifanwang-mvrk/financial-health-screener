# A2 Two-Company SEC Source Probe

Probe date: 2026-08-05

Status: **Done**

## Probe Selection

| Company | Role | Selection reason |
| --- | --- | --- |
| CHWY | Inventory-led E-commerce | Inventory-owning retailer with a 52/53-week fiscal year, comparative restatements, and a distinct asset structure |
| EBAY | Marketplace / Platform | Asset-light marketplace with net revenue recognition, multiple annual filing versions, and a debt-bearing balance sheet |

No third distress company is added. The two probes establish the annual extraction and metadata rules needed for A3; quarterly distress feasibility must be measured across all A1 events in A3 rather than inferred from one extra case.

## Field-Level Results

| Company | Canonical field | Main observed tag | Unit | Duration | Versions | Shared rule | Override status |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| CHWY | revenue | RevenueFromContractWithCustomerExcludingAssessedTax | USD | 363 | 3 | shared_direct | none_observed_in_probe |
| CHWY | net_income | NetIncomeLoss | USD | 363 | 3 | shared_direct | none_observed_in_probe |
| CHWY | total_assets | Assets | USD | Instant | 2 | shared_direct | none_observed_in_probe |
| CHWY | total_equity | StockholdersEquity | USD | Instant | 4 | shared_direct | none_observed_in_probe |
| CHWY | cash_and_equivalents | CashAndCashEquivalentsAtCarryingValue | USD | Instant | 2 | shared_direct | none_observed_in_probe |
| CHWY | inventory | InventoryNet | USD | Instant | 2 | conditional_not_applicable | none_observed_in_probe |
| CHWY | current_assets | AssetsCurrent | USD | Instant | 2 | shared_direct | none_observed_in_probe |
| CHWY | current_liabilities | LiabilitiesCurrent | USD | Instant | 2 | shared_direct | none_observed_in_probe |
| CHWY | total_debt | Not reported | Not reported | Instant | 0 | company_review_required | filing_verification_or_documented_aggregation |
| CHWY | operating_cash_flow | NetCashProvidedByUsedInOperatingActivities | USD | 363 | 3 | shared_direct | none_observed_in_probe |
| CHWY | capital_expenditure | PaymentsToAcquireProductiveAssets | USD | 363 | 3 | shared_direct | none_observed_in_probe |
| EBAY | revenue | RevenueFromContractWithCustomerExcludingAssessedTax | USD | 364 | 3 | shared_direct | none_observed_in_probe |
| EBAY | net_income | NetIncomeLoss | USD | 364 | 3 | shared_direct | none_observed_in_probe |
| EBAY | total_assets | Assets | USD | Instant | 2 | shared_direct | none_observed_in_probe |
| EBAY | total_equity | StockholdersEquity | USD | Instant | 3 | shared_direct | none_observed_in_probe |
| EBAY | cash_and_equivalents | CashAndCashEquivalentsAtCarryingValue | USD | Instant | 3 | shared_direct | none_observed_in_probe |
| EBAY | inventory | Not reported | Not reported | Instant | 0 | conditional_not_applicable | not_applicable_marketplace |
| EBAY | current_assets | AssetsCurrent | USD | Instant | 2 | shared_direct | none_observed_in_probe |
| EBAY | current_liabilities | LiabilitiesCurrent | USD | Instant | 2 | shared_direct | none_observed_in_probe |
| EBAY | total_debt | DebtAndCapitalLeaseObligations|DebtLongtermAndShorttermCombinedAmount|LongTermDebtAndCapitalLeaseObligations | USD | Instant | 4 | company_review_required | none_observed_in_probe |
| EBAY | operating_cash_flow | NetCashProvidedByUsedInOperatingActivities | USD | 364 | 3 | shared_direct | none_observed_in_probe |
| EBAY | capital_expenditure | PaymentsToAcquirePropertyPlantAndEquipment | USD | 364 | 3 | shared_direct | none_observed_in_probe |

## Mapping and Version Conclusions

- The same executable concept map covers Revenue, Net Income, Assets, Equity, Cash, Current Assets, Current Liabilities, OCF, and CapEx for both companies.
- Inventory is valid for CHWY and not applicable to EBAY's marketplace presentation; blank is not converted to zero.
- A direct Total Debt tag is available for EBAY. CHWY has no direct debt balance in Companyfacts, so zero debt requires filing verification or a documented override rather than an automated assumption.
- CHWY CapEx uses `PaymentsToAcquireProductiveAssets`; EBAY uses `PaymentsToAcquirePropertyPlantAndEquipment`. Ordered tag alternatives therefore remain necessary.
- All normalized flow facts satisfy the 330-385 day annual rule. CHWY's 363-day fiscal periods demonstrate why calendar-year assumptions are unsafe.
- Raw `fy` values describe the filing context and can differ from the comparative period's project fiscal year. Period end plus the issuer fiscal calendar is the reliable year key; `fp=FY`, filing date, and accession remain available.
- 60 latest-restated winners are unique by company-period-field. Unit and duration validation occurs before filing-date ordering; 38 discarded value records remain traceable across: capital_expenditure, cash_and_equivalents, current_assets, current_liabilities, inventory, net_income, operating_cash_flow, revenue, total_assets, total_debt, total_equity.
- Conflict severity in A2 is exploratory. The final materiality threshold is not frozen until Gate 1.

## Sign and Unit Rules

- USD facts are standardized to USD millions; expected raw units remain recorded.
- CapEx is stored as a positive cash outflow amount through an absolute-value sign rule.
- OCF preserves its reported positive or negative direction.
- Inventory and debt are nonnegative domains; missing values are not treated as zero without filing evidence.

## Incremental Cost Estimate

- Automated cost per additional company: two SEC requests on first load, then seconds for cached normalization and field diagnostics once CIK and fiscal calendar are known.
- Manual review for a clean calendar-year issuer: approximately 20-30 minutes for field coverage, winner checks, and filing reconciliation.
- Manual review for a 52/53-week, restated, missing-tag, or aggregation case: approximately 30-60 minutes, with the exact time to be measured in A3.

## Canonical Source Decision

SEC Companyfacts is suitable as the proposed Q1 canonical source for A3 scanning, provided the pipeline retains complete raw JSON, filing-level versions, expected-unit and flow-duration validation, explicit conflicts, and documented company exceptions. This is an A2 feasibility conclusion, not the Gate 1 source freeze.

## Required A3 Scan

A3 must collect FY2018-FY2024 core-field coverage, prior balances, version counts, unit/duration validity, tag conflicts, latest-restated selectability, override need, manual review cost, complete H1 transition eligibility, and every event's real quarterly/PIT feasibility fields. The executable metric list is stored in `data/reference/a3_scan_requirements.csv`.

## DoD

- Two companies use one extraction entry: `src/extract_sec.py` (155 filing-level annual facts in the formal sample).
- Complete Companyfacts and submissions JSON are checksum-manifested under stable CIK paths.
- The minimum concept map, sign rules, latest-restated selection, conflict sample, report, and notebook are executable.
- A3 scan requirements are explicit; full-sample ETL and formal sample selection have not been performed in A2.
