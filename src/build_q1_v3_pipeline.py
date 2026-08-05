from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd

from q1_formal_pipeline import build_b2_formal_sample


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "db" / "financial_health_screener.duckdb"
PROCESSED = ROOT / "data" / "processed"
REFERENCE = ROOT / "data" / "reference"
DOCS = ROOT / "docs"

SQL_FILES = [ROOT / "sql" / f"{number:02d}_{name}.sql" for number, name in [
    (1, "core_tables"),
    (2, "q1_latest_restated"),
    (3, "q1_metrics"),
    (4, "q1_shapley_contributions"),
    (5, "q1_persistence"),
    (6, "q1_h1_sample_audit"),
    (7, "q1_powerbi_mart"),
]]

TABLE_EXPORTS = [
    "q1_latest_restated",
    "q1_annual_company_metrics",
    "q1_dupont_contributions",
    "q1_peer_summary",
    "q1_company_vs_peer",
    "q1_driver_persistence",
    "q1_h1_sample_audit",
    "q1_h1_exclusion_waterfall",
    "q1_h1_evidence_summary",
    "q1_powerbi_mart",
]

MANDATORY_MARTS = [
    "q1_annual_company_metrics",
    "q1_dupont_contributions",
    "q1_driver_persistence",
    "q1_h1_sample_audit",
    "q1_peer_summary",
    "q1_company_vs_peer",
    "q1_powerbi_mart",
]

EXPORT_ORDER = {
    "q1_latest_restated": "company_id, fiscal_year, canonical_field",
    "q1_annual_company_metrics": "company_id, fiscal_year",
    "q1_dupont_contributions": "company_id, fiscal_year",
    "q1_peer_summary": "formal_peer_group, fiscal_year",
    "q1_company_vs_peer": "company_id, fiscal_year",
    "q1_driver_persistence": "company_id, fiscal_year",
    "q1_h1_sample_audit": "company_id, fiscal_year",
    "q1_h1_exclusion_waterfall": "transition_count desc, h1_exclusion_reason",
    "q1_powerbi_mart": "company_id, fiscal_year",
}

GRAINS = {
    "q1_latest_restated": "one formal company x fiscal year x canonical field",
    "q1_annual_company_metrics": "one formal company x available fiscal year",
    "q1_dupont_contributions": "one formal company x consecutive annual transition ending year",
    "q1_peer_summary": "one formal peer group x fiscal year",
    "q1_company_vs_peer": "one formal company x available fiscal year",
    "q1_driver_persistence": "one formal company x consecutive annual transition ending year",
    "q1_h1_sample_audit": "one formal company x candidate H1 transition ending year",
    "q1_h1_exclusion_waterfall": "one final H1 eligibility or exclusion reason",
    "q1_h1_evidence_summary": "one frozen formal Q1 panel",
    "q1_powerbi_mart": "one formal company x available fiscal year",
}

TABLE_PURPOSES = {
    "q1_latest_restated": "Interpretable latest-valid annual canonical fact selection plus derived free cash flow.",
    "q1_annual_company_metrics": "Average-balance DuPont, liquidity, leverage, cash-flow, validity, and quality metrics.",
    "q1_dupont_contributions": "Exact three-factor Shapley ROE-change attribution and frozen driver classification.",
    "q1_peer_summary": "Valid-observation peer-year medians, quartiles, and sample sizes.",
    "q1_company_vs_peer": "Company metrics joined to peer benchmarks and ROE percentile position.",
    "q1_driver_persistence": "Consecutive-year LEAD outcomes, including the peer-relative primary result.",
    "q1_h1_sample_audit": "Frozen H1 eligibility, exclusions, year distribution, and company concentration.",
    "q1_h1_exclusion_waterfall": "Transition and company counts by final H1 sample status.",
    "q1_h1_evidence_summary": "Evidence Tier, group counts, outcomes, concentration, and permitted inference.",
    "q1_powerbi_mart": "Exact Gate1-v1.0 60-field single-table Power BI consumption layer.",
}

