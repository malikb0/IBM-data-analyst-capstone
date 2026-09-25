# Contributing

This is a personal portfolio project, but it is organised so that someone new can pick
it up. The notes below describe the conventions.

## Getting started

```bash
make setup     # create .venv and install pinned dependencies
make demo      # offline end-to-end run on the committed sample
make test      # deterministic test suite
```

## Layout

| Path | Purpose |
|---|---|
| `src/` | Pipeline source (`build_database.py`, `generate_report.py`, `query.py`). |
| `scripts/` | Shell helpers (data download). |
| `data/sample/` | The only committed data (a small subset). |
| `docs/` | Methodology, results, limitations, data dictionary. |
| `labs/` | IBM/Coursera coursework (attributed; **not** MIT). |
| `reports/` | Committed rendered report + charts. |
| `tests/` | pytest suite. |
| `build/` | Local generated artifacts (git-ignored). |

## Conventions

- Python 3.10, `snake_case` for functions and modules, type hints where useful.
- Keep generated artifacts out of git unless they are the committed report/charts.
- Reports and figures must be **computed from the data**, never hardcoded.
- Run `make test` before proposing a change.

## Scope

- The `labs/` notebooks are historical course artifacts. Do not restructure or
  "improve" them; they are kept as-is for provenance (see `NOTICE.md`).

## Security

- Never commit secrets, credentials, or `.env` files. The project needs none.
