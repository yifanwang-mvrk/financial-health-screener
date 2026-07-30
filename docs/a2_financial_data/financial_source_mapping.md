# Financial Source Mapping


## 1. Purpose

This document defines the source, accounting interpretation, and collection rules
for financial statement data used in the Financial Health Screener project.

The purpose is to ensure that collected financial data is:

- traceable
- comparable across companies
- consistent with accounting definitions
- suitable for downstream analysis


---

# 2. Source Hierarchy


Financial data sources should follow this priority order:


## Level 1 — Official Company Filings

Preferred sources:

- Annual reports
- Form 10-K filings
- Official investor relations financial statements


Reason:

Official filings provide the highest accounting reliability and contain
company-specific definitions.


---

## Level 2 — Regulatory Filing Databases

Examples:

- SEC filings
- Official exchange filing systems


Used when official company websites are difficult to access.


---

## Level 3 — Financial Data Platforms

Examples:

- Financial databases
- Market data providers


These sources may be used for cross-checking but should not replace
official accounting sources without verification.


---

# 3. Data Collection Principles


## 3.1 Accounting Label Verification

Numbers should not be collected only based on display names.

The project must verify:

- original accounting label
- statement location
- accounting meaning


Example:


Website label:

Revenue


Possible filing labels:

- Revenue
- Net sales
- Total revenue
- Net revenues


The selected field should be documented.


---

## 3.2 Period Verification

Each financial value must confirm:


- fiscal year
- fiscal year end date
- annual or quarterly period
- whether values are restated


Example:


Company fiscal year:

2023


Period end date:

2023-12-31


Data type:

Annual


---

## 3.3 Currency Verification


Each value must record:

- reporting currency
- whether conversion is required


Example:


Currency:

USD


---

# 4. Company-Level Financial Source Mapping


This section records company-specific financial data decisions.


---

# AMZN — Amazon.com Inc

## Basic Information

| Field | Value |
|---|---|
| Ticker | AMZN |
| Company | Amazon.com Inc |
| Primary source type | SEC Form 10-K |
| Income statement and cash-flow source | Amazon 2023 Form 10-K comparative financial statements |
| 2022–2023 balance-sheet source | Amazon 2023 Form 10-K |
| 2021 balance-sheet source | Amazon 2022 Form 10-K comparative balance sheet |
| Fiscal years covered | 2021–2023 |
| Fiscal year end | December 31 |
| Currency | USD |
| Reporting unit | USD millions |

---

## Accounting Mapping

### 1. Income Statement Mapping

| Standard Field | Source Label or Derivation | Treatment | Notes |
|---|---|---|---|
| revenue | Total net sales | Directly reported | Consists of net product sales and net service sales |
| gross_profit | Total net sales - Cost of sales | Project-derived | Amazon does not separately report consolidated gross profit; calculated using the project definition |
| operating_income | Operating income | Directly reported | Consolidated operating income |
| net_income | Net income | Directly reported | Consolidated net income |

---

### 2. Balance Sheet Mapping

| Standard Field | Source Label or Derivation | Treatment | Notes |
|---|---|---|---|
| total_assets | Total assets | Directly reported | Fiscal-year-end balance |
| total_liabilities | Total assets - Total stockholders' equity | Project-derived | Total liabilities are not separately shown as one balance-sheet line; derived and reconciled to reported liability components |
| total_equity | Total stockholders' equity | Directly reported | Fiscal-year-end stockholders' equity |
| current_assets | Total current assets | Directly reported | Fiscal-year-end balance |
| current_liabilities | Total current liabilities | Directly reported | Fiscal-year-end balance |
| cash_and_equivalents | Cash and cash equivalents | Directly reported | Excludes marketable securities |
| inventory | Inventories | Directly reported | Fiscal-year-end inventory balance |
| long_term_debt | Long-term debt | Directly reported | Excludes long-term lease liabilities unless separately added in a later metric definition |
| shares_outstanding | Common stock line-item parenthetical: shares outstanding | Directly disclosed | Fiscal-year-end shares outstanding in millions; not weighted-average shares used for EPS |

---

### 3. Cash Flow Mapping

| Standard Field | Source Label or Derivation | Treatment | Notes |
|---|---|---|---|
| operating_cash_flow | Net cash provided by (used in) operating activities | Directly reported | Annual consolidated operating cash flow |
| capital_expenditure | Purchases of property and equipment | Sign-normalized direct value | Reported as a negative cash outflow; stored as a positive amount in the project |
| free_cash_flow | operating_cash_flow - capital_expenditure | Project-derived | Uses gross purchases of property and equipment and therefore differs from Amazon's issuer-defined non-GAAP free cash flow |

---

## Data Collection Notes

### Business Model Considerations

Amazon is a diversified hybrid business combining:

- First-party retail
- Third-party marketplace services
- AWS
- Advertising
- Subscription services
- Logistics and fulfillment activities

The consolidated financial statements represent the entire Amazon group rather
than a pure e-commerce retail business.