FIELD_DESCRIPTIONS = {
    "company_id": "Stable issuer identifier used for every join and window partition.",
    "ticker": "Display ticker for the selected issuer and period.",
    "company_name": "Issuer display name from the frozen formal sample.",
    "formal_peer_group": "Gate1-v1.0 peer group used for descriptive benchmarks.",
    "fiscal_year": "Issuer fiscal year assigned by the verified annual period map.",
    "period_end_date": "Fiscal-year end date of the selected annual facts.",
    "canonical_field": "Gate 1 canonical financial concept.",
    "value_standardized": "Selected value after canonical sign and unit standardization.",
    "source_selection_method": "Deterministic latest-valid or derived-component selection method.",
    "source_selection_note": "Human-readable explanation of the source/version choice.",
    "average_assets": "Mean of consecutive prior and current fiscal-year-end total assets.",
    "average_equity": "Mean of consecutive prior and current fiscal-year-end total equity.",
    "roe": "Net income divided by positive average equity; otherwise null.",
    "net_margin": "Net income divided by revenue with zero-denominator protection.",
    "asset_turnover": "Revenue divided by average assets with zero-denominator protection.",
    "equity_multiplier": "Average assets divided by positive average equity.",
    "dupont_identity_gap": "ROE minus the product of the three DuPont components.",
    "roe_change": "Current valid ROE minus prior consecutive-year valid ROE.",
    "contribution_margin": "Exact Shapley contribution of the net-margin change to ROE change.",
    "contribution_turnover": "Exact Shapley contribution of the asset-turnover change to ROE change.",
    "contribution_multiplier": "Exact Shapley contribution of the equity-multiplier change to ROE change.",
    "contribution_sum": "Sum of the three exact Shapley contributions.",
    "shapley_reconciliation_gap": "ROE change minus the Shapley contribution sum.",
    "dominant_driver": "Largest absolute valid Shapley factor: margin, turnover, or multiplier.",
    "h1_driver_group": "Frozen leverage-driven, operating-driven, mixed, or unavailable classification.",
    "leverage_contribution_share": "Positive multiplier contribution divided by all positive contributions.",
    "next_year_peer_relative_change": "Primary outcome: next-year change in ROE minus peer median ROE.",
    "next_year_roe_change": "Secondary outcome: next-year raw ROE minus current ROE.",
    "roe_reversal_flag": "True when observable next-year raw ROE change is negative.",
    "rank_retention": "Issuer next-year ROE percentile within its formal peer group.",
    "h1_eligible_flag": "Frozen positive-equity, positive-base, positive-change, valid-component, and forward-year eligibility result.",
    "h1_exclusion_reason": "First applicable frozen H1 exclusion reason, or eligible.",
    "evidence_tier": "Recomputed H1 Evidence Tier under the frozen A/B/C thresholds.",
    "permitted_inference": "Research wording permitted by the computed Evidence Tier.",
    "quality_warnings": "Semicolon-delimited automated metric and comparability warnings.",
    "interpretation_note": "SQL-generated row-level explanation for the presentation layer.",
    "limitations_note": "SQL-generated evidence and non-PIT limitation for the presentation layer.",
}


def _field_description(table_name: str, field_name: str) -> str:
    if field_name in FIELD_DESCRIPTIONS:
        return FIELD_DESCRIPTIONS[field_name]
    readable = field_name.replace("_", " ")
    if field_name.startswith("prior_"):
        return f"Prior consecutive fiscal-year {readable.removeprefix('prior ')}."
    if field_name.startswith("next_"):
        return f"Observable next consecutive fiscal-year {readable.removeprefix('next ')}."
    if field_name.startswith("peer_median_"):
        return f"Valid-observation peer-year median {readable.removeprefix('peer median ')}."
    if field_name.startswith("peer_q25_"):
        return f"Valid-observation peer-year 25th percentile {readable.removeprefix('peer q25 ')}."
    if field_name.startswith("peer_q75_"):
        return f"Valid-observation peer-year 75th percentile {readable.removeprefix('peer q75 ')}."
    if field_name.endswith("_flag"):
        return f"Boolean indicator for {readable.removesuffix(' flag')}."
    if field_name.endswith("_count"):
        return f"Count of {readable.removesuffix(' count')} at the table grain."
    if field_name.endswith("_share"):
        return f"Share measuring {readable.removesuffix(' share')} at the table grain."
    if field_name.endswith("_gap"):
        return f"Reconciliation or comparison difference for {readable.removesuffix(' gap')}."
    return f"{readable.capitalize()} produced by {table_name}; inherited fields retain source-mart meaning."


