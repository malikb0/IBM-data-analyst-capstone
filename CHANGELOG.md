# Changelog

All notable changes to this project are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Changed
- **Repository restructured** into `src/`, `docs/`, `labs/`, `reports/`, `data/` and
  `build/`; root no longer holds code, docs, or data mixed together.
- Dependencies consolidated to `requirements.txt` (removed `Pipfile`/`Pipfile.lock`).
- Generated output moved to `reports/` (report + `reports/charts/` committed) while
  local databases and demo output go to the git-ignored `build/`.
- Lab notebooks grouped under `labs/notebooks/` with their assets in `labs/data/`.
- Documentation given a consistent structure, a `docs/README.md` index, and Mermaid
  diagrams.

### Added
- `pyproject.toml` (pytest + ruff config), `.editorconfig`, `CITATION.cff`,
  `CONTRIBUTING.md`, `CHANGELOG.md`, CI workflow, and per-directory READMEs.

### Removed
- Historical `Pipfile`/`Pipfile.lock`; empty `plans/` directory.

## [1.0.0]

### Added
- ETL pipeline (`src/build_database.py`) building a normalised SQLite database.
- Report generator (`src/generate_report.py`) producing charts and a written analysis.
- Deterministic test suite, `Makefile`, and the documented data workflow.
- Attribution (`NOTICE.md`), MIT `LICENSE`, and a 500-row committed sample.
