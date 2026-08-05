from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
REFERENCE = ROOT / "data" / "reference"


class Q1V3PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [str(ROOT / ".venv/bin/python"), "src/build_b3_analytical_marts.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.latest = pd.read_csv(PROCESSED / "q1_latest_restated.csv")
        cls.metrics = pd.read_csv(PROCESSED / "q1_annual_company_metrics.csv")
        cls.shapley = pd.read_csv(PROCESSED / "q1_dupont_contributions.csv")
        cls.peer = pd.read_csv(PROCESSED / "q1_peer_summary.csv")
        cls.company_peer = pd.read_csv(PROCESSED / "q1_company_vs_peer.csv")
        cls.persistence = pd.read_csv(PROCESSED / "q1_driver_persistence.csv")
        cls.h1_audit = pd.read_csv(PROCESSED / "q1_h1_sample_audit.csv")
        cls.evidence = pd.read_csv(PROCESSED / "q1_h1_evidence_summary.csv").iloc[0]
        cls.powerbi = pd.read_csv(PROCESSED / "q1_powerbi_mart.csv")
        cls.schema = pd.read_csv(PROCESSED / "b3_mart_schema.csv")
        cls.stage_audit = json.loads(
            (PROCESSED / "b3_stage_audit.json").read_text(encoding="utf-8")
        )

    def test_concept_mapping_priority(self) -> None:
        concept_map = pd.read_csv(REFERENCE / "concept_map.csv")
        self.assertFalse(concept_map["standard_field"].duplicated().any())
        required = set(
            concept_map.loc[concept_map["required_for_q1"].eq(1), "standard_field"]
        )
        self.assertTrue(
            {
                "revenue",
                "net_income",
                "total_assets",
                "total_equity",
                "operating_cash_flow",
                "capital_expenditure",
                "free_cash_flow",
            }.issubset(required)
        )

    def test_sign_standardization(self) -> None:
        capex = self.latest[
            self.latest["canonical_field"].eq("capital_expenditure")
        ]
        self.assertTrue(capex["value_standardized"].ge(0).all())
        components = self.latest.pivot_table(
            index=["company_id", "fiscal_year"],
            columns="canonical_field",
            values="value_standardized",
            aggfunc="first",
        )
        complete = components.dropna(
            subset=["operating_cash_flow", "capital_expenditure", "free_cash_flow"]
        )
        expected = complete["operating_cash_flow"] - complete["capital_expenditure"]
        self.assertTrue(complete["free_cash_flow"].sub(expected).abs().lt(1e-8).all())

    def test_latest_restated_selection(self) -> None:
        key = ["company_id", "fiscal_year", "canonical_field"]
        self.assertFalse(self.latest.duplicated(key).any())
        self.assertTrue(self.latest["is_latest_restated"].all())
        self.assertEqual(self.latest["company_id"].nunique(), 21)
        self.assertTrue(
            set(self.latest["source_selection_method"]).issubset(
                {
                    "latest_valid_restated_sec_companyfacts",
                    "derived_from_latest_valid_components",
                }
            )
        )

    def test_dupont_identity(self) -> None:
        self.assertEqual(self.metrics["company_id"].nunique(), 21)
        self.assertEqual(len(self.metrics), 137)
        valid = self.metrics[self.metrics["dupont_valid_flag"]]
        self.assertGreater(len(valid), 0)
        self.assertTrue(valid["dupont_identity_gap"].abs().lt(1e-10).all())
        average_available = self.metrics["average_balance_available_flag"].fillna(
            False
        ).astype(bool)
        positive_equity = self.metrics["positive_average_equity_flag"].fillna(
            False
        ).astype(bool)
        invalid_equity = self.metrics[average_available & ~positive_equity]
        self.assertTrue(invalid_equity["roe"].isna().all())

    def test_shapley_contributions(self) -> None:
        valid = self.shapley[self.shapley["transition_valid_flag"]]
        self.assertGreater(len(valid), 0)
        self.assertTrue(valid["shapley_reconciliation_gap"].abs().lt(1e-10).all())
        self.assertTrue(
            valid["h1_driver_group"].isin(
                ["leverage_driven", "operating_driven", "mixed_or_ambiguous"]
            ).all()
        )

    def test_peer_statistics_exclude_invalid_metrics_and_keep_n(self) -> None:
        self.assertTrue(
            self.peer["valid_roe_company_count"].le(self.peer["company_count"]).all()
        )
        percentiles = self.company_peer["roe_peer_percentile"].dropna()
        self.assertTrue(percentiles.between(0, 1).all())
        invalid = self.company_peer[self.company_peer["roe"].isna()]
        self.assertTrue(invalid["roe_peer_percentile"].isna().all())

    def test_persistence_uses_consecutive_forward_year(self) -> None:
        observable = self.persistence[self.persistence["next_fiscal_year"].notna()]
        self.assertTrue(
            observable["next_fiscal_year"].eq(observable["fiscal_year"] + 1).all()
        )
        comparable = observable.dropna(
            subset=[
                "next_year_peer_relative_roe",
                "current_peer_relative_roe",
                "next_year_peer_relative_change",
            ]
        )
        expected = (
            comparable["next_year_peer_relative_roe"]
            - comparable["current_peer_relative_roe"]
        )
        self.assertTrue(
            comparable["next_year_peer_relative_change"]
            .sub(expected)
            .abs()
            .lt(1e-12)
            .all()
        )

    def test_h1_eligibility_and_gate1_counts(self) -> None:
        expected = (
            self.h1_audit["transition_valid_flag"]
            & self.h1_audit["prior_average_equity"].gt(0)
            & self.h1_audit["average_equity"].gt(0)
            & self.h1_audit["next_average_equity"].gt(0)
            & self.h1_audit["prior_roe"].gt(0)
            & self.h1_audit["roe_change"].gt(0)
            & self.h1_audit["next_year_roe"].notna()
            & self.h1_audit["h1_driver_group"].isin(
                ["leverage_driven", "operating_driven"]
            )
        )
        self.assertTrue((self.h1_audit["h1_eligible_flag"] == expected).all())
        self.assertEqual(int(self.evidence["eligible_transition_count"]), 21)
        self.assertEqual(int(self.evidence["eligible_unique_company_count"]), 10)
        self.assertEqual(int(self.evidence["leverage_driven_transition_count"]), 4)
        self.assertEqual(int(self.evidence["operating_driven_transition_count"]), 17)
        self.assertEqual(self.evidence["evidence_tier"], "B")
        self.assertEqual(
            bool(self.evidence["over_concentration_flag"]),
            self.evidence["maximum_company_transition_share"] > 0.20,
        )

    def test_metric_flags(self) -> None:
        flagged = self.metrics[self.metrics["metric_flag_count"].gt(0)]
        self.assertGreater(len(flagged), 0)
        self.assertTrue(flagged["quality_warnings"].fillna("").str.len().gt(0).all())
        near_zero = self.metrics[self.metrics["near_zero_average_equity_flag"]]
        self.assertTrue(
            near_zero["quality_warnings"]
            .str.contains("mechanically unstable", na=False)
            .all()
        )

    def test_powerbi_mart_matches_frozen_contract(self) -> None:
        contract = pd.read_csv(REFERENCE / "q1_powerbi_mart_contract_v1.csv")
        self.assertEqual(self.powerbi.columns.tolist(), contract["field_name"].tolist())
        self.assertEqual(len(self.powerbi), 137)
        self.assertFalse(
            self.powerbi.duplicated(["company_id", "fiscal_year"]).any()
        )
        self.assertEqual(set(self.powerbi["h1_evidence_tier"]), {"B"})
        self.assertTrue(contract["dax_recalculation_allowed"].eq(0).all())

    def test_mart_dictionary_and_stage_audit(self) -> None:
        mandatory = {
            "q1_annual_company_metrics",
            "q1_dupont_contributions",
            "q1_driver_persistence",
            "q1_h1_sample_audit",
            "q1_peer_summary",
            "q1_company_vs_peer",
            "q1_powerbi_mart",
        }
        self.assertTrue(mandatory.issubset(set(self.schema["mart_name"])))
        self.assertTrue(self.schema["grain"].str.len().gt(0).all())
        self.assertTrue(self.schema["description"].str.len().gt(0).all())
        self.assertEqual(self.stage_audit["status"], "Done")
        self.assertTrue(all(self.stage_audit["checks"].values()))


if __name__ == "__main__":
    unittest.main()
