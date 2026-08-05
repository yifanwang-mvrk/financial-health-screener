import csv
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "data" / "reference"
PROCESSED = ROOT / "data" / "processed"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


class Gate1ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.sample = read_csv(REFERENCE / "q1_formal_sample_v1.csv")
        cls.decisions = read_csv(REFERENCE / "q1_gate1_sample_decisions.csv")
        cls.fields = read_csv(REFERENCE / "q1_field_contract_v1.csv")
        cls.powerbi = read_csv(REFERENCE / "q1_powerbi_mart_contract_v1.csv")
        cls.transitions = read_csv(PROCESSED / "a3_h1_transition_audit.csv")

    def test_path_a_sample_is_21_with_seven_per_group(self) -> None:
        self.assertEqual(len(self.sample), 21)
        self.assertEqual(len({row["company_id"] for row in self.sample}), 21)
        self.assertEqual(
            Counter(row["formal_peer_group"] for row in self.sample),
            {
                "marketplace_platform": 7,
                "inventory_led_ecommerce": 7,
                "dtc_brand": 7,
            },
        )
        self.assertEqual({row["frozen_window_start"] for row in self.sample}, {"2018"})
        self.assertEqual({row["frozen_window_end"] for row in self.sample}, {"2024"})

    def test_six_pilot_companies_remain_pilot_members(self) -> None:
        pilot = {row["ticker"] for row in self.sample if row["b1_pilot_member"] == "1"}
        self.assertEqual(pilot, {"AMZN", "BKNG", "CHWY", "DASH", "EBAY", "ETSY"})

    def test_all_q1_candidates_have_a_traceable_decision(self) -> None:
        self.assertEqual(len(self.decisions), 40)
        self.assertEqual(len({row["company_id"] for row in self.decisions}), 40)
        included = {
            row["company_id"] for row in self.decisions if row["gate1_included"] == "1"
        }
        self.assertEqual(included, {row["company_id"] for row in self.sample})
        self.assertTrue(all(row["decision_reason"] for row in self.decisions))

    def test_formal_sample_supports_frozen_tier_b_counts(self) -> None:
        sample_ids = {row["company_id"] for row in self.sample}
        eligible = [
            row
            for row in self.transitions
            if row["company_id"] in sample_ids and row["eligible_h1"] == "1"
        ]
        self.assertEqual(len(eligible), 21)
        self.assertEqual(len({row["company_id"] for row in eligible}), 10)
        self.assertEqual(
            Counter(row["dominant_driver"] for row in eligible),
            {"operating_driven": 17, "leverage_driven": 4},
        )
        leverage_companies = {
            row["company_id"]
            for row in eligible
            if row["dominant_driver"] == "leverage_driven"
        }
        self.assertEqual(len(leverage_companies), 3)

    def test_field_and_powerbi_contracts_are_unique(self) -> None:
        self.assertEqual(len(self.fields), 17)
        self.assertEqual(sum(row["load_to_formal_layer"] == "1" for row in self.fields), 14)
        self.assertEqual(sum(row["load_to_formal_layer"] == "0" for row in self.fields), 3)
        self.assertEqual(len(self.powerbi), 60)
        self.assertEqual(len({row["field_name"] for row in self.powerbi}), 60)
        self.assertEqual({row["dax_recalculation_allowed"] for row in self.powerbi}, {"0"})


if __name__ == "__main__":
    unittest.main()
