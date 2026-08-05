create or replace table b1_pilot_annual_source as
select * from b1_pilot_wide_input;

create or replace table b1_pilot_annual_company_metrics as
with balances as (
    select
        *,
        lag(fiscal_year) over (partition by company_id order by fiscal_year) as prior_fiscal_year,
        lag(total_assets) over (partition by company_id order by fiscal_year) as prior_total_assets,
        lag(total_equity) over (partition by company_id order by fiscal_year) as prior_total_equity
    from b1_pilot_annual_source
), calculated as (
    select
        *,
        case when prior_fiscal_year = fiscal_year - 1
            then (total_assets + prior_total_assets) / 2.0 end as average_assets,
        case when prior_fiscal_year = fiscal_year - 1
            then (total_equity + prior_total_equity) / 2.0 end as average_equity,
        net_income / nullif(revenue, 0) as net_margin,
        operating_income / nullif(revenue, 0) as operating_margin,
        current_assets / nullif(current_liabilities, 0) as current_ratio,
        total_liabilities / nullif(total_assets, 0) as liabilities_to_assets,
        total_debt / nullif(total_assets, 0) as total_debt_to_assets,
        operating_cash_flow / nullif(revenue, 0) as operating_cash_flow_margin,
        free_cash_flow / nullif(revenue, 0) as free_cash_flow_margin
    from balances
), dupont as (
    select
        *,
        revenue / nullif(average_assets, 0) as asset_turnover,
        case when average_equity > 0 then average_assets / average_equity end as equity_multiplier,
        case when average_equity > 0 then net_income / average_equity end as roe,
        prior_fiscal_year = fiscal_year - 1
            and prior_total_assets is not null
            and prior_total_equity is not null as average_balance_available_flag,
        average_equity > 0 as positive_average_equity_flag
    from calculated
)
select
    *,
    net_margin * asset_turnover * equity_multiplier as dupont_roe,
    average_balance_available_flag
        and positive_average_equity_flag
        and revenue is not null and revenue <> 0
        and average_assets is not null and average_assets <> 0 as dupont_valid_flag,
    case when average_balance_available_flag
        and positive_average_equity_flag
        and revenue is not null and revenue <> 0
        and average_assets is not null and average_assets <> 0
        then roe - (net_margin * asset_turnover * equity_multiplier)
    end as dupont_identity_gap
from dupont
order by company_id, fiscal_year;

create or replace table b1_pilot_peer_summary as
select
    formal_peer_group,
    fiscal_year,
    count(*) as company_count,
    count(roe) as valid_roe_company_count,
    median(roe) as peer_median_roe,
    median(net_margin) as peer_median_net_margin,
    median(asset_turnover) as peer_median_asset_turnover,
    median(equity_multiplier) as peer_median_equity_multiplier
from b1_pilot_annual_company_metrics
group by formal_peer_group, fiscal_year
order by formal_peer_group, fiscal_year;

create or replace table b1_pilot_company_vs_peer as
with ranked as (
    select
        m.*,
        count(roe) over (partition by formal_peer_group, fiscal_year) as valid_peer_roe_count,
        rank() over (
            partition by formal_peer_group, fiscal_year order by roe nulls last
        ) as roe_ascending_rank
    from b1_pilot_annual_company_metrics m
)
select
    r.*,
    p.peer_median_roe,
    p.peer_median_net_margin,
    p.peer_median_asset_turnover,
    p.peer_median_equity_multiplier,
    r.roe - p.peer_median_roe as roe_vs_peer_median,
    case
        when r.roe is not null and r.valid_peer_roe_count > 1
            then (r.roe_ascending_rank - 1.0) / (r.valid_peer_roe_count - 1.0)
        when r.roe is not null and r.valid_peer_roe_count = 1 then 0.5
    end as roe_peer_percentile
from ranked r
left join b1_pilot_peer_summary p using (formal_peer_group, fiscal_year)
order by r.company_id, r.fiscal_year;

