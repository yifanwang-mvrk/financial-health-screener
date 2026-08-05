from q1_annual_pipeline import validate_pilot


if __name__ == "__main__":
    coverage, flags = validate_pilot()
    print(f"B1 validation complete: {len(coverage)} coverage rows, {len(flags)} flags")
