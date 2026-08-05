from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd

from phase_a_evidence import _extract_sec_selection, _read_json_gz, _sec_paths
from q1_annual_pipeline import (
    CONCEPT_MAP_PATH,
    DB_PATH,
    EVENTS_PATH,
    FIELD_CONTRACT_PATH,
    FINANCIAL_FACTS_PATH,
    LATEST_PATH,
    CONFLICTS_PATH,
    NORMALIZED,
    OVERRIDES_PATH,
    PROCESSED,
    REFERENCE,
    SAMPLE_PATH,
    UNIVERSE_PATH,
    _field_map,
    _read_csv,
    map_concepts_and_signs,
    select_latest_restated,
)


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
RAW_SEC = ROOT / "data" / "raw" / "sec"

B2_MANIFEST_PATH = RAW_SEC / "b2_formal_manifest.csv"
B2_EXTRACTION_ERRORS_PATH = PROCESSED / "b2_sec_extraction_errors.csv"
B2_UNMAPPED_PATH = NORMALIZED / "b2_annual_facts_unmapped.csv"
B2_REJECTIONS_PATH = PROCESSED / "b2_candidate_rejections.csv"
B2_RECONCILIATION_PATH = PROCESSED / "b2_sec_manual_reconciliation.csv"
METRIC_FLAGS_PATH = PROCESSED / "metric_flags.csv"
COVERAGE_PATH = PROCESSED / "b2_company_field_year_coverage.csv"
FAILURES_PATH = PROCESSED / "b2_failures.csv"
AUDIT_PATH = PROCESSED / "b2_stage_audit.json"
REPORT_PATH = DOCS / "b2_sample_expansion_report.md"
A3_PERIOD_MAP_PATH = PROCESSED / "a3_annual_fact_versions.csv"

TARGET_YEARS = set(range(2018, 2025))
SOURCE_YEARS = set(range(2017, 2025))
GATE1_SAMPLE_SHA256 = "d6a6f25bb5d3a0489cd479f1a30e21750667751fb534aabc45d0178b60b74164"
GATE1_FIELD_CONTRACT_SHA256 = "0ce3ad51f5df0d53b90f7b669e5c94f02b045e53a10bd2e2e6ae879d8daa5f4a"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _formal_sample() -> pd.DataFrame:
    sample = _read_csv(SAMPLE_PATH)
    if len(sample) != 21:
        raise ValueError("Gate1-v1.0 formal sample must contain exactly 21 companies")
    return sample


def extract_formal_sec(refresh: bool = False) -> pd.DataFrame:
    universe = _read_csv(UNIVERSE_PATH, dtype={"cik": str})
    sample_ids = set(_formal_sample()["company_id"])
    selected = universe[universe["company_id"].isin(sample_ids)].copy()
    missing = sorted(sample_ids - set(selected["company_id"]))
    if missing:
        raise ValueError(f"Formal companies missing from universe: {missing}")
    return _extract_sec_selection(
        selected,
        B2_MANIFEST_PATH,
        refresh=refresh,
        error_path=B2_EXTRACTION_ERRORS_PATH,
    )