### Accounting Risks

- Gross profit is project-derived because Amazon does not separately report a
  consolidated gross-profit line.
- Total liabilities are project-derived as total assets minus total
  stockholders' equity.
- Capital expenditure is stored as a positive cash-outflow amount even though
  it appears as a negative value in the cash-flow statement.
- Project free cash flow uses gross purchases of property and equipment.
- Amazon's own non-GAAP free-cash-flow definition uses purchases of property
  and equipment net of proceeds from sales and incentives, so the two FCF
  values should not be treated as identical.
- Fiscal-year-end shares outstanding are used rather than weighted-average
  shares used in earnings-per-share calculations.

### Comparability Issues

- Amazon's diversified revenue mix reduces direct comparability with
  asset-light marketplace companies.
- Amazon owns inventory and operates substantial physical infrastructure,
  unlike companies such as eBay and Etsy.
- Gross margin, asset intensity, capital expenditure, and inventory metrics
  should therefore be interpreted within the relevant business-model context.

### Directly Reported Fields

- revenue
- operating_income
- net_income
- total_assets
- total_equity
- current_assets
- current_liabilities
- cash_and_equivalents
- inventory
- long_term_debt
- operating_cash_flow
- capital_expenditure
- shares_outstanding

### Project-Derived Fields

- gross_profit
- total_liabilities
- free_cash_flow


# EBAY — eBay Inc.

## Basic Information

| Field | Value |
|---|---|
| Ticker | EBAY |
| Company | eBay Inc. |
| Primary source type | SEC Form 10-K |
| Income statement and cash-flow source | eBay 2023 Form 10-K comparative financial statements |
| 2022–2023 balance-sheet source | eBay 2023 Form 10-K |
| 2021 balance-sheet source | eBay 2022 Form 10-K comparative balance sheet |
| Fiscal years covered | 2021–2023 |
| Fiscal year end | December 31 |
| Currency | USD |
| Reporting unit | USD millions |
| 2023 Form 10-K URL | https://www.sec.gov/Archives/edgar/data/1065088/000106508824000036/ebay-20231231.htm |
| 2022 Form 10-K URL | https://www.sec.gov/Archives/edgar/data/1065088/000106508823000006/ebay-20221231.htm |

---

## Accounting Mapping

### 1. Income Statement Mapping

| Standard Field | Source Label or Derivation | Treatment | Notes |
|---|---|---|---|
| revenue | Net revenues | Directly reported | Consolidated marketplace revenue |
| gross_profit | Gross profit | Directly reported | Net revenues minus cost of net revenues |
| operating_income | Income from operations | Directly reported | Consolidated operating profit |
| net_income | Net income (loss) | Directly reported | Consolidated figure including continuing and discontinued operations |

---

### 2. Balance Sheet Mapping

| Standard Field | Source Label or Derivation | Treatment | Notes |
|---|---|---|---|
| total_assets | Total assets | Directly reported | Fiscal-year-end balance |
| total_liabilities | Total liabilities | Directly reported | Fiscal-year-end balance |
| total_equity | Total stockholders' equity | Directly reported | Fiscal-year-end stockholders' equity |
| current_assets | Total current assets | Directly reported | Fiscal-year-end balance |
| current_liabilities | Total current liabilities | Directly reported | Fiscal-year-end balance |
| cash_and_equivalents | Cash and cash equivalents | Directly reported | Excludes short-term and long-term investments |
| inventory | Not separately reported | Left blank | eBay's consolidated balance sheet does not contain a separate inventory line; blank does not mean zero |
| long_term_debt | Long-term debt | Directly reported | Excludes short-term debt and the current portion of long-term debt |
| shares_outstanding | Common stock — shares outstanding, balance at end of year | Directly disclosed | Fiscal-year-end shares outstanding in millions; not weighted-average EPS shares |

---

### 3. Cash Flow Mapping

| Standard Field | Source Label or Derivation | Treatment | Notes |
|---|---|---|---|
| operating_cash_flow | Net cash provided by operating activities | Directly reported | Consolidated figure including continuing and discontinued operating activities |
| capital_expenditure | Purchases of property and equipment | Sign-normalized direct value | Reported as a negative cash outflow; stored as a positive amount in the project |
| free_cash_flow | operating_cash_flow - capital_expenditure | Project-derived | Uses the project's consistent FCF definition |

---

## Data Collection Notes

### Business Model Considerations

eBay primarily operates an asset-light online marketplace.

The company generally facilitates transactions between buyers and sellers
rather than purchasing and reselling merchandise as a first-party retailer.

Its revenue primarily reflects marketplace monetization rather than the gross
value of merchandise sold through the platform.

### Accounting Risks

- Inventory is not separately reported and is left blank rather than recorded
  as zero.
- Net income includes both continuing and discontinued operations.
- Operating cash flow also includes discontinued operating activities.
- The 2021 net-income figure is heavily affected by income from discontinued
  operations associated with disposed businesses.
