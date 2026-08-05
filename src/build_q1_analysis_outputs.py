from __future__ import annotations

import argparse
import os
import tempfile
from pathlib import Path

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


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data/processed"
CHART_DIR = ROOT / "docs/assets/q1"
NOTEBOOK_DIR = ROOT / "notebooks"

PEER_COLORS = {
    "Inventory-led E-commerce": "#147D64",
    "Marketplace / Platform": "#D97745",
}
DRIVER_COLORS = {
    "Margin": "#2E6F9E",
    "Turnover": "#1F9D8A",
    "Multiplier": "#D97745",
}


def configure_plotting() -> None:
    sns.set_theme(style="whitegrid", context="notebook")
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.titleweight": "bold",
            "axes.titlesize": 13,
            "axes.labelsize": 10,
            "font.family": "DejaVu Sans",
            "savefig.dpi": 180,
            "savefig.bbox": "tight",
        }
    )


def load_tables() -> dict[str, pd.DataFrame]:
    names = [
        "q1_annual_company_metrics",
        "q1_dupont_contributions",
        "q1_h1_sample_audit",
        "q1_h1_exclusion_waterfall",
        "q1_powerbi_mart",
    ]
    return {name: pd.read_csv(PROCESSED / f"{name}.csv") for name in names}


def build_eda_tables(tables: dict[str, pd.DataFrame]) -> None:
    metrics = tables["q1_annual_company_metrics"]
    contributions = tables["q1_dupont_contributions"]

    coverage = (
        metrics.groupby("ticker", as_index=False)
        .agg(
            company_name=("company_name", "first"),
            analysis_peer_group=("analysis_peer_group", "first"),
            first_fiscal_year=("fiscal_year", "min"),
            last_fiscal_year=("fiscal_year", "max"),
            company_year_rows=("fiscal_year", "size"),
            valid_dupont_company_years=("dupont_valid_flag", "sum"),
            quality_warning_count=("quality_warning_count", "sum"),
        )
        .sort_values("ticker")
    )
    valid_transitions = (
        contributions.groupby("ticker")["transition_valid_flag"].sum().rename(
            "valid_dupont_transitions"
        )
    )
    coverage = coverage.join(valid_transitions, on="ticker")
    coverage.to_csv(PROCESSED / "q1_coverage_summary.csv", index=False)

    fields = [
        "gross_profit",
        "operating_income",
        "net_income",
        "total_assets",
        "total_equity",
        "current_assets",
        "current_liabilities",
        "cash_and_equivalents",
        "inventory",
        "long_term_debt",
        "operating_cash_flow",
        "capital_expenditure",
        "free_cash_flow",
    ]
    missingness = pd.DataFrame(
        {
            "field": fields,
            "missing_rows": [int(metrics[field].isna().sum()) for field in fields],
            "missing_rate": [float(metrics[field].isna().mean()) for field in fields],
        }
    ).sort_values(["missing_rows", "field"], ascending=[False, True])
    missingness.to_csv(PROCESSED / "q1_missingness_summary.csv", index=False)

    flag_columns = [
        "near_zero_average_equity_flag",
        "one_off_net_income_warning_flag",
        "structural_break_flag",
        "cash_scope_warning_flag",
    ]
    flag_summary = pd.DataFrame(
        {
            "metric_flag": flag_columns,
            "flagged_company_years": [
                int(metrics[column].fillna(False).astype(bool).sum())
                for column in flag_columns
            ],
            "unique_companies": [
                int(
                    metrics.loc[
                        metrics[column].fillna(False).astype(bool), "ticker"
                    ].nunique()
                )
                for column in flag_columns
            ],
        }
    )
    flag_summary.to_csv(PROCESSED / "q1_metric_flag_summary.csv", index=False)

    findings = pd.DataFrame(
        [
            {
                "finding_id": "Q1A-01",
                "finding_type": "comparable_roe_different_drivers",
                "finding": "AMZN and CHWY have broadly comparable 2023 ROE, but AMZN relies on margin while CHWY combines very low margin with high turnover and a much larger equity multiplier.",
                "evidence_boundary": "Descriptive company comparison; not an industry inference.",
            },
            {
                "finding_id": "Q1A-02",
                "finding_type": "counterexample",
                "finding": "BKNG's extreme 2023 ROE is driven by a near-zero average equity base; the large number is a denominator warning rather than evidence of proportionally superior operating quality.",
                "evidence_boundary": "ROE remains mathematically reconciled but is mechanically unstable.",
            },
            {
                "finding_id": "H1-01",
                "finding_type": "evidence_tier",
                "finding": "No transition meets the full H1 rule because valid improvements either begin from nonpositive ROE or lack an observable next-year outcome.",
                "evidence_boundary": "Evidence Tier C; no leverage-versus-operating group test is permitted.",
            },
            {
                "finding_id": "H1-02",
                "finding_type": "illustrative_case",
                "finding": "BKNG's 2023 ROE increase is leverage-driven under Shapley decomposition, but FY2024 is absent, so persistence cannot be evaluated.",
                "evidence_boundary": "Illustrative case only; not support for H1.",
            },
        ]
    )
    findings.to_csv(PROCESSED / "q1_research_findings.csv", index=False)


