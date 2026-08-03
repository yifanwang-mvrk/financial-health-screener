from pathlib import Path
import duckdb
import pandas as pd


RAW_PATH = Path("data/raw/financial_statements_raw.csv")
NORMALIZED_PATH = Path("data/normalized/financial_statements_normalized.csv")
DB_PATH = Path("db/financial_health_screener.duckdb")
SQL_PATH = Path("sql/financial_health_screener_mvp.sql")
METRICS_PATH = Path("data/processed/financial_metrics.csv")
RANKING_PATH = Path("data/processed/risk_ranking.csv")

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


def validate_accounting_relationships(df: pd.DataFrame) -> None:
    balance_diff = (
        df["total_assets"] - df["total_liabilities"] - df["total_equity"]
    ).abs()
    balance_tolerance = df["total_assets"].abs().mul(0.005).clip(lower=1.0)
    bad_balance = df[balance_diff > balance_tolerance]
    if not bad_balance.empty:
        raise ValueError(
            "Assets must approximately equal liabilities plus equity for all rows: "
            f"{bad_balance[['ticker', 'fiscal_year']].to_dict('records')}"
        )

    fcf_diff = (
        df["free_cash_flow"] - (df["operating_cash_flow"] - df["capital_expenditure"])
    ).abs()
    bad_fcf = df[fcf_diff > 0.01]
    if not bad_fcf.empty:
        raise ValueError(
            "Free cash flow must equal operating cash flow minus capital expenditure: "
            f"{bad_fcf[['ticker', 'fiscal_year']].to_dict('records')}"
        )


def main() -> None:
    df = pd.read_csv(RAW_PATH, keep_default_na=False)
    df = df.sort_values(["ticker", "fiscal_year"]).reset_index(drop=True)

    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    validate_accounting_relationships(df)

    NORMALIZED_PATH.parent.mkdir(parents=True, exist_ok=True)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(NORMALIZED_PATH, index=False)

    with duckdb.connect(str(DB_PATH)) as con:
        con.register("normalized_df", df)
        con.execute("create or replace table financial_statements as select * from normalized_df")
        con.execute(SQL_PATH.read_text())
        con.execute(f"copy financial_metrics to '{METRICS_PATH}' (header, delimiter ',')")
        con.execute(f"copy risk_ranking to '{RANKING_PATH}' (header, delimiter ',')")

    latest_year = int(df["fiscal_year"].max())
    ranking = pd.read_csv(RANKING_PATH)
    latest = ranking[ranking["fiscal_year"] == latest_year].sort_values(
        ["risk_rank", "ticker"]
    )

    print("MVP pipeline complete.")
    print(f"Rows loaded: {len(df)}")
    print(f"Normalized CSV: {NORMALIZED_PATH}")
    print(f"DuckDB database: {DB_PATH}")
    print(f"Metrics output: {METRICS_PATH}")
    print(f"Risk ranking output: {RANKING_PATH}")
    print("\nLatest-year risk ranking:")
    print(latest[["risk_rank", "ticker", "risk_tier", "risk_score", "triggered_signals"]])


if __name__ == "__main__":
    main()