- The 2022 net loss is materially affected by fair-value losses on equity
  investments and warrants.
- Capital expenditure appears as a negative cash-flow-statement value but is
  stored as a positive cash-outflow amount in the project.
- Fiscal-year-end shares outstanding are used rather than weighted-average
  shares used in earnings-per-share calculations.

### Comparability Issues

- eBay's asset-light marketplace model differs materially from first-party
  retailers that recognize the full selling price of merchandise as revenue.
- Its gross margin is therefore not directly comparable with inventory-owning
  retailers such as Amazon's first-party retail operations or Chewy.
- Inventory-based indicators are not applicable because inventory is not
  separately reported.
- Consolidated net income can be highly volatile because of discontinued
  operations and investment remeasurement gains or losses.
- Operating income and operating cash flow may provide a clearer view of core
  operating performance than consolidated net income in affected years.

### Directly Reported Fields

- revenue
- gross_profit
- operating_income
- net_income
- total_assets
- total_liabilities
- total_equity
- current_assets
- current_liabilities
- cash_and_equivalents
- long_term_debt
- operating_cash_flow
- capital_expenditure
- shares_outstanding

### Fields Not Separately Reported

- inventory

### Project-Derived Fields

- free_cash_flow


# ETSY — Etsy, Inc.

## Basic Information

| Field | Value |
|---|---|
| Ticker | ETSY |
| Company | Etsy, Inc. |
| Primary source type | SEC Form 10-K |
| Income statement and cash-flow source | Etsy 2023 Form 10-K comparative financial statements |
| 2022–2023 balance-sheet source | Etsy 2023 Form 10-K |
| 2021 balance-sheet source | Etsy 2022 Form 10-K comparative balance sheet |
| Fiscal years covered | 2021–2023 |
| Fiscal year end | December 31 |
| Currency | USD |
| Source reporting unit | USD thousands |
| Project reporting unit | USD millions |
| 2023 Form 10-K URL | https://www.sec.gov/Archives/edgar/data/1370637/000137063724000013/etsy-20231231.htm |
| 2022 Form 10-K URL | https://www.sec.gov/Archives/edgar/data/1370637/000137063723000017/etsy-20221231.htm |

---

## Accounting Mapping

### 1. Income Statement Mapping

| Standard Field | Source Label or Derivation | Treatment | Notes |
|---|---|---|---|
| revenue | Total revenue | Directly reported | Includes marketplace revenue and services revenue |
| gross_profit | Gross profit | Directly reported | Total revenue minus cost of revenue |
| operating_income | Income (loss) from operations | Directly reported | May be positive or negative |
| net_income | Net income (loss) | Directly reported | Consolidated net income or loss |

---

### 2. Balance Sheet Mapping

| Standard Field | Source Label or Derivation | Treatment | Notes |
|---|---|---|---|
| total_assets | Total assets | Directly reported | Fiscal-year-end balance |
| total_liabilities | Total liabilities | Directly reported | Fiscal-year-end balance |
| total_equity | Total stockholders' deficit / Total stockholders' (deficit) equity | Directly reported | Source wording varies by filing and year; values are negative in 2022 and 2023 |
| current_assets | Total current assets | Directly reported | Fiscal-year-end balance |
| current_liabilities | Total current liabilities | Directly reported | Fiscal-year-end balance |
| cash_and_equivalents | Cash and cash equivalents | Directly reported | Excludes restricted cash and short- and long-term investments |
| inventory | Not separately reported | Left blank | Blank does not mean zero; inventory is not presented as a separate consolidated balance-sheet line |
| long_term_debt | Long-term debt, net | Directly reported | Net carrying amount of long-term debt |
| shares_outstanding | Common stock line-item parenthetical: shares issued and outstanding | Directly disclosed | Fiscal-year-end shares outstanding in millions; not weighted-average EPS shares |

---

### 3. Cash Flow Mapping

| Standard Field | Source Label or Derivation | Treatment | Notes |
|---|---|---|---|
| operating_cash_flow | Net cash provided by operating activities | Directly reported | Annual consolidated operating cash flow |
| capital_expenditure | Purchases of property and equipment + Development of internal-use software | Project-derived aggregation with sign normalization | Both source values are negative cash outflows; summed and stored as one positive project CapEx amount |
| free_cash_flow | operating_cash_flow - capital_expenditure | Project-derived | Uses the project's standardized FCF definition |

---

## Data Collection Notes

### Business Model Considerations

Etsy operates asset-light online marketplaces and generates revenue primarily
from:

- Marketplace fees
- Transaction and payment-processing activities
- Advertising and other seller services
- Revenue associated with its portfolio of marketplace brands

The value of merchandise sold through the platforms is not recorded as Etsy's
revenue. Revenue represents the fees and services earned from marketplace
activity.

### Accounting Risks

- The source financial statements are reported in USD thousands, while the
  project stores monetary values in USD millions. Source values are divided by
  1,000 before entry.
