from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import date
from pathlib import Path
from typing import Any

os.environ.setdefault(
    "MPLCONFIGDIR",
    str(Path(tempfile.gettempdir()) / "financial-health-screener-matplotlib"),
)

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import nbformat as nbf
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.colors import ListedColormap
from matplotlib.ticker import PercentFormatter
from nbclient import NotebookClient

from build_q1_v3_pipeline import build_b3_analytical_marts


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
REFERENCE = ROOT / "data" / "reference"
CHART_DIR = ROOT / "docs" / "assets" / "q1"
NOTEBOOK_DIR = ROOT / "notebooks"
DOCS = ROOT / "docs"

PEER_ORDER = ["marketplace_platform", "inventory_led_ecommerce", "dtc_brand"]
PEER_LABELS = {
    "marketplace_platform": "Marketplace / Platform",
    "inventory_led_ecommerce": "Inventory-led E-commerce",
    "dtc_brand": "DTC Brand",
}
PEER_COLORS = {
    "marketplace_platform": "#2F6B8A",
    "inventory_led_ecommerce": "#C4573A",
    "dtc_brand": "#2F7D5A",
}
DRIVER_COLORS = {
    "leverage_driven": "#C4573A",
    "operating_driven": "#2F6B8A",
}
CORE_FIELDS = [
    "revenue",
    "operating_income",
    "net_income",
    "total_assets",
    "total_liabilities",
    "total_equity",
    "current_assets",
    "current_liabilities",
    "cash_and_equivalents",
    "inventory",
    "total_debt",
    "operating_cash_flow",
    "capital_expenditure",
    "free_cash_flow",
]
CHART_FILES = [
    "01_coverage_and_dupont_validity.png",
    "02_peer_group_dupont_distributions.png",
    "03_similar_roe_different_drivers.png",
    "04_h1_exclusion_waterfall.png",
    "05_h1_peer_relative_outcomes.png",
    "06_quality_warning_matrix.png",
    "07_h1_year_distribution.png",
    "08_bkng_denominator_warning.png",
]


def configure_plotting() -> None:
    sns.set_theme(style="whitegrid", context="notebook")
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.titleweight": "bold",
            "axes.titlesize": 12,
            "axes.labelsize": 10,
            "font.family": "DejaVu Sans",
            "savefig.dpi": 190,
            "savefig.bbox": "tight",
        }
    )


def load_tables() -> dict[str, pd.DataFrame]:
    names = [
        "q1_latest_restated",
        "q1_annual_company_metrics",
        "q1_dupont_contributions",
        "q1_peer_summary",
        "q1_company_vs_peer",
        "q1_driver_persistence",
        "q1_h1_sample_audit",
        "q1_h1_exclusion_waterfall",
        "q1_h1_evidence_summary",
        "q1_powerbi_mart",
    ]
    tables = {name: pd.read_csv(PROCESSED / f"{name}.csv") for name in names}
    tables["formal_sample"] = pd.read_csv(REFERENCE / "q1_formal_sample_v1.csv")
    tables["metric_flags"] = pd.read_csv(PROCESSED / "metric_flags.csv")
    tables["conflicts"] = pd.read_csv(PROCESSED / "sec_concept_conflicts.csv")
    tables["reconciliation"] = pd.read_csv(
        PROCESSED / "b2_sec_manual_reconciliation.csv"
    )
    return tables


