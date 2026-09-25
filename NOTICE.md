# NOTICE — Attribution, Provenance & Safety

This repository is a personal data-analysis portfolio project. It combines work of
several origins, listed below. **Nothing here is affiliated with, sponsored by, or
endorsed by any third party unless explicitly stated.**

> **In short:** the code, pipeline, tests and prose are the owner's own work (MIT).
> The `labs/` notebooks are completed IBM/Coursera coursework (attributed, *not* MIT).
> The dataset is Stack Overflow's 2024 survey (ODbL, *not* MIT).

## Contents

1. [Original work (repository owner)](#1-original-work-repository-owner)
2. [Course material (IBM / Coursera)](#2-course-material-ibm--coursera)
3. [Third-party assets](#3-third-party-assets)
4. [Dataset — Stack Overflow Developer Survey 2024](#4-dataset--stack-overflow-developer-survey-2024)
5. [Data provenance & integrity](#5-data-provenance--integrity)
6. [Security statement](#6-security-statement)
7. [License scope](#7-license-scope)

## 1. Original work (repository owner)

| Area | Location |
|---|---|
| Data pipeline | [`src/build_database.py`](src/build_database.py) |
| Report generator | [`src/generate_report.py`](src/generate_report.py) |
| Query helper | [`src/query.py`](src/query.py) |
| Data fetch script | [`scripts/fetch_data.sh`](scripts/fetch_data.sh) |
| Documentation | [`README.md`](README.md), [`docs/`](docs/), this file |
| Tests | [`tests/`](tests/) |
| Build/automation | [`Makefile`](Makefile) |

These are released under the MIT terms in [LICENSE](LICENSE).

## 2. Course material (IBM / Coursera)

The `*.ipynb` lab notebooks under [`labs/notebooks/`](labs/notebooks/) were completed as part of the
**IBM Data Analyst Professional Certificate** on Coursera. The lab instructions, starter
notebook templates, and the datasets supplied with the course are the property of IBM
and are included here as a record of completed coursework.

- **No affiliation / no endorsement.** This is independent coursework. It is not an
  official IBM or Coursera repository, and it is not reviewed or approved by them.
- **Separate license.** The course lab notebooks are **not** covered by this
  repository's MIT license. Their reuse is governed by the course's own terms.
- **Provenance, not originality.** The notebooks document how the skills used in the
  capstone were learned. Third-party instruction text embedded in them remains
  third-party text and is not presented here as the owner's own writing.

## 3. Third-party assets

| Asset | Origin | Handling |
|---|---|---|
| [`labs/notebooks/*.ipynb`](labs/notebooks/) (26 files) | IBM Data Analyst Professional Certificate (Coursera) | Published as completed coursework; attributed here; excluded from MIT. |
| `Data Analyst Capstone Template 2026.pptx` | IBM/Coursera capstone template | Third-party template, **unused**, and git-ignored. Not presented as original work. |
| [`docs/capstone-report.pdf`](docs/capstone-report.pdf) | Generated from this owner's analysis | Owner's report export. Covered by MIT. |
| `labs/data/astros.json` | Public NASA APOD API response (sample payload) | Public sample data used in an API lesson. Not sensitive. |
| `labs/data/job-postings.xlsx`, `labs/data/popular-languages.csv` | Public sample datasets used in course labs | Public samples; retained for lab provenance. |

No logos, trademarks, or brand styling are claimed or redistributed as this project's
own identity. The project title references the course factually only.

## 4. Dataset — Stack Overflow Developer Survey 2024

- **Source:** Stack Overflow Developer Survey 2024
  (<https://survey.stackoverflow.co/2024/>).
- **License:** published by Stack Overflow under the Open Database License (ODbL).
  Attribution: "Stack Overflow Developer Survey 2024".
- **Not committed in full.** The full survey file is large. `scripts/fetch_data.sh`
  downloads it, and `data/sample/so_survey_sample.csv` holds a small subset so that
  `make demo` runs offline. Only that subset is redistributed here, under the
  dataset's original license.
- The dataset is **not** covered by this repository's MIT license.

## 5. Data provenance & integrity

- The pipeline is deterministic: same input CSV → same database contents.
- `make demo` runs end-to-end on the committed subset with no network access.
- A full run requires `make fetch-data` (which verifies the download size) followed by
  `make build-db && make report`. See [docs/methodology.md](docs/methodology.md) §5.
- The raw download is not tracked by git; only the small subset under `data/sample/` is.

## 6. Security statement

- No credentials, API keys, tokens, or `.env` files are used by this project. The
  analysis reads a local CSV and writes a local SQLite file; no network calls are made
  at analysis time.
- The repository was scanned for secret patterns in the working tree and in git
  history; no live secrets were found. The API/scraping lab notebooks reference public,
  unauthenticated endpoints only.
- If you believe a secret is present, please open an issue and do not post the value.

## 7. License scope

MIT (see [LICENSE](LICENSE)) applies to the owner's original code and prose only. It
does **not** apply to the IBM/Coursera course lab notebooks or the Stack Overflow
survey dataset, each of which carries its own terms. The generated charts and report
are original work and are covered by MIT.

---

_If you are a rights holder and believe material here should not be public, please open
an issue so it can be reviewed._