- Inventory is not separately reported and is left blank rather than recorded
  as zero.
- Capital expenditure is not taken from one single reported line. The project
  combines purchases of property and equipment with development of
  internal-use software.
- Both CapEx components appear as negative investing cash flows but are stored
  as one positive cash-outflow amount in the project.
- Cash and cash equivalents exclude restricted cash and short- and long-term
  investments.
- Fiscal-year-end shares outstanding are used rather than weighted-average
  shares used for earnings-per-share calculations.
- The source label for total equity changes depending on whether the company
  reports positive equity or a stockholders' deficit.

### Material Events Affecting Interpretation

- Etsy reported asset impairment charges of approximately USD 1,045.0 million
  in 2022, which materially contributed to its operating loss and net loss.
- Etsy also reported asset impairment charges in 2023, but at a substantially
  lower level than in 2022.
- Total stockholders' equity became negative in 2022 and remained negative in
  2023.
- Metrics such as debt-to-equity and return on equity therefore require an
  applicability warning and should not be interpreted normally for those
  years.

### Comparability Issues

- Etsy's marketplace revenue represents fees and services rather than the
  gross value of merchandise sold on its platforms.
- Its gross margin is therefore not directly comparable with first-party
  retailers that recognize the full merchandise selling price as revenue.
- Inventory-based metrics are not applicable because inventory is not
  separately reported.
- Etsy's capitalized internal-use software is included in the project's CapEx
  definition, while other companies may report different categories of
  capitalized technology spending.
- The 2022 impairment charge creates a major one-time distortion in operating
  income, net income, operating margin, and return-based indicators.
- Negative equity in 2022 and 2023 limits the usefulness of equity-based
  ratios.

### Directly Reported Fields

- revenue
- gross_profit
- operating_income
- net_income
- total_assets
- total_liabilities
- total_equity
- current_assets
- current_liabilities
- cash_and_equivalents
- long_term_debt
- operating_cash_flow
- shares_outstanding

### Fields Not Separately Reported

- inventory

### Project-Derived Fields

- capital_expenditure
- free_cash_flow


# CHWY — Chewy, Inc.

## Basic Information

| Field | Value |
|---|---|
| Ticker | CHWY |
| Company | Chewy, Inc. |
| Primary source type | SEC Form 10-K |
| Income statement and cash-flow source | Chewy 2024 Form 10-K comparative financial statements |
| 2022–2023 balance-sheet source | Chewy 2024 Form 10-K |
| 2021 balance-sheet source | Chewy 2023 Form 10-K, supplemented by Chewy 2024 Form 10-K restatement disclosures |
| Fiscal years covered | Fiscal Years 2021–2023 |
| Fiscal Year 2021 end date | 2022-01-30 |
| Fiscal Year 2022 end date | 2023-01-29 |
| Fiscal Year 2023 end date | 2024-01-28 |
| Fiscal-year convention | 52- or 53-week fiscal year ending on the Sunday closest to January 31 |
| Currency | USD |
| Source reporting unit | USD thousands |
| Project reporting unit | USD millions |
| 2024 Form 10-K URL | https://www.sec.gov/Archives/edgar/data/1766502/000176650224000014/chwy-20240128.htm |
| 2023 Form 10-K URL | https://www.sec.gov/Archives/edgar/data/1766502/000176650223000011/chwy-20230129.htm |

---

## Accounting Mapping

### 1. Income Statement Mapping

| Standard Field | Source Label or Derivation | Treatment | Notes |
|---|---|---|---|
| revenue | Net sales | Directly reported | Revenue from product sales, shipping fees, pharmacy, and related activities, net of discounts and allowances |
| gross_profit | Gross profit | Directly reported | Net sales minus cost of goods sold |
| operating_income | (Loss) income from operations | Directly reported | Source wording accommodates both operating income and operating loss |
| net_income | Net income (loss) | Directly reported | Consolidated GAAP net income or loss |

---

### 2. Balance Sheet Mapping

| Standard Field | Source Label or Derivation | Treatment | Notes |
|---|---|---|---|
| total_assets | Total assets | Directly reported | Fiscal-year-end balance |
| total_liabilities | Total liabilities | Directly reported | Fiscal-year-end balance |
| total_equity | Total stockholders' equity / Total stockholders' equity (deficit) | Directly reported | Wording may vary depending on whether equity is positive or negative |
| current_assets | Total current assets | Directly reported | Includes cash, marketable securities, receivables, inventories, and other current assets |
| current_liabilities | Total current liabilities | Directly reported | Includes trade payables and accrued expenses and other current liabilities |
| cash_and_equivalents | Cash and cash equivalents | Directly reported | Excludes marketable securities |
| inventory | Inventories | Directly reported | First-party retail inventory valued under Chewy's inventory accounting policy |
| long_term_debt | No separate long-term debt balance-sheet line | Year-specific verified treatment | Record zero only where the filing explicitly confirms no outstanding ABL borrowings; do not classify operating lease liabilities as long-term debt |
| shares_outstanding | Class A common stock shares outstanding + Class B common stock shares outstanding | Project-derived aggregation | Sum both share classes at fiscal year end; do not use weighted-average EPS shares |

