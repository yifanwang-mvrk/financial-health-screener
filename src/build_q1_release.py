from q1_annual_pipeline import build_b1_pilot


def main() -> None:
    build_b1_pilot()
    print(
        "B1 Pilot rebuilt. The formal Q1 release remains pending B2-B5; "
        "this command does not publish an early release."
    )


if __name__ == "__main__":
    main()
