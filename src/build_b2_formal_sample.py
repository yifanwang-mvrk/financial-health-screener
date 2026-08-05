from __future__ import annotations

import argparse

from q1_formal_pipeline import build_b2_formal_sample


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Expand the frozen Gate1-v1.0 annual pipeline to all 21 formal companies."
    )
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    result = build_b2_formal_sample(refresh=args.refresh)
    print("B2 formal sample expansion complete.")
    for key, value in result.items():
        print(f"{key}: {value}")
