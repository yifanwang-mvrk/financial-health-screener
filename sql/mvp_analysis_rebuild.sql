select
    ticker,
    fiscal_year,
    revenue,
    operating_income,
    net_income,
    operating_income / nullif(revenue, 0) as operating_margin,
    net_income / nullif(revenue, 0) as net_margin
from financial_statements
order by ticker, fiscal_year;
