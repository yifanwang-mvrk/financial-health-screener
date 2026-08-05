from __future__ import annotations

import gzip
import hashlib
import json
import subprocess
import unittest
from pathlib import Path

import duckdb
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "data/reference"
RAW_SEC = ROOT / "data/raw/sec"
NORMALIZED = ROOT / "data/normalized"
PROCESSED = ROOT / "data/processed"


class PhaseAEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [str(ROOT / ".venv/bin/python"), "src/build_phase_a_release.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.universe = pd.read_csv(
            REFERENCE / "company_universe.csv",
            dtype={"cik": str},
            keep_default_na=False,
        )
        cls.events = pd.read_csv(REFERENCE / "events.csv", keep_default_na=False)
        cls.manifest = pd.read_csv(RAW_SEC / "manifest.csv", keep_default_na=False)
        cls.facts = pd.read_csv(
            NORMALIZED / "financial_facts.csv", keep_default_na=False
        )
        cls.latest = pd.read_csv(
            PROCESSED / "sec_latest_restated_long.csv", keep_default_na=False
        )
        cls.reconciliation = pd.read_csv(
            PROCESSED / "sec_manual_reconciliation.csv", keep_default_na=False
        )
        cls.coverage = pd.read_csv(
            PROCESSED / "phase_a_coverage.csv", keep_default_na=False
        )

    def test_company_universe_contract(self) -> None:
        self.assertGreaterEqual(len(self.universe), 20)
        self.assertFalse(self.universe["company_id"].duplicated().any())
        self.assertFalse(self.universe["ticker"].duplicated().any())
        self.assertTrue(self.universe["exchange"].str.len().gt(0).all())
        self.assertTrue(
            pd.to_datetime(self.universe["listing_date"], errors="coerce")
            .notna()
            .all()
        )
        self.assertTrue(
            set(self.universe["status_group"]).issubset(
                {"active", "acquired", "delisted", "bankrupt", "other"}
            )
        )
        release = self.universe[self.universe["q1_release_included"] == 1]
        self.assertEqual(set(release["ticker"]), {"AMZN", "BKNG", "CHWY", "DASH", "EBAY", "ETSY"})
        self.assertTrue(release["cik"].str.fullmatch(r"\d{10}").all())

    def test_event_census_has_sources_and_stops_q2(self) -> None:
        self.assertGreaterEqual(len(self.events), 3)
        self.assertTrue(
            set(self.events["company_id"]).issubset(
                set(self.universe["company_id"])
            )
        )
        self.assertTrue(
            pd.to_datetime(self.events["event_date"], errors="coerce")
            .notna()
            .all()
        )
        self.assertTrue(
            self.events["event_source"]
            .str.startswith("https://www.sec.gov/")
            .all()
        )
        self.assertEqual(set(self.events["coverage_verified"]), {0})
        self.assertTrue(self.events["verified_pre_event_quarters"].eq("").all())
        self.assertEqual(set(self.events["qualifies_for_q2"]), {0})
        self.assertTrue(self.events["exclusion_reason"].str.len().gt(0).all())

    def test_raw_manifest_and_checksums(self) -> None:
        self.assertEqual(len(self.manifest), 12)
        self.assertEqual(set(self.manifest["artifact"]), {"companyfacts", "submissions"})
        for row in self.manifest.itertuples():
            path = ROOT / row.relative_path
            self.assertTrue(path.exists())
            with gzip.open(path, "rt", encoding="utf-8") as handle:
                self.assertIsInstance(json.load(handle), dict)
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(digest, row.sha256)

    def test_accession_level_fact_contract(self) -> None:
        required_columns = {
            "ticker",
            "canonical_field",
            "source_tag",
            "accession",
            "filing_date",
            "value_standardized",
            "source_url",
        }
        self.assertTrue(required_columns.issubset(self.facts.columns))
        self.assertEqual(
            set(self.facts["ticker"]),
            {"AMZN", "BKNG", "CHWY", "DASH", "EBAY", "ETSY"},
        )
        self.assertTrue(self.facts["accession"].str.len().gt(0).all())

    def test_latest_restated_selection_contract(self) -> None:
        key = ["ticker", "fiscal_year", "canonical_field"]
        self.assertFalse(self.latest.duplicated(key).any())
        filing_dates = pd.to_datetime(self.latest["filing_date"])
        self.assertTrue(filing_dates.le(pd.Timestamp("2024-04-30")).all())
        self.assertEqual(set(self.latest["is_latest_restated"]), {True})

    def test_reconciliation_is_explicit(self) -> None:
        self.assertGreater(len(self.reconciliation), 0)
        self.assertTrue(
            set(self.reconciliation["reconciliation_status"]).issubset(
                {"match", "review_company_mapping", "manual_value_unavailable"}
            )
        )
        self.assertTrue(self.reconciliation["source_tag"].str.len().gt(0).all())

    def test_coverage_and_gate2_contract(self) -> None:
        self.assertGreater(len(self.coverage), 0)
        self.assertEqual(set(self.coverage["ticker"]), {"AMZN", "BKNG", "CHWY", "DASH", "EBAY", "ETSY"})
        self.assertTrue(self.coverage["coverage_complete_flag"].eq(1).all())
        amazon_liabilities = self.latest.query(
            "ticker == 'AMZN' and canonical_field == 'total_liabilities'"
        )
        self.assertEqual(len(amazon_liabilities), 3)
        self.assertEqual(
            set(amazon_liabilities["source_tag"]),
            {"derived:Assets-StockholdersEquity"},
        )
        gate2 = (ROOT / "docs/gate2_decision.md").read_text(encoding="utf-8")
        self.assertIn("Tier C / No-Go", gate2)
        self.assertIn("Do not start Q2 or Q3", gate2)

    def test_phase_a_tables_are_loaded(self) -> None:
        with duckdb.connect(str(ROOT / "db/financial_health_screener.duckdb"), read_only=True) as connection:
            tables = {
                row[0]
                for row in connection.execute("show tables").fetchall()
            }
        self.assertTrue(
            {
                "company_universe",
                "events",
                "financial_facts",
                "sec_latest_restated_long",
                "sec_concept_conflicts",
                "phase_a_coverage",
            }.issubset(tables)
        )


if __name__ == "__main__":
    unittest.main()