def build_eda_tables(tables: dict[str, pd.DataFrame]) -> dict[str, Any]:
    metrics = tables["q1_annual_company_metrics"]
    contributions = tables["q1_dupont_contributions"]
    h1 = tables["q1_h1_sample_audit"]
    latest = tables["q1_latest_restated"]
    conflicts = tables["conflicts"]
    flags = tables["metric_flags"]

    coverage = (
        metrics.groupby("company_id", as_index=False)
        .agg(
            ticker=("ticker", "first"),
            company_name=("company_name", "first"),
            formal_peer_group=("formal_peer_group", "first"),
            first_fiscal_year=("fiscal_year", "min"),
            last_fiscal_year=("fiscal_year", "max"),
            company_year_rows=("fiscal_year", "size"),
            valid_dupont_company_years=("dupont_valid_flag", "sum"),
            metric_flag_count=("metric_flag_count", "sum"),
            unresolved_conflict_count=("unresolved_conflict_count", "sum"),
        )
        .sort_values(["formal_peer_group", "ticker"])
    )
    valid_transitions = (
        contributions.groupby("company_id")["transition_valid_flag"]
        .sum()
        .rename("valid_dupont_transitions")
    )
    coverage = coverage.join(valid_transitions, on="company_id")
    coverage.to_csv(PROCESSED / "q1_coverage_summary.csv", index=False)

    missingness = pd.DataFrame(
        {
            "field": CORE_FIELDS,
            "missing_rows": [int(metrics[field].isna().sum()) for field in CORE_FIELDS],
            "missing_rate": [float(metrics[field].isna().mean()) for field in CORE_FIELDS],
        }
    ).sort_values(["missing_rows", "field"], ascending=[False, True])
    missingness.to_csv(PROCESSED / "q1_missingness_summary.csv", index=False)

    conflict_summary = (
        conflicts.groupby(["conflict_severity", "resolution_status"], as_index=False)
        .agg(conflict_count=("conflict_id", "size"), companies=("company_id", "nunique"))
        .sort_values(["conflict_severity", "resolution_status"])
    )
    conflict_summary.to_csv(PROCESSED / "q1_conflict_summary.csv", index=False)

    selection_summary = (
        latest.groupby(["source_selection_method", "canonical_field"], as_index=False)
        .agg(selected_fact_count=("company_id", "size"), companies=("company_id", "nunique"))
        .sort_values(["source_selection_method", "canonical_field"])
    )
    selection_summary.to_csv(PROCESSED / "q1_latest_selection_summary.csv", index=False)

    flag_summary = (
        flags.groupby(["flag_code", "severity"], as_index=False)
        .agg(flagged_company_years=("company_id", "size"), unique_companies=("company_id", "nunique"))
        .sort_values(["severity", "flagged_company_years"], ascending=[True, False])
    )
    flag_summary.to_csv(PROCESSED / "q1_metric_flag_summary.csv", index=False)

    eligible = h1[h1["h1_eligible_flag"]].copy()
    company_concentration = (
        eligible.groupby(["company_id", "ticker"], as_index=False)
        .agg(
            eligible_transitions=("fiscal_year", "size"),
            leverage_transitions=(
                "h1_driver_group",
                lambda values: int((values == "leverage_driven").sum()),
            ),
            operating_transitions=(
                "h1_driver_group",
                lambda values: int((values == "operating_driven").sum()),
            ),
        )
        .sort_values(["eligible_transitions", "ticker"], ascending=[False, True])
    )
    company_concentration["transition_share"] = (
        company_concentration["eligible_transitions"] / len(eligible)
    )
    company_concentration.to_csv(
        PROCESSED / "q1_h1_company_concentration.csv", index=False
    )

    peer_distribution = (
        eligible.groupby(["formal_peer_group", "h1_driver_group"], as_index=False)
        .agg(transitions=("fiscal_year", "size"), unique_companies=("company_id", "nunique"))
        .sort_values(["formal_peer_group", "h1_driver_group"])
    )
    peer_distribution.to_csv(PROCESSED / "q1_h1_peer_distribution.csv", index=False)

    year_distribution = (
        eligible.groupby(["fiscal_year", "h1_driver_group"], as_index=False)
        .agg(transitions=("company_id", "size"), unique_companies=("company_id", "nunique"))
        .sort_values(["fiscal_year", "h1_driver_group"])
    )
    year_distribution.to_csv(PROCESSED / "q1_h1_year_distribution.csv", index=False)

    h1_group_summary = (
        eligible.groupby("h1_driver_group", as_index=False)
        .agg(
            transitions=("company_id", "size"),
            unique_companies=("company_id", "nunique"),
            median_peer_relative_outcome=("next_year_peer_relative_change", "median"),
            median_raw_roe_outcome=("next_year_roe_change", "median"),
            reversal_rate=("roe_reversal_flag", "mean"),
        )
        .sort_values("h1_driver_group")
    )
    h1_group_summary.to_csv(PROCESSED / "q1_h1_group_summary.csv", index=False)

    valid_metrics = metrics[metrics["dupont_valid_flag"]]
    peer_metric_summary = (
        valid_metrics.groupby("formal_peer_group", as_index=False)
        .agg(
            valid_company_years=("company_id", "size"),
            unique_companies=("company_id", "nunique"),
            median_roe=("roe", "median"),
            median_net_margin=("net_margin", "median"),
            median_asset_turnover=("asset_turnover", "median"),
            median_equity_multiplier=("equity_multiplier", "median"),
        )
        .sort_values("formal_peer_group")
    )
    peer_metric_summary.to_csv(PROCESSED / "q1_peer_metric_summary.csv", index=False)

    case_keys = pd.DataFrame(
        [
            {"ticker": "ABNB", "fiscal_year": 2022, "case_role": "similar_roe_high_margin"},
            {"ticker": "LOVE", "fiscal_year": 2022, "case_role": "similar_roe_high_turnover"},
            {"ticker": "BKNG", "fiscal_year": 2023, "case_role": "near_zero_equity_warning"},
        ]
    )
    cases = case_keys.merge(
        tables["q1_company_vs_peer"], on=["ticker", "fiscal_year"], how="left"
    )
    cases.to_csv(PROCESSED / "q1_company_cases.csv", index=False)

    findings = pd.DataFrame(
        [
            {
                "finding_id": "Q1A-01",
                "finding_type": "peer_profile",
                "finding": "Across valid formal company-years, Marketplace / Platform has the highest median ROE and net margin, while DTC and Inventory-led groups rely more heavily on asset turnover.",
                "evidence_boundary": "Descriptive benchmark for the frozen unbalanced panel, not an industry estimate.",
            },
            {
                "finding_id": "Q1A-02",
                "finding_type": "similar_roe_different_drivers",
                "finding": "ABNB and LOVE both produced about 36% ROE in FY2022, but ABNB used a 22.5% margin and 0.56x turnover while LOVE used a 9.5% margin and 1.84x turnover.",
                "evidence_boundary": "Illustrates that similar ROE can encode different operating quality and business models.",
            },
            {
                "finding_id": "Q1A-03",
                "finding_type": "denominator_counterexample",
                "finding": "BKNG demonstrates that positive but near-zero average equity can make ROE and next-year changes mechanically extreme even when the DuPont identity is correct.",
                "evidence_boundary": "A valid arithmetic result is not automatically a stable economic comparison.",
            },
            {
                "finding_id": "H1-01",
                "finding_type": "tier_b_result",
                "finding": "The leverage-driven group has a +35.2 percentage-point median next-year peer-relative change versus -11.9 points for operating-driven improvements, opposite the H1 direction.",
                "evidence_boundary": "Tier B descriptive pattern only: four leverage transitions across three companies, with material year imbalance.",
            },
            {
                "finding_id": "H1-02",
                "finding_type": "counterexample",
                "finding": "EBAY and ETSY FY2019 leverage-driven improvements strengthened in FY2020 rather than fading, while BKNG FY2019 and ETSY FY2021 reversed.",
                "evidence_boundary": "Mixed company trajectories do not support a validated general relationship.",
            },
            {
                "finding_id": "H1-03",
                "finding_type": "year_effect",
                "finding": "FY2020-FY2021 contain 47.6% of eligible transitions, and all leverage-driven transitions occur in FY2019 or FY2021.",
                "evidence_boundary": "Peer-relative outcomes reduce but cannot remove year-composition risk.",
            },
            {
                "finding_id": "H1-04",
                "finding_type": "falsification_rule",
                "finding": "H1 would not be supported if leverage-driven improvements remain at least as persistent as operating-driven improvements across more independent companies and balanced years.",
                "evidence_boundary": "The current Tier B pattern already fails to show the expected direction.",
            },
        ]
    )
    findings.to_csv(PROCESSED / "q1_research_findings.csv", index=False)

    reconciliation = tables["reconciliation"].query(
        "ticker in ['AMZN', 'CHWY'] and fiscal_year == 2023 and "
        "canonical_field in ['revenue', 'net_income', 'total_assets', 'total_equity']"
    ).copy()
    reconciliation = reconciliation.sort_values(["ticker", "canonical_field"])
    reconciliation.to_csv(PROCESSED / "b4_filing_reconciliation.csv", index=False)

    evidence = tables["q1_h1_evidence_summary"].iloc[0].to_dict()
    return {
        "data_as_of": str(metrics["data_as_of"].max()),
        "formal_company_count": int(metrics["company_id"].nunique()),
        "formal_company_year_count": int(len(metrics)),
        "valid_dupont_company_year_count": int(metrics["dupont_valid_flag"].sum()),
        "eligible_transition_count": int(evidence["eligible_transition_count"]),
        "eligible_unique_company_count": int(evidence["eligible_unique_company_count"]),
        "evidence_tier": evidence["evidence_tier"],
        "leverage_median_outcome": float(evidence["leverage_group_median_outcome"]),
        "operating_median_outcome": float(evidence["operating_group_median_outcome"]),
        "fy2020_2021_share": float(evidence["fy2020_2021_transition_share"]),
    }