---

### 3. Cash Flow Mapping

| Standard Field | Source Label or Derivation | Treatment | Notes |
|---|---|---|---|
| operating_cash_flow | Net cash provided by operating activities | Directly reported | Annual consolidated operating cash flow |
| capital_expenditure | Capital expenditures | Sign-normalized direct value | Reported as a negative investing cash flow; stored as a positive project amount |
| free_cash_flow | operating_cash_flow - capital_expenditure | Project-derived and company-reconciled | Matches Chewy's disclosed non-GAAP FCF formula for the covered periods |

---

## Data Collection Notes

### Business Model Considerations

Chewy primarily operates as a first-party online pet retailer.

Its business includes:

- Pet food and consumables
- Pet products and hardgoods
- Pet medications and healthcare products
- Private-label products
- Autoship subscription-based repeat purchasing
- Fulfillment and logistics infrastructure

Unlike an asset-light marketplace, Chewy generally purchases and owns the
inventory sold to customers.

### Accounting Risks

- Chewy uses a 52- or 53-week fiscal year rather than a calendar year.
- Fiscal-year labels must therefore be stored separately from the actual
  period-end dates.
- Source financial statements are reported in USD thousands, while the project
  stores monetary amounts in USD millions. Source values must be divided by
  1,000.
- Chewy's 2024 Form 10-K contains restated comparative information for prior
  fiscal years. The latest restated figures should take priority over values
  shown in earlier filings.
- Cash and cash equivalents exclude marketable securities, even though
  marketable securities are an important part of Chewy's liquidity.
- Capital expenditures include purchases of property and equipment as well as
  capitalized labor and license costs associated with internal-use software
  and leasehold improvements.
- Long-term debt should not automatically include operating lease liabilities.
- A zero long-term-debt value should only be entered where the applicable
  filing explicitly confirms that no borrowings were outstanding.
- Fiscal-year-end shares outstanding must combine Class A and Class B common
  shares.
- Weighted-average shares used for EPS are not appropriate for the
  shares_outstanding project field.

### Restatement Treatment

Chewy's 2024 Form 10-K presents updated comparative figures for Fiscal Years
2021, 2022, and 2023.

Collection rules:

1. Use the 2024 Form 10-K for Fiscal Year 2021–2023 income-statement and
   cash-flow values.
2. Use the 2024 Form 10-K for Fiscal Year 2022 and Fiscal Year 2023
   balance-sheet values.
3. For Fiscal Year 2021 balance-sheet values, use the earlier comparative
   balance sheet only after checking whether the relevant field was affected
   by the later restatement.
4. Do not mix pre-restatement income-statement or cash-flow values with the
   latest restated series.
5. Record any remaining source conflict in the row-level notes field.

### Capital Expenditure Definition

Chewy directly reports a consolidated `Capital expenditures` cash-flow line.

The company explains that this amount includes:

- Purchases of property and equipment
- Capitalized labor related to websites and mobile applications
- Internal-use software development
- Leasehold improvements

The project stores the reported negative cash outflow as a positive amount.

### Long-term Debt Treatment

Chewy maintains an asset-based revolving credit facility.

For fiscal years where the filing explicitly states that no borrowings were
outstanding:

- long_term_debt may be recorded as 0

However:

- The unused borrowing capacity is not debt
- Operating lease liabilities are not included in long_term_debt
- Immaterial finance leases are not treated as the project's primary
  long-term-debt measure
- Any year without explicit confirmation should remain blank pending
  verification rather than being assumed to equal zero

### Comparability Issues

- Chewy owns inventory and operates fulfillment infrastructure, making it more
  comparable with first-party retailers than with asset-light marketplaces.
- Inventory, gross margin, fulfillment costs, and working-capital metrics are
  economically meaningful for Chewy.
- Chewy's fiscal-year dates differ from calendar-year companies such as Amazon,
  eBay, and Etsy.
- Direct year-to-year or peer comparisons must therefore use fiscal-year labels
  and period-end dates carefully.
- Chewy's Autoship program creates recurring customer behavior but should not
  be treated as identical to a software subscription business.
- Marketable securities are excluded from cash_and_equivalents, so a pure cash
  ratio may understate Chewy's broader liquid-asset position.
- Operating lease liabilities are material but remain conceptually separate
  from the project's long_term_debt field.

### Directly Reported Fields

- revenue
- gross_profit
- operating_income
- net_income
- total_assets
- total_liabilities
- total_equity
- current_assets
- current_liabilities
- cash_and_equivalents
- inventory
- operating_cash_flow
- capital_expenditure

### Year-Specific Verified Field

- long_term_debt

### Project-Derived Fields

- shares_outstanding
- free_cash_flow


# DASH — DoorDash, Inc.

