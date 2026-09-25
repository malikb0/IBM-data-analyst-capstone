#!/usr/bin/env bash
# fetch_data.sh — download the official Stack Overflow 2024 Developer Survey.
#
# Usage:
#   bash scripts/fetch_data.sh [dest_dir]
#
# Environment overrides:
#   SO_SURVEY_URL        explicit zip URL to download (skips the candidate list)
#   SO_SURVEY_LOCAL_ZIP  path to an already-downloaded zip (offline / air-gapped)
#   SO_EXPECTED_SHA256   expected sha256 of the zip; if set, the download is
#                        verified against it and the script fails on mismatch
#
# Behaviour:
#   * Idempotent: re-uses an existing archive.
#   * Records the sha256 of the archive next to it (<archive>.sha256).
#   * Extracts `survey_results_public.csv` into the destination directory.
#   * Sanity-checks the extracted CSV header (expected 114 columns).
#
# The full dataset is NOT committed to git; only `data/sample/` holds a small
# subset so that `make demo` runs offline. See NOTICE.md §4 for attribution.
set -euo pipefail

DEST="${1:-data/raw}"
mkdir -p "$DEST"

ARCHIVE="$DEST/stack-overflow-developer-survey-2024.zip"
HASH_FILE="$ARCHIVE.sha256"
EXPECTED_SHA256="${SO_EXPECTED_SHA256:-}"
CSV_NAME="survey_results_public.csv"
FINAL_CSV="$DEST/$CSV_NAME"

# Official source, as referenced by the TidyTuesday 2024-09-03 cleaning script
# (which derives from survey.stackoverflow.co/2024). The CDN path has moved
# before, so a couple of known candidates are tried in order.
CANDIDATE_URLS=(
  "https://cdn.sanity.io/files/jo7n4k8s/production/262f04c41d99fea692e0125c342e446782233fe4.zip/stack-overflow-developer-survey-2024.zip"
  "https://cdn.stackoverflow.co/files/jo7n4k8s/developer-survey-2024.zip"
)

sha256_of() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | awk '{print $1}'
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | awk '{print $1}'
  else
    echo "no sha256 tool available" >&2
    return 1
  fi
}

# --- 1. obtain the archive -------------------------------------------------
if [[ -f "$ARCHIVE" ]]; then
  echo "archive already present: $ARCHIVE"
elif [[ -n "${SO_SURVEY_LOCAL_ZIP:-}" ]]; then
  [[ -f "$SO_SURVEY_LOCAL_ZIP" ]] || { echo "SO_SURVEY_LOCAL_ZIP not found: $SO_SURVEY_LOCAL_ZIP" >&2; exit 1; }
  echo "copying local zip: $SO_SURVEY_LOCAL_ZIP"
  cp "$SO_SURVEY_LOCAL_ZIP" "$ARCHIVE"
else
  if [[ -n "${SO_SURVEY_URL:-}" ]]; then
    urls=("$SO_SURVEY_URL")
  else
    urls=("${CANDIDATE_URLS[@]}")
  fi
  ok=0
  for url in "${urls[@]}"; do
    echo "trying $url"
    if curl -fL --retry 3 --connect-timeout 20 -o "$ARCHIVE.part" "$url"; then
      mv "$ARCHIVE.part" "$ARCHIVE"
      ok=1
      break
    fi
    rm -f "$ARCHIVE.part"
  done
  if [[ "$ok" != "1" ]]; then
    cat >&2 <<EOF

ERROR: could not download the survey archive from any known URL.

The official CDN link has moved. Please do one of the following:

  1. Download the 2024 zip manually from https://survey.stackoverflow.co/2024/
     and either:
       SO_SURVEY_LOCAL_ZIP=/path/to/stack-overflow-developer-survey-2024.zip \\
         bash scripts/fetch_data.sh
     or set the URL explicitly:
       SO_SURVEY_URL=https://.../stack-overflow-developer-survey-2024.zip \\
         bash scripts/fetch_data.sh
  2. Continue offline with the committed subset: \`make demo\` (no download).

EOF
    exit 1
  fi
fi

# --- 2. integrity check ----------------------------------------------------
actual=$(sha256_of "$ARCHIVE")
echo "sha256: $actual"
if [[ -n "$EXPECTED_SHA256" && "$actual" != "$EXPECTED_SHA256" ]]; then
  echo "sha256 mismatch: expected $EXPECTED_SHA256, got $actual" >&2
  exit 1
fi
printf '%s  %s\n' "$actual" "$(basename "$ARCHIVE")" > "$HASH_FILE"
echo "wrote $HASH_FILE"

# --- 3. extract ------------------------------------------------------------
echo "unzipping $ARCHIVE -> $DEST"
unzip -o "$ARCHIVE" "$CSV_NAME" -d "$DEST"

[[ -f "$FINAL_CSV" ]] || { echo "extracted archive did not contain $CSV_NAME" >&2; exit 1; }

# --- 4. header sanity check -----------------------------------------------
cols=$(head -n 1 "$FINAL_CSV" | awk -F',' '{print NF}')
echo "extracted $FINAL_CSV (${cols} columns in header)"
if [[ "$cols" -lt 100 ]]; then
  echo "WARNING: expected ~114 columns; got $cols — check the download." >&2
fi

echo
echo "done. raw file: $FINAL_CSV"
echo "For the canonical 18,845-row working subset used by the published results,"
echo "see METHODOLOGY.md §1; the official file contains the full response set."
