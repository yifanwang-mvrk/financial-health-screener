from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data/processed"


class Q1V3PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [str(ROOT / ".venv/bin/python"), "src/build_q1_v3_pipeline.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.latest = pd.read_csv(PROCESSED / "q1_latest_restated.csv")
        cls.metrics = pd.read_csv(PROCESSED / "q1_annual_company_metrics.csv")
        cls.shapley = pd.read_csv(PROCESSED / "q1_dupont_contributions.csv")
        cls.audit = pd.read_csv(PROCESSED / "q1_h1_sample_audit.csv")
        cls.powerbi = pd.read_csv(PROCESSED / "q1_powerbi_mart.csv")

    def test_concept_mapping_priority(self) -> None:
        concept_map = pd.read_csv(ROOT / "data/reference/concept_map.csv")
        self.assertFalse(concept_map["standard_field"].duplicated().any())
        required = set(
            concept_map.loc[concept_map["required_for_q1"] == 1, "standard_field"]
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
        self.assertTrue((self.latest["capital_expenditure"] >= 0).all())
        expected_fcf = (
            self.latest["operating_cash_flow"] - self.latest["capital_expenditure"]
        )
        self.assertTrue(
            (self.latest["free_cash_flow"] - expected_fcf).abs().le(0.01).all()
        )

    def test_latest_restated_selection(self) -> None:
        self.assertFalse(self.latest.duplicated(["ticker", "fiscal_year"]).any())
        self.assertTrue(self.latest["is_latest_restated"].all())
        sorted_keys = self.latest[["ticker", "fiscal_year"]].sort_values(
            ["ticker", "fiscal_year"]
        )
        self.assertEqual(
            list(map(tuple, self.latest[["ticker", "fiscal_year"]].to_numpy())),
            list(map(tuple, sorted_keys.to_numpy())),
        )
        chewy = self.latest[self.latest["ticker"] == "CHWY"]
        self.assertTrue(
            chewy["source_selection_note"].str.contains("restated", case=False).all()
        )

    def test_dupont_identity(self) -> None:
        valid = self.metrics[self.metrics["dupont_valid_flag"]]
        self.assertGreater(len(valid), 0)
        self.assertTrue(valid["dupont_identity_gap"].abs().lt(1e-10).all())
        average_balance_available = self.metrics[
            "average_balance_available_flag"
        ].fillna(False).astype(bool)
        positive_average_equity = self.metrics[
            "positive_average_equity_flag"
        ].fillna(False).astype(bool)
        invalid_equity = self.metrics[
            average_balance_available & ~positive_average_equity
        ]
        self.assertTrue(invalid_equity["roe"].isna().all())

    def test_shapley_contributions(self) -> None:
        valid = self.shapley[self.shapley["transition_valid_flag"]]
        self.assertGreater(len(valid), 0)
        self.assertTrue(valid["shapley_reconciliation_gap"].abs().lt(1e-10).all())

    def test_h1_eligibility(self) -> None:
        expected = (
            self.audit["transition_valid_flag"]
            & self.audit["prior_average_equity"].gt(0)
            & self.audit["average_equity"].gt(0)
            & self.audit["next_average_equity"].gt(0)
            & self.audit["prior_roe"].gt(0)
            & self.audit["roe_change"].gt(0)
            & self.audit["next_year_roe"].notna()
            & self.audit["h1_driver_group"].isin(
                ["leverage_driven", "operating_driven"]
            )
        )
        self.assertTrue((self.audit["h1_eligible_flag"] == expected).all())

    def test_metric_flags(self) -> None:
        booking_2023 = self.metrics.query("ticker == 'BKNG' and fiscal_year == 2023").iloc[0]
        etsy_2023 = self.metrics.query("ticker == 'ETSY' and fiscal_year == 2023").iloc[0]
        self.assertTrue(booking_2023["near_zero_average_equity_flag"])
        self.assertFalse(etsy_2023["roe_valid_flag"])
        self.assertIn("ROE invalid", etsy_2023["quality_warnings"])

    def test_powerbi_mart_grain(self) -> None:
        self.assertEqual(len(self.powerbi), 18)
        self.assertFalse(self.powerbi.duplicated(["ticker", "fiscal_year"]).any())
        self.assertEqual(set(self.powerbi["h1_evidence_tier"]), {"C"})
        self.assertTrue(
            {
                "roe",
                "net_margin",
                "asset_turnover",
                "equity_multiplier",
                "dominant_change_driver",
                "quality_warnings",
            }.issubset(self.powerbi.columns)
        )


if __name__ == "__main__":
    unittest.main()
