# Financial Health Screener

## Project Reset Handbook

> **Last updated:** 2026-07-28  
> **Document type:** Internal project handbook  
> **Primary purpose:** Explain the stable business, data, technical, and analytical logic of the project

---

## Document Scope

This handbook explains how the **Financial Health Screener** works—from the original business question to the final analytical output.

It is designed to answer the following questions:

- What is the project trying to achieve?
- What stage is the project currently in?
- Why does each file and folder exist?
- What are Python, SQL, DuckDB, Git, and Power BI responsible for?
- How does raw financial data become an explainable risk-screening result?
- What should be checked when the project becomes confusing?
- How should future project work be explained and executed?

This handbook describes the project’s **stable structure and operating logic**.

Current progress, active tasks, completed milestones, and known gaps must be maintained separately in:

```text
docs/project_status.md
```

---

# 1. Project Objective

## 1.1 Business Problem

The project investigates whether publicly available financial information can help identify financial deterioration before a listed e-commerce-related company experiences severe financial distress.

The project is not designed to answer only:

> Which companies currently have weak financial ratios?

Instead, it addresses three connected analytical questions.

### Q1. Financial Health Assessment

How healthy is each company’s current financial position?

### Q2. Early-Warning Validation

Which financial and operating indicators deteriorated before historical cases of severe distress?

### Q3. Current-Company Screening

Which currently listed companies are showing combinations of previously validated deterioration signals?

---

## 1.2 Intended Users

Potential users include:

- Credit analysts
- Corporate banking professionals
- Investment analysts
- Risk-management teams
- Strategy teams
- Corporate-finance teams
- Business intelligence users

These users need more than a numerical score.

The final output should explain:

- Which company requires attention
- Which signals were triggered
- Whether the signals are recurring or temporary
- How the company compares with relevant peers
- Which metrics are not applicable
- Whether data-quality limitations affect the conclusion

---

## 1.3 Intended Final Product

The intended final product is an **explainable financial-health and early-warning screening system**.

Potential outputs include:

- A ranked company-screening table
- Financial-health indicators
- Financial-deterioration flags
- Peer-group benchmarks
- Historical distress-case validation
- Company-level risk explanations
- A Power BI dashboard
- A methodology and limitations report

The project is therefore:

- Not only a dashboard
- Not only a Python model
- Not only a collection of financial ratios

It is a complete **decision-support workflow**.

---

# 2. End-to-End Project Logic

The complete project follows this chain:

```text
Business problem
    ↓
Sample design
    ↓
Source discovery
    ↓
Raw data collection
    ↓
Data-quality validation
    ↓
Data normalization
    ↓
Database construction
    ↓
SQL metric calculation
    ↓
Financial deterioration signals
    ↓
Historical validation
    ↓
Current-company screening
    ↓
Power BI and business communication
```

Each stage has a different responsibility.

A later stage should not silently compensate for an error that belongs to an earlier stage.

For example:

- Power BI should not silently fix incorrect raw data.
- SQL should not hide inconsistent accounting definitions.
- Python validation should not make unsupported business decisions.
- Raw CSV files should not contain undocumented derived values.

---

# 3. Project Stages

## 3.1 Stage A1 — Sample Design

### Main Question

Which companies should be studied, and which companies are reasonably comparable?

### Main Activities

- Build the candidate-company universe
- Record company identity and listing status
- Classify business models
- Assign preliminary peer groups
- Decide whether a company is a core-sample candidate
- Record inclusion and exclusion reasons
- Identify boundary cases
- Identify historical distress references

### Main Files

```text
data/raw/sample_companies_master.csv
docs/a1_sample_design/
src/check_sample_master.py
```

### Important Principle

```text
include_in_core_sample = 1
```

is a preliminary research-design decision.

It does **not** prove that:

- Historical financial coverage is sufficient
- SEC data are available
- Accounting concepts are comparable
- The company will remain in the final analytical sample

The final sample may change after source discovery, accounting review, and data-quality validation.

---

## 3.2 Stage A2 — Financial Data Collection and Validation

### Main Question

Can reliable annual financial data be collected and stored under a consistent schema?

### Main Activities