## Basic Information

| Field | Value |
|---|---|
| Ticker | DASH |
| Company | DoorDash, Inc. |
| Primary source type | SEC Form 10-K |
| Income statement and cash-flow source | DoorDash 2023 Form 10-K comparative financial statements |
| 2022–2023 balance-sheet source | DoorDash 2023 Form 10-K |
| 2021 balance-sheet source | DoorDash 2022 Form 10-K comparative balance sheet |
| Fiscal years covered | 2021–2023 |
| Fiscal year end | December 31 |
| Currency | USD |
| Source reporting unit | USD millions |
| Project reporting unit | USD millions |
| 2023 Form 10-K URL | https://www.sec.gov/Archives/edgar/data/1792789/000162828024005600/dash-20231231.htm |
| 2022 Form 10-K URL | https://www.sec.gov/Archives/edgar/data/1792789/000162828023005131/dash-20221231.htm |

---

## Accounting Mapping

### 1. Income Statement Mapping

| Standard Field | Source Label or Derivation | Treatment | Notes |
|---|---|---|---|
| revenue | Revenue | Directly reported | Represents DoorDash's platform revenue rather than total marketplace order value |
| gross_profit | Gross profit | Directly disclosed outside the primary financial statements | Disclosed in DoorDash's non-GAAP reconciliation; equals revenue less cost of revenue and depreciation and amortization related to cost of revenue |
| operating_income | Loss from operations | Directly reported with sign preserved | Stored as a negative operating-income value for each covered year |
| net_income | Net loss attributable to DoorDash, Inc. common stockholders | Directly reported with sign preserved | Uses the amount attributable to DoorDash common stockholders rather than net loss including redeemable non-controlling interests |

---

### 2. Balance Sheet Mapping

| Standard Field | Source Label or Derivation | Treatment | Notes |
|---|---|---|---|
| total_assets | Total assets | Directly reported | Fiscal-year-end balance |
| total_liabilities | Total liabilities | Directly reported | Fiscal-year-end balance |
| total_equity | Total stockholders' equity | Directly reported | Excludes redeemable non-controlling interests presented outside stockholders' equity |
| current_assets | Total current assets | Directly reported | Includes cash, marketable securities, funds held at payment processors, receivables, and other current assets |
| current_liabilities | Total current liabilities | Directly reported | Includes accounts payable, current operating lease liabilities, and accrued expenses and other current liabilities |
| cash_and_equivalents | Cash and cash equivalents | Directly reported | Excludes restricted cash and short- and long-term marketable securities |
| inventory | Not separately reported | Left blank | DoorDash does not present inventory as a separate consolidated balance-sheet line; blank does not mean zero |
| long_term_debt | No outstanding long-term borrowing balance at fiscal year end | Year-specific verified value | Record 0 for 2021–2023; convertible notes were repaid in February 2021 and no revolving loans were outstanding at the covered year ends |
| shares_outstanding | Class A common shares outstanding + Class B common shares outstanding | Project-derived aggregation | Class C shares were zero; use fiscal-year-end shares rather than weighted-average EPS shares |

---

### 3. Cash Flow Mapping

| Standard Field | Source Label or Derivation | Treatment | Notes |
|---|---|---|---|
| operating_cash_flow | Net cash provided by operating activities | Directly reported | Annual consolidated operating cash flow |
| capital_expenditure | Purchases of property and equipment + Capitalized software and website development costs | Project-derived aggregation with sign normalization | Both source lines are negative investing cash flows; combine them and store the result as one positive CapEx amount |
| free_cash_flow | operating_cash_flow - capital_expenditure | Project-derived and company-reconciled | Matches DoorDash's disclosed FCF formula for the covered years |

---

## Data Collection Notes

### Business Model Considerations

DoorDash operates an asset-light local-commerce platform connecting:

- Merchants
- Consumers
- Dashers and other delivery partners
- Advertisers
- Platform-service customers

Its principal operations include the DoorDash Marketplace, the Wolt
Marketplace, and Platform Services.

DoorDash generally records the fees and commissions earned from marketplace
activity as revenue rather than recording the total value of orders placed
through its platforms.

### Accounting Risks

- Gross profit is not presented as a separate line in the consolidated
  statement of operations. It is disclosed in DoorDash's reconciliation of
  gross profit to non-GAAP performance measures.
- DoorDash's gross-profit definition deducts both cost of revenue and the
  portion of depreciation and amortization associated with cost of revenue.
- Operating results are reported as `Loss from operations` for all three
  covered years and must be stored as negative operating-income values.
- The project uses net loss attributable to DoorDash common stockholders for
  net_income.
- The cash-flow statement begins with net loss including redeemable
  non-controlling interests, which differs slightly from the project
  net_income field in 2022 and 2023.
- Redeemable non-controlling interests are presented between liabilities and
  stockholders' equity rather than inside either category.
- Consequently, total assets do not equal only total liabilities plus total
  stockholders' equity in years where redeemable non-controlling interests
  exist.
