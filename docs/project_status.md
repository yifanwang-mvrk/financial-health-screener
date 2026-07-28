# Financial Health Screener

## Project Status

Last updated: 2026-07-28


# 1. Project Goal

## Business Question

Can financial deterioration signals be identified before severe financial distress happens for publicly listed e-commerce related companies?


## Core Objective

Build a financial health screening framework that combines:

- Financial statement analysis
- Business model classification
- Data engineering
- SQL analysis
- Power BI visualization


The final output is designed to help identify companies showing potential financial deterioration risks.


---

# 2. Current Project Phase

Current phase:

A2 - Financial Data Collection


Overall pipeline:

A1 Sample Design
✅ Completed


A2 Financial Data Collection
🔄 In progress


A3 Data Cleaning and Standardization
⬜ Not started


A4 Financial Indicator Engineering
⬜ Not started


A5 Risk Signal Analysis
⬜ Not started


A6 Dashboard Development
⬜ Not started



---

# 3. Completed Tasks


## Project Structure

Completed:

- Created professional project environment
- Established Git repository
- Created folder structure


## Sample Design

Completed:

- Defined company universe
- Created sample company master table
- Added business model classification


## Data Quality Framework

Completed:

Implemented validation scripts:

- check_sample_master.py
- check_financial_statements.py


Current checks include:

- Schema validation
- Required field validation
- Duplicate detection
- Data type validation
- Business classification validation



---

# 4. Current Work


## Financial Statement Data Collection

Current target companies:

- AMZN
- EBAY
- ETSY


Target period:

2021-2023 annual financial statements


Required data fields:

- Revenue
- Gross profit
- Operating income
- Net income
- Total assets
- Total liabilities
- Total equity
- Operating cash flow
- Capital expenditure


---

# 5. Data Pipeline Concept


Raw data:

data/raw/

Purpose:

Store original collected financial data.


Normalized data:

data/normalized/

Purpose:

Standardize:

- Units
- Currency
- Dates
- Accounting definitions


Processed data:

data/processed/

Purpose:

Analysis-ready dataset for:

- SQL
- Python analysis
- Power BI



---

# 6. Technical Architecture


Python:

Used for:

- Data collection
- Data cleaning
- Validation
- Feature engineering


SQL:

Used for:

- Data querying
- Financial indicator calculation


Power BI:

Used for:

- Dashboard creation
- Business insight communication



---

# 7. Known Issues


Current limitations:

- Financial data has not been collected yet
- Accounting definition mapping needs verification
- Automated extraction has not been implemented


---

# 8. Next Steps


1. Collect AMZN / EBAY / ETSY 2021-2023 financial data

2. Validate collected data

3. Normalize financial statement structure

4. Calculate financial health indicators

5. Build screening logic
