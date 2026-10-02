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
from {{ source('screener_inputs', 'q1_formal_sample') }} as s
inner join {{ source('screener_inputs', 'company_universe') }} as u using (company_id)
