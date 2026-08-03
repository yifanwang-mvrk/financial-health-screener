create or replace table q1_peer_summary as
select
    analysis_peer_group,
    fiscal_year,
    count(*) as company_count,
    count(roe) as valid_roe_company_count,
    median(roe) as peer_median_roe,
    median(net_margin) as peer_median_net_margin,
    median(asset_turnover) as peer_median_asset_turnover,
    median(equity_multiplier) as peer_median_equity_multiplier,
    median(operating_margin) as peer_median_operating_margin,
    median(current_ratio) as peer_median_current_ratio,
    median(liabilities_to_assets) as peer_median_liabilities_to_assets,
    median(free_cash_flow_margin) as peer_median_free_cash_flow_margin
from q1_annual_company_metrics
group by analysis_peer_group, fiscal_year
order by analysis_peer_group, fiscal_year;

create or replace table q1_company_vs_peer as
with ranked as (
    select
        m.*,
        count(roe) over (partition by analysis_peer_group, fiscal_year) as valid_peer_roe_count,
        rank() over (
            partition by analysis_peer_group, fiscal_year
            order by roe nulls last
        ) as roe_ascending_rank
    from q1_annual_company_metrics m
)
select
    r.*,
    p.peer_median_roe,
    p.peer_median_net_margin,
    p.peer_median_asset_turnover,
    p.peer_median_equity_multiplier,
    p.peer_median_operating_margin,
    p.peer_median_current_ratio,
    p.peer_median_liabilities_to_assets,
    p.peer_median_free_cash_flow_margin,
    r.roe - p.peer_median_roe as roe_vs_peer_median,
    r.net_margin - p.peer_median_net_margin as net_margin_vs_peer_median,
    r.asset_turnover - p.peer_median_asset_turnover as asset_turnover_vs_peer_median,
    r.equity_multiplier - p.peer_median_equity_multiplier as equity_multiplier_vs_peer_median,
    r.free_cash_flow_margin - p.peer_median_free_cash_flow_margin as fcf_margin_vs_peer_median,
    case
        when r.roe is not null and r.valid_peer_roe_count > 1
            then (r.roe_ascending_rank - 1.0) / (r.valid_peer_roe_count - 1.0)
        when r.roe is not null and r.valid_peer_roe_count = 1 then 0.5
    end as roe_peer_percentile
from ranked r
left join q1_peer_summary p
    using (analysis_peer_group, fiscal_year)
order by r.ticker, r.fiscal_year;

create or replace table q1_driver_persistence as
select
    d.*,
    current_peer.roe_vs_peer_median as current_peer_relative_roe,
    current_peer.roe_peer_percentile as current_peer_percentile,
    next_year.fiscal_year as next_fiscal_year,
    next_year.roe as next_year_roe,
    next_year.roe_vs_peer_median as next_year_peer_relative_roe,
    next_year.roe_peer_percentile as next_year_peer_percentile,
    next_year.roe - d.roe as next_year_roe_change,
    next_year.roe_vs_peer_median - current_peer.roe_vs_peer_median
        as next_year_peer_relative_change,
    case when next_year.roe is not null then next_year.roe < d.roe end as roe_reversal_flag,
    case when next_year.roe_peer_percentile is not null
        then next_year.roe_peer_percentile >= current_peer.roe_peer_percentile
    end as rank_retention
from q1_dupont_contributions d
left join q1_company_vs_peer current_peer
    on d.ticker = current_peer.ticker
   and d.fiscal_year = current_peer.fiscal_year
left join q1_company_vs_peer next_year
    on d.ticker = next_year.ticker
   and d.fiscal_year + 1 = next_year.fiscal_year
order by d.ticker, d.fiscal_year;