- Define required financial fields
- Create a financial-data template
- Record field definitions and units
- Collect annual financial-statement data
- Preserve source names
- Preserve source URLs
- Document derived or non-standard values
- Run structural and format checks
- Review company-specific accounting treatments

### Main Files

```text
data/raw/financial_statements_template.csv
data/raw/financial_statements_raw.csv
docs/a2_financial_data/financial_data_dictionary.md
src/check_financial_statements.py
```

### Current Pilot Data

The initial financial-data pilot contains:

| Company | Ticker | Fiscal years |
|---|---:|---:|
| Amazon | AMZN | 2021–2023 |
| eBay | EBAY | 2021–2023 |
| Etsy | ETSY | 2021–2023 |

### Purpose of the Pilot

The pilot is used to test:

- Whether the schema is sufficient
- Whether different business models can use one common table
- Which fields are frequently missing
- Which accounting rules require special treatment
- Whether the validation program works correctly

> The pilot is not yet the final company dataset.

---

## 3.3 Stage A3 — Data Normalization

### Main Question

How should different companies, filings, currencies, units, and accounting concepts be converted into one comparable data language?

### Main Activities

- Standardize units
- Standardize currencies
- Standardize dates and fiscal-period treatment
- Standardize positive and negative signs
- Map source concepts to canonical project fields
- Distinguish reported values from derived values
- Preserve missing values correctly
- Create data-quality flags
- Create metric-applicability flags

### Example Normalization Rules

- Store monetary values in **USD millions**
- Store shares outstanding in **millions of shares**
- Store capital expenditure as a **positive cash-outflow amount**
- Do not replace unreported inventory with zero
- Mark Amazon gross profit as a derived value
- Preserve eBay discontinued-operation issues in notes or flags

### Main Output Location

```text
data/normalized/
```

Normalized data should answer:

> How do different source systems and company filings speak one common data language?

---

## 3.4 Stage A4 — Database and Analytical Tables

### Main Question

How should the data be organized so that metrics can be calculated consistently, repeatedly, and at scale?

### Main Activities

- Create database tables
- Load company-master data
- Load normalized financial data
- Define relationships between tables
- Write reusable SQL queries
- Produce analytical datasets
- Preserve data lineage between source data and output tables

### Possible Database Tables

```text
companies
annual_financials
distress_events
concept_mapping
financial_metrics
metric_flags
risk_signals
```

### Main Locations

```text
db/
sql/
```

---

## 3.5 Stage A5 — Financial Indicator Engineering

### Main Question

Which financial indicators describe profitability, liquidity, leverage, cash-flow quality, growth, and operating deterioration?

### Possible Indicators

#### Profitability

- Gross margin
- Operating margin
- Net margin
- Return on assets
- Return on equity

#### Liquidity

- Current ratio
- Cash ratio
- Working capital

#### Leverage

- Total liabilities to assets
- Long-term debt to assets
- Debt to equity

#### Cash Flow

- Operating cash-flow margin
- Free cash-flow margin
- Cash-conversion indicators

#### Growth and Deterioration

- Revenue growth
- Margin change
- Multi-year revenue decline
- Multi-year margin deterioration
- Cash-flow transition from positive to negative

### Important Principle

A metric being mathematically calculable does not guarantee that it has a useful economic interpretation.

Examples:

- ROE can be misleading when equity is negative.
- Inventory turnover may not apply to asset-light marketplaces.
- A one-time disposal can distort net income.
- Different revenue-recognition models can affect margin comparisons.
- A large ratio may be caused by a very small denominator rather than genuine improvement.

Metric calculations should therefore be accompanied by:

- Applicability flags
- Data-quality flags
- Accounting-treatment notes
- Manual-review warnings where necessary

---

## 3.6 Stage A6 — Early-Warning Signal Design and Validation

### Main Question

Which indicators—or combinations of indicators—appeared before severe financial distress?

### Candidate Signals

Possible candidate signals include:

- Revenue declining for multiple periods
- Operating margin deteriorating
- Operating cash flow turning negative
- Free cash flow remaining negative
- Leverage increasing materially
- Liquidity weakening
- Inventory growing much faster than revenue
- Multiple indicators deteriorating simultaneously

### Validation Questions

Before a signal is accepted, the project should ask:

- Did the signal appear before the distress event?
- How far in advance did it appear?
- Does the signal also appear frequently in healthy companies?
- Is the signal relevant to all business models?
- Does a signal combination work better than one isolated metric?
- Is the result driven by a one-time accounting event?
- Is the result sensitive to the chosen threshold?
- Is the signal economically meaningful or merely statistically unusual?

> A signal must be validated before it is described as an early-warning indicator.

---

## 3.7 Stage A7 — Current Screening and Power BI

### Main Question

How can validated signals be applied to current companies and communicated clearly to business users?

### Possible Outputs

- High-, medium-, and low-priority screening results
- Triggered-risk explanations
- Peer-group comparisons
- Historical indicator trends
- Data-quality warnings
- Company-detail pages
- Methodology pages
- Limitations pages

### Main Location

```text
powerbi/
```

### Role of Power BI

Power BI is the project’s **presentation and decision-support layer**.

It should not become the only place where important logic exists.

Important cleaning, accounting, metric, and risk logic should normally be implemented and documented before the data reach Power BI.

---

# 4. Repository Structure

```text
financial-health-screener/
│
├── data/
│   ├── raw/
│   ├── interim/
│   ├── normalized/
│   ├── processed/
│   └── reference/
│
├── db/
├── docs/
├── notebooks/
├── powerbi/
├── sql/
├── src/
├── tests/
│
├── .gitignore
├── README.md
└── requirements.txt
```

---

# 5. Folder Responsibilities

## 5.1 `data/raw/`

### Purpose

Stores original or near-original project inputs.

### Current Examples

```text
sample_companies_master.csv
financial_statements_template.csv
financial_statements_raw.csv
```

### Rules

Raw data should not be silently overwritten.

When a raw value is corrected:

1. Verify the original source.
2. Record why the correction is necessary.
3. Preserve relevant notes or source information.
4. Rerun validation.
5. Commit the change with a descriptive message.

---

## 5.2 `data/interim/`

### Purpose

Stores temporary intermediate data produced during processing.

### Possible Examples

- Partially cleaned SEC extracts
- Temporary accounting-concept mappings
- Data awaiting manual review
- Combined data before final normalization
- Temporary extraction outputs

Interim data are not assumed to be ready for analysis.

They may still contain:

- Inconsistent units
- Unresolved source concepts
- Missing classifications
- Duplicate observations
- Values requiring manual review

---

## 5.3 `data/normalized/`

### Purpose

Stores data after common project definitions have been applied.

### Normalization May Include

- Standard column names
- Standard units
- Standard currencies
- Standard date formats
- Standard sign conventions
- Canonical accounting concepts
- Explicit missing-value flags
- Explicit applicability flags
- Reported-versus-derived classifications

Normalized data answer:

> How do different source systems speak one common data language?

---

## 5.4 `data/processed/`

### Purpose

Stores analysis-ready data created for a defined analytical purpose.

### Possible Examples

- Company-year financial metrics
- Peer-group benchmarks
- Risk-signal tables
- Historical validation datasets
- Power BI input tables
- Current screening results

Processed data answer:

> How should normalized data be prepared for a specific analysis, model, or output?

---

## 5.5 `data/reference/`

### Purpose

Stores relatively stable mapping, classification, and rule tables.

### Possible Examples

- Allowed peer groups
- Accounting-concept mappings
- Ticker history
- Exchange mappings
- Distress-event definitions
- Country reference tables
- Currency reference tables
- Industry classifications
- Business-model classifications

---

## 5.6 `src/`

### Purpose

Stores formal Python source code used in repeatable project workflows.

### Current Scripts

```text
check_sample_master.py
check_financial_statements.py
```

### Possible Future Scripts

- SEC data extraction
- Data normalization
- Database loading
- Quality-flag generation
- Metric preparation
- Screening preparation
- Export preparation

`src/` is not merely a place for any Python file.

It is the project’s **formal program layer**.

Code placed here should normally be:

- Reusable
- Repeatable
- Understandable
- Testable
- Connected to a defined project workflow

---

## 5.7 `notebooks/`

### Purpose

Stores exploratory analysis, investigations, and experiments.

### Appropriate Uses

