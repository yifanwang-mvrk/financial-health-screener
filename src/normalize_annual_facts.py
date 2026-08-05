from phase_a_evidence import normalize_annual_facts


if __name__ == "__main__":
    facts = normalize_annual_facts()
    print(f"Annual fact normalization complete: {len(facts)} rows.")
