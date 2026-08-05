from __future__ import annotations

import hashlib
import json
import subprocess
import unittest
from pathlib import Path

import nbformat
import numpy as np
import pandas as pd
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
DOCS = ROOT / "docs"
CHARTS = DOCS / "assets" / "q1"


class B4AnalyticalReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [str(ROOT / ".venv/bin/python"), "src/build_b4_analytical_release.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.audit = json.loads(
            (PROCESSED / "b4_stage_audit.json").read_text(encoding="utf-8")
        )
        cls.manifest = pd.read_csv(PROCESSED / "b4_release_manifest.csv")
        cls.findings = pd.read_csv(PROCESSED / "q1_research_findings.csv")
        cls.reconciliation = pd.read_csv(
            PROCESSED / "b4_filing_reconciliation.csv"
        )

    def test_b4_stage_and_formal_scope(self) -> None:
        self.assertEqual(self.audit["status"], "Done")
        self.assertTrue(all(self.audit["checks"].values()))
        self.assertEqual(self.audit["formal_company_count"], 21)
        self.assertEqual(self.audit["formal_company_year_count"], 137)
        self.assertEqual(self.audit["h1_evidence_tier"], "B")
        self.assertEqual(self.audit["h1_eligible_transition_count"], 21)
        self.assertEqual(self.audit["h1_unique_company_count"], 10)

    def test_release_manifest_hashes_are_reproducible(self) -> None:
        self.assertEqual(len(self.manifest), 11)
        self.assertEqual(set(self.manifest["analytical_data_as_of"]), {"2026-08-05"})
        for row in self.manifest.itertuples(index=False):
            path = ROOT / row.relative_path
            self.assertTrue(path.exists())
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), row.sha256)

    def test_quality_eda_outputs_cover_required_audits(self) -> None:
        required = {
            "q1_coverage_summary.csv",
            "q1_missingness_summary.csv",
            "q1_conflict_summary.csv",
            "q1_latest_selection_summary.csv",
            "q1_metric_flag_summary.csv",
            "q1_h1_exclusion_waterfall.csv",
            "q1_h1_company_concentration.csv",
            "q1_h1_peer_distribution.csv",
            "q1_h1_year_distribution.csv",
            "q1_h1_group_summary.csv",
            "q1_peer_metric_summary.csv",
            "q1_company_cases.csv",
        }
        self.assertTrue(all((PROCESSED / name).exists() for name in required))
        concentration = pd.read_csv(PROCESSED / "q1_h1_company_concentration.csv")
        years = pd.read_csv(PROCESSED / "q1_h1_year_distribution.csv")
        self.assertEqual(concentration["ticker"].nunique(), 10)
        self.assertAlmostEqual(concentration["transition_share"].sum(), 1.0)
        self.assertEqual(years["transitions"].sum(), 21)

    def test_static_charts_are_nonblank_and_legible_size(self) -> None:
        self.assertEqual(len(self.audit["static_chart_files"]), 8)
        for filename in self.audit["static_chart_files"]:
            path = CHARTS / filename
            with Image.open(path) as image:
                pixels = np.asarray(image.convert("RGB"))
                self.assertGreaterEqual(image.width, 900)
                self.assertGreaterEqual(image.height, 500)
                self.assertGreater(float(pixels.std()), 5.0)

    def test_notebooks_are_executed_without_errors(self) -> None:
        self.assertEqual(
            set(self.audit["executed_notebooks"]),
            {"notebooks/02_data_quality.ipynb", "notebooks/03_q1_analysis.ipynb"},
        )
        for relative_path in self.audit["executed_notebooks"]:
            notebook = nbformat.read(ROOT / relative_path, as_version=4)
            code_cells = [cell for cell in notebook.cells if cell.cell_type == "code"]
            self.assertTrue(code_cells)
            self.assertTrue(
                all(cell.get("execution_count") is not None for cell in code_cells)
            )
            self.assertFalse(
                any(
                    output.get("output_type") == "error"
                    for cell in code_cells
                    for output in cell.get("outputs", [])
                )
            )

    def test_filing_reconciliation_has_two_companies_and_four_fields(self) -> None:
        expected_fields = {"revenue", "net_income", "total_assets", "total_equity"}
        self.assertEqual(set(self.reconciliation["ticker"]), {"AMZN", "CHWY"})
        self.assertEqual(len(self.reconciliation), 8)
        for ticker, group in self.reconciliation.groupby("ticker"):
            self.assertEqual(set(group["canonical_field"]), expected_fields, ticker)
        self.assertTrue(self.reconciliation["match_within_tolerance"].all())
        self.assertTrue(self.reconciliation["accession_number"].str.len().gt(0).all())
        self.assertEqual(set(self.reconciliation["form"]), {"10-K"})

    def test_h1_conclusion_is_tier_b_and_honest(self) -> None:
        finding_types = set(self.findings["finding_type"])
        self.assertTrue(
            {"tier_b_result", "counterexample", "year_effect", "falsification_rule"}
            .issubset(finding_types)
        )
        report = (DOCS / "q1_analysis_report.md").read_text(encoding="utf-8")
        self.assertIn("does **not support H1**", report)
        self.assertIn("Evidence Tier B", report)
        self.assertIn("No company-clustered bootstrap is run", report)
        self.assertIn("No investment recommendation", report)

    def test_cv_and_readme_match_b4_release(self) -> None:
        pitch = (DOCS / "recruiter_pitch.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("Tier B descriptive persistence patterns", pitch)
        self.assertIn("B4 Analytical Release is complete", readme)
        self.assertIn("Data as of: **2026-08-05**", readme)
        self.assertIn("does **not support H1**", readme)


if __name__ == "__main__":
    unittest.main()