def save_coverage_chart(metrics: pd.DataFrame) -> None:
    status = metrics.pivot(index="ticker", columns="fiscal_year", values="dupont_valid_flag")
    status = status.fillna(False).astype(int) + 1
    annotations = status.replace({1: "Input", 2: "Valid"})

    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    sns.heatmap(
        status,
        annot=annotations,
        fmt="",
        cmap=ListedColormap(["#E9ECEF", "#A9D8C7"]),
        vmin=1,
        vmax=2,
        cbar=False,
        linewidths=1,
        linecolor="white",
        ax=ax,
    )
    ax.set_title("Company-year coverage and DuPont validity")
    ax.set_xlabel("Fiscal year")
    ax.set_ylabel("")
    fig.text(
        0.5,
        0.01,
        "Input = financial statement row exists; Valid = average-balance DuPont metrics are usable.",
        ha="center",
        fontsize=9,
        color="#555555",
    )
    fig.tight_layout(rect=(0, 0.1, 1, 1))
    fig.savefig(CHART_DIR / "01_coverage_and_dupont_validity.png")
    plt.close(fig)


def save_dupont_profile(metrics: pd.DataFrame) -> None:
    latest = metrics[metrics["fiscal_year"] == metrics["fiscal_year"].max()].copy()
    latest = latest[latest["dupont_valid_flag"]].sort_values("ticker")
    colors = latest["analysis_peer_group"].map(PEER_COLORS)
    components = [
        ("net_margin", "Net margin", True),
        ("asset_turnover", "Asset turnover", False),
        ("equity_multiplier", "Equity multiplier (log scale)", False),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(15, 5.5))
    for ax, (column, title, percent) in zip(axes, components, strict=True):
        bars = ax.barh(latest["ticker"], latest[column], color=colors, height=0.62)
        ax.set_title(title)
        ax.set_ylabel("")
        if column == "equity_multiplier":
            ax.set_xscale("log")
            ax.set_xlim(1, max(2000, latest[column].max() * 1.3))
        if percent:
            ax.xaxis.set_major_formatter(PercentFormatter(1.0))
        for bar, value in zip(bars, latest[column], strict=True):
            label = f"{value:.1%}" if percent else f"{value:.2f}x"
            ax.text(
                bar.get_width(),
                bar.get_y() + bar.get_height() / 2,
                f"  {label}",
                va="center",
                fontsize=8,
            )
    fig.suptitle("2023 DuPont profiles: similar ROE can have different quality", fontsize=16, fontweight="bold")
    fig.text(
        0.5,
        0.01,
        "BKNG's multiplier is extreme because average equity is near zero; it is retained and flagged, not treated as superior quality.",
        ha="center",
        fontsize=9,
        color="#555555",
    )
    fig.tight_layout(rect=(0, 0.05, 1, 0.94))
    fig.savefig(CHART_DIR / "02_2023_dupont_profiles.png")
    plt.close(fig)