def _serialize(value: Any) -> Any:
    if hasattr(value, "item"):
        return value.item()
    if pd.isna(value):
        return None
    return value


def _write_schema(connection: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for table_name in TABLE_EXPORTS:
        schema = connection.execute(f"describe {table_name}").fetchdf()
        for ordinal, row in enumerate(schema.itertuples(index=False), start=1):
            rows.append(
                {
                    "mart_name": table_name,
                    "grain": GRAINS[table_name],
                    "field_ordinal": ordinal,
                    "field_name": row.column_name,
                    "data_type": row.column_type,
                    "description": _field_description(table_name, row.column_name),
                }
            )
    frame = pd.DataFrame(rows)
    frame.to_csv(PROCESSED / "b3_mart_schema.csv", index=False)
    return frame


def _write_report(audit: dict[str, Any]) -> None:
    evidence = audit["h1_evidence"]
    lines = [
        "# B3 SQL Analytical Marts Report",
        "",
        f"Generated: {audit['generated_on']}",
        "",
        f"Status: **{audit['status']}**",
        "",
        "The seven SQL files run in the frozen order from formal B2 DuckDB core tables. No Gate 1 field, sample, peer, H1, source, or version rule is changed.",
        "",
        "## Mandatory Marts",
        "",
        "| Mart | Grain | Rows | Purpose |",
        "| --- | --- | ---: | --- |",
    ]
    for table_name in MANDATORY_MARTS:
        lines.append(
            f"| `{table_name}` | {GRAINS[table_name]} | "
            f"{audit['table_row_counts'][table_name]:,} | {TABLE_PURPOSES[table_name]} |"
        )
    lines.extend(
        [
            "",
            "## H1 Frozen-Rule Result",
            "",
            f"- Evidence Tier: {evidence['evidence_tier']}",
            f"- Eligible transitions: {evidence['eligible_transition_count']}",
            f"- Unique eligible companies: {evidence['eligible_unique_company_count']}",
            f"- Leverage-driven transitions: {evidence['leverage_driven_transition_count']}",
            f"- Operating-driven transitions: {evidence['operating_driven_transition_count']}",
            f"- Maximum company transition share: {evidence['maximum_company_transition_share']:.1%}",
            f"- FY2020-FY2021 transition share: {evidence['fy2020_2021_transition_share']:.1%}",
            f"- Permitted inference: {evidence['permitted_inference']}",
            "",
            "## Reconciliation",
            "",
            f"- Maximum absolute DuPont identity gap: {audit['max_abs_dupont_identity_gap']:.3e}",
            f"- Maximum absolute Shapley reconciliation gap: {audit['max_abs_shapley_reconciliation_gap']:.3e}",
            f"- Power BI fields: {audit['powerbi_field_count']} of 60 frozen contract fields",
            "- Complete field-level schema and descriptions: `data/processed/b3_mart_schema.csv`",
        ]
    )
    DOCS.joinpath("b3_sql_mart_report.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def build_b3_analytical_marts() -> dict[str, Any]:
    build_b2_formal_sample(refresh=False)
    contract = pd.read_csv(REFERENCE / "q1_powerbi_mart_contract_v1.csv")

    with duckdb.connect(str(DB_PATH)) as connection:
        for sql_path in SQL_FILES:
            connection.execute(sql_path.read_text(encoding="utf-8"))

        table_counts: dict[str, int] = {}
        for table_name in TABLE_EXPORTS:
            order = EXPORT_ORDER.get(table_name)
            order_clause = f" order by {order}" if order else ""
            output = connection.execute(
                f"select * from {table_name}{order_clause}"
            ).fetchdf()
            output.to_csv(PROCESSED / f"{table_name}.csv", index=False)
            table_counts[table_name] = len(output)

        schema = _write_schema(connection)
        powerbi_columns = [
            row[0]
            for row in connection.execute("describe q1_powerbi_mart").fetchall()
        ]
        expected_powerbi_columns = contract["field_name"].tolist()
        evidence_row = connection.execute(
            "select * from q1_h1_evidence_summary"
        ).fetchdf().iloc[0]
        evidence = {key: _serialize(value) for key, value in evidence_row.items()}
        max_dupont_gap = connection.execute(
            "select coalesce(max(abs(dupont_identity_gap)), 0) "
            "from q1_annual_company_metrics where dupont_valid_flag"
        ).fetchone()[0]
        max_shapley_gap = connection.execute(
            "select coalesce(max(abs(shapley_reconciliation_gap)), 0) "
            "from q1_dupont_contributions where transition_valid_flag"
        ).fetchone()[0]
        formal_company_count = connection.execute(
            "select count(distinct company_id) from q1_annual_company_metrics"
        ).fetchone()[0]
        expected_metric_rows = connection.execute(
            "select count(*) from q1_formal_years"
        ).fetchone()[0]
        latest_duplicate_count = connection.execute(
            "select count(*) from ("
            "select company_id, fiscal_year, canonical_field, count(*) n "
            "from q1_latest_restated group by all having n > 1)"
        ).fetchone()[0]
        invalid_peer_count = connection.execute(
            "select count(*) from q1_peer_summary "
            "where valid_roe_company_count > company_count"
        ).fetchone()[0]

    checks = {
        "seven_mandatory_marts_built": all(
            table_counts.get(table_name, 0) > 0 for table_name in MANDATORY_MARTS
        ),
        "formal_company_count_21": formal_company_count == 21,
        "formal_metric_rows_match_frozen_years": (
            table_counts["q1_annual_company_metrics"] == expected_metric_rows
        ),
        "latest_restated_unique": latest_duplicate_count == 0,
        "peer_counts_exclude_invalid_metrics": invalid_peer_count == 0,
        "dupont_identity_reconciles": float(max_dupont_gap) < 1e-10,
        "shapley_contributions_reconcile": float(max_shapley_gap) < 1e-10,
        "h1_gate1_counts_match": evidence["eligible_transition_count"] == 21
        and evidence["eligible_unique_company_count"] == 10
        and evidence["leverage_driven_transition_count"] == 4
        and evidence["operating_driven_transition_count"] == 17,
        "h1_gate1_tier_b": evidence["evidence_tier"] == "B",
        "h1_concentration_threshold_20_percent": bool(
            evidence["over_concentration_flag"]
        )
        == (float(evidence["maximum_company_transition_share"] or 0) > 0.20),
        "powerbi_contract_exact": powerbi_columns == expected_powerbi_columns,
        "schema_dictionary_complete": len(schema) > 0
        and schema["description"].fillna("").str.len().gt(0).all(),
    }
    checks = {name: bool(passed) for name, passed in checks.items()}
    audit = {
        "generated_on": date.today().isoformat(),
        "stage": "B3 SQL Analytical Marts",
        "status": "Done" if all(checks.values()) else "Failed",
        "source_stage": "B2 Q1 Sample Expansion",
        "gate1_contract": "Gate1-v1.0",
        "sql_execution_order": [path.name for path in SQL_FILES],
        "formal_company_count": formal_company_count,
        "expected_formal_company_year_count": expected_metric_rows,
        "table_row_counts": table_counts,
        "max_abs_dupont_identity_gap": float(max_dupont_gap),
        "max_abs_shapley_reconciliation_gap": float(max_shapley_gap),
        "powerbi_field_count": len(powerbi_columns),
        "h1_evidence": evidence,
        "checks": checks,
    }
    (PROCESSED / "b3_stage_audit.json").write_text(
        json.dumps(audit, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    _write_report(audit)

    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise ValueError(f"B3 audit failed: {failed}")
    return audit


def main() -> None:
    audit = build_b3_analytical_marts()
    evidence = audit["h1_evidence"]
    print("B3 formal SQL analytical marts complete.")
    print(f"Formal companies: {audit['formal_company_count']}")
    print(f"Formal company-years: {audit['expected_formal_company_year_count']}")
    print(f"H1 eligible transitions: {evidence['eligible_transition_count']}")
    print(f"H1 unique companies: {evidence['eligible_unique_company_count']}")
    print(f"H1 Evidence Tier: {evidence['evidence_tier']}")
    print(f"Power BI mart rows: {audit['table_row_counts']['q1_powerbi_mart']}")


if __name__ == "__main__":
    main()
