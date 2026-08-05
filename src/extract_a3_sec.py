from __future__ import annotations

import argparse

from phase_a_evidence import build_company_universe, extract_a3_candidates


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Cache SEC Companyfacts and submissions for every A3 Q1 candidate."
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Fetch current SEC payloads and archive changed prior raw files.",
    )
    args = parser.parse_args()
    build_company_universe(refresh=args.refresh)
    manifest = extract_a3_candidates(refresh=args.refresh)
    print(f"A3 SEC extraction complete: {len(manifest)} raw artifacts")
