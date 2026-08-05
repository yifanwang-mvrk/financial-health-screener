from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

import nbformat
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


class A2SourceProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [str(ROOT / ".venv/bin/python"), "src/build_a2_source_probe.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.scope = pd.read_csv(
            ROOT / "data/reference/a2_probe_scope.csv", keep_default_na=False
        )
        cls.manifest = pd.read_csv(
            ROOT / "data/raw/sec/a2_probe_manifest.csv",
            dtype={"cik": str},
            keep_default_na=False,
        )
        cls.facts = pd.read_csv(
            ROOT / "data/normalized/a2_annual_financial_facts_sample.csv",
            keep_default_na=False,
        )
        cls.latest = pd.read_csv(
            ROOT / "data/processed/a2_latest_restated_sample.csv",
            keep_default_na=False,
        )
        cls.conflicts = pd.read_csv(
            ROOT / "data/processed/a2_concept_conflicts_sample.csv",
            keep_default_na=False,
        )
        cls.field_probe = pd.read_csv(
            ROOT / "data/processed/a2_field_probe.csv", keep_default_na=False
        )

    def test_probe_selection_and_raw_artifacts(self) -> None:
        self.assertEqual(set(self.scope["ticker"]), {"CHWY", "EBAY"})
        self.assertEqual(
            set(self.scope["probe_role"]),
            {"Inventory-led E-commerce", "Marketplace / Platform"},
        )
        self.assertTrue(self.scope["third_case_required"].eq(0).all())
        self.assertEqual(len(self.manifest), 4)
        self.assertEqual(set(self.manifest["artifact"]), {"companyfacts", "submissions"})
        self.assertTrue(
            pd.read_csv(
                ROOT / "data/processed/a2_sec_extraction_errors.csv",
                keep_default_na=False,
            ).empty
        )

    def test_required_fields_and_filing_metadata(self) -> None:
        first_round = {"revenue", "net_income", "total_assets", "total_equity"}
        for ticker in ["CHWY", "EBAY"]:
            observed = set(
                self.facts.loc[self.facts["ticker"].eq(ticker), "canonical_field"]
            )
            self.assertTrue(first_round.issubset(observed))
        self.assertTrue(self.facts["accession"].str.len().gt(0).all())
        self.assertTrue(
            pd.to_datetime(self.facts["filing_date"], errors="coerce").notna().all()
        )

    def test_flow_duration_and_sign_rules(self) -> None:
        flow_fields = {
            "revenue",
            "net_income",
            "operating_cash_flow",
            "capital_expenditure",
        }
        flow = self.facts[self.facts["canonical_field"].isin(flow_fields)]
        self.assertTrue(flow["duration_days"].astype(float).between(330, 385).all())
        capex = self.facts[self.facts["canonical_field"].eq("capital_expenditure")]
        self.assertTrue(capex["value_standardized"].ge(0).all())

    def test_latest_selection_and_conflict_trace(self) -> None:
        key = ["ticker", "fiscal_year", "canonical_field"]
        self.assertFalse(self.latest.duplicated(key).any())
        self.assertTrue(self.latest["is_latest_restated"].eq(True).all())
        self.assertGreater(len(self.conflicts), 0)
        self.assertTrue(
            {
                "winning_tag",
                "discarded_tag",
                "relative_difference",
                "resolution_rule",
                "winning_accession",
                "discarded_accession",
            }.issubset(self.conflicts.columns)
        )

    def test_mapping_boundaries_and_a3_design(self) -> None:
        ebay_inventory = self.field_probe.query(
            "ticker == 'EBAY' and canonical_field == 'inventory'"
        ).iloc[0]
        chwy_debt = self.field_probe.query(
            "ticker == 'CHWY' and canonical_field == 'total_debt'"
        ).iloc[0]
        self.assertEqual(
            ebay_inventory["company_override_candidate"],
            "not_applicable_marketplace",
        )
        self.assertEqual(
            chwy_debt["company_override_candidate"],
            "filing_verification_or_documented_aggregation",
        )
        requirements = pd.read_csv(
            ROOT / "data/reference/a3_scan_requirements.csv", keep_default_na=False
        )
        self.assertTrue(
            {
                "core_field_coverage",
                "transition_eligibility",
                "verified_pre_event_quarters",
                "pit_feasible",
                "manual_review_cost",
            }.issubset(set(requirements["metric"]))
        )

    def test_report_notebook_and_audit_are_complete(self) -> None:
        report = (ROOT / "docs/source_probe_report.md").read_text(encoding="utf-8")
        for phrase in [
            "Field-Level Results",
            "Mapping and Version Conclusions",
            "Incremental Cost Estimate",
            "Canonical Source Decision",
            "Required A3 Scan",
        ]:
            self.assertIn(phrase, report)
        audit = json.loads(
            (ROOT / "data/processed/a2_source_probe_audit.json").read_text()
        )
        self.assertEqual(audit["status"], "Done")
        self.assertTrue(all(audit["checks"].values()))
        notebook = nbformat.read(ROOT / "notebooks/01_source_probe.ipynb", as_version=4)
        executed = [
            cell
            for cell in notebook.cells
            if cell.cell_type == "code" and cell.get("execution_count") is not None
        ]
        self.assertGreaterEqual(len(executed), 4)
        errors = [
            output
            for cell in notebook.cells
            if cell.cell_type == "code"
            for output in cell.get("outputs", [])
            if output.get("output_type") == "error"
        ]
        self.assertFalse(errors)


if __name__ == "__main__":
    unittest.main()
