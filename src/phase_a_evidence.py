from __future__ import annotations

import gzip
import hashlib
import json
import os
import time
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd
import requests


ROOT = Path(__file__).resolve().parents[1]
RAW_SEC_DIR = ROOT / "data/raw/sec"
NORMALIZED_DIR = ROOT / "data/normalized"
PROCESSED_DIR = ROOT / "data/processed"
REFERENCE_DIR = ROOT / "data/reference"
DOCS_DIR = ROOT / "docs"
DB_PATH = ROOT / "db/financial_health_screener.duckdb"

MASTER_PATH = ROOT / "data/raw/sample_companies_master.csv"
SCOPE_PATH = REFERENCE_DIR / "q1_analysis_scope.csv"
CONCEPT_MAP_PATH = REFERENCE_DIR / "concept_map.csv"
EVENTS_PATH = REFERENCE_DIR / "events.csv"
UNIVERSE_PATH = REFERENCE_DIR / "company_universe.csv"
MANUAL_FINANCIALS_PATH = ROOT / "data/raw/financial_statements_raw.csv"

FINANCIAL_FACTS_PATH = NORMALIZED_DIR / "financial_facts.csv"
LATEST_LONG_PATH = PROCESSED_DIR / "sec_latest_restated_long.csv"
AUTO_CONFLICTS_PATH = PROCESSED_DIR / "sec_concept_conflicts.csv"
RECONCILIATION_PATH = PROCESSED_DIR / "sec_manual_reconciliation.csv"
PILOT_COVERAGE_PATH = PROCESSED_DIR / "b1_pilot_coverage.csv"
PILOT_AUDIT_SUMMARY_PATH = PROCESSED_DIR / "b1_pilot_source_audit.json"

TICKER_MAP_URL = "https://www.sec.gov/files/company_tickers_exchange.json"
COMPANYFACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"
SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik:010d}.json"
SEC_USER_AGENT = os.environ.get(
    "SEC_USER_AGENT", "FinancialHealthScreener/1.0 public-research"
)
SOURCE_CUTOFF = pd.Timestamp("2024-04-30")
PROVISIONAL_LISTING_DATES = {
    "ABNB": "2020-12-10",
    "AMZN": "1997-05-15",
    "BABA": "2014-09-19",
    "BKNG": "1999-03-30",
    "BYON": "2002-05-30",
    "CART": "2023-09-19",
    "CHWY": "2019-06-14",
    "CPNG": "2021-03-11",
    "DASH": "2020-12-09",
    "EBAY": "1998-09-24",
    "ETSY": "2015-04-16",
    "EXPE": "1999-11-10",
    "FTCH": "2018-09-21",
    "GRPN": "2011-11-04",
    "JD": "2014-05-22",
    "MELI": "2007-08-10",
    "PDD": "2018-07-26",
    "POSH": "2021-01-14",
    "REAL": "2019-06-28",
    "RVLV": "2019-06-07",
    "SE": "2017-10-20",
    "SFIX": "2017-11-17",
    "SHOP": "2015-05-21",
    "UBER": "2019-05-10",
    "VIPS": "2012-03-23",
    "W": "2014-10-02",
}
CONFLICT_COLUMNS = [
    "conflict_id",
    "company_id",
    "ticker",
    "period_end",
    "fiscal_year",
    "canonical_field",
    "winning_tag",
    "discarded_tag",
    "winning_value",
    "discarded_value",
    "relative_difference",
    "resolution_rule",
    "conflict_severity",
]


def _request_json(url: str) -> dict[str, Any]:
    last_error: requests.RequestException | None = None
    for attempt in range(3):
        try:
            response = requests.get(
                url,
                headers={
                    "User-Agent": SEC_USER_AGENT,
                    "Accept-Encoding": "gzip, deflate",
                    "Accept": "application/json",
                },
                timeout=90,
            )
        except requests.RequestException as error:
            last_error = error
            if attempt == 2:
                raise
            time.sleep(2**attempt)
            continue
        if response.status_code not in {429, 500, 502, 503, 504}:
            response.raise_for_status()
            return response.json()
        time.sleep(2**attempt)
    response.raise_for_status()
    raise RuntimeError(f"SEC request failed after retries: {url}") from last_error


