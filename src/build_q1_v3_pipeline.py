from __future__ import annotations

import json
from pathlib import Path

import duckdb
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data/raw/financial_statements_raw.csv"
COMPANY_MASTER_PATH = ROOT / "data/raw/sample_companies_master.csv"
SCOPE_PATH = ROOT / "data/reference/q1_analysis_scope.csv"
CONCEPT_MAP_PATH = ROOT / "data/reference/concept_map.csv"
CONFLICTS_PATH = ROOT / "data/reference/concept_conflicts.csv"
NORMALIZED_PATH = ROOT / "data/normalized/financial_statements_q1_normalized.csv"
DB_PATH = ROOT / "db/financial_health_screener.duckdb"
PROCESSED_DIR = ROOT / "data/processed"

SQL_FILES = [
    ROOT / "sql/01_core_tables.sql",
    ROOT / "sql/02_q1_latest_restated.sql",
    ROOT / "sql/03_q1_metrics.sql",
    ROOT / "sql/04_q1_shapley_contributions.sql",
    ROOT / "sql/05_q1_persistence.sql",
    ROOT / "sql/06_q1_h1_sample_audit.sql",
    ROOT / "sql/07_q1_powerbi_mart.sql",
]

TABLE_EXPORTS = [
    "q1_latest_restated",
    "q1_annual_company_metrics",
    "q1_dupont_contributions",
    "q1_driver_persistence",
    "q1_h1_sample_audit",
    "q1_h1_exclusion_waterfall",
    "q1_h1_evidence_summary",
    "q1_peer_summary",
    "q1_company_vs_peer",
    "q1_powerbi_mart",
]
EXPORT_ORDER = {
    "q1_latest_restated": "ticker, fiscal_year",
    "q1_annual_company_metrics": "ticker, fiscal_year",
    "q1_dupont_contributions": "ticker, fiscal_year",
    "q1_driver_persistence": "ticker, fiscal_year",
    "q1_h1_sample_audit": "ticker, fiscal_year",
    "q1_h1_exclusion_waterfall": "transition_count desc, h1_sample_status",
    "q1_peer_summary": "analysis_peer_group, fiscal_year",
    "q1_company_vs_peer": "ticker, fiscal_year",
    "q1_powerbi_mart": "ticker, fiscal_year",
}

NUMERIC_COLUMNS = [
    "revenue",
    "gross_profit",
    "operating_income",
    "net_income",
    "total_assets",
    "total_liabilities",
    "total_equity",
    "current_assets",
    "current_liabilities",
    "cash_and_equivalents",
    "inventory",
    "long_term_debt",
    "operating_cash_flow",
    "capital_expenditure",
    "free_cash_flow",
    "shares_outstanding",
]


def load_inputs() -> tuple[pd.DataFrame, ...]:
    financials = pd.read_csv(RAW_PATH, keep_default_na=False)
    company_master = pd.read_csv(COMPANY_MASTER_PATH, keep_default_na=False)
    scope = pd.read_csv(SCOPE_PATH, keep_default_na=False)
    concept_map = pd.read_csv(CONCEPT_MAP_PATH, keep_default_na=False)
    conflicts = pd.read_csv(CONFLICTS_PATH, dtype=str, keep_default_na=False)

    financials["fiscal_year"] = pd.to_numeric(
        financials["fiscal_year"], errors="raise"
    ).astype(int)
    financials["period_end_date"] = pd.to_datetime(
        financials["period_end_date"], errors="raise"
    ).dt.date
    for column in NUMERIC_COLUMNS:
        financials[column] = pd.to_numeric(financials[column], errors="coerce")

    return financials, company_master, scope, concept_map, conflicts