- The future accounting-equation validator must reconcile:

  total_assets =
  total_liabilities +
  redeemable_non_controlling_interests +
  total_equity

- Cash and cash equivalents exclude restricted cash and marketable securities.
- Inventory is not separately reported and must remain blank rather than being
  recorded as zero.
- Capital expenditure combines purchases of property and equipment with
  capitalized software and website development costs.
- Both CapEx components are reported as negative investing cash flows and are
  stored as one positive project amount.
- Operating lease liabilities are excluded from long_term_debt.
- Letters of credit and unused revolving-credit capacity are not treated as
  outstanding debt.
- Fiscal-year-end shares outstanding combine Class A and Class B shares and
  exclude weighted-average shares used for EPS.

### Acquisition and Comparability Risks

DoorDash acquired Wolt in 2022.

The acquisition materially affected:

- Goodwill
- Intangible assets
- Total assets
- International revenue
- Depreciation and amortization
- Stock-based compensation
- Redeemable non-controlling interests

Comparisons between 2021 and later years should therefore distinguish organic
operating change from acquisition-related balance-sheet and expense changes.

### Profit and Cash-Flow Interpretation

DoorDash reported net losses throughout 2021–2023 while generating positive
operating cash flow.

A material part of the difference reflects non-cash items such as:

- Stock-based compensation
- Depreciation and amortization
- Investment impairments and remeasurement effects
- Changes in operating assets and liabilities

Net loss should therefore not be interpreted without operating cash flow and
the relevant non-cash adjustments.

### Comparability Issues

- DoorDash's revenue represents platform monetization rather than marketplace
  gross order value.
- Revenue and gross-margin comparisons with first-party retailers are
  therefore structurally limited.
- Inventory metrics are not applicable because inventory is not separately
  reported.
- Marketable securities are excluded from cash_and_equivalents, so a cash-only
  liquidity metric understates DoorDash's broader liquid-asset position.
- DoorDash's marketplace includes delivery logistics and insurance-related
  obligations that differ from pure digital marketplaces such as eBay.
- Wolt's acquisition reduces direct comparability between 2021 and 2022–2023.
- High stock-based compensation can create a substantial difference between
  accounting losses and operating cash generation.

### Directly Reported Fields

- revenue
- operating_income
- net_income
- total_assets
- total_liabilities
- total_equity
- current_assets
- current_liabilities
- cash_and_equivalents
- operating_cash_flow

### Directly Disclosed Outside the Primary Statements

- gross_profit

### Fields Not Separately Reported

- inventory

### Year-Specific Verified Field

- long_term_debt

### Project-Derived Fields

- capital_expenditure
- free_cash_flow
- shares_outstanding


# BKNG — Booking Holdings Inc.

## Basic Information

| Field | Value |
|---|---|
| Ticker | BKNG |
| Company | Booking Holdings Inc. |
| Primary source type | SEC Form 10-K |
| Income statement and cash-flow source | Booking Holdings 2023 Form 10-K comparative financial statements |
| 2022–2023 balance-sheet source | Booking Holdings 2023 Form 10-K |
| 2021 balance-sheet source | Booking Holdings 2022 Form 10-K comparative balance sheet |
| Fiscal years covered | 2021–2023 |
| Fiscal year end | December 31 |
| Currency | USD |
| Source reporting unit | USD millions |
| Project reporting unit | USD millions |
| 2023 Form 10-K URL | https://www.sec.gov/Archives/edgar/data/1075531/000107553124000014/bkng-20231231.htm |
| 2022 Form 10-K URL | https://www.sec.gov/Archives/edgar/data/1075531/000107553123000016/bkng-20221231.htm |

---

## Accounting Mapping

### 1. Income Statement Mapping

| Standard Field | Source Label or Derivation | Treatment | Notes |
|---|---|---|---|
| revenue | Total revenues | Directly reported | Sum of merchant revenues, agency revenues, and advertising and other revenues |
| gross_profit | Not separately reported and not reliably derivable from the primary statements | Left blank | Booking Holdings does not present a consolidated cost-of-revenue or gross-profit line under the project definition; blank does not mean zero |
| operating_income | Operating income | Directly reported | Consolidated operating income |
| net_income | Net income | Directly reported | Consolidated GAAP net income |

---

### 2. Balance Sheet Mapping

| Standard Field | Source Label or Derivation | Treatment | Notes |
|---|---|---|---|
| total_assets | Total assets | Directly reported | Fiscal-year-end balance |
| total_liabilities | Total liabilities | Directly reported | Fiscal-year-end balance |
| total_equity | Total stockholders' equity / Total stockholders' (deficit) equity | Directly reported | Source wording changes when equity becomes negative; 2023 reports a stockholders' deficit |
| current_assets | Total current assets | Directly reported | Fiscal-year-end balance |
| current_liabilities | Total current liabilities | Directly reported | Includes short-term debt and deferred merchant bookings |
| cash_and_equivalents | Cash and cash equivalents | Directly reported | Excludes restricted cash, short-term investments, and long-term investments |
| inventory | Not separately reported | Left blank | Booking Holdings is primarily a travel-platform business and does not present inventory as a separate consolidated balance-sheet line |
| long_term_debt | Long-term debt | Directly reported | Excludes short-term debt and current debt maturities classified in current liabilities |
| shares_outstanding | Issued common shares - treasury shares | Project-derived | Fiscal-year-end outstanding shares; do not use weighted-average EPS shares |

