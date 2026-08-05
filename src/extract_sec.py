from __future__ import annotations

import argparse

from phase_a_evidence import build_company_universe, extract_a2_probe
from q1_annual_pipeline import extract_pilot_sec


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download and cache official SEC JSON through one scoped entry."
    )
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument(
        "--scope",
        choices=["pilot", "a2"],
        default="pilot",
        help="Use the six-company B1 Pilot or the historical CHWY/EBAY A2 probe.",
    )
    args = parser.parse_args()
    if args.scope == "a2":
        build_company_universe(refresh=args.refresh)
        manifest = extract_a2_probe(refresh=args.refresh)
    else:
        manifest = extract_pilot_sec(refresh=args.refresh)
    print(f"{args.scope} SEC extraction complete: {len(manifest)} raw artifacts")