- Inspecting source data
- Testing formulas
- Plotting trends
- Investigating unusual observations
- Exploring accounting concepts
- Comparing alternative approaches
- Developing ideas interactively

### Professional Distinction

```text
notebooks/
→ laboratory, exploration, and investigation

src/
→ stable, repeatable, and reusable program logic
```

Logic that becomes stable and reusable should normally be moved from a notebook into:

- A formal Python script
- A Python module
- A SQL file
- An automated test

---

## 5.8 `sql/`

### Purpose

Stores database definitions, transformations, joins, analytical queries, and metric calculations.

### Possible Future Files

```text
create_tables.sql
load_views.sql
annual_metrics.sql
risk_signals.sql
current_screen.sql
```

SQL should use standardized data to generate analytical outputs.

It should not silently hide errors in raw or normalized data.

---

## 5.9 `db/`

### Purpose

Stores database files and database-related artifacts.

### Possible Future Example

```text
db/financial_health.duckdb
```

A database becomes increasingly useful when the project contains:

- Multiple related tables
- More companies
- More fiscal periods
- More financial metrics
- More distress events
- Repeated analytical queries
- Reusable dashboard datasets

---

## 5.10 `tests/`

### Purpose

Stores automated tests that verify whether project programs behave correctly.

### Current Status

- The folder currently contains only `.gitkeep`.
- No formal automated test suite has been created yet.

### Important Distinction

```text
src/check_financial_statements.py
→ checks whether real financial data follow project rules

tests/test_financial_statements.py
→ would test whether the checker itself behaves correctly
```

The validation script checks the data.

The test suite checks the program.

---

## 5.11 `docs/`

### Purpose

Stores project definitions, methodologies, decisions, limitations, and internal knowledge.

### Current Examples

- Sample-design documentation
- Financial-data dictionary
- Project-status document
- Project Reset Handbook

### Core Distinction

```text
Documentation
→ explains rules and decisions to people

Code
→ enforces selected rules for machines
```

Not every business or accounting rule can be fully automated.

Some rules must remain documented for manual review.

---

## 5.12 `powerbi/`

### Purpose

Will store:

- Power BI dashboard files
- Data-model documentation
- Dashboard exports
- Screenshots
- Presentation notes

This layer is currently reserved and has not yet been developed.

---

## 5.13 `README.md`

### Purpose

The README is the project’s external introduction.

### Intended Audience

- Recruiters
- Interviewers
- GitHub visitors
- Collaborators
- Other analysts

### Future Content

The README should eventually explain:

- Project objective
- Business value
- Data sources
- Methodology
- Technical stack
- Repository structure
- How to run the project
- Main results
- Limitations

The README should summarize the finished project.

It should not replace detailed internal documentation.

---

## 5.14 `requirements.txt`

### Purpose

Records the Python packages required by the project.

It is the project’s written dependency list.

### Difference Between `.venv` and `requirements.txt`

```text
.venv/
→ the actual local Python environment

requirements.txt
→ the written package list used to rebuild the environment
```

The dependency list should be reviewed and updated as the project develops.

---

## 5.15 `.gitignore`

### Purpose

Tells Git which files or folders should not be tracked.

### Typical Examples

```text
.venv/
__pycache__/
.DS_Store
.env
local temporary files
sensitive credentials
generated cache files
```

A file being ignored by Git does not mean that it does not exist on the local computer.

---

# 6. Current Core Data Files

## 6.1 Company Master

### Path

```text
data/raw/sample_companies_master.csv
```

### Grain

```text
One company × one master record
```

### Main Responsibilities

- Company identity
- Listing status
- Business model
- Business-feature flags
- Peer group
- Preliminary core-sample decision
- Inclusion reason
- Exclusion reason
- Notes
- Boundary-case documentation

### Unique Key

```text
ticker
```

---

## 6.2 Financial Statements

### Path

```text
data/raw/financial_statements_raw.csv
```

### Grain

```text
One company × one fiscal year
```

### Current Pilot Coverage

```text
AMZN: 2021–2023
EBAY: 2021–2023
ETSY: 2021–2023
```

### Unique Key

```text
ticker + fiscal_year
```

### Main Responsibilities

