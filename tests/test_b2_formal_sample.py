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
REFERENCE = ROOT / "data" / "reference"
RAW_SEC = ROOT / "data" / "raw" / "sec"
NORMALIZED = ROOT / "data" / "normalized"
PROCESSED = ROOT / "data" / "processed"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class B2FormalSampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [str(ROOT / ".venv/bin/python"), "src/build_b2_formal_sample.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.sample = pd.read_csv(REFERENCE / "q1_formal_sample_v1.csv")
        cls.manifest = pd.read_csv(RAW_SEC / "b2_formal_manifest.csv")
        cls.facts = pd.read_csv(NORMALIZED / "financial_facts.csv")
        cls.latest = pd.read_csv(PROCESSED / "sec_latest_restated_long.csv")
        cls.conflicts = pd.read_csv(PROCESSED / "sec_concept_conflicts.csv")
        cls.flags = pd.read_csv(PROCESSED / "metric_flags.csv")
        cls.coverage = pd.read_csv(PROCESSED / "b2_company_field_year_coverage.csv")
        cls.failures = pd.read_csv(PROCESSED / "b2_failures.csv")
        cls.audit = json.loads(
            (PROCESSED / "b2_stage_audit.json").read_text(encoding="utf-8")
        )

    def test_raw_cache_covers_all_formal_companies(self) -> None:
        self.assertEqual(len(self.manifest), 42)
        self.assertEqual(set(self.manifest["ticker"]), set(self.sample["ticker"]))
        self.assertEqual(set(self.manifest["artifact"]), {"companyfacts", "submissions"})
        for row in self.manifest.itertuples(index=False):
            path = ROOT / row.relative_path
            self.assertTrue(path.exists())
            with gzip.open(path, "rt", encoding="utf-8") as handle:
                self.assertIsInstance(json.load(handle), dict)
            self.assertEqual(sha256(path), row.sha256)
        self.assertTrue(pd.read_csv(PROCESSED / "b2_sec_extraction_errors.csv").empty)

    def test_financial_facts_are_formal_and_gate1_compliant(self) -> None:
        self.assertEqual(set(self.facts["ticker"]), set(self.sample["ticker"]))
        self.assertTrue(set(self.facts["fiscal_year"]).issubset(set(range(2017, 2025))))
        self.assertFalse(
            {"gross_profit", "long_term_debt", "shares_outstanding"}
            & set(self.facts["canonical_field"])
        )
        required_schema = {
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
        self.assertTrue(required_schema.issubset(self.facts.columns))
        self.assertFalse(self.facts["value_standardized"].isin([-999]).any())

    def test_latest_coverage_has_no_required_failure(self) -> None:
        self.assertFalse(
            self.latest.duplicated(["company_id", "fiscal_year", "canonical_field"]).any()
        )
        expected_required = self.coverage[
            self.coverage["expected_for_company"].eq(1)
            & self.coverage["requiredness"].eq("required")
        ]
        self.assertTrue(expected_required["fact_available"].eq(1).all())
        self.assertTrue(self.failures.empty)

    def test_observed_overrides_are_accession_backed(self) -> None:
        overrides = pd.read_csv(REFERENCE / "company_overrides.csv")
        active = overrides[overrides["status"].eq("active")]
        self.assertEqual(set(active["company_id"]), {"abnb", "cvna", "dash", "etsy"})
        self.assertTrue(active["accession_number"].str.len().gt(0).all())
        self.assertTrue(active["source_url"].str.startswith("https://www.sec.gov/").all())
        selected = self.latest[self.latest["source_tag"].str.startswith("override:")]
        self.assertTrue({"abnb", "cvna", "dash", "etsy"}.issubset(set(selected["company_id"])))

    def test_conflicts_and_metric_flags_remain_traceable(self) -> None:
        expected_severity = self.conflicts["relative_difference"].map(
            lambda value: "high" if value > 0.05 else "medium" if value > 0.005 else "low"
        )
        self.assertTrue((expected_severity == self.conflicts["conflict_severity"]).all())
        self.assertFalse(self.conflicts["resolution_status"].eq("").any())
        self.assertTrue(
            {
                "source_conflict",
                "missing_prior_balance",
                "non_positive_average_equity",
                "insufficient_forward_year",
            }.issubset(set(self.flags["flag_code"]))
        )

    def test_duckdb_core_tables_and_frozen_hashes(self) -> None:
        with duckdb.connect(
            str(ROOT / "db/financial_health_screener.duckdb"), read_only=True
        ) as connection:
            tables = {row[0] for row in connection.execute("show tables").fetchall()}
            fact_count = connection.execute("select count(*) from financial_facts").fetchone()[0]
        self.assertTrue(
            {
                "q1_formal_sample",
                "financial_facts",
                "q1_latest_restated",
                "concept_conflicts",
                "metric_flags",
                "company_overrides",
                "b2_company_field_year_coverage",
                "b2_failures",
            }.issubset(tables)
        )
        self.assertEqual(fact_count, len(self.facts))
        self.assertEqual(
            self.audit["gate1_sample_sha256"],
            sha256(REFERENCE / "q1_formal_sample_v1.csv"),
        )
        self.assertEqual(
            self.audit["gate1_field_contract_sha256"],
            sha256(REFERENCE / "q1_field_contract_v1.csv"),
        )
        self.assertTrue(all(self.audit["checks"].values()))
        self.assertEqual(self.audit["missing_required_company_year_field_count"], 0)
        self.assertEqual(
            self.audit["processed_generation"], "scripted_no_manual_processed_edits"
        )


if __name__ == "__main__":
    unittest.main()