def save_coverage_chart(tables: dict[str, pd.DataFrame]) -> None:
    sample = tables["formal_sample"].set_index("ticker")
    metrics = tables["q1_annual_company_metrics"]
    years = list(range(2018, 2025))
    matrix = pd.DataFrame(0, index=sample.index, columns=years, dtype=int)
    for row in sample.itertuples():
        for year in str(row.a3_available_fiscal_years).split("|"):
            matrix.loc[row.Index, int(year)] = 1
    for row in metrics.itertuples(index=False):
        matrix.loc[row.ticker, int(row.fiscal_year)] = 2 if row.dupont_valid_flag else 1
    annotations = matrix.map({0: "", 1: "Invalid", 2: "Valid"}.get)

    fig, ax = plt.subplots(figsize=(10.5, 8.5))
    sns.heatmap(
        matrix,
        annot=annotations,
        fmt="",
        cmap=ListedColormap(["#FFFFFF", "#E7B6A8", "#A9D8C7"]),
        vmin=0,
        vmax=2,
        cbar=False,
        linewidths=0.8,
        linecolor="white",
        ax=ax,
    )
    ax.set_title("Formal company-year coverage and DuPont validity")
    ax.set_xlabel("Fiscal year")
    ax.set_ylabel("")
    fig.text(
        0.5,
        0.01,
        "Blank = outside frozen available years; Invalid = row exists but average-balance DuPont is unusable.",
        ha="center",
        fontsize=9,
        color="#555555",
    )
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(CHART_DIR / CHART_FILES[0])
    plt.close(fig)


def save_peer_distributions(metrics: pd.DataFrame) -> None:
    valid = metrics[metrics["dupont_valid_flag"]].copy()
    valid["peer_label"] = valid["formal_peer_group"].map(PEER_LABELS)
    order = [PEER_LABELS[group] for group in PEER_ORDER]
    palette = {PEER_LABELS[group]: PEER_COLORS[group] for group in PEER_ORDER}
    fields = [
        ("roe", "ROE", True),
        ("net_margin", "Net margin", True),
        ("asset_turnover", "Asset turnover", False),
        ("equity_multiplier", "Equity multiplier", False),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    for ax, (field, title, percent) in zip(axes.flat, fields, strict=True):
        sns.boxplot(
            data=valid,
            x="peer_label",
            y=field,
            order=order,
            hue="peer_label",
            palette=palette,
            legend=False,
            showfliers=False,
            ax=ax,
        )
        sns.stripplot(
            data=valid,
            x="peer_label",
            y=field,
            order=order,
            color="#2B2B2B",
            alpha=0.36,
            size=3,
            jitter=0.2,
            ax=ax,
        )
        ax.set_title(title)
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.tick_params(axis="x", rotation=12)
        if field == "roe":
            ax.set_yscale("symlog", linthresh=0.25)
        elif field == "equity_multiplier":
            ax.set_yscale("log")
        if percent:
            ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    fig.suptitle("Formal peer-group DuPont distributions, FY2018-FY2024", fontsize=16, fontweight="bold")
    fig.text(
        0.5,
        0.01,
        "Each point is a valid company-year. Scales preserve extreme values; comparisons are descriptive.",
        ha="center",
        fontsize=9,
        color="#555555",
    )
    fig.tight_layout(rect=(0, 0.04, 1, 0.96))
    fig.savefig(CHART_DIR / CHART_FILES[1])
    plt.close(fig)


def save_similar_roe_case(company_peer: pd.DataFrame) -> None:
    case = company_peer.query("ticker in ['ABNB', 'LOVE'] and fiscal_year == 2022").copy()
    case = case.set_index("ticker").loc[["ABNB", "LOVE"]].reset_index()
    fields = [
        ("net_margin", "Net margin", "percent"),
        ("asset_turnover", "Asset turnover", "multiple"),
        ("equity_multiplier", "Equity multiplier", "multiple"),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.5))
    colors = [PEER_COLORS[group] for group in case["formal_peer_group"]]
    for ax, (field, title, fmt) in zip(axes, fields, strict=True):
        bars = ax.bar(case["ticker"], case[field], color=colors, width=0.58)
        ax.set_title(title)
        ax.set_xlabel("")
        ax.set_ylabel("")
        labels = [f"{value:.1%}" if fmt == "percent" else f"{value:.2f}x" for value in case[field]]
        ax.bar_label(bars, labels=labels, padding=4, fontsize=9)
        if fmt == "percent":
            ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    roe_text = " | ".join(
        f"{row.ticker} ROE {row.roe:.1%}" for row in case.itertuples(index=False)
    )
    fig.suptitle("Similar FY2022 ROE, different financial engines", fontsize=16, fontweight="bold")
    fig.text(0.5, 0.92, roe_text, ha="center", fontsize=10)
    fig.text(
        0.5,
        0.01,
        "ABNB relies on margin; LOVE relies more on asset turnover. The ROE totals alone conceal that difference.",
        ha="center",
        fontsize=9,
        color="#555555",
    )
    fig.tight_layout(rect=(0, 0.05, 1, 0.87))
    fig.savefig(CHART_DIR / CHART_FILES[2])
    plt.close(fig)


