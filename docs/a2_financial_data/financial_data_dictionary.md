# A2 Financial Data Dictionary

## Purpose

This document defines the raw annual financial statement data structure for the Financial Health Screener project.

The table stores company-year level financial data. Each row represents one company in one fiscal year.

## File

`data/raw/financial_statements_template.csv`

## Table Grain

One row equals:

`one company × one fiscal year`

Example:

- AMZN in fiscal year 2023
- ETSY in fiscal year 2022
- EBAY in fiscal year 2021

## Fields

| Field | Meaning |
|---|---|
| ticker | Stock ticker matching the company master table |
| fiscal_year | Fiscal year of the financial statement |
| period_end_date | Fiscal year-end date |
| currency | Reporting currency, usually USD |
| revenue | Total revenue |
| gross_profit | Revenue minus cost of goods sold or cost of revenue |
| operating_income | Profit after operating expenses but before interest and taxes |
| net_income | Net income attributable to common shareholders if available |
| total_assets | Total assets |
| total_liabilities | Total liabilities |
| total_equity | Total shareholders' equity |
| current_assets | Current assets |
| current_liabilities | Current liabilities |
| cash_and_equivalents | Cash and cash equivalents |
| inventory | Inventory balance if applicable |
| long_term_debt | Long-term debt |
| operating_cash_flow | Net cash provided by operating activities |
| capital_expenditure | Capital expenditure, usually purchase of property and equipment |
| free_cash_flow | Operating cash flow minus capital expenditure |
| shares_outstanding | Shares outstanding if available |
| source | Data source name |
| source_url | Link or reference to the original source |
| notes | Data quality comments or special treatment |

## Why These Fields Matter

These fields are selected because they support the core financial health indicators used later in the project.

Examples:

- Revenue supports growth analysis.
- Gross profit supports gross margin analysis.
- Operating income supports operating margin analysis.
- Net income supports profitability analysis.
- Total assets and equity support ROA and ROE.
- Liabilities and equity support leverage analysis.
- Current assets and current liabilities support liquidity analysis.
- Operating cash flow and free cash flow support cash flow quality analysis.
- Inventory helps identify working capital pressure for first-party retailers.

## Data Collection Principle

At the A2 stage, the project prioritizes annual financial statement data.

Quarterly data may be added later, but annual data is better for the first project version because it is simpler, more stable, and easier to explain in a portfolio project.

## Data Quality Principle

Raw financial data should not be overwritten silently.

If a number is adjusted, transformed, or manually corrected, the reason should be recorded in the `notes` field or in a separate data cleaning log.

