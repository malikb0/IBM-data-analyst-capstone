# Methodology — Data Cleaning & Normalisation

This document describes how the Stack Overflow 2024 Developer Survey was turned into the
analysis database. Every rule here is implemented in `build_database.py`; the report and
chart logic lives in `generate_report.py`. Numbers quoted below come from the canonical
run (`18,845` respondents).

## 1. Source & provenance

- **Dataset:** Stack Overflow Developer Survey 2024 (public; ODbL).
- **Acquisition:** `scripts/fetch_data.sh` downloads the official archive to `data/raw/`,
  extracts `survey_results_public.csv`, and records a SHA-256 for the download.
- **Working subset:** the published analysis reads `survey_data_updated.csv` — an
  **18,845-row working subset** with the full **114 columns**. The official public file
  contains the complete response set (65k+ responses), so re-running the pipeline directly
  on the official file yields a larger sample and different absolute counts. The committed
  `data/sample/so_survey_sample.csv` (500 rows) exists only to make `make demo` run offline.
- **No invented data:** every figure in `RESULTS.md` / `output/analysis_report.md` is
  produced by running the pipeline on this input.

## 2. Cleaning rules

| Column / group | Issue | Rule applied | Code |
|---|---|---|---|
| `YearsCode`, `YearsCodePro` | Text sentinels mixed with numbers | `"Less than 1 year"` → `0.5`; `"More than 50 years"` → `55`; numeric strings → `float`; NaN/unparseable → `NULL` | `clean_years()` |
| `ConvertedCompYearly` | Extreme outliers | Clip at the **99th percentile**; NaN preserved as `NULL`. In the canonical run the cap is **$378,512** (applied exactly once). | `build()` (`p99 = df["ConvertedCompYearly"].quantile(0.99)`) |
| `Age` | `"Prefer not to say"` and any other unmapped value | → `NULL`. Unmapped values are collected and printed as a warning. | `AGE_MAP`, `build()` |
| `Knowledge_1..9` | Likert text | Mapped to `1..5` via `LIKERT_MAP`; an unrecognised response is stored with `score = NULL` **and** reported in a warning (never silently mapped to a wrong number). The canonical run has **0** unmapped Likert values. | `LIKERT_MAP`, `build()` |
| `JobSatPoints_1, 4..11` | Nine scattered numeric items | Long-format rows `(respondent_id, aspect, score)` with human-readable aspect names. | `ASPECT_MAP` |
| `Employment`, `DevType`, `LearnCode`, `CodingActivities` | `";"`-delimited multi-values | Split into one row per value in dedicated junction tables. | `split_multi()`, `build()` |
| 33 `*HaveWorkedWith` / `*WantToWorkWith` / `*Admired` columns | `";"`-delimited multi-values across 11 categories × 3 variants | Split into 33 per-category tables. | `TECH_CATEGORIES`, `VARIANTS`, `split_multi()` |

## 3. Normalisation & de-duplication

- Multi-value cells are split on `";"`, each part is stripped, blanks dropped, and
  **duplicates removed while preserving first-appearance order** (`split_multi()`).
- The de-dup key is `(respondent_id, value)` per table. So `"Python;Python"` produces a
  single `Language_have` row for that respondent. The canonical run contains **0**
  duplicate `(respondent_id, tech_name)` groups across all 33 technology tables.
- Because a value can legitimately appear in two different tables (e.g. a language in both
  `Language_have` and `Language_want`), de-duplication is applied per table, not globally.
- Resulting row counts differ from the raw respondent count by design: one respondent can
  contribute many technology rows. The `respondents` table always has exactly one row per
  `ResponseId`.

## 4. Relational schema (40 tables)

| Group | Count | Tables |
|---|---|---|
| Fact table | 1 | `respondents` (one row per participant) |
| Technology tables | 33 | `<Category>_have`, `<Category>_want`, `<Category>_admired` for 11 categories |
| Junction tables | 6 | `respondent_employment`, `respondent_devtype`, `respondent_learn_code`, `respondent_coding_activities`, `job_satisfaction_points`, `knowledge_self_assessment` |

- Primary key: `respondents.respondent_id`.
- Foreign key: every child table has `respondent_id → respondents.respondent_id`.
- Indexes are created on `respondent_id` (all child tables) and on `tech_name` (all
  technology tables), plus indexes on common `respondents` columns.

See [DATA_DICTIONARY.md](DATA_DICTIONARY.md) for column-level detail.

## 5. Reproducibility

```bash
make setup        # pinned environment
make demo         # offline: sample -> demo.sqlite -> output_demo/
make test         # deterministic tests
# full run:
make fetch-data && make build-db && make report
```

`build_database.py` and `generate_report.py` accept explicit paths:

```bash
python build_database.py --input <csv> --output <db>
python generate_report.py --db <db> --output-dir <dir>
```

Both are idempotent: `build_database.py` replaces a previous output database instead of
failing on existing tables, and `generate_report.py` produces byte-identical output when
run twice against the same database (verified in `tests/test_report_idempotency.py`).

## 6. Known deviations & judgement calls

- **Working subset vs full survey.** The canonical numbers come from an 18,845-row subset,
  not the full public response set. Re-running on the official file changes absolute counts.
- **99th-percentile cap.** Compensation is right-skewed; clipping at p99 (rather than
  winsorising or logging) is a deliberate, documented choice. It truncates the top tail.
- **Likert as interval.** `1..5` scores are ordinal; treating averages as interval is a
  simplification.
- **Age.** `"Prefer not to say"` is dropped to `NULL` rather than imputed.
- **JobSatPoints factor scale.** The nine `JobSatPoints_*` items are stored as their raw
  numeric scores; the report's "average score" reflects those raw values. Their exact
  scale/meaning should be confirmed against the official survey schema before strong
  claims are made about the ranking of factors.
- **Technology table names.** Tables use the survey's CSV prefixes, e.g. `Language_have`,
  `NEWCollabTools_want`, `AISearchDev_admired`. SQLite identifiers are case-insensitive, so
  lower-case references also resolve.