---

### 3. Cash Flow Mapping

| Standard Field | Source Label or Derivation | Treatment | Notes |
|---|---|---|---|
| operating_cash_flow | Net cash provided by operating activities | Directly reported | Annual consolidated operating cash flow |
| capital_expenditure | Additions to property and equipment | Sign-normalized direct value | Reported as a negative investing cash flow; stored as a positive amount in the project |
| free_cash_flow | operating_cash_flow - capital_expenditure | Project-derived | Uses the project's consistent FCF definition |

---

## Data Collection Notes

### Business Model Considerations

Booking Holdings operates asset-light online travel and restaurant reservation
platforms through brands including:

- Booking.com
- Priceline
- Agoda
- KAYAK
- OpenTable

The company generates revenue through three principal categories:

- Merchant revenues
- Agency revenues
- Advertising and other revenues

Gross bookings represent the total value of travel services reserved through
the platforms.

Gross bookings are not equivalent to Booking Holdings' revenue.

### Revenue Recognition Considerations

Booking Holdings generally facilitates transactions between travelers and
travel-service providers.

The company reports revenue on a net basis where it acts as an agent and
recognizes commissions or margins rather than the full value of the underlying
travel booking.

The project therefore uses:

`Total revenues`

as revenue and does not use:

`Total gross bookings`

as revenue.

### Accounting Risks

- Consolidated gross profit is not separately reported.
- The consolidated statements do not provide one clearly defined
  cost-of-revenue line that would support a consistent project gross-profit
  calculation.
- Gross profit must therefore remain blank rather than being assumed to equal
  revenue or revenue minus selected operating expenses.
- Booking Holdings reports substantial merchant bookings collected before the
  associated travel occurs. These amounts contribute to deferred merchant
  bookings and can materially affect working capital and operating cash flow.
- The shift from agency bookings toward merchant bookings can change the timing
  of cash collection, revenue recognition, receivables, and current
  liabilities.
- The company operates internationally and is materially exposed to foreign
  currency movements.
- Cash and cash equivalents exclude restricted cash and investment securities.
- Long-term debt excludes short-term debt presented in current liabilities.
- Capital expenditure appears as a negative investing cash flow but is stored
  as a positive cash-outflow amount in the project.
- Fiscal-year-end shares outstanding are calculated as issued shares less
  treasury shares and should not be confused with weighted-average shares used
  for EPS.
- Extensive share repurchases caused total stockholders' equity to become
  negative in 2023.

### Negative Equity Treatment

Booking Holdings reported negative total stockholders' equity in 2023.

The accounting equation remains valid:

total_assets =
total_liabilities +
total_equity

Because total_equity is negative, total liabilities can exceed total assets.

Consequences for later analysis:

- Debt-to-equity is not economically interpretable in the normal way
- Return on equity may be misleading
- Equity-based ratios require an applicability warning
- Negative equity should not automatically be treated as insolvency because it
  is materially influenced by cumulative share repurchases

### Cash-Flow Considerations

Booking Holdings can generate strong operating cash flow partly because
merchant bookings may be collected before payments are made to travel-service
providers.

Changes in deferred merchant bookings and related liabilities can therefore
create significant working-capital effects.

Operating cash flow should be interpreted together with:

- Revenue growth
- Deferred merchant bookings
- Current liabilities
- Travel-demand conditions
- Merchant-versus-agency revenue mix

### Comparability Issues

- Booking Holdings' revenue represents platform commissions, margins, and fees
  rather than the total value of travel booked.
- Revenue and margin comparisons with first-party retailers are structurally
  limited.
- Inventory-based indicators are not applicable.
- Gross-margin analysis is unavailable under the current standardized schema
  because consolidated gross profit cannot be reliably derived.
- Travel demand was materially affected by the COVID-19 pandemic and subsequent
  recovery, making 2021–2023 growth rates unusually volatile.
- The increasing merchant-revenue mix affects working capital and cash-flow
  timing.
- Negative equity caused by share repurchases limits the usefulness of
  equity-based ratios.

### Directly Reported Fields

- revenue
- operating_income
- net_income
- total_assets
- total_liabilities
- total_equity
- current_assets
- current_liabilities
- cash_and_equivalents
- long_term_debt
- operating_cash_flow
- capital_expenditure

### Fields Not Separately Reported

- gross_profit
- inventory

### Project-Derived Fields

- shares_outstanding
- free_cash_flow