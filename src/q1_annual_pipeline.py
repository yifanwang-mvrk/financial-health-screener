from __future__ import annotations

import json
import re
import shutil
from datetime import date
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd

from phase_a_evidence import (
    _extract_sec_selection,
    _read_json_gz,
    _sec_paths,
    build_company_universe,
)


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "data" / "reference"
RAW = ROOT / "data" / "raw"
RAW_SEC = RAW / "sec"
NORMALIZED = ROOT / "data" / "normalized"
PROCESSED = ROOT / "data" / "processed"
DOCS = ROOT / "docs"
DB_PATH = ROOT / "db" / "financial_health_screener.duckdb"

UNIVERSE_PATH = REFERENCE / "company_universe.csv"
EVENTS_PATH = REFERENCE / "events.csv"
SAMPLE_PATH = REFERENCE / "q1_formal_sample_v1.csv"
FIELD_CONTRACT_PATH = REFERENCE / "q1_field_contract_v1.csv"
CONCEPT_MAP_PATH = REFERENCE / "concept_map.csv"
OVERRIDES_PATH = REFERENCE / "company_overrides.csv"
MANUAL_FINANCIALS_PATH = RAW / "financial_statements_raw.csv"

MANIFEST_PATH = RAW_SEC / "manifest.csv"
EXTRACTION_ERRORS_PATH = PROCESSED / "b1_sec_extraction_errors.csv"
UNMAPPED_PATH = NORMALIZED / "b1_annual_facts_unmapped.csv"
FINANCIAL_FACTS_PATH = NORMALIZED / "financial_facts.csv"
CANDIDATE_REJECTIONS_PATH = PROCESSED / "b1_candidate_rejections.csv"
LATEST_PATH = PROCESSED / "sec_latest_restated_long.csv"
CONFLICTS_PATH = PROCESSED / "sec_concept_conflicts.csv"
RECONCILIATION_PATH = PROCESSED / "sec_manual_reconciliation.csv"
METRIC_FLAGS_PATH = PROCESSED / "b1_metric_flags.csv"
COVERAGE_PATH = PROCESSED / "b1_pilot_coverage.csv"
VALIDATION_ERRORS_PATH = PROCESSED / "b1_validation_errors.csv"
AUDIT_PATH = PROCESSED / "b1_pilot_source_audit.json"
PILOT_MART_SQL = ROOT / "sql" / "b1_pilot_marts.sql"

B1_FINANCIAL_FACTS_SNAPSHOT = NORMALIZED / "b1_financial_facts.csv"
B1_LATEST_SNAPSHOT = PROCESSED / "b1_latest_restated_long.csv"
B1_CONFLICTS_SNAPSHOT = PROCESSED / "b1_concept_conflicts.csv"
B1_RECONCILIATION_SNAPSHOT = PROCESSED / "b1_manual_reconciliation.csv"

PILOT_YEARS = {2021, 2022, 2023}
MART_EXPORTS = [
    "b1_pilot_annual_company_metrics",
    "b1_pilot_peer_summary",
    "b1_pilot_company_vs_peer",
    "b1_pilot_dupont_contributions",
    "b1_pilot_h1_sample_audit",
    "b1_pilot_h1_evidence_summary",
]


def _read_csv(path: Path, **kwargs: Any) -> pd.DataFrame:
    return pd.read_csv(path, keep_default_na=False, **kwargs)


def _pilot_sample() -> pd.DataFrame:
    sample = _read_csv(SAMPLE_PATH)
    pilot = sample[sample["b1_pilot_member"].astype(int).eq(1)].copy()
    if len(pilot) != 6:
        raise ValueError("Gate1-v1.0 must identify exactly six B1 Pilot companies")
    return pilot


def extract_pilot_sec(refresh: bool = False) -> pd.DataFrame:
    universe = (
        _read_csv(UNIVERSE_PATH, dtype={"cik": str})
        if UNIVERSE_PATH.exists()
        else build_company_universe(refresh=refresh)
    )
    pilot_ids = set(_pilot_sample()["company_id"])
    selected = universe[universe["company_id"].isin(pilot_ids)].copy()
    missing = sorted(pilot_ids - set(selected["company_id"]))
    if missing:
        raise ValueError(f"Pilot companies missing from company universe: {missing}")
    return _extract_sec_selection(
        selected,
        MANIFEST_PATH,
        refresh=refresh,
        error_path=EXTRACTION_ERRORS_PATH,
    )