- Store annual financial values
- Store source information
- Preserve special accounting-treatment notes
- Provide input for normalization
- Provide input for later metric calculations

---

## 6.3 Financial-Statement Template

### Path

```text
data/raw/financial_statements_template.csv
```

### Purpose

- Define the expected empty schema
- Support future data-entry consistency
- Separate table design from actual financial observations

### Important Distinction

```text
financial_statements_template.csv
→ defines what the table should look like

financial_statements_raw.csv
→ contains actual financial observations
```

The template and raw-data file have different responsibilities and should not be treated as interchangeable.

---

# 7. Current Validation Programs

## 7.1 `check_sample_master.py`

### Current Implemented Checks

- The file exists
- Column schema is correct
- Column order is correct
- The table is not empty
- Ticker is unique
- Required fields are not empty
- Binary fields contain only `0` or `1`
- Listing status uses an allowed value
- Peer group uses an allowed value
- Primary business model uses an allowed value

### Known Gaps

- `include_in_core_sample = 1` does not yet require `include_reason`
- `include_in_core_sample = 0` does not yet require `exclude_reason`
- Business-model fields and feature flags are not cross-validated
- A legally allowed classification may still be commercially incorrect
- Secondary business models are not fully validated
- Peer-group classifications are not analytically validated

---

## 7.2 `check_financial_statements.py`

### Current Implemented Checks

- Financial-data file exists
- Company-master file exists
- Full column schema is correct
- Column order is correct
- Required fields are not empty
- `ticker + fiscal_year` is unique
- Financial-data tickers exist in the company master
- Fiscal year is numeric
- Fiscal year falls within the allowed range
- Period-end dates can be parsed
- Filled numeric fields can be converted to numbers
- Row counts by ticker and fiscal year are printed

### Known Gaps

- Empty raw financial data are still treated as acceptable because of an older template-stage rule
- The accounting equation is not yet checked
- Free cash flow is not yet reconciled
- Capital-expenditure sign is not yet checked
- Complete fiscal-year coverage is not yet enforced
- Company-master companies missing from financial data are not identified
- Analytical plausibility warnings are not yet implemented

---

# 8. Five Layers of Data Quality

## Layer 1 — File and Schema

### Questions

- Does the file exist?
- Are all required columns present?
- Is the column order correct?
- Are unexpected columns present?

### Example

```text
The revenue column is missing.
```

---

## Layer 2 — Format and Type

### Questions

- Can fiscal year be converted to a number?
- Can the period-end date be parsed?
- Can financial values be converted to numbers?
- Are binary fields stored in an allowed format?

### Example

```text
revenue = "five million"
```

---

## Layer 3 — Uniqueness and Cross-Table Integrity

### Questions

- Is the company-year key unique?
- Does every financial ticker exist in the company master?
- Are relationships between tables valid?

### Example

```text
AMZN + 2023 appears twice.
```

---

## Layer 4 — Accounting and Business Rules

### Questions

- Do assets equal liabilities plus equity?
- Does free cash flow equal operating cash flow minus capital expenditure under the project definition?
- Is capital expenditure stored using the required sign convention?
- Are conditional sample-design rules satisfied?
- Are reported and derived values classified correctly?

### Examples

```text
total_assets != total_liabilities + total_equity
```

```text
free_cash_flow != operating_cash_flow - capital_expenditure
```

These checks are not yet fully implemented.

---

## Layer 5 — Analytical Plausibility

### Questions

- Is a very large growth rate real or caused by a unit error?
- Is an unusually high margin caused by a one-time gain?
- Is the ratio meaningful for this business model?
- Is a denominator close to zero?
- Does the observation require manual review?
- Is a company-specific accounting event distorting the trend?

### Example

```text
Revenue grows 950% year over year.
```

This may be real.

It should normally generate a warning or manual-review flag rather than an automatic correction.

---

# 9. Responsibility of Each Project Layer

The same business rule may appear in several layers, but each layer has a different responsibility.

## 9.1 CSV

### Responsibility

Stores the value.

### Example

```text
capital_expenditure = 52729
```

---

## 9.2 Markdown Documentation

### Responsibility

Explains what the field means and how it should be interpreted.

### Example

> Capital expenditure is stored as a positive cash-outflow amount in USD millions.

