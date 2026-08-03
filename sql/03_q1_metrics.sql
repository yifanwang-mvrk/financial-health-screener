create or replace table q1_annual_company_metrics as
with balances as (
    select
        *,
        lag(fiscal_year) over (partition by ticker order by fiscal_year) as prior_fiscal_year,
        lag(total_assets) over (partition by ticker order by fiscal_year) as prior_total_assets,
        lag(total_equity) over (partition by ticker order by fiscal_year) as prior_total_equity,
        lag(revenue) over (partition by ticker order by fiscal_year) as prior_revenue,
        lag(net_income) over (partition by ticker order by fiscal_year) as prior_net_income
    from q1_latest_restated
),
base_metrics as (
    select
        *,
        case when prior_fiscal_year = fiscal_year - 1
            then (total_assets + prior_total_assets) / 2.0
        end as average_assets,
        case when prior_fiscal_year = fiscal_year - 1
            then (total_equity + prior_total_equity) / 2.0
        end as average_equity,
        net_income / nullif(revenue, 0) as net_margin,
        operating_income / nullif(revenue, 0) as operating_margin,
        gross_profit / nullif(revenue, 0) as gross_margin,
        current_assets / nullif(current_liabilities, 0) as current_ratio,
        case
            when inventory is not null
                then (current_assets - inventory) / nullif(current_liabilities, 0)
        end as quick_ratio,
        cash_and_equivalents / nullif(current_liabilities, 0) as cash_ratio,
        total_liabilities / nullif(total_assets, 0) as liabilities_to_assets,
        long_term_debt / nullif(total_assets, 0) as long_term_debt_to_assets,
        operating_cash_flow / nullif(revenue, 0) as operating_cash_flow_margin,
        free_cash_flow / nullif(revenue, 0) as free_cash_flow_margin,
        capital_expenditure / nullif(revenue, 0) as capital_expenditure_intensity,
        free_cash_flow / nullif(operating_cash_flow, 0) as free_cash_flow_conversion,
        revenue / nullif(prior_revenue, 0) - 1 as revenue_growth,
        net_income / nullif(prior_net_income, 0) - 1 as net_income_growth
    from balances
),
dupont as (
    select
        *,
        revenue / nullif(average_assets, 0) as asset_turnover,
        case when average_equity > 0 then average_assets / average_equity end as equity_multiplier,
        case when average_equity > 0 then net_income / average_equity end as roe,
        net_income / nullif(average_assets, 0) as roa,
        prior_fiscal_year = fiscal_year - 1
            and prior_total_assets is not null
            and prior_total_equity is not null as average_balance_available_flag,
        average_equity > 0 as positive_average_equity_flag
    from base_metrics
),
quality as (
    select
        *,
        net_margin * asset_turnover * equity_multiplier as dupont_roe,
        average_balance_available_flag and positive_average_equity_flag
            and revenue is not null and revenue <> 0
            and average_assets is not null and average_assets <> 0 as dupont_valid_flag,
        average_balance_available_flag and positive_average_equity_flag as roe_valid_flag,
        coalesce(abs(average_equity) / nullif(average_assets, 0) < 0.02, false)
            as near_zero_average_equity_flag,
        ticker = 'EBAY' as one_off_net_income_warning_flag,
        ticker = 'DASH' and fiscal_year = 2022 as structural_break_flag,
        ticker in ('CHWY', 'DASH') as cash_scope_warning_flag,
        case when gross_profit is null then 1 else 0 end
            + case when inventory is null then 1 else 0 end
            + case when not average_balance_available_flag then 1 else 0 end
            + case when average_balance_available_flag and not positive_average_equity_flag then 1 else 0 end
            + case when coalesce(abs(average_equity) / nullif(average_assets, 0) < 0.02, false) then 1 else 0 end
            + case when ticker = 'EBAY' then 1 else 0 end
            + case when ticker = 'DASH' and fiscal_year = 2022 then 1 else 0 end
            + case when ticker in ('CHWY', 'DASH') then 1 else 0 end
            + case when notes ilike '%restat%' then 1 else 0 end as quality_warning_count,
        concat_ws(
            '; ',
            case when gross_profit is null then 'Gross profit unavailable' end,
            case when inventory is null then 'Inventory unavailable or not applicable' end,
            case when not average_balance_available_flag then 'Prior-year balance unavailable' end,
            case when average_balance_available_flag and not positive_average_equity_flag then 'Nonpositive average equity; ROE invalid' end,
            case when coalesce(abs(average_equity) / nullif(average_assets, 0) < 0.02, false) then 'Near-zero average equity; ROE is mechanically unstable' end,
            case when ticker = 'EBAY' then 'GAAP net income affected by one-off or non-operating items' end,
            case when ticker = 'DASH' and fiscal_year = 2022 then 'Wolt acquisition creates a structural break' end,
            case when ticker in ('CHWY', 'DASH') then 'Cash-only liquidity excludes material marketable securities' end,
            case when notes ilike '%restat%' then 'Restated comparative data' end
        ) as quality_warnings
    from dupont
)
select
    *,
    case when dupont_valid_flag then roe - dupont_roe end as dupont_identity_gap,
    case
        when not average_balance_available_flag then 'missing_prior_balance'
        when not positive_average_equity_flag then 'nonpositive_average_equity'
        when revenue is null or revenue = 0 then 'invalid_revenue'
        when average_assets is null or average_assets = 0 then 'invalid_average_assets'
        else 'valid'
    end as dupont_validity_reason
from quality
order by ticker, fiscal_year;
