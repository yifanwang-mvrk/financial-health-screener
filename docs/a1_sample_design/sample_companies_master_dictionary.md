# A1 Sample Companies Master Dictionary

## Purpose

This file defines the master company table for the Financial Health Screener project.  
The table is used to identify the core sample of US-listed e-commerce companies and classify them by business model before financial statement data is collected.

## File

`data/raw/sample_companies_master.csv`

## Fields

| Field | Meaning |
|---|---|
| ticker | Stock ticker used for financial data collection |
| company_name | Official company name |
| exchange | Listing exchange, such as NASDAQ or NYSE |
| country | Company headquarters or main listing country |
| listing_status | Active, delisted, acquired, bankrupt, etc. |
| primary_business_model | Main e-commerce business model |
| secondary_business_model | Secondary model if relevant |
| platform_type | Marketplace, first-party retailer, hybrid platform, service platform, etc. |
| has_marketplace | Whether the company operates a third-party marketplace |
| has_first_party_retail | Whether the company sells inventory directly |
| has_subscription | Whether subscription revenue is meaningful |
| has_payment_fintech | Whether payment or fintech activity is meaningful |
| has_ads_business | Whether advertising revenue is meaningful |
| peer_group | Peer group used for relative comparison |
| include_in_core_sample | 1 if included in core sample, 0 otherwise |
| include_reason | Reason for inclusion |
| exclude_reason | Reason for exclusion if not included |
| notes | Additional comments |

## Business model coding principles

- A company should be classified by its dominant business model during the study period.
- If the business model changed materially, record the dominant model and explain the change in notes.
- Hybrid firms should be marked clearly instead of forced into a pure category.
- Core sample inclusion should prioritize companies with available multi-year financial data.
- Companies with insufficient data can remain in the universe table but be excluded from the core sample.

