create or replace table q1_h1_sample_audit as
with audited as (
    select
        d.*,
        n.average_equity as next_average_equity,
        n.roe as next_year_roe,
        n.roe_vs_peer_median as next_year_peer_relative_roe,
        n.fiscal_year as next_fiscal_year,
        coalesce(d.prior_roe <= 0 and d.roe_change > 0, false) as turnaround_from_loss,
        d.transition_valid_flag
            and d.prior_average_equity > 0
            and d.average_equity > 0
            and n.average_equity > 0
            and d.prior_roe > 0
            and d.roe_change > 0
            and n.roe is not null
            and d.h1_driver_group in ('leverage_driven', 'operating_driven') as h1_eligible_flag
    from q1_dupont_contributions d
    left join q1_company_vs_peer n
        on d.ticker = n.ticker
       and d.fiscal_year + 1 = n.fiscal_year
)
select
    *,
    case
        when not transition_valid_flag then 'invalid_dupont_transition'
        when prior_average_equity is null or prior_average_equity <= 0 then 'nonpositive_prior_average_equity'
        when average_equity is null or average_equity <= 0 then 'nonpositive_current_average_equity'
        when prior_roe is null or prior_roe <= 0 then
            case when turnaround_from_loss then 'turnaround_from_loss' else 'nonpositive_prior_roe' end
        when roe_change is null or roe_change <= 0 then 'no_roe_improvement'
        when h1_driver_group = 'mixed_or_ambiguous' then 'mixed_or_ambiguous_driver'
        when next_fiscal_year is null or next_year_roe is null then 'next_year_not_observable'
        when next_average_equity is null or next_average_equity <= 0 then 'nonpositive_next_average_equity'
        when h1_eligible_flag then 'eligible'
        else 'other_exclusion'
    end as h1_sample_status
from audited
order by ticker, fiscal_year;

create or replace table q1_h1_exclusion_waterfall as
select
    h1_sample_status,
    count(*) as transition_count,
    count(distinct ticker) as unique_company_count
from q1_h1_sample_audit
group by h1_sample_status
order by transition_count desc, h1_sample_status;

create or replace table q1_h1_evidence_summary as
with eligible as (
    select * from q1_h1_sample_audit where h1_eligible_flag
),
company_counts as (
    select ticker, count(*) as transition_count
    from eligible
    group by ticker
),
counts as (
    select
        (select count(*) from eligible) as eligible_transition_count,
        (select count(distinct ticker) from eligible) as eligible_unique_company_count,
        (select count(distinct ticker) from eligible where h1_driver_group = 'leverage_driven')
            as leverage_driven_unique_company_count,
        (select count(distinct ticker) from eligible where h1_driver_group = 'operating_driven')
            as operating_driven_unique_company_count,
        coalesce((select max(transition_count) from company_counts), 0) as max_transitions_from_one_company
),
tiered as (
    select
        *,
        case
            when eligible_transition_count > 0
                then max_transitions_from_one_company::double / eligible_transition_count
            else 0
        end as maximum_company_transition_share
    from counts
)
select
    *,
    maximum_company_transition_share > 0.25 as over_concentration_flag,
    case
        when eligible_unique_company_count >= 15
         and eligible_transition_count >= 40
         and leverage_driven_unique_company_count >= 8
         and operating_driven_unique_company_count >= 8
         and maximum_company_transition_share <= 0.25 then 'A'
        when eligible_unique_company_count >= 8
          or eligible_transition_count >= 20 then 'B'
        else 'C'
    end as evidence_tier,
    case
        when eligible_unique_company_count >= 15
         and eligible_transition_count >= 40
         and leverage_driven_unique_company_count >= 8
         and operating_driven_unique_company_count >= 8
         and maximum_company_transition_share <= 0.25
            then 'Company-clustered bootstrap and group comparison permitted; no causal claim'
        when eligible_unique_company_count >= 8 or eligible_transition_count >= 20
            then 'Descriptive persistence comparison only; emphasize concentration and imbalance'
        else 'Evidence insufficient for group testing; illustrative cases only'
    end as permitted_inference
from tiered;