def validate_inputs(financials: pd.DataFrame, scope: pd.DataFrame) -> None:
    included_tickers = set(scope.loc[scope["scope_status"] == "included", "ticker"])
    observed_tickers = set(financials["ticker"])
    missing_tickers = sorted(included_tickers - observed_tickers)
    unexpected_tickers = sorted(observed_tickers - included_tickers)
    if missing_tickers or unexpected_tickers:
        raise ValueError(
            "Q1 scope and financial statement tickers differ: "
            f"missing={missing_tickers}, unexpected={unexpected_tickers}"
        )

    duplicates = financials.duplicated(["ticker", "fiscal_year"], keep=False)
    if duplicates.any():
        rows = financials.loc[duplicates, ["ticker", "fiscal_year"]]
        raise ValueError(f"Duplicate company-year rows found: {rows.to_dict('records')}")

    required = [
        "revenue",
        "operating_income",
        "net_income",
        "total_assets",
        "total_liabilities",
        "total_equity",
        "operating_cash_flow",
        "capital_expenditure",
        "free_cash_flow",
    ]
    missing_required = financials[required].isna()
    if missing_required.any().any():
        bad = financials.loc[
            missing_required.any(axis=1), ["ticker", "fiscal_year"]
        ]
        raise ValueError(f"Required Q1 values are missing: {bad.to_dict('records')}")

    fcf_gap = (
        financials["free_cash_flow"]
        - (financials["operating_cash_flow"] - financials["capital_expenditure"])
    ).abs()
    if (fcf_gap > 0.01).any():
        bad = financials.loc[fcf_gap > 0.01, ["ticker", "fiscal_year"]]
        raise ValueError(f"Free cash flow reconciliation failed: {bad.to_dict('records')}")

    balance_gap = (
        financials["total_assets"]
        - financials["total_liabilities"]
        - financials["total_equity"]
    ).abs()
    balance_tolerance = financials["total_assets"].abs().mul(0.005).clip(lower=1.0)
    if (balance_gap > balance_tolerance).any():
        bad = financials.loc[balance_gap > balance_tolerance, ["ticker", "fiscal_year"]]
        raise ValueError(f"Balance-sheet reconciliation failed: {bad.to_dict('records')}")


def execute_sql_pipeline(
    financials: pd.DataFrame,
    company_master: pd.DataFrame,
    scope: pd.DataFrame,
    concept_map: pd.DataFrame,
    conflicts: pd.DataFrame,
) -> dict[str, object]:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    NORMALIZED_PATH.parent.mkdir(parents=True, exist_ok=True)

    financials.sort_values(["ticker", "fiscal_year"]).to_csv(
        NORMALIZED_PATH, index=False
    )

    with duckdb.connect(str(DB_PATH)) as connection:
        connection.register("financial_statements_input", financials)
        connection.register("company_master_input", company_master)
        connection.register("q1_scope_input", scope)
        connection.register("concept_map_input", concept_map)
        connection.register("concept_conflicts_input", conflicts)

        for sql_path in SQL_FILES:
            connection.execute(sql_path.read_text(encoding="utf-8"))

        table_counts: dict[str, int] = {}
        for table_name in TABLE_EXPORTS:
            output_path = PROCESSED_DIR / f"{table_name}.csv"
            order_clause = (
                f" order by {EXPORT_ORDER[table_name]}"
                if table_name in EXPORT_ORDER
                else ""
            )
            output = connection.execute(
                f"select * from {table_name}{order_clause}"
            ).fetchdf()
            output.to_csv(output_path, index=False)
            table_counts[table_name] = len(output)

        evidence = connection.execute(
            "select * from q1_h1_evidence_summary"
        ).fetchdf().iloc[0].to_dict()
        valid_dupont_rows = connection.execute(
            "select count(*) from q1_annual_company_metrics where dupont_valid_flag"
        ).fetchone()[0]
        valid_transitions = connection.execute(
            "select count(*) from q1_dupont_contributions where transition_valid_flag"
        ).fetchone()[0]

    return {
        "data_as_of": str(financials["period_end_date"].max()),
        "source_company_count": int(financials["ticker"].nunique()),
        "source_company_year_count": int(len(financials)),
        "valid_dupont_company_year_count": int(valid_dupont_rows),
        "valid_dupont_transition_count": int(valid_transitions),
        "h1_evidence": {
            key: value.item() if hasattr(value, "item") else value
            for key, value in evidence.items()
        },
        "exported_table_rows": table_counts,
    }


def main() -> None:
    inputs = load_inputs()
    financials, _, scope, _, _ = inputs
    validate_inputs(financials, scope)
    summary = execute_sql_pipeline(*inputs)

    summary_path = PROCESSED_DIR / "q1_release_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=True), encoding="utf-8"
    )

    evidence = summary["h1_evidence"]
    print("Q1 v3 analytical pipeline complete.")
    print(f"Rows loaded: {summary['source_company_year_count']}")
    print(f"Valid DuPont company-years: {summary['valid_dupont_company_year_count']}")
    print(f"Valid DuPont transitions: {summary['valid_dupont_transition_count']}")
    print(f"H1 Evidence Tier: {evidence['evidence_tier']}")
    print(f"H1 permitted inference: {evidence['permitted_inference']}")
    print(f"Power BI mart: {PROCESSED_DIR / 'q1_powerbi_mart.csv'}")
    print(f"Release summary: {summary_path}")


if __name__ == "__main__":
    main()
