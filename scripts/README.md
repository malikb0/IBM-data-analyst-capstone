# Scripts

Shell helpers for obtaining data. The Python pipeline itself lives in [`../src/`](../src/).

## `fetch_data.sh`

```bash
bash scripts/fetch_data.sh [dest_dir]     # dest defaults to data/raw
```

Downloads the official Stack Overflow 2024 Developer Survey archive, records its
SHA-256 next to the archive, extracts `survey_results_public.csv`, and sanity-checks the
header. It is idempotent (re-uses an existing archive).

Environment overrides:

| Variable | Purpose |
|---|---|
| `SO_SURVEY_URL` | Explicit archive URL (skips the built-in candidate list). |
| `SO_SURVEY_LOCAL_ZIP` | Use an already-downloaded zip (offline / air-gapped). |
| `SO_EXPECTED_SHA256` | Expected checksum; the download fails on mismatch. |

If the official CDN link has moved, the script prints guidance. The committed
`data/sample/` subset lets `make demo` run with no download at all.

See [`../data/README.md`](../data/README.md) and [`../docs/methodology.md`](../docs/methodology.md).