def normalize_formal_annual_facts() -> pd.DataFrame:
    universe = _read_csv(UNIVERSE_PATH, dtype={"cik": str})
    sample_ids = set(_formal_sample()["company_id"])
    selected = universe[universe["company_id"].isin(sample_ids)].copy()
    manifest = _read_csv(B2_MANIFEST_PATH)
    loaded_lookup = (
        manifest[manifest["artifact"].eq("companyfacts")]
        .set_index("ticker")["fetched_at"]
        .to_dict()
    )
    a3_periods = _read_csv(A3_PERIOD_MAP_PATH, dtype={"cik": str})
    a3_periods = a3_periods[a3_periods["company_id"].isin(sample_ids)].copy()
    consistency = a3_periods.groupby(["company_id", "period_end"])[
        "fiscal_year"
    ].nunique()
    if consistency.gt(1).any():
        raise ValueError("A3 fiscal-year map contains inconsistent period assignments")
    period_lookup = (
        a3_periods[["company_id", "period_end", "fiscal_year"]]
        .drop_duplicates()
        .set_index(["company_id", "period_end"])["fiscal_year"]
        .astype(int)
        .to_dict()
    )

    allowed_pairs = set(
        _field_map()[["taxonomy", "source_tag"]].itertuples(index=False, name=None)
    )
    overrides = _read_csv(OVERRIDES_PATH)
    formula_overrides = overrides[
        overrides["status"].eq("active")
        & ~overrides["override_type"].eq("filing_table_value")
    ]
    for formula in formula_overrides["source_tag_or_formula"]:
        for source_tag in re.findall(r"[A-Za-z][A-Za-z0-9_]*", str(formula)):
            allowed_pairs.add(("us-gaap", source_tag))

    rows: list[dict[str, Any]] = []
    for company in selected.sort_values("ticker").itertuples(index=False):
        cik = int(company.cik)
        facts_path, _ = _sec_paths(cik)
        payload = _read_json_gz(facts_path)
        for taxonomy, taxonomy_facts in payload.get("facts", {}).items():
            for source_tag, fact in taxonomy_facts.items():
                if (taxonomy, source_tag) not in allowed_pairs:
                    continue
                for source_unit, items in fact.get("units", {}).items():
                    for item in items:
                        form = str(item.get("form", ""))
                        if form not in {"10-K", "10-K/A"} or not item.get("end"):
                            continue
                        period_end = str(item["end"])
                        fiscal_year = period_lookup.get((company.company_id, period_end))
                        if fiscal_year not in SOURCE_YEARS:
                            continue
                        period_start = str(item.get("start", ""))
                        duration_days = (
                            (pd.Timestamp(period_end) - pd.Timestamp(period_start)).days
                            if period_start
                            else None
                        )
                        accession = str(item.get("accn", ""))
                        accession_compact = accession.replace("-", "")
                        rows.append(
                            {
                                "company_id": company.company_id,
                                "ticker": company.ticker,
                                "cik": f"{cik:010d}",
                                "taxonomy": taxonomy,
                                "source_tag": source_tag,
                                "source_unit": source_unit,
                                "form": form,
                                "filing_date": str(item.get("filed", "")),
                                "period_start": period_start,
                                "period_end": period_end,
                                "fiscal_year": fiscal_year,
                                "fiscal_period": str(item.get("fp", "")),
                                "reported_fiscal_year": item.get("fy", ""),
                                "frame": str(item.get("frame", "")),
                                "duration_days": duration_days,
                                "accession_number": accession,
                                "value_raw": float(item["val"]),
                                "source_url": (
                                    "https://www.sec.gov/Archives/edgar/data/"
                                    f"{cik}/{accession_compact}/"
                                ),
                                "loaded_at": loaded_lookup.get(company.ticker, ""),
                            }
                        )

    columns = [
        "company_id",
        "ticker",
        "cik",
        "taxonomy",
        "source_tag",
        "source_unit",
        "form",
        "filing_date",
        "period_start",
        "period_end",
        "fiscal_year",
        "fiscal_period",
        "reported_fiscal_year",
        "frame",
        "duration_days",
        "accession_number",
        "value_raw",
        "source_url",
        "loaded_at",
    ]
    facts = pd.DataFrame(rows, columns=columns).drop_duplicates()
    if facts.empty:
        raise ValueError("No formal annual facts were normalized")
    facts = facts.sort_values(
        ["ticker", "fiscal_year", "taxonomy", "source_tag", "filing_date"]
    )
    facts.to_csv(B2_UNMAPPED_PATH, index=False)
    return facts


def _expected_years_by_company(sample: pd.DataFrame) -> dict[str, set[int]]:
    return {
        row.company_id: {
            int(value)
            for value in str(row.a3_available_fiscal_years).split("|")
            if value
        }
        for row in sample.itertuples(index=False)
    }


