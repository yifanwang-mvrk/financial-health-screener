from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


class A1CensusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [str(ROOT / ".venv/bin/python"), "src/build_a1_census.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.universe = pd.read_csv(
            ROOT / "data/reference/company_universe.csv", keep_default_na=False
        )
        cls.events = pd.read_csv(
            ROOT / "data/reference/events.csv", keep_default_na=False
        )

    def test_company_stopping_rule_and_structure(self) -> None:
        candidates = self.universe[self.universe["include_q1_candidate"].eq(1)]
        self.assertGreaterEqual(len(candidates), 30)
        self.assertLessEqual(len(candidates), 40)
        self.assertFalse(self.universe["company_id"].duplicated().any())
        self.assertFalse(self.universe["ticker"].duplicated().any())
        self.assertTrue(
            set(candidates["peer_group"]).issubset(
                {
                    "marketplace_platform",
                    "inventory_led_ecommerce",
                    "dtc_brand",
                    "hybrid",
                    "boundary",
                }
            )
        )

    def test_event_stopping_rule_and_a1_provisional_fields(self) -> None:
        self.assertGreaterEqual(len(self.events), 10)
        self.assertLessEqual(len(self.events), 15)
        self.assertFalse(self.events["event_id"].duplicated().any())
        self.assertTrue(
            set(self.events["company_id"]).issubset(set(self.universe["company_id"]))
        )
        a3_audit = ROOT / "data/processed/a3_stage_audit.json"
        if a3_audit.exists():
            self.assertTrue(
                self.events["coverage_verified"].astype(str).eq("1").all()
            )
            self.assertTrue(
                self.events["verified_pre_event_quarters"]
                .astype(str)
                .str.len()
                .gt(0)
                .all()
            )
            self.assertTrue(
                self.events["qualifies_for_q2"].astype(str).isin({"0", "1"}).all()
            )
        else:
            self.assertTrue(
                self.events["coverage_verified"].astype(str).eq("0").all()
            )
            self.assertTrue(self.events["verified_pre_event_quarters"].eq("").all())
            self.assertTrue(self.events["qualifies_for_q2"].eq("").all())


if __name__ == "__main__":
    unittest.main()
