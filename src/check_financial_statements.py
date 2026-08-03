from pathlib import Path
import sys
import pandas as pd


FINANCIAL_DATA_PATH = Path("data/raw/financial_statements_raw.csv")
COMPANY_MASTER_PATH = Path("data/raw/sample_companies_master.csv")

EXPECTED_COLUMNS = [
    "ticker",
    "fiscal_year",
    "period_end_date",
    "currency",
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
    "source",
    "source_url",
    "notes",
]

REQUIRED_COLUMNS = [
    "ticker",
    "fiscal_year",
    "period_end_date",
    "currency",
    "revenue",
    "net_income",
    "total_assets",
    "total_liabilities",
    "total_equity",
    "operating_cash_flow",
    "source",
]

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

YEAR_MIN = 2000
YEAR_MAX = 2030
CORE_TICKERS = ["AMZN", "EBAY", "ETSY", "CHWY", "DASH", "BKNG"]
CORE_YEARS = ["2021", "2022", "2023"]


def fail(message: str) -> None:
    print(f"❌ {message}")
    sys.exit(1)


def main() -> None:
    if not FINANCIAL_DATA_PATH.exists():
        fail(f"Financial data file not found: {FINANCIAL_DATA_PATH}")

    if not COMPANY_MASTER_PATH.exists():
        fail(f"Company master file not found: {COMPANY_MASTER_PATH}")

    financial_df = pd.read_csv(FINANCIAL_DATA_PATH, dtype=str, keep_default_na=False)
    master_df = pd.read_csv(COMPANY_MASTER_PATH, dtype=str, keep_default_na=False)

    print("=== Financial Statements Quality Check ===")
    print(f"Financial data file: {FINANCIAL_DATA_PATH}")
    print(f"Company master file: {COMPANY_MASTER_PATH}")
    print(f"Financial data shape: {financial_df.shape}")
    print(f"Company master shape: {master_df.shape}")

    if list(financial_df.columns) != EXPECTED_COLUMNS:
        print("\nExpected columns:")
        print(EXPECTED_COLUMNS)
        print("\nActual columns:")
        print(list(financial_df.columns))
        fail("Financial data column structure does not match expected schema.")

    print("\n✅ Column schema check passed.")

    # If the template has only headers and no rows, this is acceptable at A2-2.
    if financial_df.empty:
        print("⚠️ Financial data has no rows yet. This is acceptable for the current template stage.")
        print("✅ All available checks passed.")
        return

    financial_df = financial_df.map(lambda x: x.strip() if isinstance(x, str) else x)
    master_df = master_df.map(lambda x: x.strip() if isinstance(x, str) else x)

    for col in REQUIRED_COLUMNS:
        empty_count = (financial_df[col] == "").sum()
        if empty_count > 0:
            fail(f"Required column '{col}' has {empty_count} empty values.")

    print("✅ Required field check passed.")

    duplicated_rows = financial_df[
        financial_df.duplicated(subset=["ticker", "fiscal_year"], keep=False)
    ]

    if not duplicated_rows.empty:
        print(duplicated_rows[["ticker", "fiscal_year"]])
        fail("Duplicate ticker-fiscal_year rows found.")

    print("✅ Duplicate ticker-year check passed.")

    expected_core_rows = pd.MultiIndex.from_product(
        [CORE_TICKERS, CORE_YEARS], names=["ticker", "fiscal_year"]
    )
    actual_rows = pd.MultiIndex.from_frame(financial_df[["ticker", "fiscal_year"]])
    missing_core_rows = expected_core_rows.difference(actual_rows)

    if len(missing_core_rows) > 0:
        fail(f"Missing current Q1 scope ticker-year rows: {list(missing_core_rows)}")

    print("✅ Current Q1 scope coverage check passed.")

    valid_tickers = set(master_df["ticker"])
    financial_tickers = set(financial_df["ticker"])
    unknown_tickers = sorted(financial_tickers - valid_tickers)

    if unknown_tickers:
        fail(f"Financial data contains tickers not found in company master: {unknown_tickers}")

    print("✅ Ticker reference check passed.")

    fiscal_year_numeric = pd.to_numeric(financial_df["fiscal_year"], errors="coerce")

    if fiscal_year_numeric.isna().any():
        bad_rows = financial_df[fiscal_year_numeric.isna()][["ticker", "fiscal_year"]]
        print(bad_rows)
        fail("Some fiscal_year values cannot be converted to numbers.")

    invalid_years = financial_df[
        (fiscal_year_numeric < YEAR_MIN) | (fiscal_year_numeric > YEAR_MAX)
    ]

    if not invalid_years.empty:
        print(invalid_years[["ticker", "fiscal_year"]])
        fail(f"Some fiscal_year values are outside the allowed range {YEAR_MIN}-{YEAR_MAX}.")

    print("✅ Fiscal year check passed.")

    parsed_dates = pd.to_datetime(financial_df["period_end_date"], errors="coerce")

    if parsed_dates.isna().any():
        bad_rows = financial_df[parsed_dates.isna()][["ticker", "fiscal_year", "period_end_date"]]
        print(bad_rows)
        fail("Some period_end_date values cannot be parsed as dates.")

    print("✅ Period end date check passed.")

    for col in NUMERIC_COLUMNS:
        # Empty optional numeric fields are allowed at raw-data stage.
        non_empty_values = financial_df[col][financial_df[col] != ""]
        converted = pd.to_numeric(non_empty_values, errors="coerce")

        if converted.isna().any():
            bad_values = sorted(set(non_empty_values[converted.isna()]))
            fail(f"Column '{col}' has non-numeric values: {bad_values}")

    print("✅ Numeric field check passed.")

    numeric_df = financial_df.copy()
    for col in NUMERIC_COLUMNS:
        numeric_df[col] = pd.to_numeric(numeric_df[col], errors="coerce")

    fcf_diff = (
        numeric_df["free_cash_flow"]
        - (numeric_df["operating_cash_flow"] - numeric_df["capital_expenditure"])
    ).abs()
    bad_fcf_rows = numeric_df[fcf_diff > 0.01]

    if not bad_fcf_rows.empty:
        print(bad_fcf_rows[["ticker", "fiscal_year", "operating_cash_flow", "capital_expenditure", "free_cash_flow"]])
        fail("Some free_cash_flow values do not equal operating_cash_flow minus capital_expenditure.")

    print("✅ Free cash flow formula check passed.")

    balance_diff = (
        numeric_df["total_assets"] - numeric_df["total_liabilities"] - numeric_df["total_equity"]
    ).abs()
    balance_tolerance = numeric_df["total_assets"].abs().mul(0.005).clip(lower=1.0)
    bad_balance_rows = numeric_df[balance_diff > balance_tolerance]

    if not bad_balance_rows.empty:
        print(bad_balance_rows[["ticker", "fiscal_year", "total_assets", "total_liabilities", "total_equity"]])
        fail("Some balance-sheet rows are outside the accounting tolerance.")

    print("✅ Balance-sheet relationship check passed.")

    print("\nRows by ticker:")
    print(financial_df["ticker"].value_counts().sort_index())

    print("\nRows by fiscal year:")
    print(financial_df["fiscal_year"].value_counts().sort_index())

    print("\n✅ All financial statement checks passed.")


if __name__ == "__main__":
    main()
