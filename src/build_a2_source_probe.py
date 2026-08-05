from __future__ import annotations

import gzip
import hashlib
import json
from datetime import date
from pathlib import Path

import nbformat as nbf
import pandas as pd
from nbclient import NotebookClient

from phase_a_evidence import (
    A2_EXTRACTION_ERRORS_PATH,
    A2_PROBE_MANIFEST_PATH,
    A2_PROBE_SCOPE_PATH,
    CONCEPT_MAP_PATH,
    FINANCIAL_FACTS_PATH,
    ROOT,
    build_company_universe,
    extract_a2_probe,
    normalize_annual_facts,
)


PROBE_FIELDS = [
    "revenue",
    "net_income",
    "total_assets",
    "total_equity",
    "cash_and_equivalents",
    "inventory",
    "current_assets",
    "current_liabilities",
    "total_debt",
    "operating_cash_flow",
    "capital_expenditure",
]
FIRST_ROUND_FIELDS = {"revenue", "net_income", "total_assets", "total_equity"}
FIELD_PROBE_PATH = ROOT / "data/processed/a2_field_probe.csv"
FACT_SAMPLE_PATH = ROOT / "data/normalized/a2_annual_financial_facts_sample.csv"
LATEST_SAMPLE_PATH = ROOT / "data/processed/a2_latest_restated_sample.csv"
CONFLICT_SAMPLE_PATH = ROOT / "data/processed/a2_concept_conflicts_sample.csv"
AUDIT_PATH = ROOT / "data/processed/a2_source_probe_audit.json"
REPORT_PATH = ROOT / "docs/source_probe_report.md"
NOTEBOOK_PATH = ROOT / "notebooks/01_source_probe.ipynb"
A3_REQUIREMENTS_PATH = ROOT / "data/reference/a3_scan_requirements.csv"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _select_latest_current(
    facts: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    run_date = pd.Timestamp(date.today())
    eligible = facts.copy()
    eligible["filing_date_parsed"] = pd.to_datetime(
        eligible["filing_date"], errors="coerce"
    )
    eligible = eligible[eligible["filing_date_parsed"].le(run_date)].copy()
    group_key = ["ticker", "fiscal_year", "canonical_field"]
    eligible = eligible.sort_values(
        group_key + ["filing_date_parsed", "source_priority", "accession"],
        ascending=[True, True, True, False, True, False],
    )
    winners = eligible.drop_duplicates(group_key, keep="first").copy()
    winners["is_latest_restated"] = True
    winners["source_selection_note"] = (
        f"Latest valid annual filing available by {run_date.date().isoformat()} after "
        "unit and duration validation; configured tag priority breaks same-date ties"
    )

    winner_lookup = winners.set_index(group_key)
    conflict_rows: list[dict[str, object]] = []
    for keys, group in eligible.groupby(group_key, sort=True):
        distinct = group.drop_duplicates(
            ["source_tag", "accession", "value_standardized"]
        )
        if distinct["value_standardized"].nunique() <= 1:
            continue
        winner = winner_lookup.loc[keys]
        for _, discarded in distinct.iterrows():
            if (
                discarded["source_tag"] == winner["source_tag"]
                and discarded["accession"] == winner["accession"]
                and float(discarded["value_standardized"])
                == float(winner["value_standardized"])
            ):
                continue
            denominator = max(abs(float(winner["value_standardized"])), 1e-9)
            relative_difference = abs(
                float(discarded["value_standardized"])
                - float(winner["value_standardized"])
            ) / denominator
            conflict_rows.append(
                {
                    "company_id": winner["company_id"],
                    "period_end": winner["period_end"],
                    "canonical_field": keys[2],
                    "winning_tag": winner["source_tag"],
                    "discarded_tag": discarded["source_tag"],
                    "winning_value": winner["value_standardized"],
                    "discarded_value": discarded["value_standardized"],
                    "relative_difference": relative_difference,
                    "resolution_rule": (
                        "latest valid filing then configured source-tag priority"
                    ),
                    "conflict_severity": (
                        "high"
                        if relative_difference > 0.05
                        else "medium"
                        if relative_difference > 0.005
                        else "low"
                    ),
                    "winning_accession": winner["accession"],
                    "discarded_accession": discarded["accession"],
                    "winning_filing_date": winner["filing_date"],
                    "discarded_filing_date": discarded["filing_date"],
                }
            )

    conflict_columns = [
        "company_id",
        "period_end",
        "canonical_field",
        "winning_tag",
        "discarded_tag",
        "winning_value",
        "discarded_value",
        "relative_difference",
        "resolution_rule",
        "conflict_severity",
        "winning_accession",
        "discarded_accession",
        "winning_filing_date",
        "discarded_filing_date",
    ]
    conflicts = pd.DataFrame(conflict_rows, columns=conflict_columns)
    return winners.drop(columns=["filing_date_parsed"]), conflicts


def _raw_tag_observations(cik: str, concept: pd.Series) -> dict[str, str]:
    path = ROOT / f"data/raw/sec/CIK{int(cik):010d}/companyfacts.json.gz"
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        payload = json.load(handle)
    source_tags = [tag for tag in str(concept["source_tag"]).split("|") if tag]
    observed_tags: list[str] = []
    observed_units: set[str] = set()
    observed_taxonomies: set[str] = set()
    for taxonomy in [str(concept["taxonomy"])]:
        taxonomy_facts = payload.get("facts", {}).get(taxonomy, {})
        for source_tag in source_tags:
            raw_fact = taxonomy_facts.get(source_tag)
            if not raw_fact:
                continue
            observed_tags.append(source_tag)
            observed_units.update(raw_fact.get("units", {}).keys())
            observed_taxonomies.add(taxonomy)
    return {
        "raw_observed_tags": "|".join(observed_tags),
        "raw_observed_taxonomies": "|".join(sorted(observed_taxonomies)),
        "raw_observed_units": "|".join(sorted(observed_units)),
    }


def _build_field_probe(
    scope: pd.DataFrame, concepts: pd.DataFrame, facts: pd.DataFrame
) -> pd.DataFrame:
    universe = pd.read_csv(
        ROOT / "data/reference/company_universe.csv",
        dtype={"cik": str},
        keep_default_na=False,
    ).set_index("company_id")
    concept_by_field = concepts.set_index("canonical_field")
    rows: list[dict[str, object]] = []
    for company in scope.itertuples():
        cik = universe.loc[company.company_id, "cik"]
        company_facts = facts[facts["ticker"].eq(company.ticker)]
        for field in PROBE_FIELDS:
            concept = concept_by_field.loc[field]
            selected = company_facts[company_facts["canonical_field"].eq(field)]
            raw = _raw_tag_observations(cik, concept)
            duration_values = sorted(
                {
                    int(float(value))
                    for value in selected["duration_days"]
                    if str(value).strip()
                }
            )
            version_max = (
                int(selected.groupby("fiscal_year").size().max())
                if not selected.empty
                else 0
            )
            if field == "inventory" and selected.empty and company.ticker == "EBAY":
                override = "not_applicable_marketplace"
            elif field == "total_debt" and selected.empty:
                override = "filing_verification_or_documented_aggregation"
            elif selected.empty:
                override = "coverage_review"
            else:
                override = "none_observed_in_probe"
            rows.append(
                {
                    "company_id": company.company_id,
                    "ticker": company.ticker,
                    "probe_role": company.probe_role,
                    "field_round": (
                        "first_round_required"
                        if field in FIRST_ROUND_FIELDS
                        else "second_round_conditional"
                    ),
                    "canonical_field": field,
                    "configured_tags": concept["source_tag"],
                    **raw,
                    "normalized_source_tags": "|".join(
                        sorted(selected["source_tag"].unique())
                    ),
                    "normalized_units": "|".join(sorted(selected["unit"].unique())),
                    "normalized_fact_rows": int(len(selected)),
                    "fiscal_years": "|".join(
                        str(value) for value in sorted(selected["fiscal_year"].unique())
                    ),
                    "period_ends": "|".join(sorted(selected["period_end"].unique())),
                    "duration_days": "|".join(str(value) for value in duration_values),
                    "raw_fy_values": "|".join(
                        sorted(str(value) for value in selected["fy"].unique())
                    ),
                    "raw_fp_values": "|".join(
                        sorted(str(value) for value in selected["fp"].unique())
                    ),
                    "accession_complete": int(
                        not selected.empty and selected["accession"].str.len().gt(0).all()
                    ),
                    "filing_date_complete": int(
                        not selected.empty
                        and pd.to_datetime(
                            selected["filing_date"], errors="coerce"
                        ).notna().all()
                    ),
                    "multiple_filing_versions": int(version_max > 1),
                    "max_versions_per_fiscal_year": version_max,
                    "company_override_candidate": override,
                    "fiscal_period_note": (
                        "52/53-week period; map project fiscal year from period end"
                        if company.ticker == "CHWY"
                        else "Comparative facts repeat filer FY metadata; map project fiscal year from period end"
                    ),
                }
            )
    probe = pd.DataFrame(rows)
    companies_with_facts = (
        probe[probe["normalized_fact_rows"].gt(0)]
        .groupby("canonical_field")["ticker"]
        .nunique()
        .to_dict()
    )
    probe["shared_mapping_status"] = probe["canonical_field"].map(
        lambda field: (
            "shared_direct"
            if companies_with_facts.get(field, 0) == 2
            else "conditional_not_applicable"
            if field == "inventory"
            else "company_review_required"
        )
    )
    return probe


def _write_a3_requirements() -> pd.DataFrame:
    rows = [
        ("annual", "company_id", "Stable link to the completed A1 census"),
        ("annual", "fiscal_year", "FY2018-FY2024 coverage by project fiscal year"),
        ("annual", "core_field_coverage", "Coverage for Gate 1 canonical field candidates"),
        ("annual", "prior_balance_available", "Opening assets and equity for average balances"),
        ("annual", "unit_duration_valid", "Expected units and flow/stock period rules"),
        ("annual", "filing_version_count", "Restatement and comparative-version visibility"),
        ("annual", "tag_conflict_count", "Winner/discarded conflicts by field and company"),
        ("annual", "latest_restated_selectable", "Valid explainable current winner"),
        ("annual", "override_required", "Company exception and review reason"),
        ("annual", "manual_review_minutes", "Observed incremental review cost"),
        ("h1", "transition_eligibility", "All frozen H1 eligibility components"),
        ("h1", "driver_group", "Leverage-driven versus operating-driven"),
        ("h1", "next_year_observable", "Forward-year outcome availability"),
        ("h1", "company_concentration", "Unique-company and group concentration"),
        ("event", "verified_pre_event_quarters", "Real quarters, not listing-age estimate"),
        ("event", "three_statement_coverage", "Quarterly IS/BS/CF availability"),
        ("event", "filing_dates_available", "Point-in-time public availability"),
        ("event", "pit_feasible", "No look-ahead in event-time features"),
        ("event", "ytd_cashflow_reconstruction", "Whether standalone quarters require reconstruction"),
        ("event", "eligible_controls", "Contemporaneous peer/control availability"),
        ("event", "manual_review_cost", "Per-event quarterly normalization burden"),
    ]
    requirements = pd.DataFrame(rows, columns=["scan_area", "metric", "purpose"])
    requirements.to_csv(A3_REQUIREMENTS_PATH, index=False)
    return requirements


def _write_notebook() -> None:
    notebook = nbf.v4.new_notebook()
    notebook["metadata"]["kernelspec"] = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }
    notebook["cells"] = [
        nbf.v4.new_markdown_cell(
            "# A2 Two-company SEC Source Probe\n\n"
            "Formal probe for CHWY (Inventory-led) and EBAY (Marketplace / Platform)."
        ),
        nbf.v4.new_code_cell(
            "from pathlib import Path\n"
            "import json\n"
            "import pandas as pd\n"
            "from IPython.display import display\n\n"
            "ROOT = Path.cwd()\n"
            "if ROOT.name == 'notebooks': ROOT = ROOT.parent\n"
            "pd.set_option('display.max_colwidth', 120)"
        ),
        nbf.v4.new_code_cell(
            "scope = pd.read_csv(ROOT / 'data/reference/a2_probe_scope.csv')\n"
            "manifest = pd.read_csv(ROOT / 'data/raw/sec/a2_probe_manifest.csv', dtype={'cik': str})\n"
            "display(scope)\n"
            "display(manifest[['company_id','ticker','artifact','relative_path','sha256']])"
        ),
        nbf.v4.new_code_cell(
            "field_probe = pd.read_csv(ROOT / 'data/processed/a2_field_probe.csv')\n"
            "display(field_probe[['ticker','canonical_field','normalized_source_tags','normalized_units','duration_days','multiple_filing_versions','shared_mapping_status','company_override_candidate']])"
        ),
        nbf.v4.new_code_cell(
            "latest = pd.read_csv(ROOT / 'data/processed/a2_latest_restated_sample.csv')\n"
            "conflicts = pd.read_csv(ROOT / 'data/processed/a2_concept_conflicts_sample.csv')\n"
            "display(latest[['ticker','fiscal_year','canonical_field','source_tag','accession','filing_date','value_standardized']].head(20))\n"
            "display(conflicts.head(20))"
        ),
        nbf.v4.new_code_cell(
            "audit = json.loads((ROOT / 'data/processed/a2_source_probe_audit.json').read_text())\n"
            "display(pd.Series(audit['checks'], name='passed'))\n"
            "audit"
        ),
        nbf.v4.new_markdown_cell(
            "The probe keeps every filing-level version, validates expected units and flow durations before winner selection, and logs discarded values. Raw `fy` identifies the filing context for comparative facts, so the project fiscal year is mapped from the period end and issuer fiscal calendar. No third distress case is added at A2; event-quarter feasibility is measured across the full event pool in A3."
        ),
    ]
    nbf.write(notebook, NOTEBOOK_PATH)


