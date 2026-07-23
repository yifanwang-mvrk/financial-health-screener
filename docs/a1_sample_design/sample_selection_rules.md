# A1 Sample Selection Rules

## Project Scope

This project studies financial distress early warning signals among US-listed e-commerce companies.

The sample design separates the company universe from the core analytical sample:

- Universe: companies that are potentially relevant to the e-commerce sector.
- Core sample: companies that satisfy the final inclusion rules and have sufficient financial data for analysis.

## Definition of E-commerce Company

A company is considered relevant to the e-commerce universe if a meaningful part of its business involves digital commerce, online marketplace activity, internet-based retail, or transaction-enabled digital platforms.

Relevant business types include:

1. First-party online retail
2. Third-party marketplace
3. Hybrid first-party retail and marketplace
4. Online travel and booking platforms
5. Online food delivery and local commerce platforms
6. Online service commerce platforms
7. E-commerce infrastructure and merchant enablement platforms

## Core Inclusion Rules

A company may enter the core sample if it satisfies all of the following:

1. It is listed in the United States, primarily on NASDAQ or NYSE.
2. It has meaningful exposure to e-commerce or digital transaction-based commerce.
3. It has available multi-year annual financial statement data.
4. It reports enough information to calculate core financial health indicators, including revenue, net income, total assets, total liabilities or equity, and cash flow variables.
5. Its business model can be classified into a defensible peer group.

## Exclusion Rules

A company should be excluded from the core sample if:

1. E-commerce exposure is too small or only incidental.
2. Financial statement data is insufficient for multi-year comparison.
3. The company is primarily a payment processor, software vendor, media company, or logistics company without direct e-commerce exposure.
4. The company has undergone a major structural event that makes comparison unreliable, unless the event itself is relevant to financial distress analysis.
5. The company is a foreign-listed firm without comparable US financial reporting access, unless its US listing and filings are sufficiently complete.

## Treatment of Delisted, Acquired, or Bankrupt Companies

Delisted, acquired, or bankrupt companies should not be automatically removed from the universe.

They may be retained if they are useful for distress analysis and if pre-event financial data are available.

However:

- They should be clearly marked in `listing_status`.
- They should be excluded from the core sample if financial data are too incomplete.
- The reason for inclusion or exclusion should be documented in `include_reason` or `exclude_reason`.

## Business Model Categories

The project uses the following business model categories:

| Category | Meaning |
|---|---|
| first_party_retail | Company primarily sells inventory directly to customers online |
| marketplace | Company primarily connects third-party buyers and sellers |
| hybrid_retail_marketplace | Company combines first-party retail and third-party marketplace activity |
| travel_booking_platform | Company enables online travel booking or reservation transactions |
| food_delivery_local_commerce | Company enables online food delivery or local commerce transactions |
| service_commerce_platform | Company enables online purchase of services |
| merchant_enablement | Company provides infrastructure enabling merchants to sell online |

## Peer Group Principles

Peer groups should be based on business model similarity rather than broad sector labels.

The main peer group should reflect the company's dominant revenue model and operating logic.

Hybrid firms should not be forced into pure categories. They should be classified as hybrid and explained in notes.

## Data Availability Principle

The core sample should prioritize companies with enough annual data to support:

1. Cross-sectional comparison
2. Time-series trend analysis
3. Peer-relative financial health screening
4. Distress or deterioration signal construction

Companies with limited data can remain in the universe table but should be marked as non-core.

## Current Design Decision

At the A1 stage, the project will first build a broad candidate universe.

The final core sample will be selected only after data availability has been checked.

