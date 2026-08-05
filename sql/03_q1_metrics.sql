create or replace table q1_annual_company_metrics as
with annual_wide as (
    select
        company_id,
        ticker,
        fiscal_year,
        max(try_cast(period_end as date)) as period_end_date,
        max(value_standardized) filter (where canonical_field = 'revenue') as revenue,
        max(value_standardized) filter (where canonical_field = 'operating_income') as operating_income,
        max(value_standardized) filter (where canonical_field = 'net_income') as net_income,
        max(value_standardized) filter (where canonical_field = 'total_assets') as total_assets,
        max(value_standardized) filter (where canonical_field = 'total_liabilities') as total_liabilities,
        max(value_standardized) filter (where canonical_field = 'total_equity') as total_equity,
        max(value_standardized) filter (where canonical_field = 'current_assets') as current_assets,
        max(value_standardized) filter (where canonical_field = 'current_liabilities') as current_liabilities,
        max(value_standardized) filter (where canonical_field = 'cash_and_equivalents') as cash_and_equivalents,
        max(value_standardized) filter (where canonical_field = 'inventory') as inventory,
        max(value_standardized) filter (where canonical_field = 'total_debt') as total_debt,
        max(value_standardized) filter (where canonical_field = 'operating_cash_flow') as operating_cash_flow,
        max(value_standardized) filter (where canonical_field = 'capital_expenditure') as capital_expenditure,
        max(value_standardized) filter (where canonical_field = 'free_cash_flow') as free_cash_flow,
        max(try_cast(substr(loaded_at, 1, 10) as date)) as row_data_as_of
    from q1_latest_restated
    group by company_id, ticker, fiscal_year
),
balances as (
    select
        *,
        lag(fiscal_year) over (partition by company_id order by fiscal_year) as prior_fiscal_year,
        lag(total_assets) over (partition by company_id order by fiscal_year) as prior_total_assets,
        lag(total_equity) over (partition by company_id order by fiscal_year) as prior_total_equity,
        lag(revenue) over (partition by company_id order by fiscal_year) as prior_revenue
    from annual_wide
),
formal_rows as (
    select b.*
    from balances b
    inner join q1_formal_years y using (company_id, fiscal_year)
),
base_metrics as (
    select
        f.*,
        d.company_name,
        d.formal_peer_group,
        d.status_group,
        d.formal_sample_status,
        d.comparability_note,
        max(f.row_data_as_of) over () as data_as_of,
        case when f.prior_fiscal_year = f.fiscal_year - 1
            then (f.total_assets + f.prior_total_assets) / 2.0
        end as average_assets,
        case when f.prior_fiscal_year = f.fiscal_year - 1
            then (f.total_equity + f.prior_total_equity) / 2.0
        end as average_equity,
        f.net_income / nullif(f.revenue, 0) as net_margin,
        f.operating_income / nullif(f.revenue, 0) as operating_margin,
        f.current_assets / nullif(f.current_liabilities, 0) as current_ratio,
        case when f.inventory is not null
            then (f.current_assets - f.inventory) / nullif(f.current_liabilities, 0)
        end as quick_ratio,
        f.cash_and_equivalents / nullif(f.current_liabilities, 0) as cash_ratio,
        f.total_liabilities / nullif(f.total_assets, 0) as liabilities_to_assets,
        f.total_debt / nullif(f.total_assets, 0) as total_debt_to_assets,
        f.operating_cash_flow / nullif(f.revenue, 0) as operating_cash_flow_margin,
        f.free_cash_flow / nullif(f.revenue, 0) as free_cash_flow_margin,
        f.capital_expenditure / nullif(f.revenue, 0) as capital_expenditure_intensity,
        f.free_cash_flow / nullif(f.operating_cash_flow, 0) as free_cash_flow_conversion,
        case when f.prior_fiscal_year = f.fiscal_year - 1
            then f.revenue / nullif(f.prior_revenue, 0) - 1
        end as revenue_growth,
        f.prior_fiscal_year = f.fiscal_year - 1
            and f.prior_total_assets is not null
            and f.prior_total_equity is not null as average_balance_available_flag
    from formal_rows f
    inner join q1_formal_company_dim d using (company_id)
),
dupont as (
    select
        *,
        revenue / nullif(average_assets, 0) as asset_turnover,
        case when average_equity > 0 then average_assets / average_equity end
            as equity_multiplier,
        case when average_equity > 0 then net_income / average_equity end as roe,
        net_income / nullif(average_assets, 0) as roa,
        average_equity > 0 as positive_average_equity_flag
    from base_metrics
),
validated as (
    select
        *,
        net_margin * asset_turnover * equity_multiplier as dupont_roe,
        average_balance_available_flag
            and positive_average_equity_flag
            and revenue is not null and revenue <> 0
            and average_assets is not null and average_assets <> 0
            and net_margin is not null
            and asset_turnover is not null
            and equity_multiplier is not null as dupont_valid_flag,
        average_balance_available_flag
            and positive_average_equity_flag
            and net_income is not null as roe_valid_flag,
        coalesce(abs(average_equity) / nullif(abs(average_assets), 0) < 0.02, false)
            as near_zero_average_equity_flag
    from dupont
)
select
    v.*,
    case when v.dupont_valid_flag then v.roe - v.dupont_roe end
        as dupont_identity_gap,
    case
        when not v.average_balance_available_flag then 'missing_prior_balance'
        when not v.positive_average_equity_flag then 'nonpositive_average_equity'
        when v.revenue is null or v.revenue = 0 then 'invalid_revenue'
        when v.average_assets is null or v.average_assets = 0 then 'invalid_average_assets'
        when v.dupont_valid_flag then 'valid'
        else 'missing_component'
    end as dupont_validity_reason,
    coalesce(fs.metric_flag_count, 0) as metric_flag_count,
    coalesce(cs.unresolved_conflict_count, 0) as unresolved_conflict_count,
    coalesce(fs.metric_flag_count, 0)
        + case when v.near_zero_average_equity_flag then 1 else 0 end
        as quality_warning_count,
    concat_ws(
        '; ',
        nullif(fs.metric_flag_warnings, ''),
        case when v.near_zero_average_equity_flag
            then 'Near-zero average equity; ROE is mechanically unstable' end
    ) as quality_warnings,
    'latest_valid_restated_sec_companyfacts'::varchar as source_selection_method,
    concat(
        'Latest valid filing through ', cast(v.data_as_of as varchar),
        '; filing date, source priority, and accession provide deterministic selection.'
    ) as source_selection_note
from validated v
left join q1_metric_flag_summary fs using (company_id, fiscal_year)
left join q1_conflict_summary cs using (company_id, fiscal_year)
order by v.company_id, v.fiscal_year;