def save_h1_waterfall(waterfall: pd.DataFrame) -> None:
    labels = {
        "eligible": "Eligible",
        "invalid_dupont_transition": "Invalid DuPont transition",
        "turnaround_from_loss": "Turnaround from loss",
        "nonpositive_prior_roe": "Nonpositive prior ROE",
        "no_roe_improvement": "No ROE improvement",
        "mixed_or_ambiguous_driver": "Mixed / ambiguous driver",
        "next_year_not_observable": "Next year not observable",
        "nonpositive_next_average_equity": "Nonpositive next average equity",
    }
    plot_data = waterfall.copy()
    plot_data["label"] = plot_data["h1_exclusion_reason"].map(labels).fillna(
        plot_data["h1_exclusion_reason"]
    )
    plot_data = plot_data.sort_values("transition_count")
    colors = ["#2F7D5A" if value == "eligible" else "#7A8791" for value in plot_data["h1_exclusion_reason"]]
    fig, ax = plt.subplots(figsize=(10, 5.8))
    bars = ax.barh(plot_data["label"], plot_data["transition_count"], color=colors)
    ax.bar_label(bars, padding=4, fontsize=9)
    ax.set_xlabel("Candidate transitions")
    ax.set_ylabel("")
    ax.set_title("Formal H1 eligibility waterfall")
    fig.text(
        0.5,
        0.01,
        "Frozen rules retain 21 eligible transitions across 10 companies; exclusions are not relaxed to increase sample size.",
        ha="center",
        fontsize=9,
        color="#555555",
    )
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(CHART_DIR / CHART_FILES[3])
    plt.close(fig)


def save_h1_outcomes(h1: pd.DataFrame) -> None:
    eligible = h1[h1["h1_eligible_flag"]].copy()
    fig, ax = plt.subplots(figsize=(11, 6.4))
    for x, driver in enumerate(["leverage_driven", "operating_driven"]):
        group = eligible[eligible["h1_driver_group"].eq(driver)].sort_values(
            ["ticker", "fiscal_year"]
        )
        offsets = np.linspace(-0.16, 0.16, len(group)) if len(group) > 1 else np.array([0.0])
        ax.scatter(
            x + offsets,
            group["next_year_peer_relative_change"],
            s=55,
            color=DRIVER_COLORS[driver],
            alpha=0.84,
            edgecolor="white",
            linewidth=0.8,
            zorder=3,
        )
        for offset, row in zip(offsets, group.itertuples(index=False), strict=True):
            should_label = driver == "leverage_driven" or abs(
                row.next_year_peer_relative_change
            ) > 0.4
            if not should_label:
                continue
            vertical_offset = (
                -14
                if row.next_year_peer_relative_change
                == group["next_year_peer_relative_change"].max()
                else 4
            )
            ax.annotate(
                f"{row.ticker} {row.fiscal_year}",
                (x + offset, row.next_year_peer_relative_change),
                xytext=(3, vertical_offset),
                textcoords="offset points",
                fontsize=7,
                alpha=0.82,
            )
        median = group["next_year_peer_relative_change"].median()
        ax.hlines(median, x - 0.28, x + 0.28, color="#111111", linewidth=2.2)
    ax.axhline(0, color="#555555", linewidth=0.9)
    ax.set_yscale("symlog", linthresh=0.25)
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax.set_xticks([0, 1], ["Leverage-driven\n4 transitions / 3 companies", "Operating-driven\n17 transitions / 10 companies"])
    ax.set_ylabel("Next-year peer-relative ROE change")
    ax.set_title("Tier B persistence outcomes: the expected H1 direction is not observed")
    fig.text(
        0.5,
        0.01,
        "Black bars show medians. Symmetric-log scale retains extreme denominator-sensitive outcomes without truncation.",
        ha="center",
        fontsize=9,
        color="#555555",
    )
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(CHART_DIR / CHART_FILES[4])
    plt.close(fig)


def save_quality_matrix(metrics: pd.DataFrame) -> None:
    matrix = metrics.pivot(index="ticker", columns="fiscal_year", values="quality_warning_count")
    fig, ax = plt.subplots(figsize=(10.5, 8.2))
    sns.heatmap(
        matrix,
        cmap=sns.color_palette("YlOrRd", as_cmap=True),
        annot=True,
        fmt=".0f",
        linewidths=0.7,
        linecolor="white",
        cbar_kws={"label": "Automated warning count"},
        ax=ax,
    )
    ax.set_title("Formal metric and source warning counts")
    ax.set_xlabel("Fiscal year")
    ax.set_ylabel("")
    fig.text(
        0.5,
        0.01,
        "Warnings preserve missing prior balances, nonpositive equity, source conflicts, and unavailable forward years.",
        ha="center",
        fontsize=9,
        color="#555555",
    )
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(CHART_DIR / CHART_FILES[5])
    plt.close(fig)


