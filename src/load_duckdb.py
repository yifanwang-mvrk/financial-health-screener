import pandas as pd

from phase_a_evidence import (
    AUTO_CONFLICTS_PATH,
    PILOT_COVERAGE_PATH,
    FINANCIAL_FACTS_PATH,
    LATEST_LONG_PATH,
    UNIVERSE_PATH,
    load_phase_a_tables,
)


if __name__ == "__main__":
    load_phase_a_tables(
        pd.read_csv(
            UNIVERSE_PATH, dtype={"cik": str}, keep_default_na=False
        ),
        pd.read_csv(
            FINANCIAL_FACTS_PATH, dtype={"cik": str}, keep_default_na=False
        ),
        pd.read_csv(
            LATEST_LONG_PATH, dtype={"cik": str}, keep_default_na=False
        ),
        pd.read_csv(AUTO_CONFLICTS_PATH, keep_default_na=False),
        pd.read_csv(PILOT_COVERAGE_PATH, keep_default_na=False),
    )
    print("B1 Pilot evidence tables loaded into DuckDB.")