def save_shapley_chart(contributions: pd.DataFrame) -> None:
    valid = contributions[contributions["transition_valid_flag"]].copy()
    valid = valid[valid["fiscal_year"] == valid["fiscal_year"].max()]
    columns = {
        "contribution_margin": "Margin",
        "contribution_turnover": "Turnover",
        "contribution_multiplier": "Multiplier",
    }
    denominator = valid[list(columns)].abs().sum(axis=1).replace(0, np.nan)
    long = valid.melt(
        id_vars=["ticker", "roe_change"],
        value_vars=list(columns),
        var_name="component",
        value_name="contribution",
    )
    long["component"] = long["component"].map(columns)
    long = long.merge(
        pd.DataFrame({"ticker": valid["ticker"], "absolute_total": denominator}),
        on="ticker",
    )
    long["normalized_contribution"] = long["contribution"] / long["absolute_total"]

    fig, ax = plt.subplots(figsize=(10.5, 5.8))
    sns.barplot(
        data=long,
        y="ticker",
        x="normalized_contribution",
        hue="component",
        palette=DRIVER_COLORS,
        ax=ax,
    )
    ax.axvline(0, color="#222222", linewidth=0.9)
    ax.xaxis.set_major_formatter(PercentFormatter(1.0))
    ax.set_xlabel("Signed share of absolute Shapley contributions")
    ax.set_ylabel("")
    ax.set_title("2022 to 2023 ROE change decomposition")
    ax.legend(
        title="Driver",
        ncol=1,
        loc="center left",
        bbox_to_anchor=(1.01, 0.5),
    )
    fig.text(
        0.5,
        0.01,
        "Shares are normalized for readability; exact contribution units and reconciliation gaps remain in q1_dupont_contributions.",
        ha="center",
        fontsize=9,
        color="#555555",
    )
    fig.tight_layout(rect=(0, 0.05, 0.86, 1))
    fig.savefig(CHART_DIR / "03_2023_shapley_contributions.png")
    plt.close(fig)


def save_h1_waterfall(waterfall: pd.DataFrame) -> None:
    labels = {
        "invalid_dupont_transition": "Invalid prior/current DuPont",
        "turnaround_from_loss": "Turnaround from nonpositive ROE",
        "next_year_not_observable": "Next year not observable",
        "no_roe_improvement": "No ROE improvement",
    }
    plot_data = waterfall.copy()
    plot_data["label"] = plot_data["h1_sample_status"].map(labels).fillna(
        plot_data["h1_sample_status"]
    )
    plot_data = plot_data.sort_values("transition_count")

    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    bars = ax.barh(
        plot_data["label"],
        plot_data["transition_count"],
        color=["#7A8B99", "#D97745", "#C4A35A", "#2E6F9E"][: len(plot_data)],
    )
    ax.bar_label(bars, padding=4, fontsize=9)
    ax.set_xlabel("Candidate transitions")
    ax.set_ylabel("")
    ax.set_title("H1 eligibility audit: why no transition enters the main test")
    ax.set_xlim(0, max(plot_data["transition_count"].max() + 1, 2))
    fig.text(
        0.5,
        0.01,
        "Evidence Tier C. The exclusion rules are applied as designed; no group test is reported.",
        ha="center",
        fontsize=9,
        color="#555555",
    )
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(CHART_DIR / "04_h1_exclusion_waterfall.png")
    plt.close(fig)


def save_company_peer_map(metrics: pd.DataFrame) -> None:
    latest = metrics[
        (metrics["fiscal_year"] == metrics["fiscal_year"].max())
        & metrics["dupont_valid_flag"]
    ].copy()
    latest["bubble_size"] = np.log1p(latest["equity_multiplier"]) * 140 + 80

    fig, ax = plt.subplots(figsize=(10.5, 6.2))
    for peer_group, group in latest.groupby("analysis_peer_group"):
        ax.scatter(
            group["net_margin"],
            group["asset_turnover"],
            s=group["bubble_size"],
            color=PEER_COLORS[peer_group],
            alpha=0.78,
            edgecolor="white",
            linewidth=1.2,
            label=peer_group,
        )
        for row in group.itertuples():
            ax.annotate(
                row.ticker,
                (row.net_margin, row.asset_turnover),
                xytext=(6, 5),
                textcoords="offset points",
                fontsize=9,
                fontweight="bold",
            )
    ax.axvline(0, color="#777777", linewidth=0.8)
    ax.xaxis.set_major_formatter(PercentFormatter(1.0))
    ax.set_xlabel("Net margin")
    ax.set_ylabel("Asset turnover")
    ax.set_title("2023 operating profile by company and peer group")
    ax.legend(title="Analysis peer group", loc="upper right")
    fig.text(
        0.5,
        0.01,
        "Bubble size reflects log equity multiplier. Peer comparisons are descriptive for this six-company pilot.",
        ha="center",
        fontsize=9,
        color="#555555",
    )
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(CHART_DIR / "05_2023_company_peer_map.png")
    plt.close(fig)