def save_h1_year_distribution(h1: pd.DataFrame) -> None:
    eligible = h1[h1["h1_eligible_flag"]]
    counts = (
        eligible.groupby(["fiscal_year", "h1_driver_group"])
        .size()
        .unstack(fill_value=0)
        .reindex(columns=["leverage_driven", "operating_driven"], fill_value=0)
    )
    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    counts.plot(
        kind="bar",
        color=[DRIVER_COLORS[column] for column in counts.columns],
        width=0.72,
        ax=ax,
    )
    ax.set_xlabel("Transition ending fiscal year")
    ax.set_ylabel("Eligible transitions")
    ax.set_title("H1 driver groups are not balanced across fiscal years")
    ax.legend(["Leverage-driven", "Operating-driven"], title="Driver")
    ax.tick_params(axis="x", rotation=0)
    fig.text(
        0.5,
        0.01,
        "FY2020-FY2021 contain 47.6% of eligible transitions; leverage cases occur only in FY2019 and FY2021.",
        ha="center",
        fontsize=9,
        color="#555555",
    )
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(CHART_DIR / CHART_FILES[6])
    plt.close(fig)


def save_denominator_case(metrics: pd.DataFrame) -> None:
    bkng = metrics[metrics["ticker"].eq("BKNG")].sort_values("fiscal_year")
    fig, ax1 = plt.subplots(figsize=(10, 5.6))
    ax2 = ax1.twinx()
    roe_line, = ax1.plot(
        bkng["fiscal_year"],
        bkng["roe"],
        marker="o",
        color="#2F6B8A",
        linewidth=2,
        label="ROE",
    )
    equity_line, = ax2.plot(
        bkng["fiscal_year"],
        bkng["average_equity"],
        marker="s",
        color="#C4573A",
        linewidth=2,
        label="Average equity",
    )
    ax1.axhline(0, color="#777777", linewidth=0.8)
    ax2.axhline(0, color="#C4573A", linewidth=0.6, alpha=0.45)
    ax1.set_yscale("symlog", linthresh=0.5)
    ax1.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax1.set_xlabel("Fiscal year")
    ax1.set_ylabel("ROE", color="#2F6B8A")
    ax2.set_ylabel("Average equity, USD millions", color="#C4573A")
    ax1.set_title("BKNG: correct DuPont arithmetic can still be economically unstable")
    ax1.legend([roe_line, equity_line], ["ROE", "Average equity"], loc="upper left")
    fig.text(
        0.5,
        0.01,
        "ROE becomes extreme as average equity approaches zero and becomes invalid after average equity turns nonpositive.",
        ha="center",
        fontsize=9,
        color="#555555",
    )
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(CHART_DIR / CHART_FILES[7])
    plt.close(fig)


def make_notebook(title: str, purpose: str, cells: list[Any], filename: str, data_as_of: str) -> Path:
    notebook = nbf.v4.new_notebook()
    notebook["metadata"]["kernelspec"] = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }
    notebook["cells"] = [
        nbf.v4.new_markdown_cell(
            f"# {title}\n\n{purpose}\n\n**Analytical data as of:** {data_as_of}"
        ),
        nbf.v4.new_code_cell(
            "from pathlib import Path\n"
            "import pandas as pd\n"
            "from IPython.display import Image, display\n\n"
            "ROOT = Path.cwd()\n"
            "if ROOT.name == 'notebooks':\n"
            "    ROOT = ROOT.parent\n"
            "pd.set_option('display.max_columns', 100)\n"
            "pd.set_option('display.float_format', lambda value: f'{value:,.4f}')"
        ),
        *cells,
    ]
    path = NOTEBOOK_DIR / filename
    client = NotebookClient(
        notebook,
        timeout=600,
        kernel_name="python3",
        resources={"metadata": {"path": str(ROOT)}},
    )
    executed = client.execute()
    nbf.write(executed, path)
    return path


def build_notebooks(data_as_of: str) -> list[Path]:
    quality_cells = [
        nbf.v4.new_markdown_cell(
            "## Quality boundary\n\nAll missing values remain null. Ratios use protected denominators, latest-restated is explicitly non-point-in-time, and every source conflict remains traceable."
        ),
        nbf.v4.new_code_cell(
            "coverage = pd.read_csv(ROOT / 'data/processed/q1_coverage_summary.csv')\n"
            "missingness = pd.read_csv(ROOT / 'data/processed/q1_missingness_summary.csv')\n"
            "conflicts = pd.read_csv(ROOT / 'data/processed/q1_conflict_summary.csv')\n"
            "flags = pd.read_csv(ROOT / 'data/processed/q1_metric_flag_summary.csv')\n"
            "waterfall = pd.read_csv(ROOT / 'data/processed/q1_h1_exclusion_waterfall.csv')\n"
            "display(coverage)\n"
            "display(missingness)\n"
            "display(conflicts)\n"
            "display(flags)\n"
            "display(waterfall)"
        ),
        nbf.v4.new_code_cell(
            "for name in ['01_coverage_and_dupont_validity.png', '04_h1_exclusion_waterfall.png', '06_quality_warning_matrix.png']:\n"
            "    display(Image(filename=ROOT / 'docs/assets/q1' / name))"
        ),
    ]
    analysis_cells = [
        nbf.v4.new_markdown_cell(
            "## Research questions\n\nQ1-A asks whether similar ROE can come from different margin, turnover, and leverage structures. H1 asks whether leverage-driven improvements are less persistent; Tier B permits descriptive patterns only."
        ),
        nbf.v4.new_code_cell(
            "peer = pd.read_csv(ROOT / 'data/processed/q1_peer_metric_summary.csv')\n"
            "cases = pd.read_csv(ROOT / 'data/processed/q1_company_cases.csv')\n"
            "h1 = pd.read_csv(ROOT / 'data/processed/q1_h1_group_summary.csv')\n"
            "evidence = pd.read_csv(ROOT / 'data/processed/q1_h1_evidence_summary.csv')\n"
            "findings = pd.read_csv(ROOT / 'data/processed/q1_research_findings.csv')\n"
            "display(peer)\n"
            "display(cases[['ticker', 'fiscal_year', 'case_role', 'roe', 'net_margin', 'asset_turnover', 'equity_multiplier', 'quality_warnings']])\n"
            "display(h1)\n"
            "display(evidence)\n"
            "display(findings)"
        ),
        nbf.v4.new_code_cell(
            "for name in ['02_peer_group_dupont_distributions.png', '03_similar_roe_different_drivers.png', '05_h1_peer_relative_outcomes.png', '07_h1_year_distribution.png', '08_bkng_denominator_warning.png']:\n"
            "    display(Image(filename=ROOT / 'docs/assets/q1' / name))"
        ),
        nbf.v4.new_markdown_cell(
            "## Conclusion\n\nThe formal panel confirms that ROE totals conceal materially different financial engines. The Tier B persistence pattern does **not** support H1: leverage-driven outcomes are not descriptively weaker in this small, year-imbalanced sample. No causal, validation, prediction, or investment claim is made."
        ),
    ]
    return [
        make_notebook(
            "Q1 Formal Data Quality",
            "Audits formal coverage, missingness, conflicts, latest-restated handling, metric flags, and H1 exclusions before interpretation.",
            quality_cells,
            "02_data_quality.ipynb",
            data_as_of,
        ),
        make_notebook(
            "Q1 Financial Quality and Tier B Persistence Analysis",
            "Presents formal peer profiles, company cases, exact Shapley drivers, and the frozen-rule Tier B H1 result.",
            analysis_cells,
            "03_q1_analysis.ipynb",
            data_as_of,
        ),
    ]


