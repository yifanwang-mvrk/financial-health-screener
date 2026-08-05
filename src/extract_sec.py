from __future__ import annotations

import argparse

from phase_a_evidence import build_company_universe, extract_a2_probe


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract the two-company A2 SEC source probe through one entry point."
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Fetch current SEC payloads and archive changed prior raw files.",
    )
    args = parser.parse_args()
    build_company_universe(refresh=args.refresh)
    manifest = extract_a2_probe(refresh=args.refresh)
    print(f"A2 SEC extraction complete: {len(manifest)} raw artifacts")
