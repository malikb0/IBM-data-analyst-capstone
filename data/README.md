# Data

Only one data file is committed. Large and regenerable data is kept out of git.

```text
data/
├── sample/so_survey_sample.csv   # committed: 500-row subset, used by `make demo`
├── raw/                          # git-ignored: official survey download
└── interim/                      # git-ignored: working CSVs derived during analysis
```

| Directory | Tracked? | Contents |
|---|---|---|
| `sample/` | Yes | `so_survey_sample.csv` — a 500-row subset so the pipeline runs offline. |
| `raw/` | No | The official survey archive/CSV, downloaded by `make fetch-data`. |
| `interim/` | No | Working/derived CSVs (e.g. the 18,845-row analysis subset used for the published results). |

## Getting the full dataset

```bash
make fetch-data     # downloads into data/raw/ and records a SHA-256
```

Optionally set `SO_SURVEY_LOCAL_ZIP` or `SO_SURVEY_URL` (see
[`../scripts/fetch_data.sh`](../scripts/fetch_data.sh)) if the official CDN link has
moved.

## License

The Stack Overflow Developer Survey 2024 is published under the **Open Database License
(ODbL)** and is **not** covered by this repository's MIT license. See
[`../NOTICE.md`](../NOTICE.md) §4.
