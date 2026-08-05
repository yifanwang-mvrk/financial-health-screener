create or replace table q1_latest_restated as
with eligible as (
    select
        f.*,
        try_cast(f.filing_date as date) as filing_date_parsed,
        row_number() over (
            partition by f.company_id, f.fiscal_year, f.canonical_field
            order by
                try_cast(f.filing_date as date) desc,
                f.source_priority asc,
                f.accession_number desc
        ) as selection_rank
    from financial_facts f
    inner join q1_formal_company_dim d using (company_id)
    where f.fiscal_year between d.frozen_window_start - 1 and d.frozen_window_end
      and try_cast(f.filing_date as date) <= current_date
),
winners as (
    select
        company_id,
        ticker,
        accession_number,
        form,
        filing_date,
        period_start,
        period_end,
        fiscal_year,
        fiscal_period,
        duration_days,
        canonical_field,
        taxonomy,
        source_tag,
        value_raw,
        value_standardized,
        unit,
        flow_or_stock,
        source_priority,
        source_url,
        loaded_at,
        cik,
        source_unit,
        reported_fiscal_year,
        frame,
        true as is_latest_restated,
        'latest_valid_restated_sec_companyfacts'::varchar as source_selection_method,
        concat(
            'Latest valid filing available as of ', cast(current_date as varchar),
            '; configured source-tag priority breaks valid same-filing ties.'
        ) as source_selection_note
    from eligible
    where selection_rank = 1
),
free_cash_flow as (
    select
        ocf.company_id,
        ocf.ticker,
        ocf.accession_number,
        ocf.form,
        ocf.filing_date,
        ocf.period_start,
        ocf.period_end,
        ocf.fiscal_year,
        ocf.fiscal_period,
        ocf.duration_days,
        'free_cash_flow'::varchar as canonical_field,
        'project'::varchar as taxonomy,
        'derived:OperatingCashFlow-CapitalExpenditure'::varchar as source_tag,
        null::double as value_raw,
        ocf.value_standardized - capex.value_standardized as value_standardized,
        'USD'::varchar as unit,
        'flow'::varchar as flow_or_stock,
        0::bigint as source_priority,
        ocf.source_url,
        greatest(ocf.loaded_at, capex.loaded_at) as loaded_at,
        ocf.cik,
        'USD'::varchar as source_unit,
        ocf.reported_fiscal_year,
        ocf.frame,
        true as is_latest_restated,
        'derived_from_latest_valid_components'::varchar as source_selection_method,
        'Operating cash flow minus positive CapEx outflow.'::varchar as source_selection_note
    from winners ocf
    inner join winners capex
        on ocf.company_id = capex.company_id
       and ocf.fiscal_year = capex.fiscal_year
       and capex.canonical_field = 'capital_expenditure'
    where ocf.canonical_field = 'operating_cash_flow'
)
select * from winners
union all
select * from free_cash_flow
order by ticker, fiscal_year, canonical_field;
