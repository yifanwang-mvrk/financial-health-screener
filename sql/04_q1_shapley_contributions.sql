create or replace table q1_dupont_contributions as
with transitions as (
    select
        ticker,
        company_name,
        analysis_peer_group,
        fiscal_year,
        fiscal_year - 1 as prior_fiscal_year,
        net_margin,
        asset_turnover,
        equity_multiplier,
        roe,
        average_equity,
        dupont_valid_flag,
        lag(fiscal_year) over (partition by ticker order by fiscal_year) as observed_prior_fiscal_year,
        lag(net_margin) over (partition by ticker order by fiscal_year) as prior_net_margin,
        lag(asset_turnover) over (partition by ticker order by fiscal_year) as prior_asset_turnover,
        lag(equity_multiplier) over (partition by ticker order by fiscal_year) as prior_equity_multiplier,
        lag(roe) over (partition by ticker order by fiscal_year) as prior_roe,
        lag(average_equity) over (partition by ticker order by fiscal_year) as prior_average_equity,
        lag(dupont_valid_flag) over (partition by ticker order by fiscal_year) as prior_dupont_valid_flag
    from q1_annual_company_metrics
),
validity as (
    select
        *,
        dupont_valid_flag
            and coalesce(prior_dupont_valid_flag, false)
            and observed_prior_fiscal_year = fiscal_year - 1 as transition_valid_flag,
        roe - prior_roe as roe_change
    from transitions
),
shapley as (
    select
        *,
        case when transition_valid_flag then
            (net_margin - prior_net_margin) * (
                (1.0 / 3.0) * prior_asset_turnover * prior_equity_multiplier
                + (1.0 / 6.0) * asset_turnover * prior_equity_multiplier
                + (1.0 / 6.0) * prior_asset_turnover * equity_multiplier
                + (1.0 / 3.0) * asset_turnover * equity_multiplier
            )
        end as contribution_margin,
        case when transition_valid_flag then
            (asset_turnover - prior_asset_turnover) * (
                (1.0 / 3.0) * prior_net_margin * prior_equity_multiplier
                + (1.0 / 6.0) * net_margin * prior_equity_multiplier
                + (1.0 / 6.0) * prior_net_margin * equity_multiplier
                + (1.0 / 3.0) * net_margin * equity_multiplier
            )
        end as contribution_turnover,
        case when transition_valid_flag then
            (equity_multiplier - prior_equity_multiplier) * (
                (1.0 / 3.0) * prior_net_margin * prior_asset_turnover
                + (1.0 / 6.0) * net_margin * prior_asset_turnover
                + (1.0 / 6.0) * prior_net_margin * asset_turnover
                + (1.0 / 3.0) * net_margin * asset_turnover
            )
        end as contribution_multiplier
    from validity
),
classified as (
    select
        *,
        contribution_margin + contribution_turnover + contribution_multiplier as contribution_sum,
        case
            when not transition_valid_flag then 'not_available'
            when abs(contribution_margin) >= abs(contribution_turnover)
             and abs(contribution_margin) >= abs(contribution_multiplier) then 'margin'
            when abs(contribution_turnover) >= abs(contribution_margin)
             and abs(contribution_turnover) >= abs(contribution_multiplier) then 'turnover'
            else 'multiplier'
        end as dominant_change_driver,
        case
            when not transition_valid_flag or roe_change <= 0 then 'not_improvement'
            when contribution_multiplier > 0
             and contribution_multiplier > contribution_margin
             and contribution_multiplier > contribution_turnover then 'leverage_driven'
            when contribution_margin > 0
             and contribution_margin > contribution_turnover
             and contribution_margin > contribution_multiplier then 'operating_driven'
            when contribution_turnover > 0
             and contribution_turnover > contribution_margin
             and contribution_turnover > contribution_multiplier then 'operating_driven'
            else 'mixed_or_ambiguous'
        end as h1_driver_group,
        case when transition_valid_flag then
            greatest(contribution_multiplier, 0.0) / nullif(
                greatest(contribution_margin, 0.0)
                + greatest(contribution_turnover, 0.0)
                + greatest(contribution_multiplier, 0.0),
                0
            )
        end as leverage_contribution_share
    from shapley
)
select
    *,
    case when transition_valid_flag then roe_change - contribution_sum end as shapley_reconciliation_gap
from classified
where fiscal_year > (select min(fiscal_year) from q1_annual_company_metrics)
order by ticker, fiscal_year;
