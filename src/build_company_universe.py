from phase_a_evidence import build_company_universe


if __name__ == "__main__":
    universe = build_company_universe()
    print(f"Company universe complete: {len(universe)} companies.")