---

## 9.3 Python

### Responsibility

Checks, extracts, cleans, or transforms data.

### Example

Fail validation if a filled capital-expenditure value is negative under the normalized project convention.

---

## 9.4 SQL

### Responsibility

Joins standardized data and calculates analytical results.

### Example

```sql
free_cash_flow =
    operating_cash_flow - capital_expenditure
```

---

## 9.5 Power BI

### Responsibility

Communicates results to business users.

### Example

Show:

- Free-cash-flow margin
- Historical trend
- Triggered deterioration signal
- Applicable data-quality warning

---

## 9.6 Rule Lifecycle

A mature project rule moves through the following chain:

```text
Definition
    ↓
Data storage
    ↓
Validation
    ↓
Calculation
    ↓
Presentation
```

---

# 10. Local Development Environment

## 10.1 Main VS Code Areas

### Explorer

Used to locate files and folders.

### Editor

Used to open, read, and modify files.

### Terminal

Used to run shell commands and programs.

### Chat

Used to obtain AI assistance.

> The project exists on the Mac file system. It does not exist only inside VS Code.

---

## 10.2 Current Working Directory

Relative file paths depend on the terminal’s current working directory.

### Useful Commands

#### Show Current Directory

```bash
pwd
```

Displays the current working directory.

#### List Directory Contents

```bash
ls
```

Lists the files and folders in the current directory.

#### Enter a Folder

```bash
cd folder_name
```

Moves into the specified folder.

#### Move to the Parent Folder

```bash
cd ..
```

Moves one level upward.

### Project Rule

Project scripts should normally be run from the project root unless a script is explicitly designed otherwise.

---

## 10.3 Terminal and Shell

The **Terminal** is the visible input-and-output interface.

The **shell**, normally `zsh` on macOS, interprets commands.

Example:

```bash
python src/check_financial_statements.py
```

In this command:

- `python` starts the active Python interpreter.
- `src/check_financial_statements.py` is the script path.
- The shell locates Python and passes the script path to it.

---

## 10.4 Notebook and Python Script

### Notebook

Best suited for:

- Interactive exploration
- Learning
- Charts
- Experiments
- Investigation
- Formula testing

### Python Script

Best suited for:

- Stable workflows
- Repeatable processes
- Automated execution
- Testing
- Reusable project logic

Both are professional tools with different responsibilities.

---

# 11. Virtual Environment and Dependencies

## 11.1 `.venv`

`.venv` is the project-specific Python environment.

When the terminal prompt shows:

```text
(.venv)
```

the virtual environment is active.

---

## 11.2 Activating the Environment on macOS

```bash
source .venv/bin/activate
```

This command does not reinstall packages.

It tells the current shell to prefer the Python interpreter and packages stored inside `.venv`.

---

## 11.3 Confirming the Active Python Interpreter

```bash
which python
```

The returned path should point to the project’s `.venv`.

Example:

```text
.../financial-health-screener/.venv/bin/python
```

Check the Python version with:

```bash
python --version
```

---

## 11.4 Installing Packages

```bash
pip install pandas
```

This installs `pandas` into the currently active Python environment.

Packages do not normally need to be reinstalled every time VS Code is opened.

They remain installed until:

- The environment is deleted
- The environment is replaced
- The environment becomes damaged
- The package is explicitly uninstalled

---

## 11.5 Reproducing the Environment

A typical environment setup process is:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

This allows another user to rebuild the project environment without receiving the original `.venv` folder.

---

# 12. Git and GitHub

## 12.1 Git

Git is the local version-control system.

It records how the project changes over time.

---

## 12.2 GitHub

GitHub is the remote hosting and project-sharing platform built around Git repositories.

---

## 12.3 Core Workflow

```text
Modify
    ↓
Save
    ↓
Review
    ↓
Stage
    ↓
Commit
    ↓
Push
```

---

## 12.4 Save

Keyboard shortcut:

```text
Command + S
```

Saving writes the editor content to the Mac disk.

Saving is not the same as committing.

---

## 12.5 Review

```bash
git status
```

Shows the current repository state.

```bash
git diff
```

Shows unstaged changes in tracked files.

---

## 12.6 Stage

