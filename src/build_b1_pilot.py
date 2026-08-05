from __future__ import annotations

import argparse

from q1_annual_pipeline import build_b1_pilot


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Rebuild the six-company B1 Pilot from SEC raw JSON through DuckDB marts."
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Refresh SEC cache and archive changed prior payloads.",
    )
    args = parser.parse_args()
    result = build_b1_pilot(refresh=args.refresh)
    print("B1 Pilot pipeline rebuilt against Gate1-v1.0.")
    for key, value in result.items():
        print(f"{key}: {value}")
