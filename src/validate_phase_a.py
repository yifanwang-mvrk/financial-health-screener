import pandas as pd

from phase_a_evidence import (
    AUTO_CONFLICTS_PATH,
    FINANCIAL_FACTS_PATH,
    LATEST_LONG_PATH,
    RECONCILIATION_PATH,
    build_coverage_and_gate2,
)


if __name__ == "__main__":
    facts = pd.read_csv(FINANCIAL_FACTS_PATH, keep_default_na=False)
    latest = pd.read_csv(LATEST_LONG_PATH, keep_default_na=False)
    conflicts = pd.read_csv(AUTO_CONFLICTS_PATH, keep_default_na=False)
    reconciliation = pd.read_csv(RECONCILIATION_PATH, keep_default_na=False)
    coverage = build_coverage_and_gate2(
        facts, latest, conflicts, reconciliation
    )
    print(f"Phase A validation complete: {len(coverage)} coverage checks.")
