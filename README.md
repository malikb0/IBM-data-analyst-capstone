# Developer Survey Analysis — Stack Overflow 2024

> Cleaning, normalising and analysing 18,845 responses to the Stack Overflow 2024
> Developer Survey: a reproducible data pipeline plus a written analysis of technology
> trends, pay, job satisfaction and AI-tool adoption.
>
> **Not affiliated with, sponsored by, or endorsed by IBM, Coursera, or Stack Overflow.**
> This is an independent portfolio project; the survey data belongs to Stack Overflow and
> the course labs belong to IBM/Coursera. See [NOTICE.md](NOTICE.md).

This is a documentation-first data-analysis project. The ETL and reporting code are small
and readable; the value is the **reproducible pipeline** (CSV → relational SQLite → charts
→ report) and the **analysis** it produces.

## Results at a glance

Exact figures from the current run (`18,845` respondents; see [RESULTS.md](RESULTS.md) and
[`output/analysis_report.md`](output/analysis_report.md)):

- **JavaScript leads usage** at **79%** of respondents and is also the most-wanted language
  (**61%**). TypeScript sits at **57%** current vs **55%** desired.
- **Rust has the strongest want/have ratio** of any major language (**~2.45×**: 2,284 use it,
  5,597 want to).
- **PostgreSQL is the most-used and most-wanted database** (**61%** use, **65%** want),
  ahead of MySQL (**45%**) and SQLite (**37%**).
- **Remote work tracks higher pay and satisfaction**: remote median pay **$90,712** vs
  in-person **$55,850**; mean satisfaction **7.27** vs **6.75** (out of 10).
- **Global median pay is $65,858**; the United States has the highest national median among
  countries with 30+ respondents (**$148,000**).
- **AI sentiment is broadly favourable**: 3,962 "very favorable" + 7,458 "favorable" vs
  734 "unfavorable" + 167 "very unfavorable".

## What this project does

1. **ETL** — `build_database.py` reads the survey CSV, applies documented cleaning rules
   (sentinel mapping for years, a 99th-percentile compensation cap, Likert mapping), and
   normalises `";"`-delimited multi-value columns into a relational SQLite schema with
   de-duplication.
2. **Analysis** — `generate_report.py` queries that database and emits 40+ charts plus a
   generated Markdown report with computed figures.
3. **Reproducibility** — a `Makefile`, a scripted data fetch, a tiny committed sample, and
   deterministic tests let anyone reproduce the pipeline offline (`make demo`) or in full.

## Repository structure

```
build_database.py      # CSV -> normalised SQLite (40 tables)
generate_report.py     # SQLite -> charts + generated analysis report
analysis_report.md     # see output/analysis_report.md (generated)
data/sample/           # tiny committed subset so `make demo` runs offline
scripts/fetch_data.sh  # download the official survey + integrity check
scripts/query.py       # read-only query helper for the SQLite database
tests/                 # deterministic tests (cleaning, ETL, report idempotency)
docs/images/           # README screenshots
output/                # generated charts + analysis_report.md
0..24 *.ipynb          # IBM/Coursera course labs (attributed; see NOTICE.md)
METHODOLOGY.md         # cleaning + normalisation rules
DATA_DICTIONARY.md     # the 40 tables and the 114 source columns
LIMITATIONS.md         # what this analysis does and does not prove
RESULTS.md             # headline findings with exact numbers and queries
NOTICE.md / LICENSE    # attribution and reuse terms
```

## Data

- **Source:** Stack Overflow Developer Survey 2024 (public; ODbL). Attribution:
  "Stack Overflow Developer Survey 2024".
- **The full survey file is not committed** (it is large). `make fetch-data` downloads the
  official archive into `data/raw/` and records a SHA-256 for the download.
- **A small subset is committed** (`data/sample/so_survey_sample.csv`, 500 rows) so that
  `make demo` works with **no download and no network**.
- The published analysis uses an **18,845-row working subset** (`survey_data_updated.csv`).
  The official public file contains the full response set (65k+ responses); running the
  pipeline on it produces a larger sample and different absolute counts. This is recorded
  as a limitation — see [METHODOLOGY.md](METHODOLOGY.md) §1 and [LIMITATIONS.md](LIMITATIONS.md).

## Environment setup (bare machine)

Requires **Python 3.10.11** and `make`.

```bash
git clone https://github.com/malikb0/IBM-data-analyst-capstone.git
cd IBM-data-analyst-capstone
make setup        # creates .venv and installs the pinned dependencies
```

## Quickstart

```bash
make demo         # end-to-end on the committed sample (offline, deterministic)
make test         # fast deterministic unit tests
make verify       # run the readiness checks

# Full pipeline (needs the data):
make fetch-data   # download the official survey into data/raw/
make build-db     # CSV -> survey_cleaned.sqlite
make report       # SQLite -> output/ charts + report
```

`make` targets are idempotent: re-running them is safe. Use `make help` to list them.

## Results

- Written findings with exact numbers and the queries behind them: **[RESULTS.md](RESULTS.md)**.
- Full generated report (charts + figures): **[output/analysis_report.md](output/analysis_report.md)**.
- Charts are regenerated into `output/` by `make report` (or `output_demo/` by `make demo`).

![Top 10 programming languages currently used](docs/images/chart_lang_current.png)

![Top 10 databases currently used](docs/images/chart_db_current.png)

![Median compensation by country, top 10](docs/images/chart_comp_country.png)

## Limitations

Self-selected respondents, self-reported figures, a single survey year, nominal USD
compensation, and mapping/cleaning choices all bound what these charts can claim. Read
[LIMITATIONS.md](LIMITATIONS.md) before drawing conclusions. Charts are descriptive, not
causal.

## Attribution & license

- **Original work** (pipeline, report, docs, tests, scripts) is **MIT** — see [LICENSE](LICENSE).
- **Course work**: the `*.ipynb` lab notebooks were completed for the IBM Data Analyst
  Professional Certificate on Coursera and remain IBM/Coursera material; they are included
  as credited coursework and are **not** covered by the MIT license.
- **Dataset**: Stack Overflow Developer Survey 2024, under its own (ODbL) terms.
- Full details, including third-party assets and a security note: **[NOTICE.md](NOTICE.md)**.

_This project is independent coursework and is not affiliated with or endorsed by IBM,
Coursera, or Stack Overflow._