def save_quality_matrix(metrics: pd.DataFrame) -> None:
    average_balance_available = metrics[
        "average_balance_available_flag"
    ].fillna(False).astype(bool)
    positive_average_equity = metrics[
        "positive_average_equity_flag"
    ].fillna(False).astype(bool)
    matrix = pd.DataFrame(
        {
            "Gross profit gap": metrics["gross_profit"].isna().to_numpy(),
            "Inventory N/A": metrics["inventory"].isna().to_numpy(),
            "No prior balance": (~average_balance_available).to_numpy(),
            "Invalid equity": (average_balance_available & ~positive_average_equity).to_numpy(),
            "Near-zero equity": metrics["near_zero_average_equity_flag"].fillna(False).to_numpy(),
            "One-off net income": metrics["one_off_net_income_warning_flag"].fillna(False).to_numpy(),
            "Structural break": metrics["structural_break_flag"].fillna(False).to_numpy(),
            "Cash scope": metrics["cash_scope_warning_flag"].fillna(False).to_numpy(),
            "Restated": metrics["quality_warnings"].fillna("").str.contains("Restated").to_numpy(),
        },
        index=metrics["ticker"] + " " + metrics["fiscal_year"].astype(str),
    ).astype(int)

    fig, ax = plt.subplots(figsize=(12, 8.2))
    sns.heatmap(
        matrix,
        cmap=ListedColormap(["#F3F4F6", "#D97745"]),
        vmin=0,
        vmax=1,
        cbar=False,
        linewidths=0.7,
        linecolor="white",
        ax=ax,
    )
    ax.set_title("Metric and comparability warning matrix")
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.tick_params(axis="x", rotation=35)
    fig.tight_layout()
    fig.savefig(CHART_DIR / "06_quality_warning_matrix.png")
    plt.close(fig)


def make_notebook(title: str, purpose: str, cells: list[object], filename: str) -> None:
    notebook = nbf.v4.new_notebook()
    notebook["metadata"]["kernelspec"] = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }
    notebook["cells"] = [
        nbf.v4.new_markdown_cell(f"# {title}\n\n{purpose}\n\nData as of: 2024-01-28."),
        nbf.v4.new_code_cell(
            "from pathlib import Path\n"
            "import pandas as pd\n"
            "from IPython.display import Image, display\n\n"
            "ROOT = Path.cwd()\n"
            "if ROOT.name == 'notebooks':\n"
            "    ROOT = ROOT.parent\n"
            "pd.set_option('display.max_columns', 100)"
        ),
        *cells,
    ]
    nbf.write(notebook, NOTEBOOK_DIR / filename)