def _execute_notebook() -> None:
    notebook = nbf.read(NOTEBOOK_PATH, as_version=4)
    client = NotebookClient(
        notebook,
        timeout=180,
        kernel_name="python3",
        resources={"metadata": {"path": str(ROOT)}},
    )
    client.execute()
    nbf.write(notebook, NOTEBOOK_PATH)


def _write_report(
    scope: pd.DataFrame,
    field_probe: pd.DataFrame,
    facts: pd.DataFrame,
    winners: pd.DataFrame,
    conflicts: pd.DataFrame,
) -> None:
    lines = [
        "# A2 Two-Company SEC Source Probe",
        "",
        f"Probe date: {date.today().isoformat()}",
        "",
        "Status: **Done**",
        "",
        "## Probe Selection",
        "",
        "| Company | Role | Selection reason |",
        "| --- | --- | --- |",
    ]
    for row in scope.itertuples():
        lines.append(f"| {row.ticker} | {row.probe_role} | {row.selection_reason} |")
    lines.extend(
        [
            "",
            "No third distress company is added. The two probes establish the annual extraction and metadata rules needed for A3; quarterly distress feasibility must be measured across all A1 events in A3 rather than inferred from one extra case.",
            "",
            "## Field-Level Results",
            "",
            "| Company | Canonical field | Main observed tag | Unit | Duration | Versions | Shared rule | Override status |",
            "| --- | --- | --- | --- | --- | ---: | --- | --- |",
        ]
    )
    for row in field_probe.itertuples():
        tag = row.normalized_source_tags or "Not reported"
        unit = row.normalized_units or row.raw_observed_units or "Not reported"
        duration = row.duration_days or "Instant"
        lines.append(
            f"| {row.ticker} | {row.canonical_field} | {tag} | {unit} | "
            f"{duration} | {row.max_versions_per_fiscal_year} | "
            f"{row.shared_mapping_status} | {row.company_override_candidate} |"
        )
    conflict_fields = (
        ", ".join(sorted(conflicts["canonical_field"].unique()))
        if not conflicts.empty
        else "None"
    )
    lines.extend(
        [
            "",
            "## Mapping and Version Conclusions",
            "",
            "- The same executable concept map covers Revenue, Net Income, Assets, Equity, Cash, Current Assets, Current Liabilities, OCF, and CapEx for both companies.",
            "- Inventory is valid for CHWY and not applicable to EBAY's marketplace presentation; blank is not converted to zero.",
            "- A direct Total Debt tag is available for EBAY. CHWY has no direct debt balance in Companyfacts, so zero debt requires filing verification or a documented override rather than an automated assumption.",
            "- CHWY CapEx uses `PaymentsToAcquireProductiveAssets`; EBAY uses `PaymentsToAcquirePropertyPlantAndEquipment`. Ordered tag alternatives therefore remain necessary.",
            "- All normalized flow facts satisfy the 330-385 day annual rule. CHWY's 363-day fiscal periods demonstrate why calendar-year assumptions are unsafe.",
            "- Raw `fy` values describe the filing context and can differ from the comparative period's project fiscal year. Period end plus the issuer fiscal calendar is the reliable year key; `fp=FY`, filing date, and accession remain available.",
            f"- {len(winners)} latest-restated winners are unique by company-period-field. Unit and duration validation occurs before filing-date ordering; {len(conflicts)} discarded value records remain traceable across: {conflict_fields}.",
            "- Conflict severity in A2 is exploratory. The final materiality threshold is not frozen until Gate 1.",
            "",
            "## Sign and Unit Rules",
            "",
            "- USD facts are standardized to USD millions; expected raw units remain recorded.",
            "- CapEx is stored as a positive cash outflow amount through an absolute-value sign rule.",
            "- OCF preserves its reported positive or negative direction.",
            "- Inventory and debt are nonnegative domains; missing values are not treated as zero without filing evidence.",
            "",
            "## Incremental Cost Estimate",
            "",
            "- Automated cost per additional company: two SEC requests on first load, then seconds for cached normalization and field diagnostics once CIK and fiscal calendar are known.",
            "- Manual review for a clean calendar-year issuer: approximately 20-30 minutes for field coverage, winner checks, and filing reconciliation.",
            "- Manual review for a 52/53-week, restated, missing-tag, or aggregation case: approximately 30-60 minutes, with the exact time to be measured in A3.",
            "",
            "## Canonical Source Decision",
            "",
            "SEC Companyfacts is suitable as the proposed Q1 canonical source for A3 scanning, provided the pipeline retains complete raw JSON, filing-level versions, expected-unit and flow-duration validation, explicit conflicts, and documented company exceptions. This is an A2 feasibility conclusion, not the Gate 1 source freeze.",
            "",
            "## Required A3 Scan",
            "",
            "A3 must collect FY2018-FY2024 core-field coverage, prior balances, version counts, unit/duration validity, tag conflicts, latest-restated selectability, override need, manual review cost, complete H1 transition eligibility, and every event's real quarterly/PIT feasibility fields. The executable metric list is stored in `data/reference/a3_scan_requirements.csv`.",
            "",
            "## DoD",
            "",
            f"- Two companies use one extraction entry: `src/extract_sec.py` ({len(facts)} filing-level annual facts in the formal sample).",
            "- Complete Companyfacts and submissions JSON are checksum-manifested under stable CIK paths.",
            "- The minimum concept map, sign rules, latest-restated selection, conflict sample, report, and notebook are executable.",
            "- A3 scan requirements are explicit; full-sample ETL and formal sample selection have not been performed in A2.",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_a2_source_probe() -> dict[str, object]:
    build_company_universe()
    manifest = extract_a2_probe()
    normalize_annual_facts()
    scope = pd.read_csv(A2_PROBE_SCOPE_PATH, keep_default_na=False)
    concepts = pd.read_csv(CONCEPT_MAP_PATH, keep_default_na=False)
    all_facts = pd.read_csv(
        FINANCIAL_FACTS_PATH, dtype={"cik": str}, keep_default_na=False
    )
    facts = all_facts[
        all_facts["ticker"].isin(scope["ticker"])
        & all_facts["canonical_field"].isin(PROBE_FIELDS)
    ].copy()
    winners, conflicts = _select_latest_current(facts)
    field_probe = _build_field_probe(scope, concepts, facts)
    _write_a3_requirements()

    FACT_SAMPLE_PATH.parent.mkdir(parents=True, exist_ok=True)
    facts.to_csv(FACT_SAMPLE_PATH, index=False)
    winners.to_csv(LATEST_SAMPLE_PATH, index=False)
    conflicts.to_csv(CONFLICT_SAMPLE_PATH, index=False)
    field_probe.to_csv(FIELD_PROBE_PATH, index=False)
    _write_notebook()
    _write_report(scope, field_probe, facts, winners, conflicts)

    concept_required_columns = {
        "canonical_field",
        "taxonomy",
        "source_tag",
        "priority",
        "statement_type",
        "flow_or_stock",
        "expected_unit",
        "sign_multiplier",
        "expected_domain",
        "duration_rule",
        "notes",
    }
    error_log = pd.read_csv(A2_EXTRACTION_ERRORS_PATH, keep_default_na=False)
    flow = facts[facts["canonical_field"].isin(
        ["revenue", "net_income", "operating_cash_flow", "capital_expenditure"]
    )]
    checks = {
        "probe_roles_exact": set(scope["probe_role"])
        == {"Inventory-led E-commerce", "Marketplace / Platform"},
        "single_extraction_entry_exists": (ROOT / "src/extract_sec.py").exists(),
        "raw_manifest_complete": len(manifest) == 4,
        "raw_checksums_valid": all(
            _sha256(ROOT / row.relative_path) == row.sha256
            for row in manifest.itertuples()
        ),
        "extraction_error_log_clear": error_log.empty,
        "concept_map_executable": concept_required_columns.issubset(concepts.columns),
        "all_first_round_fields_observed": set(FIRST_ROUND_FIELDS).issubset(
            set(facts["canonical_field"])
        ),
        "filing_metadata_complete": facts["accession"].str.len().gt(0).all()
        and pd.to_datetime(facts["filing_date"], errors="coerce").notna().all(),
        "annual_flow_durations_valid": flow["duration_days"]
        .astype(float)
        .between(330, 385)
        .all(),
        "latest_winners_unique": not winners.duplicated(
            ["ticker", "fiscal_year", "canonical_field"]
        ).any(),
        "conflict_log_schema_complete": {
            "winning_tag",
            "discarded_tag",
            "relative_difference",
            "resolution_rule",
        }.issubset(conflicts.columns),
        "capex_sign_rule_explicit": concepts.set_index("canonical_field").loc[
            "capital_expenditure", "sign_multiplier"
        ]
        == "abs",
        "ocf_sign_rule_explicit": str(
            concepts.set_index("canonical_field").loc[
                "operating_cash_flow", "sign_multiplier"
            ]
        )
        == "1",
        "a3_scan_design_written": A3_REQUIREMENTS_PATH.exists(),
        "probe_report_written": REPORT_PATH.exists(),
        "probe_notebook_written": NOTEBOOK_PATH.exists(),
        "third_case_not_added": scope["third_case_required"].eq(0).all(),
    }
    checks = {key: bool(value) for key, value in checks.items()}
    if not all(checks.values()):
        failures = [key for key, value in checks.items() if not value]
        raise ValueError(f"A2 source probe audit failed: {failures}")

    audit = {
        "generated_on": date.today().isoformat(),
        "stage": "A2 Two-company Source Probe",
        "status": "Done",
        "probe_companies": scope["ticker"].tolist(),
        "raw_artifact_count": int(len(manifest)),
        "annual_fact_sample_rows": int(len(facts)),
        "latest_winner_rows": int(len(winners)),
        "conflict_rows": int(len(conflicts)),
        "field_probe_rows": int(len(field_probe)),
        "canonical_source_conclusion": "suitable_for_a3_with_validation",
        "third_distress_case": "not_required",
        "gate1_status": "pending_a3",
        "checks": checks,
        "next_stage": "A3 Coverage Verification + H1 Sample Audit",
    }
    AUDIT_PATH.write_text(
        json.dumps(audit, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    _execute_notebook()
    return audit


if __name__ == "__main__":
    result = build_a2_source_probe()
    print(
        "A2 source probe passed: "
        f"{result['annual_fact_sample_rows']} facts, "
        f"{result['conflict_rows']} conflicts"
    )
