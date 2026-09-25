# Limitations

An honest account of the boundaries of this analysis. A portfolio analysis is stronger when
it names its own limits.

## Contents

- [Data](#data)
- [Method](#method)
- [Scope](#scope)
- [Reproducibility caveat](#reproducibility-caveat)

## Data

- **Self-selected sample.** Stack Overflow survey respondents are not representative of all
  developers. Results describe respondents, not the developer population.
- **Working subset, not the full survey.** The published numbers use an **18,845-row
  working subset** (`survey_data_updated.csv`). The official public file contains the full
  response set (65k+ responses), so absolute counts differ if you run the pipeline on the
  official file. Percentages are also affected by which rows are in the subset.
- **Self-reported.** Compensation, satisfaction, and experience are self-reported and
  unverified.
- **Single snapshot.** This is the 2024 survey only. "Want/have ratio" compares alternatives
  within one survey; it is not a time series.
- **Compensation.** Nominal USD, not PPP- or cost-of-living-adjusted. The 99th-percentile
  cap ($378,512) truncates the top tail, and **49.3%** of respondents have no compensation
  value at all, which is likely non-random.
- **Geography.** Country labels are inconsistent across years (e.g. `United Kingdom of
  Great Britain and Northern Ireland`). Small countries can show extreme medians; chart and
  reported country figures use a minimum of 30 respondents.
- **Age.** `"Prefer not to say"` and unmapped values become `NULL` (24 respondents), so age
  charts exclude them.

## Method

- **De-duplication and normalisation change row counts.** Child-table percentages are
  per-response, not per-respondent, unless explicitly noted. A respondent can contribute
  multiple rows to a technology or junction table.
- **Likert items are ordinal.** Mapping the five text responses to `1..5` and averaging them
  treats an ordinal scale as interval — a simplification.
- **JobSatPoints factor scale.** The nine `JobSatPoints_*` items are stored and averaged as
  raw numeric scores. The report's ranking of satisfaction factors (compensation/resources
  highest, coworkers lowest) depends on that scale; confirm the official item definition
  before making strong claims.
- **Capping and sentinel mapping are modelling choices**, not ground truth. `"Less than 1
  year" → 0.5` and `"More than 50 years" → 55` are conventions.
- **Unmapped values.** Unrecognised Likert responses are kept with `score = NULL` and
  reported in a build warning rather than guessed (the canonical run has none).

## Scope

- **Charts are descriptive, not causal.** No significance testing is claimed. Correlations
  such as remote-work ↔ compensation may be confounded by role, seniority, and country.
- **The 26 lab notebooks are course exercises**, not part of the analysed dataset and not
  covered by this project's MIT license (see [NOTICE.md](../NOTICE.md)).
- **AI-tool questions changed over survey years**; cross-year AI comparisons are not made
  here.

## Reproducibility caveat

- `make demo` runs on the 500-row committed sample, so it will **not** reproduce the
  headline numbers in [results.md](results.md); it verifies that the pipeline runs.
- The full run needs either the working subset or `make fetch-data` plus the official
  archive. The official CDN link has moved historically; `scripts/fetch_data.sh` tries known
  URLs and accepts an explicit `SO_SURVEY_URL` / `SO_SURVEY_LOCAL_ZIP` override.