def write_analysis_report(summary: dict[str, Any]) -> None:
    report = f"""# Q1 Formal Analysis Report

Analytical data as of: **{summary['data_as_of']}**

Release stage: **B4 Analytical Release**

## Scope and Questions

The frozen Path A panel contains {summary['formal_company_count']} U.S.-listed e-commerce companies across Marketplace / Platform, Inventory-led E-commerce, and DTC Brand groups. It contains {summary['formal_company_year_count']} available company-years from FY2018-FY2024; FY2017 is used only for opening balances.

Q1-A asks whether ROE is driven by net margin, asset turnover, or the equity multiplier, and whether similar ROE values conceal different financial quality. H1 asks whether leverage-driven ROE improvements are less persistent one year later than operating-driven improvements.

## Data Quality

- {summary['valid_dupont_company_year_count']} company-years have valid average-balance DuPont metrics.
- Missing values remain null; ratios use protected denominators.
- Latest-restated annual facts are current as of the project run date and are not historical point-in-time observations.
- All source conflicts, candidate rejections, metric flags, and company overrides remain traceable to the B2 layer.
- DuPont and exact Shapley identities reconcile below `1e-10`.

![Formal coverage](assets/q1/01_coverage_and_dupont_validity.png)

## Q1-A: Financial Quality

Across valid company-years, Marketplace / Platform has the highest median ROE and net margin. Inventory-led and DTC companies generally depend more on asset turnover, but within-group dispersion is substantial. These are descriptive benchmarks for the frozen unbalanced panel, not industry estimates.

![Peer distributions](assets/q1/02_peer_group_dupont_distributions.png)

ABNB and LOVE are the clearest same-year example. Both generated roughly 36% ROE in FY2022. ABNB combined a 22.5% net margin with 0.56x turnover; LOVE combined a 9.5% margin with 1.84x turnover. Similar headline return therefore came from different economic engines.

![Similar ROE case](assets/q1/03_similar_roe_different_drivers.png)

BKNG is the required denominator counterexample. Positive but near-zero average equity makes mathematically correct ROE mechanically extreme; once average equity becomes nonpositive, ROE is invalidated rather than ranked.

![BKNG denominator warning](assets/q1/08_bkng_denominator_warning.png)

## H1: Tier B Persistence Pattern

The frozen rules retain {summary['eligible_transition_count']} eligible transitions across {summary['eligible_unique_company_count']} companies. Only four transitions across three companies are leverage-driven; 17 transitions across 10 companies are operating-driven. This is Evidence Tier {summary['evidence_tier']}, so only descriptive persistence patterns are permitted.

The observed direction does **not support H1**. Median next-year peer-relative ROE change is {summary['leverage_median_outcome']:.1%} for leverage-driven improvements and {summary['operating_median_outcome']:.1%} for operating-driven improvements. Reversal rates are close, while individual paths are mixed: EBAY and ETSY FY2019 strengthen, whereas BKNG FY2019 and ETSY FY2021 reverse.

![Tier B outcomes](assets/q1/05_h1_peer_relative_outcomes.png)

The result is not a rejection based on a balanced comparative panel. FY2020-FY2021 contain {summary['fy2020_2021_share']:.1%} of eligible transitions, and all leverage-driven cases occur in FY2019 or FY2021. Peer-relative outcomes reduce common-year effects but cannot remove this composition risk.

![H1 year distribution](assets/q1/07_h1_year_distribution.png)

H1 would not be supported if leverage-driven improvements remain at least as persistent as operating-driven improvements across more independent companies and balanced years. The current Tier B pattern already fails to show the expected direction, but the sample is too small and imbalanced for validation.

## Evidence Boundary

- Company is the independent unit; transitions are repeated observations within companies.
- No company-clustered bootstrap is run because Gate 1 freezes Tier B, not Tier A.
- Turnarounds from nonpositive ROE are excluded from the main H1 sample and retained as separate audit cases.
- Near-zero and nonpositive equity are explicitly flagged; arithmetic validity does not imply economic stability.
- No investment recommendation, distress prediction, causal claim, or population-level industry inference is made.

The executed notebooks are [`02_data_quality.ipynb`](../notebooks/02_data_quality.ipynb) and [`03_q1_analysis.ipynb`](../notebooks/03_q1_analysis.ipynb).
"""
    (DOCS / "q1_analysis_report.md").write_text(report, encoding="utf-8")


