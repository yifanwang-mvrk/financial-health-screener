with grain_counts as (
    select
        company_id,
        fiscal_year,
        canonical_field,
        count(*) as row_count
    from {{ ref('int_q1_latest_restated') }}
    group by all
)

select *
from grain_counts
where company_id is null
   or fiscal_year is null
   or canonical_field is null
   or row_count <> 1
