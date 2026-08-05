from q1_annual_pipeline import map_concepts_and_signs


if __name__ == "__main__":
    facts, rejected = map_concepts_and_signs()
    print(
        f"B1 concept mapping complete: {len(facts)} valid facts, "
        f"{len(rejected)} rejected candidates"
    )
