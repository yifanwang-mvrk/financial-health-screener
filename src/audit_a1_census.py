from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
UNIVERSE_PATH = ROOT / "data/reference/company_universe.csv"
EVENTS_PATH = ROOT / "data/reference/events.csv"
AUDIT_PATH = ROOT / "data/processed/a1_census_audit.json"
REPORT_PATH = ROOT / "docs/a1_census_report.md"
A3_AUDIT_PATH = ROOT / "data/processed/a3_stage_audit.json"

COMPANY_REQUIRED_COLUMNS = {
    "company_id",
    "ticker",
    "company_name",
    "cik",
    "exchange",
    "listing_date",
    "peer_group",
    "classification_confidence",
    "status_group",
    "online_core_flag",
    "inventory_ownership_flag",
    "revenue_recognition_model",
    "fiscal_year_end",
    "include_q1_candidate",
    "q2_event_candidate",
    "exclusion_reason",
}
EVENT_REQUIRED_COLUMNS = {
    "event_id",
    "company_id",
    "event_type",
    "event_date",
    "event_date_basis",
    "event_effective_date",
    "event_source",
    "event_date_confidence",
    "estimated_pre_event_quarters",
    "coverage_verified",
    "verified_pre_event_quarters",
    "qualifies_for_q2",
    "exclusion_reason",
}
ALLOWED_PEER_GROUPS = {
    "marketplace_platform",
    "inventory_led_ecommerce",
    "dtc_brand",
    "hybrid",
    "boundary",
}
ALLOWED_EVENT_TYPES = {
    "Chapter 11",
    "Going concern",
    "Covenant breach",
    "Debt restructuring",
    "Emergency financing",
    "Asset exit / liquidation",
}


