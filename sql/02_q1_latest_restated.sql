create or replace table q1_latest_restated as
select
    *,
    true as is_latest_restated,
    'manual_verified_latest_comparative_filing'::varchar as source_selection_method,
    case
        when ticker = 'CHWY' then 'Latest restated comparative series documented in source mapping'
        else 'Single manually verified company-year version in the current source dataset'
    end as source_selection_note
from q1_core_financials
qualify row_number() over (
    partition by ticker, fiscal_year
    order by period_end_date desc, source_url desc
) = 1;