```bash
git add file_path
```

Selects changes for the next commit.

Example:

```bash
git add docs/project_reset_handbook.md
```

---

## 12.7 Commit

```bash
git commit -m "Descriptive message"
```

Creates a local historical snapshot.

A commit does not mean “run the program.”

Example:

```bash
git commit -m "Add project reset handbook"
```

---

## 12.8 Push

```bash
git push
```

Uploads local commits to GitHub.

---

## 12.9 Important Git States

### Working Directory

Current file changes on the computer.

### Staging Area

Changes selected for the next commit.

### Repository History

Completed commits.

---

## 12.10 VS Code Git Indicators

```text
U
→ Untracked: a new file that Git is not tracking yet

M
→ Modified: a tracked file has changed

A
→ Added: a file has been staged for the next commit
```

An unsaved editor file is normally indicated by a dot on its tab.

> Git status and editor save status are different systems.

---

# 13. Project Collaboration Rules

All future project work should follow the rules below.

## 13.1 Explain the Global Position First

Before performing an operation, explain:

- Which project stage we are in
- What the previous input is
- What the current step produces
- Which later stage will use the output

---

## 13.2 Separate Logic Layers

Explanations should distinguish between relevant layers:

- Business logic
- Financial and accounting logic
- Data logic
- Python
- SQL
- Terminal
- Git
- Presentation logic

---

## 13.3 Explain Terminal Commands

Every new terminal command should include:

- What the command does
- What each important part means
- Why the command is needed
- What output is expected
- What a failure would mean

---

## 13.4 Explain Code Through Input, Processing, and Output

For important code, explain:

### Input

What data, file, table, or parameter enters the program?

### Processing

What validation, transformation, or calculation occurs?

### Output

What result, file, table, warning, or error is produced?

### Project Connection

- Why does the code exist?
- What can fail?
- Which project stage uses the output?
- Which later step depends on it?

---

## 13.5 Work in Small Units

Default working rhythm:

```text
Understand
    ↓
Operate
    ↓
Inspect the result
    ↓
Explain the result
    ↓
Continue
```

Avoid delivering many unexplained commands or large code blocks at once.

---

## 13.6 Prevent Copy-Only Execution

AI may assist with code generation, but the project owner should understand:

- The purpose of the file
- The role of the data
- The rule being implemented
- The meaning of the output
- The relationship to the business objective

Understanding every syntax detail is not required before progress can continue.

However, the project logic must remain clear.

---

## 13.7 Check Understanding Before Committing

Before a meaningful commit, confirm:

- Which files changed
- Why each file exists
- What the program reads
- What the program produces
- What was implemented or checked
- Which later step depends on the change

---

## 13.8 Maintain One Official Project Status

```text
docs/project_status.md
```

is the official progress record.

Chat descriptions should not silently redefine project stage numbers or completed milestones.

If actual repository files disagree with a previous chat summary:

> The repository and the verified current state take priority.

---

# 14. Troubleshooting Map

When something goes wrong, first identify the layer where the problem belongs.

## 14.1 Shell-Level Problem

### Example

```text
command not found
```

### Possible Causes

- The command is misspelled
- The program is not installed
- The environment path is incorrect
- The command is being entered in the wrong interface

---

## 14.2 Python-Environment Problem

### Example

```text
ModuleNotFoundError: No module named 'pandas'
```

### Possible Causes

- `.venv` is not active
- VS Code and the terminal use different Python interpreters
- `pandas` is installed in another environment
- The package has not been installed

---

## 14.3 File-Path Problem

### Example

```text
FileNotFoundError
```

### Possible Causes

- The terminal is not in the project root
- The file name is incorrect
- The relative path is incorrect
- The file was moved
- The file was not saved
- The script expects a different folder structure

---

## 14.4 Schema Problem

### Example

```text
Column structure does not match expected schema.
```

### Possible Causes

- A required column is missing
- An unexpected column exists
- A column name is misspelled
- The column order is wrong
- The wrong file was loaded

---

## 14.5 Data-Rule Problem

### Example

```text
Duplicate ticker-fiscal_year rows found.
```

### Meaning

The program may be running correctly.

The input data violate a defined project rule.

This is different from a Python or shell failure.