def _field_map() -> pd.DataFrame:
    contract = _read_csv(FIELD_CONTRACT_PATH)
    extracted = set(
        contract.loc[
            contract["load_to_formal_layer"].astype(int).eq(1)
            & ~contract["field_role"].eq("derived"),
            "canonical_field",
        ]
    )
    concepts = _read_csv(CONCEPT_MAP_PATH)
    concepts = concepts[concepts["canonical_field"].isin(extracted)].copy()
    rows: list[dict[str, Any]] = []
    for concept in concepts.itertuples(index=False):
        for priority, source_tag in enumerate(
            str(concept.source_tag).split("|"), start=1
        ):
            if not source_tag:
                continue
            rows.append(
                {
                    "canonical_field": concept.canonical_field,
                    "taxonomy": concept.taxonomy,
                    "source_tag": source_tag,
                    "source_priority": priority,
                    "expected_unit": concept.expected_unit,
                    "flow_or_stock": concept.flow_or_stock,
                    "sign_multiplier": concept.sign_multiplier,
                    "expected_domain": concept.expected_domain,
                }
            )
    return pd.DataFrame(rows)


def normalize_annual_facts() -> pd.DataFrame:
    universe = _read_csv(UNIVERSE_PATH, dtype={"cik": str})
    pilot_ids = set(_pilot_sample()["company_id"])
    pilot = universe[universe["company_id"].isin(pilot_ids)].copy()
    manual = _read_csv(MANUAL_FINANCIALS_PATH)
    manual["period_end_date"] = pd.to_datetime(manual["period_end_date"]).dt.date
    period_lookup = {
        (row.ticker, row.period_end_date): int(row.fiscal_year)
        for row in manual.itertuples()
        if row.ticker in set(pilot["ticker"])
    }
    manifest = _read_csv(MANIFEST_PATH)
    loaded_lookup = (
        manifest[manifest["artifact"].eq("companyfacts")]
        .set_index("ticker")["fetched_at"]
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
        for source_tag in str(formula).split("+"):
            for parsed_tag in re.findall(r"[A-Za-z][A-Za-z0-9_]*", source_tag):
                allowed_pairs.add(("us-gaap", parsed_tag))

    rows: list[dict[str, Any]] = []
    for company in pilot.sort_values("ticker").itertuples(index=False):
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
                        period_end = pd.Timestamp(item["end"]).date()
                        fiscal_year = period_lookup.get((company.ticker, period_end))
                        if fiscal_year not in PILOT_YEARS:
                            continue
                        period_start = (
                            pd.Timestamp(item["start"]).date()
                            if item.get("start")
                            else None
                        )
                        duration_days = (
                            (period_end - period_start).days
                            if period_start is not None
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
                                "period_start": (
                                    period_start.isoformat() if period_start else ""
                                ),
                                "period_end": period_end.isoformat(),
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
        raise ValueError("No B1 annual facts were normalized from cached SEC JSON")
    facts = facts.sort_values(
        ["ticker", "fiscal_year", "taxonomy", "source_tag", "filing_date"]
    )
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    facts.to_csv(UNMAPPED_PATH, index=False)
    return facts


def map_concepts_and_signs(
    unmapped_path: Path = UNMAPPED_PATH,
    financial_facts_path: Path = FINANCIAL_FACTS_PATH,
    rejection_path: Path = CANDIDATE_REJECTIONS_PATH,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    raw = _read_csv(unmapped_path, dtype={"cik": str})
    mappings = _field_map()
    mapped = raw.merge(mappings, on=["taxonomy", "source_tag"], how="inner")
    mapped["duration_days"] = pd.to_numeric(
        mapped["duration_days"], errors="coerce"
    )
    mapped["value_raw"] = pd.to_numeric(mapped["value_raw"], errors="coerce")

    mapped["rejection_reason"] = ""
    mapped.loc[
        ~mapped["source_unit"].eq(mapped["expected_unit"]), "rejection_reason"
    ] = "unit_mismatch"
    invalid_duration = mapped["flow_or_stock"].eq("flow") & ~mapped[
        "duration_days"
    ].between(330, 385, inclusive="both")
    mapped.loc[
        mapped["rejection_reason"].eq("") & invalid_duration, "rejection_reason"
    ] = "invalid_annual_duration"
    nonnegative = mapped["expected_domain"].eq("nonnegative") & mapped[
        "value_raw"
    ].lt(0)
    positive = mapped["expected_domain"].eq("positive") & mapped[
        "value_raw"
    ].le(0)
    mapped.loc[
        mapped["rejection_reason"].eq("") & (nonnegative | positive),
        "rejection_reason",
    ] = "invalid_domain"

    rejected = mapped[mapped["rejection_reason"].ne("")].copy()
    valid = mapped[mapped["rejection_reason"].eq("")].copy()
    valid["value_standardized"] = valid["value_raw"]
    valid.loc[valid["expected_unit"].eq("USD"), "value_standardized"] /= 1_000_000
    valid.loc[
        valid["sign_multiplier"].eq("abs"), "value_standardized"
    ] = valid.loc[valid["sign_multiplier"].eq("abs"), "value_standardized"].abs()
    valid["unit"] = valid["expected_unit"].replace(
        {"USD": "USD_millions", "shares": "shares_millions"}
    )

    overrides = _read_csv(OVERRIDES_PATH)
    override_rows: list[dict[str, Any]] = []
    raw_company_years = set(
        raw[["company_id", "fiscal_year"]].assign(
            fiscal_year=lambda frame: frame["fiscal_year"].astype(int)
        ).itertuples(index=False, name=None)
    )
    for override in overrides[overrides["status"].eq("active")].itertuples(index=False):
        if (override.company_id, int(override.fiscal_year)) not in raw_company_years:
            continue
        if override.override_type == "filing_table_value":
            base_rows = raw[
                raw["company_id"].eq(override.company_id)
                & raw["fiscal_year"].astype(int).eq(int(override.fiscal_year))
                & raw["accession_number"].eq(override.accession_number)
                & raw["source_unit"].eq("USD")
            ]
            if base_rows.empty:
                raise ValueError(
                    "Filing-table override lacks an accession-level base row for "
                    f"{override.company_id} FY{override.fiscal_year}"
                )
            base = base_rows.iloc[0].to_dict()
            value_standardized = float(override.override_value_standardized)
            base.update(
                {
                    "canonical_field": override.canonical_field,
                    "source_tag": "override:" + override.source_tag_or_formula,
                    "source_priority": 0,
                    "expected_unit": "USD",
                    "flow_or_stock": "flow",
                    "sign_multiplier": "abs",
                    "expected_domain": "nonnegative",
                    "rejection_reason": "",
                    "value_raw": value_standardized * 1_000_000,
                    "value_standardized": value_standardized,
                    "unit": "USD_millions",
                    "source_url": override.source_url,
                }
            )
            override_rows.append(base)
            continue

        terms = re.findall(
            r"([+-]?)\s*([A-Za-z][A-Za-z0-9_]*)",
            override.source_tag_or_formula,
        )
        component_tags = [tag for _, tag in terms]
        components = raw[
            raw["company_id"].eq(override.company_id)
            & raw["fiscal_year"].astype(int).eq(int(override.fiscal_year))
            & raw["accession_number"].eq(override.accession_number)
            & raw["source_tag"].isin(component_tags)
            & raw["source_unit"].eq("USD")
        ].copy()
        components["duration_days"] = pd.to_numeric(
            components["duration_days"], errors="coerce"
        )
        components = components[components["duration_days"].between(330, 385)]
        components = components.sort_values("source_tag").drop_duplicates(
            "source_tag", keep="last"
        )
        if set(components["source_tag"]) != set(component_tags):
            raise ValueError(
                "Company override components are incomplete for "
                f"{override.company_id} FY{override.fiscal_year}"
            )
        base = components.iloc[0].to_dict()
        value_by_tag = components.set_index("source_tag")["value_raw"].to_dict()
        value_raw = sum(
            (-1.0 if sign == "-" else 1.0) * float(value_by_tag[tag])
            for sign, tag in terms
        )
        base.update(
            {
                "canonical_field": override.canonical_field,
                "source_tag": "override:" + override.source_tag_or_formula.replace(" ", ""),
                "source_priority": 0,
                "expected_unit": "USD",
                "flow_or_stock": "flow",
                "sign_multiplier": "abs",
                "expected_domain": "nonnegative",
                "rejection_reason": "",
                "value_raw": value_raw,
                "value_standardized": abs(value_raw) / 1_000_000,
                "unit": "USD_millions",
                "source_url": override.source_url,
            }
        )
        override_rows.append(base)
    if override_rows:
        valid = pd.concat([valid, pd.DataFrame(override_rows)], ignore_index=True)

    key = [
        "company_id",
        "fiscal_year",
        "period_end",
        "accession_number",
        "canonical_field",
    ]
    preferred = valid.sort_values("source_priority").drop_duplicates(key)
    derived_rows: list[dict[str, Any]] = []
    accession_key = ["company_id", "fiscal_year", "period_end", "accession_number"]
    for _, group in preferred.groupby(accession_key, sort=False):
        fields = set(group["canonical_field"])
        if "total_liabilities" in fields or not {
            "total_assets",
            "total_equity",
        }.issubset(fields):
            continue
        assets = group[group["canonical_field"].eq("total_assets")].iloc[0]
        equity = group[group["canonical_field"].eq("total_equity")].iloc[0]
        row = assets.to_dict()
        row.update(
            {
                "canonical_field": "total_liabilities",
                "taxonomy": "project",
                "source_tag": "derived:Assets-StockholdersEquity",
                "source_priority": 99,
                "value_raw": float(assets["value_raw"]) - float(equity["value_raw"]),
                "value_standardized": float(assets["value_standardized"])
                - float(equity["value_standardized"]),
                "flow_or_stock": "stock",
                "period_start": "",
                "duration_days": None,
            }
        )
        derived_rows.append(row)
    if derived_rows:
        valid = pd.concat([valid, pd.DataFrame(derived_rows)], ignore_index=True)

    output_columns = [
        "company_id",
        "ticker",
        "accession_number",
        "form",
        "filing_date",
        "period_start",
        "period_end",
        "fiscal_year",
        "fiscal_period",
        "duration_days",
        "canonical_field",
        "taxonomy",
        "source_tag",
        "value_raw",
        "value_standardized",
        "unit",
        "flow_or_stock",
        "source_priority",
        "source_url",
        "loaded_at",
        "cik",
        "source_unit",
        "reported_fiscal_year",
        "frame",
    ]
    facts = valid[output_columns].drop_duplicates().sort_values(
        [
            "ticker",
            "fiscal_year",
            "canonical_field",
            "filing_date",
            "source_priority",
        ]
    )
    facts.to_csv(financial_facts_path, index=False)
    rejection_columns = [
        "company_id",
        "ticker",
        "fiscal_year",
        "canonical_field",
        "taxonomy",
        "source_tag",
        "source_unit",
        "form",
        "filing_date",
        "period_start",
        "period_end",
        "duration_days",
        "accession_number",
        "value_raw",
        "rejection_reason",
    ]
    rejected[rejection_columns].to_csv(rejection_path, index=False)
    return facts, rejected


def select_latest_restated(
    financial_facts_path: Path = FINANCIAL_FACTS_PATH,
    latest_path: Path = LATEST_PATH,
    conflicts_path: Path = CONFLICTS_PATH,
    reconciliation_path: Path = RECONCILIATION_PATH,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    facts = _read_csv(financial_facts_path, dtype={"cik": str})
    facts["filing_date_parsed"] = pd.to_datetime(
        facts["filing_date"], errors="coerce"
    )
    run_date = pd.Timestamp(date.today())
    eligible = facts[facts["filing_date_parsed"].le(run_date)].copy()
    group_key = ["company_id", "fiscal_year", "canonical_field"]
    eligible = eligible.sort_values(
        group_key + ["filing_date_parsed", "source_priority", "accession_number"],
        ascending=[True, True, True, False, True, False],
    )
    winners = eligible.drop_duplicates(group_key, keep="first").copy()
    winner_lookup = winners.set_index(group_key)

    conflict_rows: list[dict[str, Any]] = []
    conflict_number = 1
    for keys, group in eligible.groupby(group_key, sort=True):
        distinct = group.drop_duplicates(
            ["source_tag", "accession_number", "value_standardized"]
        )
        if distinct["value_standardized"].nunique() <= 1:
            continue
        winner = winner_lookup.loc[keys]
        for discarded in distinct.itertuples(index=False):
            if (
                discarded.source_tag == winner["source_tag"]
                and discarded.accession_number == winner["accession_number"]
                and float(discarded.value_standardized)
                == float(winner["value_standardized"])
            ):
                continue
            relative_difference = abs(
                float(discarded.value_standardized)
                - float(winner["value_standardized"])
            ) / max(abs(float(winner["value_standardized"])), 1e-9)
            if discarded.filing_date < winner["filing_date"]:
                resolution_status = "resolved_latest_restated"
                review_note = "Later valid filing supplies the current comparative value"
            elif discarded.source_tag != winner["source_tag"]:
                resolution_status = "resolved_tag_priority"
                review_note = "Configured canonical tag priority selects the concept-aligned value"
            else:
                resolution_status = "requires_review"
                review_note = "Same-filing same-tag value difference requires filing reconciliation"
            conflict_rows.append(
                {
                    "conflict_id": f"B1-{conflict_number:05d}",
                    "company_id": keys[0],
                    "ticker": winner["ticker"],
                    "fiscal_year": keys[1],
                    "canonical_field": keys[2],
                    "winning_accession": winner["accession_number"],
                    "winning_filing_date": winner["filing_date"],
                    "winning_source_tag": winner["source_tag"],
                    "winning_value": winner["value_standardized"],
                    "discarded_accession": discarded.accession_number,
                    "discarded_filing_date": discarded.filing_date,
                    "discarded_source_tag": discarded.source_tag,
                    "discarded_value": discarded.value_standardized,
                    "relative_difference": relative_difference,
                    "conflict_severity": (
                        "high"
                        if relative_difference > 0.05
                        else "medium"
                        if relative_difference > 0.005
                        else "low"
                    ),
                    "resolution_rule": (
                        "latest valid filing then configured source-tag priority"
                    ),
                    "resolution_status": resolution_status,
                    "review_note": review_note,
                    "created_at": f"{date.today().isoformat()}T00:00:00+00:00",
                }
            )
            conflict_number += 1

    conflict_columns = [
        "conflict_id",
        "company_id",
        "ticker",
        "fiscal_year",
        "canonical_field",
        "winning_accession",
        "winning_filing_date",
        "winning_source_tag",
        "winning_value",
        "discarded_accession",
        "discarded_filing_date",
        "discarded_source_tag",
        "discarded_value",
        "relative_difference",
        "conflict_severity",
        "resolution_rule",
        "resolution_status",
        "review_note",
        "created_at",
    ]
    conflicts = pd.DataFrame(conflict_rows, columns=conflict_columns)
    conflicts.to_csv(conflicts_path, index=False)

    winners["is_latest_restated"] = True
    winners["source_selection_method"] = "latest_valid_restated_sec_companyfacts"
    winners["source_selection_note"] = (
        f"Latest valid filing available as of {date.today().isoformat()}; "
        "configured source-tag priority breaks valid same-filing ties"
    )
    winners = winners.drop(columns=["filing_date_parsed"])

    derived_rows: list[dict[str, Any]] = []
    for _, group in winners.groupby(["company_id", "fiscal_year"], sort=False):
        fields = set(group["canonical_field"])
        if not {"operating_cash_flow", "capital_expenditure"}.issubset(fields):
            continue
        ocf = group[group["canonical_field"].eq("operating_cash_flow")].iloc[0]
        capex = group[group["canonical_field"].eq("capital_expenditure")].iloc[0]
        row = ocf.to_dict()
        row.update(
            {
                "canonical_field": "free_cash_flow",
                "taxonomy": "project",
                "source_tag": "derived:OperatingCashFlow-CapitalExpenditure",
                "source_priority": 0,
                "value_raw": None,
                "value_standardized": float(ocf["value_standardized"])
                - float(capex["value_standardized"]),
                "source_selection_method": "derived_from_latest_valid_components",
                "source_selection_note": "Operating cash flow minus positive CapEx outflow",
            }
        )
        derived_rows.append(row)
    if derived_rows:
        winners = pd.concat([winners, pd.DataFrame(derived_rows)], ignore_index=True)
    winners = winners.sort_values(["ticker", "fiscal_year", "canonical_field"])
    winners.to_csv(latest_path, index=False)

    manual = _read_csv(MANUAL_FINANCIALS_PATH)
    manual_fields = sorted(set(winners["canonical_field"]) & set(manual.columns))
    manual_long = manual.melt(
        id_vars=["ticker", "fiscal_year"],
        value_vars=manual_fields,
        var_name="canonical_field",
        value_name="manual_value",
    )
    manual_long["manual_value"] = pd.to_numeric(
        manual_long["manual_value"], errors="coerce"
    )
    reconciliation = winners.merge(
        manual_long,
        on=["ticker", "fiscal_year", "canonical_field"],
        how="left",
    )
    reconciliation["absolute_gap"] = (
        reconciliation["value_standardized"] - reconciliation["manual_value"]
    ).abs()
    reconciliation["relative_gap"] = reconciliation["absolute_gap"] / reconciliation[
        "manual_value"
    ].abs().clip(lower=1e-9)
    reconciliation["match_within_tolerance"] = reconciliation[
        "absolute_gap"
    ].le(reconciliation["manual_value"].abs().mul(0.005).clip(lower=0.01))
    reconciliation["reconciliation_status"] = reconciliation.apply(
        lambda row: "manual_value_unavailable"
        if pd.isna(row["manual_value"])
        else "match"
        if bool(row["match_within_tolerance"])
        else "review_company_mapping",
        axis=1,
    )
    reconciliation.to_csv(reconciliation_path, index=False)
    return winners, conflicts, reconciliation


def validate_pilot() -> tuple[pd.DataFrame, pd.DataFrame]:
    facts = _read_csv(FINANCIAL_FACTS_PATH, dtype={"cik": str})
    latest = _read_csv(LATEST_PATH, dtype={"cik": str})
    conflicts = _read_csv(CONFLICTS_PATH)
    rejected = _read_csv(CANDIDATE_REJECTIONS_PATH)
    sample = _pilot_sample()
    contract = _read_csv(FIELD_CONTRACT_PATH)
    extracted = contract[
        contract["load_to_formal_layer"].astype(int).eq(1)
        & ~contract["field_role"].eq("derived")
    ]
    extracted_fields = set(extracted["canonical_field"])
    required_fields = set(
        extracted.loc[extracted["requiredness"].eq("required"), "canonical_field"]
    )

    critical_errors: list[dict[str, str]] = []
    required_schema = {
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
    }
    missing_schema = sorted(required_schema - set(facts.columns))
    if missing_schema:
        critical_errors.append(
            {
                "stage": "validate",
                "company_id": "",
                "error_type": "missing_schema_columns",
                "message": "|".join(missing_schema),
            }
        )
    if facts["accession_number"].eq("").any():
        critical_errors.append(
            {
                "stage": "validate",
                "company_id": "",
                "error_type": "missing_accession",
                "message": "One or more normalized facts lack accession metadata",
            }
        )

    coverage_rows: list[dict[str, Any]] = []
    for company in sample.sort_values("ticker").itertuples(index=False):
        for field in sorted(extracted_fields):
            observed = latest[
                latest["company_id"].eq(company.company_id)
                & latest["canonical_field"].eq(field)
            ]
            years = sorted(set(pd.to_numeric(observed["fiscal_year"], errors="coerce").dropna().astype(int)))
            coverage_rows.append(
                {
                    "company_id": company.company_id,
                    "ticker": company.ticker,
                    "canonical_field": field,
                    "requiredness": extracted.set_index("canonical_field").loc[
                        field, "requiredness"
                    ],
                    "years_present": "|".join(map(str, years)),
                    "year_count": len(years),
                    "expected_year_count": 3,
                    "coverage_complete_flag": int(set(years) == PILOT_YEARS),
                }
            )
    coverage = pd.DataFrame(coverage_rows)
    coverage.to_csv(COVERAGE_PATH, index=False)

    wide = latest.pivot_table(
        index=["company_id", "ticker", "fiscal_year"],
        columns="canonical_field",
        values="value_standardized",
        aggfunc="first",
    ).reset_index()
    for field in extracted_fields | {"free_cash_flow"}:
        if field not in wide:
            wide[field] = pd.NA
    wide = wide.sort_values(["company_id", "fiscal_year"])
    wide["prior_fiscal_year"] = wide.groupby("company_id")["fiscal_year"].shift(1)
    wide["prior_assets"] = wide.groupby("company_id")["total_assets"].shift(1)
    wide["prior_equity"] = wide.groupby("company_id")["total_equity"].shift(1)
    wide["average_assets"] = (wide["total_assets"] + wide["prior_assets"]) / 2
    wide["average_equity"] = (wide["total_equity"] + wide["prior_equity"]) / 2

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
        for field in sorted(required_fields):
            if pd.isna(getattr(row, field)):
                add_flag(
                    row.company_id,
                    int(row.fiscal_year),
                    field,
                    "missing_required_field",
                    "high",
                    f"Required Gate 1 field {field} is missing",
                    field,
                )
        if pd.isna(row.prior_assets) or int(row.prior_fiscal_year) != int(row.fiscal_year) - 1:
            add_flag(
                row.company_id,
                int(row.fiscal_year),
                "dupont",
                "missing_prior_balance",
                "high",
                "Consecutive prior-year assets/equity are unavailable",
                "total_assets|total_equity",
            )
        elif row.average_equity <= 0:
            add_flag(
                row.company_id,
                int(row.fiscal_year),
                "roe",
                "non_positive_average_equity",
                "high",
                "Average equity is nonpositive; ROE is invalid",
                "total_equity",
            )
        for metric_name, value, fields in [
            ("net_margin", row.revenue, "revenue"),
            ("asset_turnover", row.average_assets, "total_assets"),
            ("roe", row.average_equity, "total_equity"),
        ]:
            if pd.notna(value) and float(value) == 0:
                add_flag(
                    row.company_id,
                    int(row.fiscal_year),
                    metric_name,
                    "zero_denominator",
                    "high",
                    "Metric denominator equals zero",
                    fields,
                )
        if int(row.fiscal_year) == max(PILOT_YEARS):
            add_flag(
                row.company_id,
                int(row.fiscal_year),
                "h1_outcome",
                "insufficient_forward_year",
                "medium",
                "No t+1 year exists inside the B1 Pilot window",
                "roe",
            )

    for conflict in conflicts.itertuples(index=False):
        if conflict.conflict_severity in {"medium", "high"}:
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
        if rejection.rejection_reason in {"unit_mismatch", "invalid_domain"}:
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
    pd.DataFrame(
        critical_errors,
        columns=["stage", "company_id", "error_type", "message"],
    ).to_csv(VALIDATION_ERRORS_PATH, index=False)
    if critical_errors:
        raise ValueError(f"B1 validation found {len(critical_errors)} critical errors")
    return coverage, flags


def load_duckdb() -> None:
    tables = {
        "company_universe": _read_csv(UNIVERSE_PATH, dtype={"cik": str}),
        "events": _read_csv(EVENTS_PATH),
        "financial_facts": _read_csv(FINANCIAL_FACTS_PATH, dtype={"cik": str}),
        "concept_map": _read_csv(CONCEPT_MAP_PATH),
        "concept_conflicts": _read_csv(CONFLICTS_PATH),
        "metric_flags": _read_csv(METRIC_FLAGS_PATH),
        "q1_latest_restated": _read_csv(LATEST_PATH, dtype={"cik": str}),
        "b1_pilot_coverage": _read_csv(COVERAGE_PATH),
        "b1_candidate_rejections": _read_csv(CANDIDATE_REJECTIONS_PATH),
        "company_overrides": _read_csv(OVERRIDES_PATH),
    }
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(DB_PATH)) as connection:
        for table_name, frame in tables.items():
            connection.register(f"{table_name}_input", frame)
            connection.execute(
                f"create or replace table {table_name} as "
                f"select * from {table_name}_input"
            )


def build_pilot_marts() -> dict[str, int]:
    latest = _read_csv(LATEST_PATH)
    sample = _pilot_sample()
    universe = _read_csv(UNIVERSE_PATH)
    period_end = (
        latest.groupby(["company_id", "ticker", "fiscal_year"])["period_end"]
        .max()
        .rename("period_end_date")
    )
    wide = latest.pivot_table(
        index=["company_id", "ticker", "fiscal_year"],
        columns="canonical_field",
        values="value_standardized",
        aggfunc="first",
    ).join(period_end).reset_index()
    for field in _read_csv(FIELD_CONTRACT_PATH).query(
        "load_to_formal_layer == 1"
    )["canonical_field"]:
        if field not in wide:
            wide[field] = pd.NA
    wide = wide.merge(
        sample[["company_id", "formal_peer_group"]], on="company_id", how="inner"
    ).merge(
        universe[["company_id", "company_name", "status_group"]],
        on="company_id",
        how="left",
    )
    wide["fiscal_year"] = pd.to_numeric(wide["fiscal_year"]).astype(int)
    if len(wide) != 18:
        raise ValueError(f"B1 Pilot mart source must contain 18 company-years, found {len(wide)}")

    counts: dict[str, int] = {}
    with duckdb.connect(str(DB_PATH)) as connection:
        connection.register("b1_pilot_wide_input", wide)
        connection.execute(PILOT_MART_SQL.read_text(encoding="utf-8"))
        for table_name in MART_EXPORTS:
            frame = connection.execute(f"select * from {table_name}").fetchdf()
            frame.to_csv(PROCESSED / f"{table_name}.csv", index=False)
            counts[table_name] = len(frame)
    return counts


def _write_reconciliation_report(reconciliation: pd.DataFrame) -> None:
    core = {"revenue", "net_income", "total_assets", "total_equity"}
    sample = reconciliation[
        reconciliation["ticker"].isin(["AMZN", "CHWY"])
        & reconciliation["fiscal_year"].astype(int).eq(2023)
        & reconciliation["canonical_field"].isin(core)
    ].copy()
    lines = [
        "# B1 Filing Reconciliation",
        "",
        f"Revalidated: {date.today().isoformat()}",
        "",
        "This B1 check compares the scripted latest-valid SEC selection with the existing manually transcribed annual filing values. It does not overwrite either source.",
        "",
        "| Ticker | FY | Field | SEC latest | Manual | Status | Accession |",
        "| --- | ---: | --- | ---: | ---: | --- | --- |",
    ]
    for row in sample.sort_values(["ticker", "canonical_field"]).itertuples(index=False):
        manual_value = "" if pd.isna(row.manual_value) else f"{row.manual_value:,.3f}"
        lines.append(
            f"| {row.ticker} | {int(row.fiscal_year)} | {row.canonical_field} | "
            f"{row.value_standardized:,.3f} | {manual_value} | "
            f"{row.reconciliation_status} | {row.accession_number} |"
        )
    lines.extend(
        [
            "",
            "AMZN supplies the clean filing check. CHWY supplies the complex 52/53-week and comparative-restatement check. Review differences remain explicit in `sec_manual_reconciliation.csv`; no processed value is hand-edited.",
        ]
    )
    (DOCS / "b1_filing_reconciliation.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def _write_coverage_report(
    coverage: pd.DataFrame,
    conflicts: pd.DataFrame,
    flags: pd.DataFrame,
    reconciliation: pd.DataFrame,
) -> None:
    sample = _pilot_sample()
    lines = [
        "# B1 Pilot Pipeline Report",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "Status: **Done - revalidated against Gate1-v1.0**",
        "",
        "The six companies remain the Pilot. They do not define the 21-company formal sample.",
        "",
        "## Selection Coverage",
        "",
        "- AMZN and CHWY: Inventory-led E-commerce; CHWY tests a 52/53-week fiscal year.",
        "- BKNG, DASH, EBAY, and ETSY: Marketplace / Platform.",
        "- CHWY and EBAY provide restatement/concept-conflict cases.",
        "- BKNG and ETSY provide near-zero or nonpositive-equity metric-invalid cases.",
        "- AMZN and CHWY provide filing reconciliation cases.",
        "",
        "## Pipeline Evidence",
        "",
        "| Ticker | Complete extracted fields | Extracted fields | Medium/high conflicts | Metric flags | Reconciliation reviews |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for company in sample.sort_values("ticker").itertuples(index=False):
        company_coverage = coverage[coverage["company_id"].eq(company.company_id)]
        company_conflicts = conflicts[
            conflicts["company_id"].eq(company.company_id)
            & conflicts["conflict_severity"].isin(["medium", "high"])
        ]
        company_flags = flags[flags["company_id"].eq(company.company_id)]
        company_reviews = reconciliation[
            reconciliation["company_id"].eq(company.company_id)
            & reconciliation["reconciliation_status"].eq("review_company_mapping")
        ]
        lines.append(
            f"| {company.ticker} | {int(company_coverage['coverage_complete_flag'].sum())} | "
            f"{len(company_coverage)} | {len(company_conflicts)} | {len(company_flags)} | "
            f"{len(company_reviews)} |"
        )
    lines.extend(
        [
            "",
        "The scripted order is Extract -> Normalize -> Map & Sign -> Conflicts -> Latest-restated -> Validate -> DuckDB -> Pilot marts. Extraction and validation errors have dedicated CSV logs. DASH and ETSY use documented CapEx aggregation overrides after the shared single-tag rule failed filing reconciliation.",
            "",
            "DuPont identity and Shapley reconciliation are tested automatically. The Pilot H1 result does not determine the frozen formal Tier B conclusion.",
        ]
    )
    (DOCS / "b1_pilot_coverage_report.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def build_b1_pilot(refresh: bool = False) -> dict[str, Any]:
    pilot_ids = set(_pilot_sample()["company_id"])
    manifest = extract_pilot_sec(refresh=refresh)
    unmapped = normalize_annual_facts()
    facts, rejected = map_concepts_and_signs()
    latest, conflicts, reconciliation = select_latest_restated()
    coverage, flags = validate_pilot()
    load_duckdb()
    mart_counts = build_pilot_marts()
    _write_reconciliation_report(reconciliation)
    _write_coverage_report(coverage, conflicts, flags, reconciliation)
    for source, destination in [
        (FINANCIAL_FACTS_PATH, B1_FINANCIAL_FACTS_SNAPSHOT),
        (LATEST_PATH, B1_LATEST_SNAPSHOT),
        (CONFLICTS_PATH, B1_CONFLICTS_SNAPSHOT),
        (RECONCILIATION_PATH, B1_RECONCILIATION_SNAPSHOT),
    ]:
        shutil.copyfile(source, destination)

    with duckdb.connect(str(DB_PATH), read_only=True) as connection:
        max_dupont_gap = connection.execute(
            "select coalesce(max(abs(dupont_identity_gap)), 0) "
            "from b1_pilot_annual_company_metrics where dupont_valid_flag"
        ).fetchone()[0]
        max_shapley_gap = connection.execute(
            "select coalesce(max(abs(shapley_reconciliation_gap)), 0) "
            "from b1_pilot_dupont_contributions where transition_valid_flag"
        ).fetchone()[0]

    summary = {
        "generated_on": date.today().isoformat(),
        "gate1_contract": "Gate1-v1.0",
        "gate1_status": "Passed",
        "gate2_status": "Pending formal Gate 2 after B5",
        "pipeline_order": [
            "extract",
            "normalize",
            "map_and_sign",
            "conflicts",
            "latest_restated",
            "validate",
            "duckdb",
            "pilot_marts",
        ],
        "pilot_company_count": 6,
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
        "reconciliation_review_count": int(
            reconciliation["reconciliation_status"]
            .eq("review_company_mapping")
            .sum()
        ),
        "max_dupont_identity_gap": float(max_dupont_gap),
        "max_shapley_reconciliation_gap": float(max_shapley_gap),
        "processed_generation": "scripted_no_manual_processed_edits",
        "company_override_count": int(
            _read_csv(OVERRIDES_PATH)
            .query("status == 'active' and company_id in @pilot_ids")[["company_id", "canonical_field"]]
            .drop_duplicates()
            .shape[0]
        ),
        "mart_row_counts": mart_counts,
    }
    AUDIT_PATH.write_text(
        json.dumps(summary, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    return summary
