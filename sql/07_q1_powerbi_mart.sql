create or replace table q1_powerbi_mart as
select
    c.ticker,
    c.company_name,
    c.fiscal_year,
    c.period_end_date,
    c.analysis_peer_group,
    c.primary_business_model,
    c.revenue,
    c.net_income,
    c.average_assets,
    c.average_equity,
    c.roe,
    c.roa,
    c.net_margin,
    c.operating_margin,
    c.gross_margin,
    c.asset_turnover,
    c.equity_multiplier,
    c.current_ratio,
    c.quick_ratio,
    c.cash_ratio,
    c.liabilities_to_assets,
    c.long_term_debt_to_assets,
    c.operating_cash_flow_margin,
    c.free_cash_flow_margin,
    c.capital_expenditure_intensity,
    c.free_cash_flow_conversion,
    c.revenue_growth,
    c.roe_valid_flag,
    c.dupont_valid_flag,
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
    d.roe_change,
    d.contribution_margin,
    d.contribution_turnover,
    d.contribution_multiplier,
    d.dominant_change_driver,
    d.h1_driver_group,
    d.leverage_contribution_share,
    p.next_year_roe_change,
    p.next_year_peer_relative_change,
    p.roe_reversal_flag,
    p.rank_retention,
    a.h1_eligible_flag,
    a.h1_sample_status,
    c.near_zero_average_equity_flag,
    c.one_off_net_income_warning_flag,
    c.structural_break_flag,
    c.cash_scope_warning_flag,
    c.quality_warning_count,
    c.quality_warnings,
    c.comparability_note,
    e.evidence_tier as h1_evidence_tier,
    e.permitted_inference as h1_permitted_inference,
    c.source_selection_method,
    c.source_selection_note
from q1_company_vs_peer c
left join q1_dupont_contributions d
    on c.ticker = d.ticker
   and c.fiscal_year = d.fiscal_year
left join q1_driver_persistence p
    on c.ticker = p.ticker
   and c.fiscal_year = p.fiscal_year
left join q1_h1_sample_audit a
    on c.ticker = a.ticker
   and c.fiscal_year = a.fiscal_year
cross join q1_h1_evidence_summary e
order by c.ticker, c.fiscal_year;
