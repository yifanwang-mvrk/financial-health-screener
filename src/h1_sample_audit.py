from q1_annual_pipeline import build_pilot_marts


if __name__ == "__main__":
    counts = build_pilot_marts()
    print(f"B1 Pilot marts and H1 audit complete: {counts}")
