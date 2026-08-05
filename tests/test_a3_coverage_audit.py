from __future__ import annotations

import json
import hashlib
import subprocess
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data/processed"


class A3CoverageAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [str(ROOT / ".venv/bin/python"), "src/build_a3_coverage_audit.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.coverage = pd.read_csv(
            PROCESSED / "a3_coverage_company_field_year.csv",
            keep_default_na=False,
        )
        cls.company_coverage = pd.read_csv(
            PROCESSED / "a3_company_coverage_summary.csv", keep_default_na=False
        )
        cls.latest = pd.read_csv(
            PROCESSED / "a3_latest_restated_core.csv", keep_default_na=False
        )
        cls.transitions = pd.read_csv(
            PROCESSED / "a3_h1_transition_audit.csv", keep_default_na=False
        )
        cls.q2 = pd.read_csv(
            PROCESSED / "a3_q2_feasibility_scan.csv", keep_default_na=False
        )
        cls.audit = json.loads(
            (PROCESSED / "a3_stage_audit.json").read_text(encoding="utf-8")
        )
        cls.recommendation = json.loads(
            (PROCESSED / "a3_recommendation.json").read_text(encoding="utf-8")
        )

    def test_full_candidate_coverage_scan(self) -> None:
        self.assertEqual(len(self.company_coverage), 40)
        self.assertEqual(len(self.coverage), 40 * 7 * 4)
        self.assertTrue(self.coverage["coverage_verified"].eq(1).all())
        self.assertEqual(
            set(self.coverage["canonical_field"]),
            {"revenue", "net_income", "total_assets", "total_equity"},
        )
        self.assertTrue(
            self.company_coverage["primary_failure_reason"].str.len().gt(0).all()
        )
        manifest = pd.read_csv(
            ROOT / "data/raw/sec/a3_candidate_manifest.csv", keep_default_na=False
        )
        self.assertEqual(len(manifest), 80)
        for row in manifest.itertuples():
            self.assertEqual(
                hashlib.sha256((ROOT / row.relative_path).read_bytes()).hexdigest(),
                row.sha256,
            )

    def test_latest_restated_and_conflicts_are_traceable(self) -> None:
        key = ["company_id", "fiscal_year", "canonical_field"]
        self.assertFalse(self.latest.duplicated(key).any())
        self.assertTrue(self.latest["accession_number"].str.len().gt(0).all())
        conflicts = pd.read_csv(
            PROCESSED / "a3_concept_conflicts.csv", keep_default_na=False
        )
        self.assertGreater(len(conflicts), 0)
        self.assertTrue(
            {
                "winning_tag",
                "discarded_tag",
                "relative_difference",
                "resolution_rule",
                "conflict_severity",
            }.issubset(conflicts.columns)
        )

    def test_h1_rules_and_shapley_reconciliation(self) -> None:
        self.assertEqual(len(self.transitions), 40 * 5)
        required = {
            "roe_t_minus_1",
            "roe_t",
            "roe_t_plus_1",
            "average_equity_valid",
            "components_valid",
            "positive_roe_base",
            "positive_roe_change",
            "forward_year_available",
            "dominant_driver",
            "leverage_contribution_share",
            "eligible_h1",
            "exclusion_reason",
            "next_year_peer_relative_change",
            "next_year_roe_change",
            "roe_reversal_flag",
            "rank_retention",
        }
        self.assertTrue(required.issubset(self.transitions.columns))
        valid = self.transitions[self.transitions["components_valid"].eq(1)]
        self.assertTrue(
            valid["shapley_reconciliation_gap"].astype(float).abs().lt(1e-10).all()
        )
        eligible = self.transitions[self.transitions["eligible_h1"].eq(1)]
        self.assertTrue(eligible["average_equity_valid"].eq(1).all())
        self.assertTrue(eligible["positive_roe_base"].eq(1).all())
        self.assertTrue(eligible["positive_roe_change"].eq(1).all())
        self.assertTrue(eligible["forward_year_available"].eq(1).all())
        self.assertTrue(
            set(eligible["dominant_driver"]).issubset(
                {"leverage_driven", "operating_driven"}
            )
        )

    def test_evidence_tier_and_concentration_are_recomputed(self) -> None:
        h1 = self.audit["h1"]
        eligible = self.transitions[self.transitions["eligible_h1"].eq(1)]
        self.assertEqual(h1["eligible_transition_count"], len(eligible))
        self.assertEqual(
            h1["eligible_unique_company_count"], eligible["company_id"].nunique()
        )
        self.assertEqual(h1["evidence_tier_recommendation"], "B")
        self.assertTrue(h1["driver_year_imbalance_flag"])
        self.assertLessEqual(h1["maximum_company_transition_share"], 0.20)

    def test_event_coverage_and_provisional_gate2_tier(self) -> None:
        self.assertEqual(len(self.q2), 14)
        self.assertTrue(self.q2["coverage_verified"].eq(1).all())
        qualified = self.q2[self.q2["qualifies_for_q2"].eq(1)]
        self.assertGreaterEqual(len(qualified), 10)
        self.assertTrue(qualified["verified_pre_event_quarters"].ge(8).all())
        self.assertTrue(qualified["cashflow_quarter_end_count"].ge(8).all())
        self.assertTrue(qualified["eligible_peer_control_count"].ge(3).all())
        self.assertTrue(qualified["pit_feasible"].eq(1).all())
        excluded = self.q2[self.q2["qualifies_for_q2"].eq(0)]
        self.assertTrue(excluded["exclusion_reason"].str.len().gt(0).all())
        self.assertEqual(
            self.audit["q2"]["provisional_gate2_tier_recommendation"], "A"
        )
        self.assertEqual(self.audit["q2"]["formal_gate2_status"], "pending_after_b5")

    def test_path_a_recommendation_uses_hybrid_merge(self) -> None:
        self.assertEqual(self.recommendation["data_path_recommendation"], "A")
        proposed = self.recommendation["data_path_basis"][
            "proposed_counts_after_hybrid_merge"
        ]
        self.assertGreaterEqual(proposed["marketplace_platform"], 6)
        self.assertGreaterEqual(proposed["inventory_led_ecommerce"], 6)
        self.assertGreaterEqual(proposed["dtc_brand"], 6)
        self.assertEqual(self.recommendation["gate1_status"], "pending_formal_freeze")
        self.assertEqual(self.recommendation["gate2_status"], "pending_after_b5")

    def test_reports_and_stage_audit(self) -> None:
        for path in [
            ROOT / "docs/a3_coverage_report.md",
            ROOT / "docs/a3_h1_sample_audit.md",
            ROOT / "docs/a3_q2_feasibility_report.md",
            ROOT / "docs/a3_recommendation_memo.md",
            ROOT / "docs/gate2_decision.md",
        ]:
            self.assertTrue(path.exists())
            self.assertGreater(path.stat().st_size, 100)
        self.assertEqual(self.audit["status"], "Done")
        self.assertTrue(all(self.audit["checks"].values()))


if __name__ == "__main__":
    unittest.main()
