create or replace table q1_peer_summary as
select
    formal_peer_group,
    fiscal_year,
    count(*) as company_count,
    count(roe) as valid_roe_company_count,
    median(roe) as peer_median_roe,
    quantile_cont(roe, 0.25) as peer_q25_roe,
    quantile_cont(roe, 0.75) as peer_q75_roe,
    count(net_margin) as valid_net_margin_company_count,
    median(net_margin) as peer_median_net_margin,
    quantile_cont(net_margin, 0.25) as peer_q25_net_margin,
    quantile_cont(net_margin, 0.75) as peer_q75_net_margin,
    count(asset_turnover) as valid_asset_turnover_company_count,
    median(asset_turnover) as peer_median_asset_turnover,
    quantile_cont(asset_turnover, 0.25) as peer_q25_asset_turnover,
    quantile_cont(asset_turnover, 0.75) as peer_q75_asset_turnover,
    count(equity_multiplier) as valid_equity_multiplier_company_count,
    median(equity_multiplier) as peer_median_equity_multiplier,
    quantile_cont(equity_multiplier, 0.25) as peer_q25_equity_multiplier,
    quantile_cont(equity_multiplier, 0.75) as peer_q75_equity_multiplier,
    count(current_ratio) as valid_current_ratio_company_count,
    median(current_ratio) as peer_median_current_ratio,
    count(total_debt_to_assets) as valid_total_debt_to_assets_company_count,
    median(total_debt_to_assets) as peer_median_total_debt_to_assets,
    count(free_cash_flow_margin) as valid_fcf_margin_company_count,
    median(free_cash_flow_margin) as peer_median_free_cash_flow_margin
from q1_annual_company_metrics
group by formal_peer_group, fiscal_year
order by formal_peer_group, fiscal_year;

create or replace table q1_company_vs_peer as
with valid_roe_percentiles as (
    select
        company_id,
        fiscal_year,
        percent_rank() over (
            partition by formal_peer_group, fiscal_year
            order by roe
        ) as roe_peer_percentile
    from q1_annual_company_metrics
    where roe is not null
)
select
    m.*,
    p.company_count as peer_company_count,
    p.valid_roe_company_count as valid_peer_roe_count,
    p.peer_median_roe,
    p.peer_q25_roe,
    p.peer_q75_roe,
    p.peer_median_net_margin,
    p.peer_median_asset_turnover,
    p.peer_median_equity_multiplier,
    p.peer_median_current_ratio,
    p.peer_median_total_debt_to_assets,
    p.peer_median_free_cash_flow_margin,
    m.roe - p.peer_median_roe as roe_vs_peer_median,
    m.net_margin - p.peer_median_net_margin as net_margin_vs_peer_median,
    m.asset_turnover - p.peer_median_asset_turnover
        as asset_turnover_vs_peer_median,
    m.equity_multiplier - p.peer_median_equity_multiplier
        as equity_multiplier_vs_peer_median,
    m.free_cash_flow_margin - p.peer_median_free_cash_flow_margin
        as fcf_margin_vs_peer_median,
    r.roe_peer_percentile
from q1_annual_company_metrics m
left join q1_peer_summary p using (formal_peer_group, fiscal_year)
left join valid_roe_percentiles r using (company_id, fiscal_year)
order by m.company_id, m.fiscal_year;

create or replace table q1_driver_persistence as
with outcomes as (
    select
        company_id,
        fiscal_year,
        roe,
        roe_vs_peer_median,
        roe_peer_percentile,
        lead(fiscal_year) over (partition by company_id order by fiscal_year)
            as observed_next_fiscal_year,
        lead(roe) over (partition by company_id order by fiscal_year) as observed_next_roe,
        lead(roe_vs_peer_median) over (partition by company_id order by fiscal_year)
            as observed_next_peer_relative_roe,
        lead(roe_peer_percentile) over (partition by company_id order by fiscal_year)
            as observed_next_peer_percentile
    from q1_company_vs_peer
)
select
    d.*,
    o.roe_vs_peer_median as current_peer_relative_roe,
    o.roe_peer_percentile as current_peer_percentile,
    case when o.observed_next_fiscal_year = d.fiscal_year + 1
        then o.observed_next_fiscal_year
    end as next_fiscal_year,
    case when o.observed_next_fiscal_year = d.fiscal_year + 1
        then o.observed_next_roe
    end as next_year_roe,
    case when o.observed_next_fiscal_year = d.fiscal_year + 1
        then o.observed_next_peer_relative_roe
    end as next_year_peer_relative_roe,
    case when o.observed_next_fiscal_year = d.fiscal_year + 1
        then o.observed_next_peer_percentile
    end as next_year_peer_percentile,
    case when o.observed_next_fiscal_year = d.fiscal_year + 1
        then o.observed_next_roe - d.roe
    end as next_year_roe_change,
    case when o.observed_next_fiscal_year = d.fiscal_year + 1
        then o.observed_next_peer_relative_roe - o.roe_vs_peer_median
    end as next_year_peer_relative_change,
    case when o.observed_next_fiscal_year = d.fiscal_year + 1
          and o.observed_next_roe is not null
        then o.observed_next_roe - d.roe < 0
    end as roe_reversal_flag,
    case when o.observed_next_fiscal_year = d.fiscal_year + 1
        then o.observed_next_peer_percentile
    end as rank_retention
from q1_dupont_contributions d
left join outcomes o using (company_id, fiscal_year)
order by d.company_id, d.fiscal_year;
