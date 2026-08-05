from q1_annual_pipeline import normalize_annual_facts


if __name__ == "__main__":
    facts = normalize_annual_facts()
    print(f"B1 annual normalization complete: {len(facts)} unmapped filing facts")
