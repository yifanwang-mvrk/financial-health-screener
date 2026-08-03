create or replace table financial_statements as
select
    trim(ticker)::varchar as ticker,
    fiscal_year::integer as fiscal_year,
    period_end_date::date as period_end_date,
    trim(currency)::varchar as currency,
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
    shares_outstanding::double as shares_outstanding,
    source::varchar as source,
    source_url::varchar as source_url,
    notes::varchar as notes
from financial_statements_input;

create or replace table company_master as
select * from company_master_input;

create or replace table q1_analysis_scope as
select * from q1_scope_input;

create or replace table concept_map as
select * from concept_map_input;

create or replace table concept_conflicts as
select * from concept_conflicts_input;

create or replace table q1_core_financials as
select
    f.*,
    m.company_name,
    m.primary_business_model,
    m.peer_group as detailed_peer_group,
    s.analysis_peer_group,
    s.comparability_note,
    count(*) over (partition by f.ticker, f.fiscal_year) as ticker_year_version_count
from financial_statements f
inner join q1_analysis_scope s
    on f.ticker = s.ticker
   and s.scope_status = 'included'
left join company_master m
    on f.ticker = m.ticker;
