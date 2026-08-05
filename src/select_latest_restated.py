from phase_a_evidence import select_latest_restated


if __name__ == "__main__":
    latest, conflicts, reconciliation = select_latest_restated()
    print(
        "Latest-restated selection complete: "
        f"{len(latest)} facts, {len(conflicts)} conflicts, "
        f"{len(reconciliation)} reconciliation rows."
    )
