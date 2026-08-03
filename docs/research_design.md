# Q1 Research Design

Last updated: 2026-08-03

## 1. Purpose

The analysis separates the level of return on equity from the quality of the mechanism producing it. A high ROE can come from operating economics, efficient use of assets, or a thin equity base. Those mechanisms do not carry the same business meaning.

## 2. Questions

### Q1-A: Financial Quality

How much of each company's ROE is associated with net margin, asset turnover, and the equity multiplier? Can companies with similar ROE have different driver quality?

### H1: Persistence

Leverage-driven ROE improvements have lower one-year persistence than operating-driven improvements.

The main H1 comparison is `leverage_driven` versus `operating_driven`. Margin-driven and turnover-driven labels may be retained for descriptive detail, but they are combined for the pre-specified main comparison.

## 3. Unit of Analysis

- Q1-A: company x fiscal year.
- H1: company x fiscal-year transition.
- Independent entities for H1 evidence thresholds: unique companies, not company-years.

## 4. DuPont Definitions

```text
Average Assets_t = (Assets_(t-1) + Assets_t) / 2
Average Equity_t = (Equity_(t-1) + Equity_t) / 2

Net Margin_t        = Net Income_t / Revenue_t
Asset Turnover_t    = Revenue_t / Average Assets_t
Equity Multiplier_t = Average Assets_t / Average Equity_t
ROE_t               = Net Income_t / Average Equity_t

ROE_t = Net Margin_t x Asset Turnover_t x Equity Multiplier_t
```

ROE and the equity multiplier are invalid when average equity is nonpositive. Metrics requiring prior balances are unavailable for the first observed year.

## 5. Shapley Decomposition

For the product `f(M, T, L) = M x T x L`, exact three-factor Shapley values average each factor's marginal effect across all six possible factor orders.

For margin:

```text
phi_M = delta_M x [
    (1/3) T0 L0 +
    (1/6) T1 L0 +
    (1/6) T0 L1 +
    (1/3) T1 L1
]
```

Turnover and multiplier contributions use the corresponding symmetric formula. The implementation must satisfy:

```text
delta_ROE = phi_M + phi_T + phi_L
```

`dominant_change_driver` identifies the largest absolute contribution for descriptive analysis.

For a positive ROE change:

- `leverage_driven`: multiplier is the unique largest positive contribution.
- `operating_driven`: margin or turnover is the unique largest positive contribution.
- `mixed_or_ambiguous`: no unique positive dominant contribution.

`leverage_contribution_share` is the positive multiplier contribution divided by the sum of all positive contributions.

## 6. H1 Eligibility

A transition ending in year `t` enters the main H1 sample only if all conditions hold:

```text
Average Equity_(t-1) > 0
Average Equity_t > 0
Average Equity_(t+1) > 0
ROE_(t-1) > 0
ROE_t - ROE_(t-1) > 0
DuPont components are valid at t-1 and t
ROE_(t+1) is observable
driver group is leverage_driven or operating_driven
```

An improvement beginning from nonpositive ROE is labeled `turnaround_from_loss` and excluded from the main H1 sample.

## 7. Persistence Outcomes

Main outcome:

- `next_year_peer_relative_change`: change from the company's current peer-relative ROE to next-year peer-relative ROE.

Secondary outcomes:

- `next_year_roe_change`
- `roe_reversal_flag`
- `rank_retention`

## 8. Evidence Tiers

| Tier | Minimum evidence | Permitted inference |
| --- | --- | --- |
| A | At least 15 eligible companies, 40 transitions, 8 companies in each main group, and no material concentration | Company-clustered bootstrap and group comparison; no causal claim |
| B | 8-14 eligible companies, 20-39 transitions, group imbalance, or concentration | Descriptive persistence comparison only |
| C | Fewer than 8 eligible companies or fewer than 20 transitions | No group test; illustrative cases only |

The current release is Tier C with zero eligible transitions. The threshold is not relaxed.

## 9. Peer Groups

- Inventory-led E-commerce: AMZN, CHWY.
- Marketplace / Platform: BKNG, DASH, EBAY, ETSY.

The wider operating-model categories create a usable descriptive benchmark while retaining each issuer's detailed business model in the mart. The small sample prevents industry inference.

## 10. Research Boundaries

- No black-box composite score.
- No investment recommendation.
- No causal interpretation.
- No silent replacement of missing values with zero.
- No use of end-of-period equity where the design requires average equity.
- No Power BI calculation of research logic already owned by SQL.