create or replace table b1_pilot_dupont_contributions as
with transitions as (
    select
        *,
        lag(fiscal_year) over (partition by company_id order by fiscal_year) as observed_prior_fiscal_year,
        lag(net_margin) over (partition by company_id order by fiscal_year) as prior_net_margin,
        lag(asset_turnover) over (partition by company_id order by fiscal_year) as prior_asset_turnover,
        lag(equity_multiplier) over (partition by company_id order by fiscal_year) as prior_equity_multiplier,
        lag(roe) over (partition by company_id order by fiscal_year) as prior_roe,
        lag(average_equity) over (partition by company_id order by fiscal_year) as prior_average_equity,
        lag(dupont_valid_flag) over (partition by company_id order by fiscal_year) as prior_dupont_valid_flag
    from b1_pilot_company_vs_peer
), validity as (
    select
        *,
        dupont_valid_flag and coalesce(prior_dupont_valid_flag, false)
            and observed_prior_fiscal_year = fiscal_year - 1 as transition_valid_flag,
        roe - prior_roe as roe_change
    from transitions
), shapley as (
    select
        *,
        case when transition_valid_flag then
            (net_margin - prior_net_margin) * (
                (1.0 / 3.0) * prior_asset_turnover * prior_equity_multiplier
                + (1.0 / 6.0) * asset_turnover * prior_equity_multiplier
                + (1.0 / 6.0) * prior_asset_turnover * equity_multiplier
                + (1.0 / 3.0) * asset_turnover * equity_multiplier
            ) end as contribution_margin,
        case when transition_valid_flag then
            (asset_turnover - prior_asset_turnover) * (
                (1.0 / 3.0) * prior_net_margin * prior_equity_multiplier
                + (1.0 / 6.0) * net_margin * prior_equity_multiplier
                + (1.0 / 6.0) * prior_net_margin * equity_multiplier
                + (1.0 / 3.0) * net_margin * equity_multiplier
            ) end as contribution_turnover,
        case when transition_valid_flag then
            (equity_multiplier - prior_equity_multiplier) * (
                (1.0 / 3.0) * prior_net_margin * prior_asset_turnover
                + (1.0 / 6.0) * net_margin * prior_asset_turnover
                + (1.0 / 6.0) * prior_net_margin * asset_turnover
                + (1.0 / 3.0) * net_margin * asset_turnover
            ) end as contribution_multiplier
    from validity
), classified as (
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
        end as dominant_driver,
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
                + greatest(contribution_multiplier, 0.0), 0
            ) end as leverage_contribution_share
    from shapley
)
select
    *,
    case when transition_valid_flag then roe_change - contribution_sum end
        as shapley_reconciliation_gap
from classified
where fiscal_year > (select min(fiscal_year) from b1_pilot_annual_company_metrics)
order by company_id, fiscal_year;

create or replace table b1_pilot_h1_sample_audit as
with audited as (
    select
        d.*,
        n.average_equity as next_average_equity,
        n.roe as next_year_roe,
        n.roe_vs_peer_median as next_year_peer_relative_roe,
        n.fiscal_year as next_fiscal_year,
        n.roe - d.roe as next_year_roe_change,
        n.roe_vs_peer_median - d.roe_vs_peer_median as next_year_peer_relative_change,
        coalesce(d.prior_roe <= 0 and d.roe_change > 0, false) as turnaround_from_loss,
        d.transition_valid_flag
            and d.prior_average_equity > 0
            and d.average_equity > 0
            and n.average_equity > 0
            and d.prior_roe > 0
            and d.roe_change > 0
            and n.roe is not null
            and d.h1_driver_group in ('leverage_driven', 'operating_driven') as h1_eligible_flag
    from b1_pilot_dupont_contributions d
    left join b1_pilot_company_vs_peer n
        on d.company_id = n.company_id and d.fiscal_year + 1 = n.fiscal_year
)
select
    *,
    case
        when not transition_valid_flag then 'invalid_dupont_transition'
        when prior_average_equity is null or prior_average_equity <= 0 then 'nonpositive_prior_average_equity'
        when average_equity is null or average_equity <= 0 then 'nonpositive_current_average_equity'
        when prior_roe is null or prior_roe <= 0 then
            case when turnaround_from_loss then 'turnaround_from_loss' else 'nonpositive_prior_roe' end
        when roe_change is null or roe_change <= 0 then 'no_roe_improvement'
        when h1_driver_group = 'mixed_or_ambiguous' then 'mixed_or_ambiguous_driver'
        when next_fiscal_year is null or next_year_roe is null then 'next_year_not_observable'
        when next_average_equity is null or next_average_equity <= 0 then 'nonpositive_next_average_equity'
        when h1_eligible_flag then 'eligible'
        else 'other_exclusion'
    end as h1_sample_status
from audited
order by company_id, fiscal_year;

create or replace table b1_pilot_h1_evidence_summary as
with eligible as (
    select * from b1_pilot_h1_sample_audit where h1_eligible_flag
), counts as (
    select
        (select count(*) from eligible) as eligible_transition_count,
        (select count(distinct company_id) from eligible) as eligible_unique_company_count,
        (select count(distinct company_id) from eligible where h1_driver_group = 'leverage_driven')
            as leverage_driven_unique_company_count,
        (select count(distinct company_id) from eligible where h1_driver_group = 'operating_driven')
            as operating_driven_unique_company_count
)
select
    *,
    case
        when eligible_unique_company_count >= 15
         and eligible_transition_count >= 40
         and leverage_driven_unique_company_count >= 8
         and operating_driven_unique_company_count >= 8 then 'A'
        when eligible_unique_company_count >= 8
         and eligible_transition_count >= 20 then 'B'
        else 'C'
    end as evidence_tier,
    case
        when eligible_unique_company_count >= 15
         and eligible_transition_count >= 40
         and leverage_driven_unique_company_count >= 8
         and operating_driven_unique_company_count >= 8
            then 'Company-clustered comparison permitted; no causal claim'
        when eligible_unique_company_count >= 8
         and eligible_transition_count >= 20
            then 'Descriptive persistence comparison only'
        else 'Evidence insufficient for group testing; illustrative cases only'
    end as permitted_inference
from counts;