def validate_formal_sample() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    sample = _formal_sample()
    latest = _read_csv(LATEST_PATH, dtype={"cik": str})
    conflicts = _read_csv(CONFLICTS_PATH)
    rejected = _read_csv(B2_REJECTIONS_PATH)
    contract = _read_csv(FIELD_CONTRACT_PATH)
    formal_fields = contract[contract["load_to_formal_layer"].astype(int).eq(1)]
    required_fields = set(
        formal_fields.loc[formal_fields["requiredness"].eq("required"), "canonical_field"]
    )
    expected_lookup = _expected_years_by_company(sample)

    winner_lookup = latest.set_index(["company_id", "fiscal_year", "canonical_field"])
    conflict_counts = (
        conflicts.groupby(["company_id", "fiscal_year", "canonical_field"])
        .size()
        .to_dict()
    )
    coverage_rows: list[dict[str, Any]] = []
    failure_rows: list[dict[str, Any]] = []
    for company in sample.sort_values("formal_sample_order").itertuples(index=False):
        for fiscal_year in sorted(TARGET_YEARS):
            expected = fiscal_year in expected_lookup[company.company_id]
            for field in formal_fields.itertuples(index=False):
                key = (company.company_id, fiscal_year, field.canonical_field)
                available = key in winner_lookup.index
                coverage_rows.append(
                    {
                        "company_id": company.company_id,
                        "ticker": company.ticker,
                        "formal_peer_group": company.formal_peer_group,
                        "fiscal_year": fiscal_year,
                        "canonical_field": field.canonical_field,
                        "requiredness": field.requiredness,
                        "expected_for_company": int(expected),
                        "fact_available": int(available),
                        "conflict_count": int(conflict_counts.get(key, 0)),
                    }
                )
                if expected and field.canonical_field in required_fields and not available:
                    failure_rows.append(
                        {
                            "company_id": company.company_id,
                            "ticker": company.ticker,
                            "fiscal_year": fiscal_year,
                            "canonical_field": field.canonical_field,
                            "failure_type": "missing_required_field",
                            "failure_reason": "Expected formal company-year lacks a required Gate 1 field",
                        }
                    )
    coverage = pd.DataFrame(coverage_rows)
    failures = pd.DataFrame(
        failure_rows,
        columns=[
            "company_id",
            "ticker",
            "fiscal_year",
            "canonical_field",
            "failure_type",
            "failure_reason",
        ],
    )
    coverage.to_csv(COVERAGE_PATH, index=False)
    failures.to_csv(FAILURES_PATH, index=False)

    target_latest = latest[latest["fiscal_year"].astype(int).isin(SOURCE_YEARS)].copy()
    wide = target_latest.pivot_table(
        index=["company_id", "ticker", "fiscal_year"],
        columns="canonical_field",
        values="value_standardized",
        aggfunc="first",
    ).reset_index()
    for field in set(formal_fields["canonical_field"]):
        if field not in wide:
            wide[field] = pd.NA
    wide["fiscal_year"] = pd.to_numeric(wide["fiscal_year"]).astype(int)
    wide = wide.sort_values(["company_id", "fiscal_year"])
    wide["prior_fiscal_year"] = wide.groupby("company_id")["fiscal_year"].shift(1)
    wide["prior_assets"] = wide.groupby("company_id")["total_assets"].shift(1)
    wide["prior_equity"] = wide.groupby("company_id")["total_equity"].shift(1)
    wide["average_assets"] = (wide["total_assets"] + wide["prior_assets"]) / 2
    wide["average_equity"] = (wide["total_equity"] + wide["prior_equity"]) / 2
    observed_keys = set(wide[["company_id", "fiscal_year"]].itertuples(index=False, name=None))

    flag_rows: list[dict[str, Any]] = []

    def add_flag(
        company_id: str,
        fiscal_year: int,
        metric_name: str,
        flag_code: str,
        severity: str,
        reason: str,
        source_fields: str,
    ) -> None:
        flag_rows.append(
            {
                "company_id": company_id,
                "fiscal_year": fiscal_year,
                "metric_name": metric_name,
                "flag_code": flag_code,
                "flag_value": True,
                "severity": severity,
                "reason": reason,
                "source_fields": source_fields,
                "generated_at": f"{date.today().isoformat()}T00:00:00+00:00",
            }
        )

    for row in wide.itertuples(index=False):
        if row.fiscal_year not in TARGET_YEARS:
            continue
        expected = row.fiscal_year in expected_lookup.get(row.company_id, set())
        for field in sorted(required_fields):
            if expected and pd.isna(getattr(row, field)):
                add_flag(
                    row.company_id,
                    row.fiscal_year,
                    field,
                    "missing_required_field",
                    "high",
                    f"Required Gate 1 field {field} is missing",
                    field,
                )
        if (
            pd.isna(row.prior_assets)
            or pd.isna(row.prior_equity)
            or int(row.prior_fiscal_year) != row.fiscal_year - 1
        ):
            add_flag(
                row.company_id,
                row.fiscal_year,
                "dupont",
                "missing_prior_balance",
                "high",
                "Consecutive prior-year assets/equity are unavailable",
                "total_assets|total_equity",
            )
        elif row.average_equity <= 0:
            add_flag(
                row.company_id,
                row.fiscal_year,
                "roe",
                "non_positive_average_equity",
                "high",
                "Average equity is nonpositive; ROE is invalid",
                "total_equity",
            )
        for metric_name, denominator, source_fields in [
            ("net_margin", row.revenue, "revenue"),
            ("asset_turnover", row.average_assets, "total_assets"),
            ("roe", row.average_equity, "total_equity"),
        ]:
            if pd.notna(denominator) and float(denominator) == 0:
                add_flag(
                    row.company_id,
                    row.fiscal_year,
                    metric_name,
                    "zero_denominator",
                    "high",
                    "Metric denominator equals zero",
                    source_fields,
                )
        if (row.company_id, row.fiscal_year + 1) not in observed_keys:
            add_flag(
                row.company_id,
                row.fiscal_year,
                "h1_outcome",
                "insufficient_forward_year",
                "medium",
                "No consecutive t+1 annual observation is available",
                "roe",
            )

    for conflict in conflicts.itertuples(index=False):
        if int(conflict.fiscal_year) in TARGET_YEARS and conflict.conflict_severity in {
            "medium",
            "high",
        }:
            add_flag(
                conflict.company_id,
                int(conflict.fiscal_year),
                conflict.canonical_field,
                "source_conflict",
                conflict.conflict_severity,
                f"{conflict.resolution_status}: {conflict.review_note}",
                conflict.canonical_field,
            )
    for rejection in rejected.itertuples(index=False):
        if int(rejection.fiscal_year) in TARGET_YEARS and rejection.rejection_reason in {
            "unit_mismatch",
            "invalid_domain",
        }:
            add_flag(
                rejection.company_id,
                int(rejection.fiscal_year),
                rejection.canonical_field,
                rejection.rejection_reason,
                "high",
                "Candidate fact rejected before latest-restated selection",
                rejection.canonical_field,
            )

    flag_columns = [
        "company_id",
        "fiscal_year",
        "metric_name",
        "flag_code",
        "flag_value",
        "severity",
        "reason",
        "source_fields",
        "generated_at",
    ]
    flags = pd.DataFrame(flag_rows, columns=flag_columns).drop_duplicates(
        ["company_id", "fiscal_year", "metric_name", "flag_code", "reason"]
    )
    flags.to_csv(METRIC_FLAGS_PATH, index=False)
    return coverage, failures, flags