---

## 14.6 Git-Interface Problem

### Example

A file shows:

```text
U
```

### Meaning

- The file exists
- The file is new
- Git is not tracking it yet

This does not mean the file is unsaved.

---

## 14.7 Pager Problem

When `git diff` opens a full-screen view:

```text
Press q to exit.
```

Do not enter shell commands until the normal terminal prompt returns.

A command typed inside the pager is interpreted by the pager, not by the shell.

---

# 15. Questions to Ask When Lost

When the project becomes confusing, stop and answer the following questions.

## Business Position

- What business question is this step helping answer?
- Which stage of the pipeline are we in?
- Why is this step necessary?

## Input

- What is the input?
- Which file or table contains the input?
- Is the input raw, interim, normalized, or processed?

## Processing

- What transformation, validation, or calculation is happening?
- Is this a data rule, accounting rule, analytical rule, or presentation rule?
- Is the logic implemented in the correct layer?

## Output

- What is the output?
- Which file or table will contain it?
- Which later step will use the output?

## Execution State

- Has the file been saved?
- Has the program been run?
- Has the result been inspected?
- Has the change been tested?
- Has the change been committed?
- Has the change been pushed?
- Is `docs/project_status.md` up to date?

---

# 16. Current Project Position

## 16.1 What Has Been Established

The project has currently established:

- A professional local repository structure
- A Python virtual environment
- A Git and GitHub workflow
- A candidate-company universe
- Preliminary company classifications
- Preliminary core-sample decisions
- A company-master validation script
- A financial-data schema
- A financial-data dictionary
- Initial AMZN, EBAY, and ETSY annual financial data for 2021–2023
- A first version of financial-data validation
- A project-status document
- A project handbook

---

## 16.2 What Has Not Yet Been Established

The project has not yet established:

- A complete automated SEC extraction pipeline
- Final sample coverage
- A normalized financial-data layer
- A database
- Formal SQL metric tables
- A complete accounting-validation layer
- Automated tests
- Historical distress-signal validation
- A current-company risk score
- A Power BI dashboard

---

## 16.3 Current Stage Assessment

The project is still in the:

```text
Data-foundation stage
```

The immediate objective is not yet to build a polished dashboard or final risk score.

The current objective is to establish data that are:

- Reliable
- Consistent
- Documented
- Validated
- Suitable for later analytical use

---

# 17. Recommended Development Sequence After Reset

## 17.1 Immediate Priorities

1. Correct `docs/project_status.md` so that it reflects the verified repository state.
2. Review and document company-specific accounting-source treatments.
3. Fix the outdated empty-financial-data validation rule.
4. Add accounting-equation validation.
5. Add free-cash-flow reconciliation.
6. Add capital-expenditure sign validation.
7. Modularize validation logic where necessary.
8. Add basic automated tests.
9. Define the normalized-data output.
10. Expand financial-data collection.

---

## 17.2 Later Priorities

1. Build DuckDB tables.
2. Write SQL financial metrics.
3. Add metric-quality and applicability flags.
4. Define historical distress events.
5. Validate candidate early-warning signals.
6. Construct the current-company screener.
7. Develop the Power BI dashboard.
8. Complete the external README.
9. Complete the portfolio and interview narrative.

---

# 18. Final Mental Model

The project should always be understood through the following chain:

```text
Business question
    ↓
Company sample
    ↓
Reliable source data
    ↓
Raw data
    ↓
Validation
    ↓
Normalization
    ↓
Database and SQL
    ↓
Financial indicators
    ↓
Validated risk signals
    ↓
Explainable screening
    ↓
Power BI and decision support
```

The purpose of Python, SQL, Git, VS Code, DuckDB, and Power BI is not to replace business judgment.

Their purpose is to make business analysis:

- Reliable
- Repeatable
- Traceable
- Scalable
- Explainable

---

# 19. Core Project Principle

> The value of the Financial Health Screener does not come from calculating the largest possible number of ratios.

Its value comes from building a transparent chain between:

```text
Reliable financial data
    ↓
Economically meaningful indicators
    ↓
Historically validated deterioration signals
    ↓
Explainable business decisions
```

Every new file, script, table, metric, and dashboard element should strengthen that chain.