def _write_json_gz(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(payload, ensure_ascii=True, separators=(",", ":")).encode(
        "utf-8"
    )
    with gzip.open(path, "wb", compresslevel=9) as handle:
        handle.write(encoded)


def _read_json_gz(path: Path) -> dict[str, Any]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return json.load(handle)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _cached_json(url: str, path: Path, refresh: bool = False) -> dict[str, Any]:
    if path.exists() and not refresh:
        return _read_json_gz(path)
    payload = _request_json(url)
    _write_json_gz(path, payload)
    time.sleep(0.15)
    return payload


def _ticker_map(refresh: bool = False) -> dict[str, dict[str, Any]]:
    raw_path = RAW_SEC_DIR / "company_tickers_exchange.json.gz"
    payload = _cached_json(TICKER_MAP_URL, raw_path, refresh=refresh)
    fields = payload["fields"]
    return {
        str(row[2]).upper(): dict(zip(fields, row, strict=True))
        for row in payload["data"]
    }


def _sec_paths(cik: int) -> tuple[Path, Path]:
    company_dir = RAW_SEC_DIR / f"CIK{cik:010d}"
    return company_dir / "companyfacts.json.gz", company_dir / "submissions.json.gz"


def _revenue_model(row: pd.Series) -> str:
    first_party = int(row["has_first_party_retail"]) == 1
    marketplace = int(row["has_marketplace"]) == 1
    if first_party and marketplace:
        return "mixed"
    if first_party:
        return "gross"
    if marketplace:
        return "net"
    return "unknown"


def _inventory_ownership(row: pd.Series) -> str:
    first_party = int(row["has_first_party_retail"]) == 1
    marketplace = int(row["has_marketplace"]) == 1
    if first_party and marketplace:
        return "mixed"
    return "true" if first_party else "false"


def _online_core(row: pd.Series) -> str:
    exclusion = str(row["exclude_reason"]).lower()
    if int(row["include_in_core_sample"]) == 1:
        return "true"
    if any(
        phrase in exclusion
        for phrase in ["infrastructure provider", "mobility business dominates"]
    ):
        return "false"
    return "boundary"


def build_company_universe(refresh: bool = False) -> pd.DataFrame:
    master = pd.read_csv(MASTER_PATH, keep_default_na=False)
    scope = pd.read_csv(SCOPE_PATH, keep_default_na=False)
    events = pd.read_csv(EVENTS_PATH, keep_default_na=False)
    ticker_map = _ticker_map(refresh=refresh)
    pilot_tickers = set(scope.loc[scope["scope_status"] == "pilot", "ticker"])
    event_tickers = {company_id.upper() for company_id in events["company_id"]}

    rows: list[dict[str, Any]] = []
    for _, source in master.iterrows():
        ticker = str(source["ticker"]).upper()
        sec_item = ticker_map.get(ticker, {})
        cik_value = sec_item.get("cik")
        fiscal_year_end = ""
        sec_entity_name = ""
        if cik_value and ticker in pilot_tickers:
            cik = int(cik_value)
            _, submissions_path = _sec_paths(cik)
            submissions = _cached_json(
                SUBMISSIONS_URL.format(cik=cik), submissions_path, refresh=refresh
            )
            fiscal_year_end = str(submissions.get("fiscalYearEnd") or "")
            sec_entity_name = str(submissions.get("name", ""))

        if ticker in pilot_tickers:
            confidence = "high"
            analysis_scope_group = "b1_pilot"
        elif int(source["include_in_core_sample"]) == 1:
            confidence = "medium"
            analysis_scope_group = "q1_candidate"
        elif source["listing_status"] != "active":
            confidence = "medium"
            analysis_scope_group = "historical_reference"
        else:
            confidence = "low"
            analysis_scope_group = "watchlist"

        status_group = (
            "acquired"
            if source["listing_status"] == "delisted_acquired"
            else source["listing_status"]
        )

        rows.append(
            {
                "company_id": ticker.lower(),
                "ticker": ticker,
                "company_name": source["company_name"],
                "cik": f"{int(cik_value):010d}" if cik_value else "",
                "exchange": sec_item.get("exchange") or source["exchange"],
                "listing_date": PROVISIONAL_LISTING_DATES[ticker],
                "listing_date_source_note": (
                    "Provisional public-listing date from the project census; "
                    "reverify during A1 before A3 coverage verification"
                ),
                "peer_group": source["peer_group"],
                "classification_confidence": confidence,
                "status_group": status_group,
                "analysis_scope_group": analysis_scope_group,
                "online_core_flag": _online_core(source),
                "inventory_ownership_flag": _inventory_ownership(source),
                "revenue_recognition_model": _revenue_model(source),
                "fiscal_year_end": fiscal_year_end,
                "include_q1_candidate": int(source["include_in_core_sample"]),
                "b1_pilot_included": int(ticker in pilot_tickers),
                "q2_event_candidate": int(ticker in event_tickers),
                "exclusion_reason": source["exclude_reason"],
                "sec_entity_name": sec_entity_name,
                "source_note": (
                    "SEC ticker map and submissions metadata; project classification"
                    if ticker in pilot_tickers
                    else "SEC ticker map where current; project census classification"
                ),
            }
        )

    universe = pd.DataFrame(rows).sort_values(["analysis_scope_group", "ticker"])
    if universe["company_id"].duplicated().any() or universe["ticker"].duplicated().any():
        raise ValueError("Company universe contains duplicate identifiers")
    UNIVERSE_PATH.parent.mkdir(parents=True, exist_ok=True)
    universe.to_csv(UNIVERSE_PATH, index=False)
    return universe


def extract_sec(refresh: bool = False) -> pd.DataFrame:
    universe = (
        pd.read_csv(UNIVERSE_PATH, keep_default_na=False)
        if UNIVERSE_PATH.exists()
        else build_company_universe(refresh=refresh)
    )
    selected = universe[universe["b1_pilot_included"] == 1].copy()
    manifest_rows: list[dict[str, Any]] = []
    fetched_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    for _, company in selected.sort_values("ticker").iterrows():
        cik = int(company["cik"])
        facts_path, submissions_path = _sec_paths(cik)
        _cached_json(
            COMPANYFACTS_URL.format(cik=cik), facts_path, refresh=refresh
        )
        _cached_json(
            SUBMISSIONS_URL.format(cik=cik), submissions_path, refresh=refresh
        )
        manifest_rows.extend(
            [
                {
                    "ticker": company["ticker"],
                    "cik": f"{cik:010d}",
                    "artifact": "companyfacts",
                    "relative_path": str(facts_path.relative_to(ROOT)),
                    "source_url": COMPANYFACTS_URL.format(cik=cik),
                    "sha256": _sha256(facts_path),
                    "fetched_at": fetched_at,
                },
                {
                    "ticker": company["ticker"],
                    "cik": f"{cik:010d}",
                    "artifact": "submissions",
                    "relative_path": str(submissions_path.relative_to(ROOT)),
                    "source_url": SUBMISSIONS_URL.format(cik=cik),
                    "sha256": _sha256(submissions_path),
                    "fetched_at": fetched_at,
                },
            ]
        )

    manifest_path = RAW_SEC_DIR / "manifest.csv"
    if manifest_path.exists() and not refresh:
        existing = pd.read_csv(manifest_path, keep_default_na=False)
        fetched_lookup = existing.set_index(["ticker", "artifact"])["fetched_at"].to_dict()
        for row in manifest_rows:
            row["fetched_at"] = fetched_lookup.get(
                (row["ticker"], row["artifact"]), row["fetched_at"]
            )
    manifest = pd.DataFrame(manifest_rows).sort_values(["ticker", "artifact"])
    manifest.to_csv(manifest_path, index=False)
    return manifest


def normalize_annual_facts() -> pd.DataFrame:
    universe = pd.read_csv(UNIVERSE_PATH, dtype={"cik": str}, keep_default_na=False)
    concepts = pd.read_csv(CONCEPT_MAP_PATH, keep_default_na=False)
    manual = pd.read_csv(MANUAL_FINANCIALS_PATH, keep_default_na=False)
    manual["period_end_date"] = pd.to_datetime(manual["period_end_date"]).dt.date
    period_lookup = {
        (row.ticker, row.period_end_date): int(row.fiscal_year)
        for row in manual[["ticker", "fiscal_year", "period_end_date"]].itertuples()
    }
    manifest = pd.read_csv(RAW_SEC_DIR / "manifest.csv", keep_default_na=False)
    loaded_lookup = (
        manifest[manifest["artifact"] == "companyfacts"]
        .set_index("ticker")["fetched_at"]
        .to_dict()
    )

    rows: list[dict[str, Any]] = []
    pilot = universe[universe["b1_pilot_included"] == 1]
    mapped_concepts = concepts[concepts["taxonomy"].isin(["us-gaap", "dei"])]
    for _, company in pilot.sort_values("ticker").iterrows():
        ticker = company["ticker"]
        cik = int(company["cik"])
        facts_path, _ = _sec_paths(cik)
        payload = _read_json_gz(facts_path)
        all_taxonomies = payload.get("facts", {})
        for _, concept in mapped_concepts.iterrows():
            taxonomy = concept["taxonomy"]
            expected_unit = concept["expected_unit"]
            source_tags = [tag for tag in concept["source_tag"].split("|") if tag]
            for source_priority, source_tag in enumerate(source_tags, start=1):
                fact = all_taxonomies.get(taxonomy, {}).get(source_tag)
                if not fact:
                    continue
                units = fact.get("units", {})
                entries = units.get(expected_unit, [])
                for item in entries:
                    form = str(item.get("form", ""))
                    if form not in {"10-K", "10-K/A"}:
                        continue
                    end_value = item.get("end")
                    if not end_value:
                        continue
                    end_date = pd.Timestamp(end_value).date()
                    fiscal_year = period_lookup.get((ticker, end_date))
                    if fiscal_year is None:
                        continue
                    start_value = item.get("start")
                    duration_days: int | None = None
                    if start_value:
                        start_date = pd.Timestamp(start_value).date()
                        duration_days = (end_date - start_date).days
                    else:
                        start_date = None
                    if concept["flow_or_stock"] == "flow" and not (
                        duration_days is not None and 330 <= duration_days <= 385
                    ):
                        continue
                    value_reported = float(item["val"])
                    if expected_unit == "USD":
                        value_standardized = value_reported / 1_000_000
                        unit_scale = "USD_millions"
                    elif expected_unit == "shares":
                        value_standardized = value_reported / 1_000_000
                        unit_scale = "shares_millions"
                    else:
                        value_standardized = value_reported
                        unit_scale = expected_unit
                    if concept["sign_multiplier"] == "abs":
                        value_standardized = abs(value_standardized)
                    accession = str(item.get("accn", ""))
                    filing_date = str(item.get("filed", ""))
                    accession_compact = accession.replace("-", "")
                    source_url = (
                        f"https://www.sec.gov/Archives/edgar/data/{cik}/"
                        f"{accession_compact}/"
                    )
                    rows.append(
                        {
                            "company_id": company["company_id"],
                            "ticker": ticker,
                            "cik": f"{cik:010d}",
                            "fiscal_year": fiscal_year,
                            "period_end": end_date.isoformat(),
                            "start_date": start_date.isoformat() if start_date else "",
                            "canonical_field": concept["canonical_field"],
                            "taxonomy": taxonomy,
                            "source_tag": source_tag,
                            "source_priority": source_priority,
                            "value_reported": value_reported,
                            "value_standardized": value_standardized,
                            "unit": expected_unit,
                            "unit_scale": unit_scale,
                            "form": form,
                            "fy": item.get("fy", ""),
                            "fp": item.get("fp", ""),
                            "frame": item.get("frame", ""),
                            "accession": accession,
                            "filing_date": filing_date,
                            "is_amendment": int(form.endswith("/A")),
                            "duration_days": duration_days,
                            "source_url": source_url,
                            "loaded_at": loaded_lookup.get(ticker, ""),
                        }
                    )

    financial_facts = pd.DataFrame(rows)
    if financial_facts.empty:
        raise ValueError("No annual SEC facts were normalized")
    preferred_by_accession = financial_facts.sort_values("source_priority").drop_duplicates(
        ["ticker", "fiscal_year", "accession", "canonical_field"]
    )
    derived_rows: list[dict[str, Any]] = []
    accession_key = ["ticker", "fiscal_year", "accession"]
    for _, group in preferred_by_accession.groupby(accession_key, sort=False):
        concepts_in_group = set(group["canonical_field"])
        if "total_liabilities" in concepts_in_group or not {
            "total_assets",
            "total_equity",
        }.issubset(concepts_in_group):
            continue
        assets = group[group["canonical_field"] == "total_assets"].iloc[0]
        equity = group[group["canonical_field"] == "total_equity"].iloc[0]
        derived = assets.to_dict()
        derived.update(
            {
                "canonical_field": "total_liabilities",
                "taxonomy": "project",
                "source_tag": "derived:Assets-StockholdersEquity",
                "source_priority": 99,
                "value_reported": (
                    float(assets["value_reported"])
                    - float(equity["value_reported"])
                ),
                "value_standardized": (
                    float(assets["value_standardized"])
                    - float(equity["value_standardized"])
                ),
                "start_date": "",
                "duration_days": None,
            }
        )
        derived_rows.append(derived)
    if derived_rows:
        financial_facts = pd.concat(
            [financial_facts, pd.DataFrame(derived_rows)], ignore_index=True
        )
    key = [
        "ticker",
        "canonical_field",
        "period_end",
        "start_date",
        "source_tag",
        "accession",
        "value_standardized",
    ]
    financial_facts = financial_facts.drop_duplicates(key).sort_values(
        ["ticker", "fiscal_year", "canonical_field", "filing_date", "source_priority"]
    )
    NORMALIZED_DIR.mkdir(parents=True, exist_ok=True)
    financial_facts.to_csv(FINANCIAL_FACTS_PATH, index=False)
    return financial_facts


def select_latest_restated() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    facts = pd.read_csv(FINANCIAL_FACTS_PATH, dtype={"cik": str}, keep_default_na=False)
    facts["filing_date_parsed"] = pd.to_datetime(facts["filing_date"], errors="coerce")
    eligible = facts[facts["filing_date_parsed"].le(SOURCE_CUTOFF)].copy()
    eligible = eligible.sort_values(
        [
            "ticker",
            "fiscal_year",
            "canonical_field",
            "filing_date_parsed",
            "source_priority",
            "accession",
        ],
        ascending=[True, True, True, False, True, False],
    )
    group_key = ["ticker", "fiscal_year", "canonical_field"]
    latest = eligible.drop_duplicates(group_key, keep="first").copy()
    latest["is_latest_restated"] = True
    latest["source_selection_note"] = (
        "Latest annual filing available by 2024-04-30; source-tag priority breaks ties"
    )
    latest = latest.drop(columns=["filing_date_parsed"])
    latest.to_csv(LATEST_LONG_PATH, index=False)

    winner_lookup = latest.set_index(group_key)
    conflict_rows: list[dict[str, Any]] = []
    conflict_number = 1
    for keys, group in eligible.groupby(group_key, sort=True):
        distinct = group.drop_duplicates(
            ["source_tag", "accession", "value_standardized"]
        )
        if distinct["value_standardized"].nunique() <= 1:
            continue
        winner = winner_lookup.loc[keys]
        for _, discarded in distinct.iterrows():
            same_winner = (
                discarded["source_tag"] == winner["source_tag"]
                and discarded["accession"] == winner["accession"]
                and float(discarded["value_standardized"])
                == float(winner["value_standardized"])
            )
            if same_winner:
                continue
            denominator = max(abs(float(winner["value_standardized"])), 1e-9)
            relative_difference = abs(
                float(discarded["value_standardized"])
                - float(winner["value_standardized"])
            ) / denominator
            conflict_rows.append(
                {
                    "conflict_id": f"AUTO-{conflict_number:05d}",
                    "company_id": winner["company_id"],
                    "ticker": keys[0],
                    "period_end": winner["period_end"],
                    "fiscal_year": keys[1],
                    "canonical_field": keys[2],
                    "winning_tag": winner["source_tag"],
                    "discarded_tag": discarded["source_tag"],
                    "winning_value": winner["value_standardized"],
                    "discarded_value": discarded["value_standardized"],
                    "relative_difference": relative_difference,
                    "resolution_rule": "latest filing then source-tag priority",
                    "conflict_severity": (
                        "high"
                        if relative_difference > 0.05
                        else "medium"
                        if relative_difference > 0.005
                        else "low"
                    ),
                }
            )
            conflict_number += 1
    conflicts = pd.DataFrame(conflict_rows, columns=CONFLICT_COLUMNS)
    conflicts.to_csv(AUTO_CONFLICTS_PATH, index=False)

    manual = pd.read_csv(MANUAL_FINANCIALS_PATH, keep_default_na=False)
    manual_long = manual.melt(
        id_vars=["ticker", "fiscal_year"],
        value_vars=sorted(set(latest["canonical_field"]) & set(manual.columns)),
        var_name="canonical_field",
        value_name="manual_value",
    )
    manual_long["manual_value"] = pd.to_numeric(
        manual_long["manual_value"], errors="coerce"
    )
    reconciliation = latest.merge(manual_long, on=group_key, how="left")
    reconciliation["absolute_gap"] = (
        reconciliation["value_standardized"] - reconciliation["manual_value"]
    ).abs()
    reconciliation["relative_gap"] = reconciliation["absolute_gap"] / reconciliation[
        "manual_value"
    ].abs().clip(lower=1e-9)
    reconciliation["match_within_tolerance"] = reconciliation["absolute_gap"].le(
        reconciliation["manual_value"].abs().mul(0.005).clip(lower=0.01)
    )
    reconciliation["reconciliation_status"] = reconciliation.apply(
        lambda row: "manual_value_unavailable"
        if pd.isna(row["manual_value"])
        else "match"
        if bool(row["match_within_tolerance"])
        else "review_company_mapping",
        axis=1,
    )
    reconciliation.to_csv(RECONCILIATION_PATH, index=False)
    return latest, conflicts, reconciliation


def _write_source_probe_report(
    facts: pd.DataFrame, latest: pd.DataFrame, reconciliation: pd.DataFrame
) -> None:
    generated_on = date.today().isoformat()
    lines = [
        "# A2 Two-Company SEC Source Probe",
        "",
        f"Probe date: {generated_on}",
        "",
        "The probe uses Amazon (inventory-led/hybrid) and eBay (marketplace) to test the official SEC companyfacts source, accession-level version retention, annual-duration filtering, source-tag priority, sign handling, and latest-restated selection.",
        "",
        "## Probe Results",
        "",
        "| Ticker | Normalized facts | Latest canonical facts | Manual matches | Review mappings |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for ticker in ["AMZN", "EBAY"]:
        probe_facts = facts[facts["ticker"] == ticker]
        probe_latest = latest[latest["ticker"] == ticker]
        probe_recon = reconciliation[reconciliation["ticker"] == ticker]
        lines.append(
            f"| {ticker} | {len(probe_facts)} | {len(probe_latest)} | "
            f"{int((probe_recon['reconciliation_status'] == 'match').sum())} | "
            f"{int((probe_recon['reconciliation_status'] == 'review_company_mapping').sum())} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- SEC raw JSON is cached without replacing the manually reconciled Pilot mart.",
            "- Comparative annual facts retain accession and filing date, so restatements are visible rather than silently overwritten.",
            "- Differences are routed to `sec_manual_reconciliation.csv`; they are not auto-forced into the Pilot mart.",
            "- The Pilot source cutoff is 2024-04-30, matching the filing vintage used for the FY2021-FY2023 snapshot.",
            "",
            "This is reusable A2 probe evidence. A2 is formally closed only after A1 reaches its stopping rules and the probe is revalidated against that candidate pool.",
        ]
    )
    (DOCS_DIR / "source_probe_report.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def build_pilot_coverage(
    facts: pd.DataFrame, latest: pd.DataFrame, conflicts: pd.DataFrame, reconciliation: pd.DataFrame
) -> pd.DataFrame:
    generated_on = date.today().isoformat()
    concepts = pd.read_csv(CONCEPT_MAP_PATH, keep_default_na=False)
    required = set(
        concepts.loc[concepts["required_for_q1"] == 1, "canonical_field"]
    ) - {"free_cash_flow"}
    pilot = pd.read_csv(SCOPE_PATH, keep_default_na=False).query(
        "scope_status == 'pilot'"
    )
    rows: list[dict[str, Any]] = []
    for ticker in sorted(pilot["ticker"]):
        for field in sorted(required):
            selected = latest[
                (latest["ticker"] == ticker) & (latest["canonical_field"] == field)
            ]
            recon = reconciliation[
                (reconciliation["ticker"] == ticker)
                & (reconciliation["canonical_field"] == field)
            ]
            rows.append(
                {
                    "ticker": ticker,
                    "canonical_field": field,
                    "required_for_q1": 1,
                    "years_present": "|".join(
                        str(year) for year in sorted(selected["fiscal_year"].unique())
                    ),
                    "year_count": int(selected["fiscal_year"].nunique()),
                    "expected_year_count": 3,
                    "coverage_complete_flag": int(
                        selected["fiscal_year"].nunique() == 3
                    ),
                    "manual_match_count": int(
                        (recon["reconciliation_status"] == "match").sum()
                    ),
                    "review_mapping_count": int(
                        (recon["reconciliation_status"] == "review_company_mapping").sum()
                    ),
                }
            )
    coverage = pd.DataFrame(rows)
    coverage.to_csv(PILOT_COVERAGE_PATH, index=False)

    manifest = pd.read_csv(RAW_SEC_DIR / "manifest.csv", keep_default_na=False)
    events = pd.read_csv(EVENTS_PATH, keep_default_na=False)
    universe = pd.read_csv(UNIVERSE_PATH, keep_default_na=False)
    summary = {
        "generated_on": generated_on,
        "source_cutoff": SOURCE_CUTOFF.date().isoformat(),
        "universe_company_count": int(len(universe)),
        "b1_pilot_company_count": int(universe["b1_pilot_included"].sum()),
        "event_candidate_count": int(events["company_id"].nunique()),
        "cached_raw_artifact_count": int(len(manifest)),
        "normalized_financial_fact_count": int(len(facts)),
        "latest_canonical_fact_count": int(len(latest)),
        "auto_conflict_count": int(len(conflicts)),
        "required_company_field_complete_count": int(
            coverage["coverage_complete_flag"].sum()
        ),
        "required_company_field_total_count": int(len(coverage)),
        "manual_match_count": int(
            (reconciliation["reconciliation_status"] == "match").sum()
        ),
        "manual_review_mapping_count": int(
            (reconciliation["reconciliation_status"] == "review_company_mapping").sum()
        ),
        "gate1_status": "Pending A1 and A3",
        "gate2_status": "Pending A3 event verification",
    }
    PILOT_AUDIT_SUMMARY_PATH.write_text(
        json.dumps(summary, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )

    coverage_by_ticker = coverage.groupby("ticker").agg(
        complete_fields=("coverage_complete_flag", "sum"),
        required_fields=("canonical_field", "count"),
        review_mappings=("review_mapping_count", "sum"),
    )
    coverage_lines = [
        "# B1 Pilot Coverage Snapshot",
        "",
        f"Generated: {generated_on}",
        "",
        "This snapshot caches official SEC JSON for the six Pilot companies, retains accession-level annual facts, and compares latest-restated canonical selections with the manually reconciled Pilot table. It is not the A3 all-candidate coverage report.",
        "",
        "| Ticker | Complete required fields | Required fields | Review mappings |",
        "| --- | ---: | ---: | ---: |",
    ]
    for ticker, row in coverage_by_ticker.iterrows():
        coverage_lines.append(
            f"| {ticker} | {int(row['complete_fields'])} | {int(row['required_fields'])} | {int(row['review_mappings'])} |"
        )
    coverage_lines.extend(
        [
            "",
            "## Decision Use",
            "",
            "- Missing or mismatched SEC facts do not overwrite manually reconciled analytical values.",
            "- Mapping reviews are explicit evidence tasks, not silent pipeline failures.",
            "- The six-company Pilot has zero eligible H1 transitions; this does not determine the formal H1 Evidence Tier.",
            "- Formal H1 Tier and Data Path remain pending the A3 scan across all A1 candidates.",
        ]
    )
    (DOCS_DIR / "b1_pilot_coverage_report.md").write_text(
        "\n".join(coverage_lines) + "\n", encoding="utf-8"
    )

    gate2_lines = [
        "# Gate 2 Status",
        "",
        f"Status date: {generated_on}",
        "",
        "## Current Status",
        "",
        "**Pending. No Tier A/B/C decision is valid until A3 verifies the full event candidate pool.**",
        "",
        "## Why the Earlier No-Go Is Withdrawn",
        "",
        f"- The current event table contains only {len(events)} records across {events['company_id'].nunique()} companies, below the A1 stopping range of approximately 10-15 candidates.",
        "- Blank or unverified quarterly coverage is missing evidence, not proof that point-in-time coverage is infeasible.",
        "- A3 has not yet checked real pre-event quarters, three-statement coverage, filing dates, PIT feasibility, YTD cash-flow reconstruction, peer availability, or manual cost for the full event pool.",
        "",
        "## Required Next Step",
        "",
        "Complete A1 to approximately 10-15 event candidates, perform the A3 event feasibility scan, and then apply the frozen Gate 2 thresholds. Q2 and Q3 remain unbuilt while the decision is pending.",
    ]
    (DOCS_DIR / "gate2_decision.md").write_text(
        "\n".join(gate2_lines) + "\n", encoding="utf-8"
    )
    _write_source_probe_report(facts, latest, reconciliation)
    return coverage


def load_phase_a_tables(
    universe: pd.DataFrame,
    facts: pd.DataFrame,
    latest: pd.DataFrame,
    conflicts: pd.DataFrame,
    coverage: pd.DataFrame,
) -> None:
    events = pd.read_csv(EVENTS_PATH, keep_default_na=False)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(DB_PATH)) as connection:
        tables = {
            "company_universe": universe,
            "events": events,
            "financial_facts": facts,
            "sec_latest_restated_long": latest,
            "sec_concept_conflicts": conflicts,
            "b1_pilot_coverage": coverage,
        }
        for table_name, frame in tables.items():
            connection.register(f"{table_name}_input", frame)
            connection.execute(
                f"create or replace table {table_name} as "
                f"select * from {table_name}_input"
            )


def build_b1_pilot_evidence(refresh: bool = False) -> dict[str, int]:
    universe = build_company_universe(refresh=refresh)
    manifest = extract_sec(refresh=refresh)
    facts = normalize_annual_facts()
    latest, conflicts, reconciliation = select_latest_restated()
    coverage = build_pilot_coverage(
        facts, latest, conflicts, reconciliation
    )
    load_phase_a_tables(universe, facts, latest, conflicts, coverage)
    result = {
        "universe_companies": len(universe),
        "raw_artifacts": len(manifest),
        "normalized_facts": len(facts),
        "latest_facts": len(latest),
        "conflicts": len(conflicts),
        "coverage_rows": len(coverage),
    }
    print("Six-company Pilot evidence layer rebuilt.")
    for key, value in result.items():
        print(f"{key}: {value}")
    print("Gate 1: pending A1/A3; Gate 2: pending A3 event verification")
    return result


if __name__ == "__main__":
    build_b1_pilot_evidence()
