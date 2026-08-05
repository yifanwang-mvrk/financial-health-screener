create or replace table q1_h1_sample_audit as
with audited as (
    select
        p.*,
        n.average_equity as next_average_equity,
        coalesce(p.prior_roe <= 0 and p.roe_change > 0, false)
            as turnaround_from_loss,
        p.transition_valid_flag
            and p.prior_average_equity > 0
            and p.average_equity > 0
            and n.average_equity > 0
            and p.prior_roe > 0
            and p.roe_change > 0
            and p.next_year_roe is not null
            and p.h1_driver_group in ('leverage_driven', 'operating_driven')
            as h1_eligible_flag
    from q1_driver_persistence p
    left join q1_annual_company_metrics n
        on p.company_id = n.company_id
       and p.fiscal_year + 1 = n.fiscal_year
),
statused as (
    select
        *,
        case
            when not transition_valid_flag then 'invalid_dupont_transition'
            when prior_average_equity is null or prior_average_equity <= 0
                then 'nonpositive_prior_average_equity'
            when average_equity is null or average_equity <= 0
                then 'nonpositive_current_average_equity'
            when prior_roe is null or prior_roe <= 0 then
                case when turnaround_from_loss
                    then 'turnaround_from_loss' else 'nonpositive_prior_roe' end
            when roe_change is null or roe_change <= 0 then 'no_roe_improvement'
            when h1_driver_group = 'mixed_or_ambiguous'
                then 'mixed_or_ambiguous_driver'
            when next_fiscal_year is null or next_year_roe is null
                then 'next_year_not_observable'
            when next_average_equity is null or next_average_equity <= 0
                then 'nonpositive_next_average_equity'
            when h1_eligible_flag then 'eligible'
            else 'other_exclusion'
        end as h1_exclusion_reason
    from audited
),
eligible_total as (
    select count(*) as eligible_transition_count
    from statused
    where h1_eligible_flag
),
company_counts as (
    select company_id, count(*) as company_eligible_transition_count
    from statused
    where h1_eligible_flag
    group by company_id
),
year_counts as (
    select fiscal_year, count(*) as fiscal_year_eligible_transition_count
    from statused
    where h1_eligible_flag
    group by fiscal_year
),
driver_year_counts as (
    select
        fiscal_year,
        h1_driver_group,
        count(*) as driver_year_eligible_transition_count
    from statused
    where h1_eligible_flag
    group by fiscal_year, h1_driver_group
)
select
    s.*,
    coalesce(c.company_eligible_transition_count, 0)
        as company_eligible_transition_count,
    coalesce(c.company_eligible_transition_count, 0)
        / nullif(t.eligible_transition_count, 0)::double as company_transition_share,
    coalesce(y.fiscal_year_eligible_transition_count, 0)
        as fiscal_year_eligible_transition_count,
    coalesce(y.fiscal_year_eligible_transition_count, 0)
        / nullif(t.eligible_transition_count, 0)::double as fiscal_year_transition_share,
    coalesce(d.driver_year_eligible_transition_count, 0)
        as driver_year_eligible_transition_count
from statused s
cross join eligible_total t
left join company_counts c using (company_id)
left join year_counts y using (fiscal_year)
left join driver_year_counts d using (fiscal_year, h1_driver_group)
order by s.company_id, s.fiscal_year;

create or replace table q1_h1_exclusion_waterfall as
select
    h1_exclusion_reason,
    count(*) as transition_count,
    count(distinct company_id) as unique_company_count
from q1_h1_sample_audit
group by h1_exclusion_reason
order by transition_count desc, h1_exclusion_reason;

create or replace table q1_h1_evidence_summary as
with eligible as (
    select * from q1_h1_sample_audit where h1_eligible_flag
),
counts as (
    select
        count(*) as eligible_transition_count,
        count(distinct company_id) as eligible_unique_company_count,
        count(*) filter (where h1_driver_group = 'leverage_driven')
            as leverage_driven_transition_count,
        count(*) filter (where h1_driver_group = 'operating_driven')
            as operating_driven_transition_count,
        count(distinct company_id) filter (where h1_driver_group = 'leverage_driven')
            as leverage_driven_unique_company_count,
        count(distinct company_id) filter (where h1_driver_group = 'operating_driven')
            as operating_driven_unique_company_count,
        max(company_transition_share) as maximum_company_transition_share,
        max(fiscal_year_transition_share) as maximum_fiscal_year_transition_share,
        count(*) filter (where fiscal_year in (2020, 2021))
            / nullif(count(*), 0)::double as fy2020_2021_transition_share,
        median(next_year_peer_relative_change)
            filter (where h1_driver_group = 'leverage_driven')
            as leverage_group_median_outcome,
        median(next_year_peer_relative_change)
            filter (where h1_driver_group = 'operating_driven')
            as operating_group_median_outcome,
        avg(case when roe_reversal_flag then 1.0 else 0.0 end)
            filter (where h1_driver_group = 'leverage_driven')
            as leverage_group_reversal_rate,
        avg(case when roe_reversal_flag then 1.0 else 0.0 end)
            filter (where h1_driver_group = 'operating_driven')
            as operating_group_reversal_rate
    from eligible
),
tiered as (
    select
        *,
        leverage_group_median_outcome - operating_group_median_outcome
            as group_median_difference,
        coalesce(maximum_company_transition_share, 0) > 0.20
            as over_concentration_flag,
        case
            when eligible_unique_company_count >= 15
             and eligible_transition_count >= 40
             and leverage_driven_unique_company_count >= 8
             and operating_driven_unique_company_count >= 8
             and coalesce(maximum_company_transition_share, 0) <= 0.20 then 'A'
            when eligible_unique_company_count < 8
              or eligible_transition_count < 20 then 'C'
            else 'B'
        end as evidence_tier
    from counts
)
select
    *,
    case evidence_tier
        when 'A' then
            'Exploratory company-clustered group comparison permitted; no causal claim.'
        when 'B' then
            'Descriptive persistence patterns only; emphasize company concentration and year imbalance.'
        else
            'Evidence insufficient for group testing; illustrative cases only.'
    end as permitted_inference
from tiered;