def _quarter_upper_bound(listing_date: str, event_date: str) -> int:
    listing = pd.Timestamp(listing_date)
    event = pd.Timestamp(event_date)
    months = (event.year - listing.year) * 12 + event.month - listing.month
    return max(0, months // 3)


def audit_a1_census() -> dict[str, object]:
    universe = pd.read_csv(UNIVERSE_PATH, dtype={"cik": str}, keep_default_na=False)
    events = pd.read_csv(EVENTS_PATH, keep_default_na=False)

    missing_company_columns = sorted(COMPANY_REQUIRED_COLUMNS - set(universe.columns))
    missing_event_columns = sorted(EVENT_REQUIRED_COLUMNS - set(events.columns))
    if missing_company_columns or missing_event_columns:
        raise ValueError(
            "A1 schema mismatch: "
            f"company={missing_company_columns}, event={missing_event_columns}"
        )

    candidates = universe[universe["include_q1_candidate"].eq(1)].copy()
    excluded = universe[universe["include_q1_candidate"].eq(0)].copy()
    duplicate_company_ids = sorted(
        universe.loc[universe["company_id"].duplicated(False), "company_id"].unique()
    )
    duplicate_tickers = sorted(
        universe.loc[universe["ticker"].duplicated(False), "ticker"].unique()
    )
    duplicate_event_ids = sorted(
        events.loc[events["event_id"].duplicated(False), "event_id"].unique()
    )
    orphan_event_company_ids = sorted(set(events["company_id"]) - set(universe["company_id"]))

    invalid_candidate_groups = sorted(
        set(candidates["peer_group"]) - ALLOWED_PEER_GROUPS
    )
    vague_exclusions = sorted(
        excluded.loc[
            excluded["exclusion_reason"].str.strip().isin({"", "NA", "not suitable"}),
            "ticker",
        ].tolist()
    )
    invalid_event_types = sorted(set(events["event_type"]) - ALLOWED_EVENT_TYPES)
    event_required_text = [
        "event_id",
        "company_id",
        "event_type",
        "event_date",
        "event_date_basis",
        "event_source",
        "event_date_confidence",
    ]
    incomplete_event_rows = sorted(
        events.loc[
            events[event_required_text].apply(
                lambda row: any(not str(value).strip() for value in row), axis=1
            ),
            "event_id",
        ].tolist()
    )

    date_errors: list[str] = []
    quarter_estimate_errors: list[str] = []
    universe_by_id = universe.set_index("company_id")
    for event in events.itertuples():
        try:
            pd.Timestamp(event.event_date)
        except (TypeError, ValueError):
            date_errors.append(event.event_id)
            continue
        expected_quarters = _quarter_upper_bound(
            universe_by_id.loc[event.company_id, "listing_date"], event.event_date
        )
        if abs(int(event.estimated_pre_event_quarters) - expected_quarters) > 1:
            quarter_estimate_errors.append(event.event_id)

    a3_complete = False
    if A3_AUDIT_PATH.exists():
        a3_complete = (
            json.loads(A3_AUDIT_PATH.read_text(encoding="utf-8")).get("status")
            == "Done"
        )
    if a3_complete:
        a3_fields_valid = (
            events["coverage_verified"].astype(str).eq("1").all()
            and events["verified_pre_event_quarters"].astype(str).str.len().gt(0).all()
            and events["qualifies_for_q2"].astype(str).isin({"0", "1"}).all()
            and events.loc[
                events["qualifies_for_q2"].astype(str).eq("0"), "exclusion_reason"
            ].str.len().gt(0).all()
        )
        a3_check_name = "a3_fields_verified"
    else:
        a3_fields_valid = (
            events["coverage_verified"].astype(str).eq("0").all()
            and events["verified_pre_event_quarters"].eq("").all()
            and events["qualifies_for_q2"].eq("").all()
        )
        a3_check_name = "a3_fields_remain_provisional"
    listing_dates_valid = pd.to_datetime(
        universe["listing_date"], errors="coerce"
    ).notna().all()
    listing_sources_present = universe["listing_date_source_note"].str.len().gt(0).all()

    checks = {
        "company_schema_complete": not missing_company_columns,
        "event_schema_complete": not missing_event_columns,
        "company_ids_unique": not duplicate_company_ids,
        "tickers_unique": not duplicate_tickers,
        "event_ids_unique": not duplicate_event_ids,
        "event_company_links_valid": not orphan_event_company_ids,
        "q1_candidate_stopping_rule_met": 30 <= len(candidates) <= 40,
        "event_candidate_stopping_rule_met": 10 <= len(events) <= 15,
        "candidate_groups_valid": not invalid_candidate_groups,
        "excluded_companies_have_specific_reason": not vague_exclusions,
        "listing_dates_valid": bool(listing_dates_valid),
        "listing_sources_present": bool(listing_sources_present),
        "event_types_valid": not invalid_event_types,
        "event_required_text_complete": not incomplete_event_rows,
        "event_dates_valid": not date_errors,
        "event_sources_present": events["event_source"].str.len().gt(0).all(),
        "theoretical_quarters_plausible": not quarter_estimate_errors,
        a3_check_name: bool(a3_fields_valid),
    }
    checks = {name: bool(passed) for name, passed in checks.items()}
    if not all(checks.values()):
        failures = sorted(name for name, passed in checks.items() if not passed)
        raise ValueError(f"A1 audit failed: {failures}")

    peer_counts = candidates.groupby("peer_group").size().sort_index().to_dict()
    status_counts = candidates.groupby("status_group").size().sort_index().to_dict()
    event_type_counts = events.groupby("event_type").size().sort_index().to_dict()
    missing_cik = sorted(candidates.loc[candidates["cik"].eq(""), "ticker"].tolist())
    missing_fiscal_year_end = sorted(
        candidates.loc[candidates["fiscal_year_end"].eq(""), "ticker"].tolist()
    )
    missing_listing_date = sorted(
        universe.loc[
            pd.to_datetime(universe["listing_date"], errors="coerce").isna(), "ticker"
        ].tolist()
    )

    audit = {
        "generated_on": date.today().isoformat(),
        "stage": "A1 Unified Company & Event Census",
        "status": "Done",
        "company_count": int(len(universe)),
        "q1_candidate_count": int(len(candidates)),
        "event_candidate_count": int(len(events)),
        "peer_group_counts": {key: int(value) for key, value in peer_counts.items()},
        "candidate_status_counts": {
            key: int(value) for key, value in status_counts.items()
        },
        "event_type_counts": {
            key: int(value) for key, value in event_type_counts.items()
        },
        "missing_cik_candidates": missing_cik,
        "missing_fiscal_year_end_candidates": missing_fiscal_year_end,
        "missing_listing_date_companies": missing_listing_date,
        "checks": checks,
        "next_stage": (
            "Gate 1 Freeze" if a3_complete else "A2 Two-company Source Probe revalidation"
        ),
    }
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_PATH.write_text(
        json.dumps(audit, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )

    lines = [
        "# A1 Unified Company & Event Census Report",
        "",
        f"Generated: {audit['generated_on']}",
        "",
        "Status: **Done**",
        "",
        "## Stopping Rules",
        "",
        f"- Total company universe: {len(universe)}",
        f"- Q1 candidates: {len(candidates)} (required stopping range: approximately 30-40)",
        f"- Event candidates: {len(events)} (required stopping range: approximately 10-15)",
        "",
        "## Q1 Candidate Structure",
        "",
        "| Peer group | Companies |",
        "| --- | ---: |",
    ]
    lines.extend(f"| {key} | {value} |" for key, value in peer_counts.items())
    lines.extend(["", "| Status | Companies |", "| --- | ---: |"])
    lines.extend(f"| {key} | {value} |" for key, value in status_counts.items())
    lines.extend(["", "## Event Structure", "", "| Event type | Candidates |", "| --- | ---: |"])
    lines.extend(f"| {key} | {value} |" for key, value in event_type_counts.items())
    lines.extend(
        [
            "",
            "## Missing Fields for A2/A3 Verification",
            "",
            f"- Missing CIK among Q1 candidates: {', '.join(missing_cik) or 'None'}",
            f"- Missing fiscal-year end among Q1 candidates: {', '.join(missing_fiscal_year_end) or 'None'}",
            f"- Missing listing date: {', '.join(missing_listing_date) or 'None'}",
            "",
            (
                "CIK and fiscal-year-end gaps were allowed at A1. A3 has now verified "
                "the event coverage fields; listing dates remain census provenance fields."
                if a3_complete
                else "CIK and fiscal-year-end gaps are allowed at A1 and are explicitly carried into A2/A3. Listing dates and theoretical pre-event quarters remain provisional until verified."
            ),
            "",
            "## DoD Result",
            "",
        ]
    )
    lines.extend(
        f"- [{'x' if passed else ' '}] {name}"
        for name, passed in checks.items()
    )
    lines.extend(
        [
            "",
            "A1 itself performed no Companyfacts mapping, real quarterly coverage, or formal sample decision. Later-stage fields are preserved when the audit is rerun.",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return audit


if __name__ == "__main__":
    result = audit_a1_census()
    print(
        "A1 census audit passed: "
        f"{result['q1_candidate_count']} Q1 candidates, "
        f"{result['event_candidate_count']} event candidates."
    )
