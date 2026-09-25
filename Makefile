# Makefile — one-command bring-up for the Stack Overflow 2024 capstone.
#
#   make setup       create .venv + install pinned deps
#   make demo        end-to-end on the committed sample (offline, deterministic)
#   make test        fast deterministic unit tests
#   make fetch-data  download the official survey into data/raw (network)
#   make build-db    CSV -> normalized SQLite
#   make report      SQLite -> charts + analysis report
#   make verify      run the readiness gate
#   make clean       remove local generated artifacts
#
# All targets are idempotent: safe to run more than once.

PYTHON   ?= python3.10
VENV     ?= .venv
BIN      := $(VENV)/bin
PIP      := $(BIN)/pip
PY       := $(BIN)/python

# Full-pipeline inputs/outputs (override on the command line, e.g. CSV=...).
RAW      ?= data/raw
CSV      ?= survey_data_updated.csv
DB       ?= survey_cleaned.sqlite
OUTPUT   ?= output

# Offline demo artifacts.
SAMPLE   ?= data/sample/so_survey_sample.csv
DEMO_DB  ?= demo.sqlite
DEMO_OUT ?= output_demo

.PHONY: help setup fetch-data build-db report test demo verify query clean

help: ## show this help
	@awk 'BEGIN{FS=":.*##"} /^[a-zA-Z_-]+:.*##/{printf "  %-12s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## create venv + install pinned deps
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

fetch-data: ## download the official survey into data/raw (network)
	bash scripts/fetch_data.sh $(RAW)

build-db: ## build $(DB) from $(CSV)
	$(PY) build_database.py --input $(CSV) --output $(DB)

report: ## generate charts + report from $(DB)
	$(PY) generate_report.py --db $(DB) --output-dir $(OUTPUT)

test: ## fast deterministic tests (no big data)
	$(PY) -m pytest tests/ -q

demo: ## end-to-end on the committed sample (no download)
	@test -f $(SAMPLE) || { echo "missing committed sample: $(SAMPLE)"; exit 1; }
	$(PY) build_database.py --input $(SAMPLE) --output $(DEMO_DB)
	$(PY) generate_report.py --db $(DEMO_DB) --output-dir $(DEMO_OUT)
	@echo "demo complete -> see $(DEMO_OUT)/"

verify: ## readiness gate
	bash .orchestrator/scripts/verify-readiness.sh

query: ## run a read-only query, e.g. make query Q="SELECT COUNT(*) FROM respondents"
	$(PY) scripts/query.py "$(Q)"

clean: ## remove local generated artifacts (keeps committed files)
	rm -rf $(DEMO_DB) $(DEMO_OUT) .pytest_cache
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
