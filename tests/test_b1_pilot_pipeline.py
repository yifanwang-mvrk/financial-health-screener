from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

import duckdb
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "data" / "reference"
NORMALIZED = ROOT / "data" / "normalized"
PROCESSED = ROOT / "data" / "processed"


class B1PilotPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [str(ROOT / ".venv/bin/python"), "src/build_b1_pilot.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.facts = pd.read_csv(NORMALIZED / "b1_financial_facts.csv")
        cls.latest = pd.read_csv(PROCESSED / "b1_latest_restated_long.csv")
        cls.conflicts = pd.read_csv(PROCESSED / "b1_concept_conflicts.csv")
        cls.flags = pd.read_csv(PROCESSED / "b1_metric_flags.csv")
        cls.metrics = pd.read_csv(PROCESSED / "b1_pilot_annual_company_metrics.csv")
        cls.shapley = pd.read_csv(PROCESSED / "b1_pilot_dupont_contributions.csv")
        cls.audit = pd.read_csv(PROCESSED / "b1_pilot_h1_sample_audit.csv")
        cls.evidence = pd.read_csv(PROCESSED / "b1_pilot_h1_evidence_summary.csv")
        cls.summary = json.loads(
            (PROCESSED / "b1_pilot_source_audit.json").read_text(encoding="utf-8")
        )

    def test_pilot_selection_covers_required_cases(self) -> None:
        sample = pd.read_csv(REFERENCE / "q1_formal_sample_v1.csv")
        pilot = sample[sample["b1_pilot_member"].eq(1)]
        self.assertEqual(
            set(pilot["ticker"]), {"AMZN", "BKNG", "CHWY", "DASH", "EBAY", "ETSY"}
        )
        self.assertEqual(len(set(pilot["formal_peer_group"])), 2)
        report = (ROOT / "docs/b1_pilot_coverage_report.md").read_text(
            encoding="utf-8"
        )
        for phrase in ["52/53-week", "concept-conflict", "nonpositive-equity"]:
            self.assertIn(phrase, report)

    def test_financial_facts_follow_gate1_schema_and_fields(self) -> None:
        required = {
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
        self.assertTrue(required.issubset(self.facts.columns))
        self.assertTrue(self.facts["accession_number"].str.len().gt(0).all())
        self.assertFalse(
            {"gross_profit", "long_term_debt", "shares_outstanding"}
            & set(self.facts["canonical_field"])
        )

    def test_real_company_overrides_are_explicit_and_reconciled(self) -> None:
        overrides = pd.read_csv(REFERENCE / "company_overrides.csv")
        active = overrides[
            overrides["status"].eq("active")
            & overrides["company_id"].isin({"dash", "etsy"})
            & overrides["fiscal_year"].isin({2021, 2022, 2023})
        ]
        self.assertEqual(
            set(active["company_id"]), {"dash", "etsy"}
        )
        self.assertTrue(
            active["source_tag_or_formula"].str.contains(
                "PaymentsToDevelopSoftware", regex=False
            ).all()
        )
        selected = self.latest.query(
            "company_id in ['dash', 'etsy'] and canonical_field == 'capital_expenditure'"
        )
        self.assertEqual(len(selected), 6)
        self.assertTrue(selected["source_tag"].str.startswith("override:").all())
        reconciliation = pd.read_csv(PROCESSED / "b1_manual_reconciliation.csv")
        capex = reconciliation.query(
            "company_id in ['dash', 'etsy'] and canonical_field == 'capital_expenditure'"
        )
        self.assertTrue(capex["match_within_tolerance"].all())

    def test_conflicts_flags_and_error_logs_are_explicit(self) -> None:
        self.assertTrue(
            {
                "winning_accession",
                "discarded_accession",
                "relative_difference",
                "resolution_status",
            }.issubset(self.conflicts.columns)
        )
        self.assertFalse(self.conflicts["resolution_status"].eq("requires_review").any())
        self.assertTrue(
            {"missing_prior_balance", "non_positive_average_equity", "source_conflict"}
            .issubset(set(self.flags["flag_code"]))
        )
        self.assertTrue(pd.read_csv(PROCESSED / "b1_sec_extraction_errors.csv").empty)
        self.assertTrue(pd.read_csv(PROCESSED / "b1_validation_errors.csv").empty)

    def test_raw_to_duckdb_and_pilot_marts_rebuild(self) -> None:
        self.assertEqual(len(self.metrics), 18)
        valid = self.metrics[self.metrics["dupont_valid_flag"]]
        self.assertTrue(valid["dupont_identity_gap"].abs().lt(1e-10).all())
        valid_shapley = self.shapley[self.shapley["transition_valid_flag"]]
        self.assertTrue(
            valid_shapley["shapley_reconciliation_gap"].abs().lt(1e-10).all()
        )
        self.assertEqual(set(self.evidence["evidence_tier"]), {"C"})
        with duckdb.connect(
            str(ROOT / "db/financial_health_screener.duckdb"), read_only=True
        ) as connection:
            tables = {row[0] for row in connection.execute("show tables").fetchall()}
        self.assertTrue(
            {
                "financial_facts",
                "concept_conflicts",
                "metric_flags",
                "b1_pilot_annual_company_metrics",
                "b1_pilot_h1_sample_audit",
            }.issubset(tables)
        )

    def test_stage_audit_records_no_manual_processed_edits(self) -> None:
        self.assertEqual(self.summary["gate1_contract"], "Gate1-v1.0")
        self.assertEqual(
            self.summary["pipeline_order"],
            [
                "extract",
                "normalize",
                "map_and_sign",
                "conflicts",
                "latest_restated",
                "validate",
                "duckdb",
                "pilot_marts",
            ],
        )
        self.assertEqual(
            self.summary["processed_generation"],
            "scripted_no_manual_processed_edits",
        )
        self.assertEqual(self.summary["company_override_count"], 2)


if __name__ == "__main__":
    unittest.main()
