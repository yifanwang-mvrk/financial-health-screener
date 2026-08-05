create or replace table q1_powerbi_mart as
select
    c.company_id,
    c.ticker,
    c.company_name,
    c.formal_peer_group,
    c.fiscal_year,
    c.period_end_date,
    c.status_group,
    c.formal_sample_status,
    c.data_as_of,
    c.comparability_note,
    c.roe,
    c.net_margin,
    c.asset_turnover,
    c.equity_multiplier,
    c.roe_valid_flag,
    c.dupont_valid_flag,
    c.dupont_validity_reason,
    c.dupont_identity_gap,
    c.peer_median_roe,
    c.peer_median_net_margin,
    c.peer_median_asset_turnover,
    c.peer_median_equity_multiplier,
    c.roe_vs_peer_median,
    c.net_margin_vs_peer_median,
    c.asset_turnover_vs_peer_median,
    c.equity_multiplier_vs_peer_median,
    c.roe_peer_percentile,
    c.valid_peer_roe_count,
    d.roe_change,
    d.contribution_margin,
    d.contribution_turnover,
    d.contribution_multiplier,
    d.contribution_sum,
    d.shapley_reconciliation_gap,
    d.dominant_driver,
    d.h1_driver_group,
    d.leverage_contribution_share,
    a.h1_eligible_flag,
    a.h1_exclusion_reason,
    p.next_year_peer_relative_change,
    p.next_year_roe_change,
    p.roe_reversal_flag,
    p.rank_retention,
    e.evidence_tier as h1_evidence_tier,
    e.permitted_inference as h1_permitted_inference,
    e.eligible_transition_count as h1_eligible_transition_count,
    e.eligible_unique_company_count as h1_unique_company_count,
    e.leverage_driven_transition_count as h1_leverage_transition_count,
    e.operating_driven_transition_count as h1_operating_transition_count,
    e.leverage_group_median_outcome as h1_leverage_group_median_outcome,
    e.operating_group_median_outcome as h1_operating_group_median_outcome,
    e.group_median_difference as h1_group_median_difference,
    c.metric_flag_count,
    c.unresolved_conflict_count,
    c.quality_warning_count,
    c.quality_warnings,
    c.source_selection_method,
    c.source_selection_note,
    case
        when not c.dupont_valid_flag then
            concat('DuPont unavailable: ', c.dupont_validity_reason, '.')
        when d.h1_driver_group = 'leverage_driven' then
            'The latest valid ROE improvement is leverage-driven under the frozen Shapley rule.'
        when d.h1_driver_group = 'operating_driven' then
            concat('The latest valid ROE improvement is operating-driven; dominant factor: ', d.dominant_driver, '.')
        when d.h1_driver_group = 'mixed_or_ambiguous' then
            'The latest ROE transition is not a clear positive leverage- or operating-driven improvement.'
        else
            'No valid consecutive-year ROE transition is available for driver classification.'
    end as interpretation_note,
    concat(
        e.permitted_inference,
        ' Latest-restated annual data are not point-in-time; peer benchmarks are descriptive.'
    ) as limitations_note
from q1_company_vs_peer c
left join q1_dupont_contributions d using (company_id, fiscal_year)
left join q1_driver_persistence p using (company_id, fiscal_year)
left join q1_h1_sample_audit a using (company_id, fiscal_year)
cross join q1_h1_evidence_summary e
order by c.company_id, c.fiscal_year;
