create or replace table financial_metrics as
with typed as (
    select
        ticker,
        fiscal_year::integer as fiscal_year,
        period_end_date,
        currency,
        revenue::double as revenue,
        gross_profit::double as gross_profit,
        operating_income::double as operating_income,
        net_income::double as net_income,
        total_assets::double as total_assets,
        total_liabilities::double as total_liabilities,
        total_equity::double as total_equity,
        current_assets::double as current_assets,
        current_liabilities::double as current_liabilities,
        cash_and_equivalents::double as cash_and_equivalents,
        inventory::double as inventory,
        long_term_debt::double as long_term_debt,
        operating_cash_flow::double as operating_cash_flow,
        capital_expenditure::double as capital_expenditure,
        free_cash_flow::double as free_cash_flow,
        shares_outstanding::double as shares_outstanding
    from financial_statements
),
metrics as (
    select
        *,
        operating_income / nullif(revenue, 0) as operating_margin,
        net_income / nullif(revenue, 0) as net_margin,
        current_assets / nullif(current_liabilities, 0) as current_ratio,
        cash_and_equivalents / nullif(current_liabilities, 0) as cash_ratio,
        total_liabilities / nullif(total_assets, 0) as liabilities_to_assets,
        operating_cash_flow / nullif(revenue, 0) as operating_cash_flow_margin,
        free_cash_flow / nullif(revenue, 0) as free_cash_flow_margin
    from typed
)
select
    *,
    revenue / nullif(lag(revenue) over (partition by ticker order by fiscal_year), 0) - 1 as revenue_growth,
    operating_margin - lag(operating_margin) over (partition by ticker order by fiscal_year) as operating_margin_change,
    free_cash_flow_margin - lag(free_cash_flow_margin) over (partition by ticker order by fiscal_year) as free_cash_flow_margin_change,
    liabilities_to_assets - lag(liabilities_to_assets) over (partition by ticker order by fiscal_year) as liabilities_to_assets_change
from metrics;

create or replace table risk_signals as
select
    *,
    coalesce(revenue_growth < 0, false) as signal_revenue_decline,
    operating_income < 0 as signal_negative_operating_income,
    coalesce(operating_margin_change < -0.03, false) as signal_operating_margin_deterioration,
    free_cash_flow < 0 as signal_negative_free_cash_flow,
    coalesce(free_cash_flow_margin_change < -0.05, false) as signal_free_cash_flow_deterioration,
    current_ratio < 1 as signal_current_ratio_below_1,
    total_equity < 0 as signal_negative_equity,
    coalesce(liabilities_to_assets_change > 0.05, false) as signal_rising_liabilities_to_assets
from financial_metrics;

create or replace table risk_ranking as
with scored as (
    select
        ticker,
        fiscal_year,
        revenue,
        operating_margin,
        net_margin,
        current_ratio,
        cash_ratio,
        liabilities_to_assets,
        operating_cash_flow_margin,
        free_cash_flow_margin,
        revenue_growth,
        operating_margin_change,
        free_cash_flow_margin_change,
        liabilities_to_assets_change,
        signal_revenue_decline::integer
            + signal_negative_operating_income::integer
            + signal_operating_margin_deterioration::integer
            + signal_negative_free_cash_flow::integer
            + signal_free_cash_flow_deterioration::integer
            + signal_current_ratio_below_1::integer
            + signal_negative_equity::integer
            + signal_rising_liabilities_to_assets::integer as risk_score,
        concat_ws(
            '; ',
            case when signal_revenue_decline then 'Revenue decline' end,
            case when signal_negative_operating_income then 'Negative operating income' end,
            case when signal_operating_margin_deterioration then 'Operating margin deterioration' end,
            case when signal_negative_free_cash_flow then 'Negative free cash flow' end,
            case when signal_free_cash_flow_deterioration then 'Free cash flow deterioration' end,
            case when signal_current_ratio_below_1 then 'Current ratio below 1' end,
            case when signal_negative_equity then 'Negative equity' end,
            case when signal_rising_liabilities_to_assets then 'Rising liabilities-to-assets' end
        ) as triggered_signals
    from risk_signals
)
select
    *,
    case
        when risk_score >= 4 then 'High'
        when risk_score >= 2 then 'Medium'
        else 'Low'
    end as risk_tier,
    rank() over (partition by fiscal_year order by risk_score desc, ticker) as risk_rank
from scored;