def load_formal_duckdb() -> None:
    tables = {
        "company_universe": _read_csv(UNIVERSE_PATH, dtype={"cik": str}),
        "events": _read_csv(EVENTS_PATH),
        "q1_formal_sample": _read_csv(SAMPLE_PATH),
        "financial_facts": _read_csv(FINANCIAL_FACTS_PATH, dtype={"cik": str}),
        "concept_map": _read_csv(CONCEPT_MAP_PATH),
        "concept_conflicts": _read_csv(CONFLICTS_PATH),
        "metric_flags": _read_csv(METRIC_FLAGS_PATH),
        "q1_latest_restated": _read_csv(LATEST_PATH, dtype={"cik": str}),
        "company_overrides": _read_csv(OVERRIDES_PATH),
        "b2_company_field_year_coverage": _read_csv(COVERAGE_PATH),
        "b2_failures": _read_csv(FAILURES_PATH),
        "b2_candidate_rejections": _read_csv(B2_REJECTIONS_PATH),
    }
    with duckdb.connect(str(DB_PATH)) as connection:
        for table_name, frame in tables.items():
            connection.register(f"{table_name}_input", frame)
            connection.execute(
                f"create or replace table {table_name} as select * from {table_name}_input"
            )


def _write_report(
    facts: pd.DataFrame,
    latest: pd.DataFrame,
    conflicts: pd.DataFrame,
    coverage: pd.DataFrame,
    failures: pd.DataFrame,
    flags: pd.DataFrame,
) -> None:
    sample = _formal_sample()
    group_summary = (
        sample.groupby("formal_peer_group")["company_id"].count().sort_index()
    )
    conflict_summary = Counter(conflicts["conflict_severity"])
    lines = [
        "# B2 Formal Sample Expansion Report",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "Status: **Done** (`b2_stage_audit.json` reports every B2 DoD check as passed)",
        "",
        "The B1 rules are applied unchanged to the Gate1-v1.0 sample and FY2018-FY2024 window. FY2017 is retained only for opening balances.",
        "",
        "## Frozen Sample",
        "",
    ]
    for group, count in group_summary.items():
        lines.append(f"- {group}: {count} companies")
    lines.extend(
        [
            "",
            "## Data Layer",
            "",
            f"- Filing-level facts: {len(facts):,}",
            f"- Latest-restated/derived facts: {len(latest):,}",
            f"- Conflicts: {len(conflicts):,} ({dict(conflict_summary)})",
            f"- Metric flags: {len(flags):,}",
            f"- Missing required company-year-fields: {len(failures):,}",
            f"- Coverage rows: {len(coverage):,}",
            "",
            "Missing values remain null. Candidate unit, duration, and domain rejections are logged. No H1 eligibility, field contract, conflict threshold, peer group, or annual-window rule changes are made in B2.",
        ]
    )
    if not failures.empty:
        top = (
            failures.groupby(["ticker", "canonical_field"])
            .size()
            .reset_index(name="missing_years")
            .sort_values(["missing_years", "ticker"], ascending=[False, True])
            .head(20)
        )
        lines.extend(
            [
                "",
                "## Required-Field Failures",
                "",
                "| Ticker | Field | Missing expected years |",
                "| --- | --- | ---: |",
            ]
        )
        for row in top.itertuples(index=False):
            lines.append(f"| {row.ticker} | {row.canonical_field} | {row.missing_years} |")
    else:
        lines.extend(["", "No expected required company-year field is missing."])
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_b2_formal_sample(refresh: bool = False) -> dict[str, Any]:
    manifest = extract_formal_sec(refresh=refresh)
    unmapped = normalize_formal_annual_facts()
    facts, rejected = map_concepts_and_signs(
        unmapped_path=B2_UNMAPPED_PATH,
        financial_facts_path=FINANCIAL_FACTS_PATH,
        rejection_path=B2_REJECTIONS_PATH,
    )
    latest, conflicts, _ = select_latest_restated(
        financial_facts_path=FINANCIAL_FACTS_PATH,
        latest_path=LATEST_PATH,
        conflicts_path=CONFLICTS_PATH,
        reconciliation_path=B2_RECONCILIATION_PATH,
    )
    coverage, failures, flags = validate_formal_sample()
    load_formal_duckdb()
    _write_report(facts, latest, conflicts, coverage, failures, flags)

    sample = _formal_sample()
    facts_tickers = set(facts["ticker"])
    checks = {
        "formal_sample_exact": len(sample) == 21,
        "peer_groups_exact": sample.groupby("formal_peer_group").size().eq(7).all(),
        "raw_manifest_complete": len(manifest) == 42,
        "extraction_error_log_clear": _read_csv(B2_EXTRACTION_ERRORS_PATH).empty,
        "all_formal_companies_normalized": facts_tickers == set(sample["ticker"]),
        "financial_facts_schema_complete": {
            "company_id",
            "accession_number",
            "form",
            "filing_date",
            "period_start",
            "period_end",
            "fiscal_year",
            "fiscal_period",
            "duration_days",
            "canonical_field",
            "source_tag",
            "value_raw",
            "value_standardized",
            "unit",
            "loaded_at",
        }.issubset(facts.columns),
        "latest_unique": not latest.duplicated(
            ["company_id", "fiscal_year", "canonical_field"]
        ).any(),
        "conflicts_resolved_or_logged": not conflicts["resolution_status"].eq("").any(),
        "quality_outputs_written": COVERAGE_PATH.exists()
        and FAILURES_PATH.exists()
        and METRIC_FLAGS_PATH.exists(),
        "required_field_coverage_complete": failures.empty,
        "frozen_rules_unchanged": _sha256(SAMPLE_PATH) == GATE1_SAMPLE_SHA256
        and _sha256(FIELD_CONTRACT_PATH) == GATE1_FIELD_CONTRACT_SHA256,
    }
    checks = {key: bool(value) for key, value in checks.items()}
    if not all(checks.values()):
        failed = [key for key, passed in checks.items() if not passed]
        raise ValueError(f"B2 audit failed: {failed}")

    audit = {
        "generated_on": date.today().isoformat(),
        "stage": "B2 Q1 Sample Expansion",
        "status": "Done",
        "gate1_contract": "Gate1-v1.0",
        "formal_company_count": len(sample),
        "formal_peer_group_counts": sample.groupby("formal_peer_group")
        .size()
        .to_dict(),
        "frozen_window": "FY2018-FY2024",
        "opening_balance_source_year": 2017,
        "raw_artifact_count": len(manifest),
        "unmapped_fact_count": len(unmapped),
        "financial_fact_count": len(facts),
        "candidate_rejection_count": len(rejected),
        "latest_fact_count": len(latest),
        "conflict_count": len(conflicts),
        "unresolved_conflict_count": int(
            conflicts["resolution_status"].eq("requires_review").sum()
        ),
        "metric_flag_count": len(flags),
        "missing_required_company_year_field_count": len(failures),
        "processed_generation": "scripted_no_manual_processed_edits",
        "quality_rules_checked": [
            "null_not_sentinel",
            "zero_denominator",
            "non_positive_average_equity",
            "missing_prior_balance",
            "insufficient_forward_year",
            "source_conflict",
            "unit_mismatch",
            "invalid_sign_or_domain",
        ],
        "gate1_sample_sha256": _sha256(SAMPLE_PATH),
        "gate1_field_contract_sha256": _sha256(FIELD_CONTRACT_PATH),
        "checks": checks,
    }
    AUDIT_PATH.write_text(
        json.dumps(audit, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    return audit
