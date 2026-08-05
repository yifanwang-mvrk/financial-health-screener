create or replace table q1_formal_company_dim as
select
    s.sample_version,
    s.formal_sample_order,
    s.company_id,
    s.ticker,
    s.company_name,
    s.formal_peer_group,
    s.frozen_window_start,
    s.frozen_window_end,
    s.a3_available_fiscal_years,
    s.b1_pilot_member,
    s.selection_basis,
    u.status_group,
    u.classification_confidence,
    u.inventory_ownership_flag,
    u.revenue_recognition_model,
    u.fiscal_year_end,
    'formal_included'::varchar as formal_sample_status,
    case s.formal_peer_group
        when 'marketplace_platform' then
            'Marketplace revenue recognition and asset intensity differ; interpret margin and turnover together.'
        when 'inventory_led_ecommerce' then
            'Inventory ownership, fulfillment intensity, and hybrid business exposure differ within this peer group.'
        when 'dtc_brand' then
            'Channel mix, fiscal calendars, and inventory intensity differ within this peer group.'
    end as comparability_note
from q1_formal_sample s
inner join company_universe u using (company_id);

create or replace table q1_formal_years as
select
    s.company_id,
    cast(y.fiscal_year_text as integer) as fiscal_year
from q1_formal_sample s
cross join unnest(string_split(s.a3_available_fiscal_years, '|')) as y(fiscal_year_text)
where cast(y.fiscal_year_text as integer)
    between s.frozen_window_start and s.frozen_window_end;

create or replace table q1_metric_flag_summary as
select
    company_id,
    fiscal_year,
    count(*) filter (where flag_value) as metric_flag_count,
    string_agg(distinct reason, '; ' order by reason)
        filter (where flag_value) as metric_flag_warnings
from metric_flags
group by company_id, fiscal_year;

create or replace table q1_conflict_summary as
select
    company_id,
    fiscal_year,
    count(*) as conflict_count,
    count(*) filter (where resolution_status = 'requires_review')
        as unresolved_conflict_count,
    count(*) filter (where conflict_severity = 'high') as high_conflict_count
from concept_conflicts
group by company_id, fiscal_year;