def build_notebooks() -> None:
    make_notebook(
        "Q1 Source Probe",
        "Audits the official SEC evidence layer, accession-level facts, concept mapping, latest-restated selection, and reconciliation to the frozen analytical release.",
        [
            nbf.v4.new_code_cell(
                "universe = pd.read_csv(ROOT / 'data/reference/company_universe.csv')\n"
                "events = pd.read_csv(ROOT / 'data/reference/events.csv')\n"
                "concept_map = pd.read_csv(ROOT / 'data/reference/concept_map.csv')\n"
                "facts = pd.read_csv(ROOT / 'data/normalized/financial_facts.csv')\n"
                "latest = pd.read_csv(ROOT / 'data/processed/sec_latest_restated_long.csv')\n"
                "reconciliation = pd.read_csv(ROOT / 'data/processed/sec_manual_reconciliation.csv')\n"
                "display(universe[['ticker', 'status_group', 'analysis_scope_group', 'q1_release_included', 'q2_event_candidate']])\n"
                "display(events[['event_id', 'company_id', 'event_type', 'event_date', 'qualifies_for_q2']])\n"
                "display(concept_map[['canonical_field', 'source_tag', 'sign_multiplier', 'required_for_q1']])"
            ),
            nbf.v4.new_code_cell(
                "probe = pd.DataFrame({\n"
                "    'normalized_facts': facts.groupby('ticker').size(),\n"
                "    'latest_canonical_facts': latest.groupby('ticker').size(),\n"
                "    'manual_matches': reconciliation.query(\"reconciliation_status == 'match'\").groupby('ticker').size(),\n"
                "    'mapping_reviews': reconciliation.query(\"reconciliation_status == 'review_company_mapping'\").groupby('ticker').size(),\n"
                "}).fillna(0).astype(int)\n"
                "display(probe)"
            ),
            nbf.v4.new_markdown_cell(
                "Official SEC companyfacts and submissions JSON are cached for all six release companies. Accession and filing-date history is retained in the normalized layer. Mapping differences remain explicit review items and do not silently overwrite the manually reconciled Q1 analytical mart."
            ),
        ],
        "01_source_probe.ipynb",
    )
    make_notebook(
        "Q1 Data Quality",
        "Reviews coverage, missingness, metric warnings, latest-restated handling, and the H1 exclusion waterfall before interpreting results.",
        [
            nbf.v4.new_code_cell(
                "coverage = pd.read_csv(ROOT / 'data/processed/q1_coverage_summary.csv')\n"
                "missingness = pd.read_csv(ROOT / 'data/processed/q1_missingness_summary.csv')\n"
                "flags = pd.read_csv(ROOT / 'data/processed/q1_metric_flag_summary.csv')\n"
                "waterfall = pd.read_csv(ROOT / 'data/processed/q1_h1_exclusion_waterfall.csv')\n"
                "display(coverage)\n"
                "display(missingness)\n"
                "display(flags)\n"
                "display(waterfall)"
            ),
            nbf.v4.new_code_cell(
                "display(Image(filename=ROOT / 'docs/assets/q1/01_coverage_and_dupont_validity.png'))\n"
                "display(Image(filename=ROOT / 'docs/assets/q1/04_h1_exclusion_waterfall.png'))\n"
                "display(Image(filename=ROOT / 'docs/assets/q1/06_quality_warning_matrix.png'))"
            ),
        ],
        "02_data_quality.ipynb",
    )
    make_notebook(
        "Q1 DuPont and H1 Analysis",
        "Answers Q1-A with average-balance DuPont metrics and applies the pre-registered H1 rules without relaxing the evidence threshold.",
        [
            nbf.v4.new_code_cell(
                "mart = pd.read_csv(ROOT / 'data/processed/q1_powerbi_mart.csv')\n"
                "contributions = pd.read_csv(ROOT / 'data/processed/q1_dupont_contributions.csv')\n"
                "findings = pd.read_csv(ROOT / 'data/processed/q1_research_findings.csv')\n"
                "latest = mart[mart['fiscal_year'] == mart['fiscal_year'].max()]\n"
                "display(latest[['ticker', 'analysis_peer_group', 'roe', 'net_margin', 'asset_turnover', 'equity_multiplier', 'quality_warnings']])\n"
                "display(contributions[contributions['transition_valid_flag']][['ticker', 'fiscal_year', 'roe_change', 'contribution_margin', 'contribution_turnover', 'contribution_multiplier', 'h1_driver_group']])\n"
                "display(findings)"
            ),
            nbf.v4.new_code_cell(
                "display(Image(filename=ROOT / 'docs/assets/q1/02_2023_dupont_profiles.png'))\n"
                "display(Image(filename=ROOT / 'docs/assets/q1/03_2023_shapley_contributions.png'))\n"
                "display(Image(filename=ROOT / 'docs/assets/q1/05_2023_company_peer_map.png'))"
            ),
            nbf.v4.new_markdown_cell(
                "**H1 conclusion:** Evidence Tier C. There are no eligible transitions, so the release reports illustrative decomposition cases only and does not compare persistence groups."
            ),
        ],
        "03_q1_analysis.ipynb",
    )


def main(refresh_notebooks: bool = False) -> None:
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)
    configure_plotting()
    tables = load_tables()
    build_eda_tables(tables)
    metrics = tables["q1_annual_company_metrics"]
    save_coverage_chart(metrics)
    save_dupont_profile(metrics)
    save_shapley_chart(tables["q1_dupont_contributions"])
    save_h1_waterfall(tables["q1_h1_exclusion_waterfall"])
    save_company_peer_map(metrics)
    save_quality_matrix(metrics)
    notebook_paths = [
        NOTEBOOK_DIR / "01_source_probe.ipynb",
        NOTEBOOK_DIR / "02_data_quality.ipynb",
        NOTEBOOK_DIR / "03_q1_analysis.ipynb",
    ]
    if refresh_notebooks or not all(path.exists() for path in notebook_paths):
        build_notebooks()
        notebook_message = f"Notebooks written to: {NOTEBOOK_DIR}"
    else:
        notebook_message = "Existing executed notebooks preserved"
    print(f"Q1 EDA tables written to: {PROCESSED}")
    print(f"Static charts written to: {CHART_DIR}")
    print(notebook_message)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--refresh-notebooks",
        action="store_true",
        help="Regenerate notebook source files; execute them separately to embed outputs.",
    )
    args = parser.parse_args()
    main(refresh_notebooks=args.refresh_notebooks)
