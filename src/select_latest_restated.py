from q1_annual_pipeline import select_latest_restated


if __name__ == "__main__":
    latest, conflicts, reconciliation = select_latest_restated()
    print(
        f"B1 latest-restated selection complete: {len(latest)} facts, "
        f"{len(conflicts)} conflicts, {len(reconciliation)} reconciliation rows"
    )