def write_reconciliation_report(reconciliation: pd.DataFrame, data_as_of: str) -> None:
    lines = [
        "# B4 Manual Filing Reconciliation",
        "",
        f"Analytical data as of: **{data_as_of}**",
        "",
        "This check compares the scripted latest-valid SEC selection with manually transcribed annual filing values. It does not overwrite either source. Values are USD millions; all selected rows are Form 10-K facts.",
        "",
        "| Ticker | FY | Field | SEC latest | Manual | Relative gap | Status | Accession |",
        "| --- | ---: | --- | ---: | ---: | ---: | --- | --- |",
    ]
    for row in reconciliation.itertuples(index=False):
        lines.append(
            f"| {row.ticker} | {int(row.fiscal_year)} | {row.canonical_field} | "
            f"{row.value_standardized:,.3f} | {row.manual_value:,.3f} | "
            f"{row.relative_gap:.3%} | {row.reconciliation_status} | `{row.accession_number}` |"
        )
    lines.extend(
        [
            "",
            "## Review Result",
            "",
            "- AMZN is the clean calendar-year control; all four fields match exactly.",
            "- CHWY is the complex 52/53-week and comparative-restatement case. Small rounded differences remain below the frozen 0.5% tolerance.",
            "- Period end, unit conversion, reported sign, accession, filing date, and latest-restated version are retained in `data/processed/b4_filing_reconciliation.csv`.",
            "- No processed value was manually edited during reconciliation.",
        ]
    )
    (DOCS / "filing_reconciliation.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def write_recruiter_pitch(summary: dict[str, Any]) -> None:
    content = f"""# Q1 Recruiter and Interview Narrative

## CV Bullet

Built a reproducible Python-DuckDB-Power BI financial-quality screener for 21 U.S.-listed e-commerce companies; normalized filing-level XBRL facts through explicit mapping and restatement rules, decomposed ROE changes with exact Shapley attribution, and examined Tier B descriptive persistence patterns across leverage- and operating-driven improvements.

## 30-Second Introduction

I built a reproducible financial-quality screener for 21 U.S.-listed e-commerce companies. It converts SEC filing facts into average-balance DuPont metrics, peer benchmarks, and exact Shapley explanations of ROE changes. The project also tests a pre-registered persistence idea. The available panel reached Tier B rather than a validation sample, and the descriptive result did not support the expected leverage-is-less-persistent direction. That evidence boundary is part of the product, not something hidden after the analysis.

## Five-Minute Narrative

1. **Question.** Similar ROE can come from margin, asset efficiency, or leverage, so I wanted a product that separates those drivers and tests whether leverage-led improvements fade faster.
2. **Data discipline.** I began with 40 Q1 candidates, probed two issuers, audited full coverage, and froze a 21-company Path A sample before engineering the formal release.
3. **Engineering.** The pipeline retains filing-level accessions, explicit concept conflicts, latest-valid restatements, sign rules, nulls, metric flags, and accession-backed exceptions. Seven ordered DuckDB SQL files produce the analytical marts.
4. **Q1-A result.** ABNB and LOVE both generated roughly 36% FY2022 ROE, but ABNB relied on margin while LOVE relied much more on turnover. BKNG shows why near-zero equity can make correct ROE economically unstable.
5. **H1 result.** The frozen sample has {summary['eligible_transition_count']} eligible transitions across {summary['eligible_unique_company_count']} companies, but only four leverage-driven transitions across three companies. The leverage group median peer-relative next-year outcome is {summary['leverage_median_outcome']:.1%}, versus {summary['operating_median_outcome']:.1%} for the operating group, so the observed direction does not support H1.
6. **Limits.** This is Tier B descriptive evidence. Years are imbalanced, latest-restated is not point-in-time, company-years are not independent companies, and no investment or distress-prediction claim is made.
7. **Product boundary.** B4 is a complete standalone analytical release. B5 adds the single-page Power BI presentation, published in Power BI Service and reconciled against the frozen mart, without moving research logic into DAX.

## Interview Checks

- The independent unit is the company because annual transitions repeat within issuers; the audit reports both {summary['eligible_transition_count']} transitions and {summary['eligible_unique_company_count']} unique companies, and Tier A (not reached) would additionally require company-clustered bootstrap rather than treating transitions as i.i.d.
- The A3 sample audit applied Gate 1's pre-frozen thresholds (Tier A: >=15 unique companies, >=40 transitions, >=8 per driver group): the scan returned {summary['eligible_unique_company_count']} companies with the leverage group at 3-4, short of Tier A on unique-company count, landing in the Tier B band.
- Margin and turnover are combined into "operating-driven" because both represent execution inside the business (pricing/cost control, asset efficiency) as opposed to a capital-structure change; this keeps the primary test binary while margin-only and turnover-only splits stay available as secondary description.
- Exact Shapley attribution handles the multiplicative DuPont identity and reconciles exactly because ROE is a product of three factors, not a sum, and naive per-factor deltas leave an unallocated interaction term.
- Negative-base-ROE turnarounds remain visible but outside the main H1 sample; they are flagged `turnaround_from_loss` for case-level description only.
- XBRL tag conflicts and restatements go through an explicit concept map with frozen tag priority; every disagreement is logged with winning/discarded value and relative difference, with severity thresholds frozen at Gate 1. Version selection always takes the latest *valid* restated filing, not just the most recent filing date.
- Peer-relative change is primary because it reduces common-year shocks, though it cannot remove year-composition risk.
- A larger, balanced sample showing leverage outcomes at least as persistent as operating outcomes would fail to support H1 — and the project's actual Tier B result already points that way ({summary['leverage_median_outcome']:.1%} leverage vs. {summary['operating_median_outcome']:.1%} operating), which is why it is reported as a counter-pattern rather than reframed as support.
"""
    (DOCS / "recruiter_pitch.md").write_text(content, encoding="utf-8")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_release_manifest(data_as_of: str) -> pd.DataFrame:
    paths = [
        REFERENCE / "q1_formal_sample_v1.csv",
        REFERENCE / "q1_field_contract_v1.csv",
        REFERENCE / "q1_powerbi_mart_contract_v1.csv",
        PROCESSED / "q1_annual_company_metrics.csv",
        PROCESSED / "q1_dupont_contributions.csv",
        PROCESSED / "q1_driver_persistence.csv",
        PROCESSED / "q1_h1_sample_audit.csv",
        PROCESSED / "q1_peer_summary.csv",
        PROCESSED / "q1_company_vs_peer.csv",
        PROCESSED / "q1_powerbi_mart.csv",
        PROCESSED / "b3_stage_audit.json",
    ]
    rows = []
    for path in paths:
        row_count = None
        if path.suffix == ".csv":
            row_count = len(pd.read_csv(path))
        rows.append(
            {
                "relative_path": str(path.relative_to(ROOT)),
                "sha256": _sha256(path),
                "bytes": path.stat().st_size,
                "row_count": row_count,
                "analytical_data_as_of": data_as_of,
                "frozen_on": date.today().isoformat(),
            }
        )
    manifest = pd.DataFrame(rows)
    manifest.to_csv(PROCESSED / "b4_release_manifest.csv", index=False)
    return manifest


def _notebook_passed(path: Path) -> bool:
    notebook = nbf.read(path, as_version=4)
    code_cells = [cell for cell in notebook.cells if cell.cell_type == "code"]
    return bool(code_cells) and all(
        cell.get("execution_count") is not None
        and not any(output.get("output_type") == "error" for output in cell.get("outputs", []))
        for cell in code_cells
    )


def build_b4_analytical_release() -> dict[str, Any]:
    b3_audit = build_b3_analytical_marts()
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)
    configure_plotting()
    tables = load_tables()
    summary = build_eda_tables(tables)

    save_coverage_chart(tables)
    save_peer_distributions(tables["q1_annual_company_metrics"])
    save_similar_roe_case(tables["q1_company_vs_peer"])
    save_h1_waterfall(tables["q1_h1_exclusion_waterfall"])
    save_h1_outcomes(tables["q1_h1_sample_audit"])
    save_quality_matrix(tables["q1_annual_company_metrics"])
    save_h1_year_distribution(tables["q1_h1_sample_audit"])
    save_denominator_case(tables["q1_annual_company_metrics"])

    notebooks = build_notebooks(summary["data_as_of"])
    reconciliation = pd.read_csv(PROCESSED / "b4_filing_reconciliation.csv")
    write_analysis_report(summary)
    write_reconciliation_report(reconciliation, summary["data_as_of"])
    write_recruiter_pitch(summary)
    manifest = write_release_manifest(summary["data_as_of"])

    required_outputs = [
        "q1_coverage_summary.csv",
        "q1_missingness_summary.csv",
        "q1_conflict_summary.csv",
        "q1_latest_selection_summary.csv",
        "q1_metric_flag_summary.csv",
        "q1_h1_company_concentration.csv",
        "q1_h1_peer_distribution.csv",
        "q1_h1_year_distribution.csv",
        "q1_h1_group_summary.csv",
        "q1_peer_metric_summary.csv",
        "q1_company_cases.csv",
        "q1_research_findings.csv",
        "b4_filing_reconciliation.csv",
        "b4_release_manifest.csv",
    ]
    checks = {
        "b3_source_is_done": b3_audit["status"] == "Done",
        "formal_scope_21_companies": summary["formal_company_count"] == 21,
        "h1_tier_b_frozen_counts": summary["evidence_tier"] == "B"
        and summary["eligible_transition_count"] == 21
        and summary["eligible_unique_company_count"] == 10,
        "all_quality_eda_outputs_written": all(
            (PROCESSED / name).exists() for name in required_outputs
        ),
        "eight_static_charts_written": all(
            (CHART_DIR / name).exists() and (CHART_DIR / name).stat().st_size > 0
            for name in CHART_FILES
        ),
        "executed_notebooks_pass": all(_notebook_passed(path) for path in notebooks),
        "two_company_filing_reconciliation": reconciliation["ticker"].nunique() == 2
        and len(reconciliation) == 8
        and reconciliation["match_within_tolerance"].all(),
        "release_manifest_complete": len(manifest) == 11,
        "analysis_report_complete": (DOCS / "q1_analysis_report.md").exists()
        and "does **not support H1**" in (DOCS / "q1_analysis_report.md").read_text(encoding="utf-8"),
        "cv_and_interview_narrative_complete": (DOCS / "recruiter_pitch.md").exists(),
    }
    checks = {name: bool(passed) for name, passed in checks.items()}
    audit = {
        "generated_on": date.today().isoformat(),
        "stage": "B4 Analytical Release",
        "status": "Done" if all(checks.values()) else "Failed",
        "analytical_data_as_of": summary["data_as_of"],
        "source_stage": "B3 SQL Analytical Marts",
        "formal_company_count": summary["formal_company_count"],
        "formal_company_year_count": summary["formal_company_year_count"],
        "valid_dupont_company_year_count": summary[
            "valid_dupont_company_year_count"
        ],
        "h1_evidence_tier": summary["evidence_tier"],
        "h1_eligible_transition_count": summary["eligible_transition_count"],
        "h1_unique_company_count": summary["eligible_unique_company_count"],
        "static_chart_files": CHART_FILES,
        "executed_notebooks": [str(path.relative_to(ROOT)) for path in notebooks],
        "minimum_test_command": ".venv/bin/python -m unittest discover -s tests -v",
        "checks": checks,
    }
    (PROCESSED / "b4_stage_audit.json").write_text(
        json.dumps(audit, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise ValueError(f"B4 audit failed: {failed}")
    return audit


def main() -> None:
    audit = build_b4_analytical_release()
    print("B4 formal analytical release complete.")
    print(f"Analytical data as of: {audit['analytical_data_as_of']}")
    print(f"Formal companies: {audit['formal_company_count']}")
    print(f"Formal company-years: {audit['formal_company_year_count']}")
    print(f"Valid DuPont company-years: {audit['valid_dupont_company_year_count']}")
    print(f"H1 Evidence Tier: {audit['h1_evidence_tier']}")
    print(f"Static charts: {len(audit['static_chart_files'])}")


if __name__ == "__main__":
    main()
