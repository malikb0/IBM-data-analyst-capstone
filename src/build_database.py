"""Build a normalised SQLite database from the Stack Overflow 2024 survey CSV.

Usage:
    python src/build_database.py [--input CSV] [--output DB]

Defaults preserve the original pipeline paths:
    --input  survey_data_updated.csv
    --output survey_cleaned.sqlite

The database layout is unchanged from the original capstone run:
    respondents                         (1 row per participant)
    33 per-category technology tables   (11 categories x 3 variants)
    6 junction tables                   (employment, devtype, learncode,
                                         coding activities, job satisfaction,
                                         knowledge self-assessment)

Multi-value (";"-delimited) columns are split into one row per value and
de-duplicated so that a participant never appears twice for the same value
(e.g. "Python;Python" yields a single row).
"""

from __future__ import annotations

import argparse
import os
import sqlite3
import sys

import pandas as pd

# --------------------------------------------------------------------------
# Cleaning rules (pure, importable, unit-tested in tests/)
# --------------------------------------------------------------------------

YEARS_CODE_MAP = {"Less than 1 year": 0.5, "More than 50 years": 55}

AGE_MAP = {
    "Under 18 years old": "Under 18",
    "18-24 years old": "18-24",
    "25-34 years old": "25-34",
    "35-44 years old": "35-44",
    "45-54 years old": "45-54",
    "55-64 years old": "55-64",
    "65 years or older": "65+",
    "Prefer not to say": None,
}

LIKERT_MAP = {
    "Strongly disagree": 1,
    "Disagree": 2,
    "Neither agree nor disagree": 3,
    "Agree": 4,
    "Strongly agree": 5,
}

# 11 technology categories (CSV prefix == SQLite table prefix) x 3 variants.
TECH_CATEGORIES = [
    "Language",
    "Database",
    "Platform",
    "Webframe",
    "Embedded",
    "MiscTech",
    "ToolsTech",
    "NEWCollabTools",
    "OfficeStackAsync",
    "OfficeStackSync",
    "AISearchDev",
]

VARIANTS = [("HaveWorkedWith", "have"), ("WantToWorkWith", "want"), ("Admired", "admired")]

ASPECT_MAP = {
    "JobSatPoints_1": "career_satisfaction",
    "JobSatPoints_4": "coworkers",
    "JobSatPoints_5": "work_life_balance",
    "JobSatPoints_6": "compensation",
    "JobSatPoints_7": "resources",
    "JobSatPoints_8": "autonomy",
    "JobSatPoints_9": "growth",
    "JobSatPoints_10": "management",
    "JobSatPoints_11": "retention",
}


def clean_years(val):
    """Map the survey's sentinel strings to numbers; return None for NaN/blank.

    "Less than 1 year" -> 0.5, "More than 50 years" -> 55, numeric -> float.
    Anything unparseable (including NaN) -> None.
    """
    if pd.isna(val):
        return None
    val = str(val).strip()
    if val in YEARS_CODE_MAP:
        return YEARS_CODE_MAP[val]
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def split_multi(val):
    """Split a ';'-delimited cell, stripping whitespace and de-duplicating.

    Order of first appearance is preserved so results are deterministic.
    Returns an empty list for NaN/blank input.
    """
    if pd.isna(val):
        return []
    parts = [p.strip() for p in str(val).split(";")]
    return list(dict.fromkeys(p for p in parts if p))


def _clean_str(val):
    """Return a stripped string, or None for NaN/blank."""
    if pd.isna(val):
        return None
    text = str(val).strip()
    return text if text else None


def _default_input():
    return os.environ.get("SURVEY_CSV", "survey_data_updated.csv")


def _default_output():
    return os.environ.get("SURVEY_DB", "survey_cleaned.sqlite")


RESPONDENT_COLUMNS = [
    "respondent_id",
    "main_branch",
    "age_group",
    "remote_work",
    "ed_level",
    "years_code",
    "years_code_pro",
    "org_size",
    "country",
    "converted_comp_yearly",
    "work_exp",
    "job_sat",
    "icor_pm",
    "t_branch",
    "industry",
    "os_personal",
    "os_professional",
    "so_visit_freq",
    "so_account",
    "so_part_freq",
    "so_comm",
    "ai_select",
    "ai_sent",
    "ai_ben",
    "ai_acc",
    "ai_complex",
    "ai_threat",
    "ai_ethics",
    "survey_length",
    "survey_ease",
]

_SCHEMA_SQL = """
CREATE TABLE respondents (
    respondent_id INTEGER PRIMARY KEY,
    main_branch TEXT,
    age_group TEXT,
    remote_work TEXT,
    ed_level TEXT,
    years_code REAL,
    years_code_pro REAL,
    org_size TEXT,
    country TEXT,
    converted_comp_yearly REAL,
    work_exp REAL,
    job_sat REAL,
    icor_pm TEXT,
    t_branch TEXT,
    industry TEXT,
    os_personal TEXT,
    os_professional TEXT,
    so_visit_freq TEXT,
    so_account TEXT,
    so_part_freq TEXT,
    so_comm TEXT,
    ai_select TEXT,
    ai_sent TEXT,
    ai_ben TEXT,
    ai_acc TEXT,
    ai_complex TEXT,
    ai_threat TEXT,
    ai_ethics TEXT,
    survey_length TEXT,
    survey_ease TEXT
)
"""

_JUNCTION_SQL = {
    "respondent_employment": "employment_type",
    "respondent_devtype": "dev_type",
    "respondent_learn_code": "learning_source",
    "respondent_coding_activities": "activity",
}


def _prepare_output(output_db):
    """Remove a previous database (and WAL sidecars) so the build is idempotent."""
    for path in (output_db, output_db + "-wal", output_db + "-shm"):
        if os.path.exists(path):
            os.remove(path)
    parent = os.path.dirname(os.path.abspath(output_db))
    os.makedirs(parent, exist_ok=True)


def build(input_csv=_default_input, output_db=_default_output, verbose=True):
    """Run the ETL. Returns a dict of row counts for verification/tests."""
    input_csv = input_csv() if callable(input_csv) else input_csv
    output_db = output_db() if callable(output_db) else output_db

    if verbose:
        print(f"Reading {input_csv} ...")
    df = pd.read_csv(input_csv)

    df["years_code_clean"] = df["YearsCode"].apply(clean_years)
    df["years_code_pro_clean"] = df["YearsCodePro"].apply(clean_years)

    p99 = df["ConvertedCompYearly"].quantile(0.99)
    df["comp_clean"] = df["ConvertedCompYearly"].clip(upper=p99)
    df["comp_clean"] = df["comp_clean"].where(df["ConvertedCompYearly"].notna())

    # Age mapping: unknown values become NaN (surface them as a warning).
    mapped_age = df["Age"].map(AGE_MAP)
    unknown_ages = sorted({str(a) for a in df["Age"].dropna() if a not in AGE_MAP})
    df["age_clean"] = mapped_age

    if verbose:
        print(f"  compensation p99 cap = {p99:,.0f}")
        if unknown_ages:
            print(f"  WARNING: unmapped Age values -> NULL: {unknown_ages}")

    _prepare_output(output_db)
    conn = sqlite3.connect(output_db)
    c = conn.cursor()
    c.executescript(
        """
        PRAGMA journal_mode=WAL;
        PRAGMA synchronous=OFF;
        PRAGMA foreign_keys=ON;
        """
    )

    c.execute(_SCHEMA_SQL)

    # 33 per-category tech tables, named "<CSV prefix>_<variant>".
    for cat_prefix in TECH_CATEGORIES:
        for _, var_suffix in VARIANTS:
            c.execute(
                f"""
                CREATE TABLE {cat_prefix}_{var_suffix} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    respondent_id INTEGER NOT NULL,
                    tech_name TEXT NOT NULL,
                    FOREIGN KEY (respondent_id) REFERENCES respondents(respondent_id)
                )
                """
            )

    # Multi-value junction tables.
    for table, value_col in _JUNCTION_SQL.items():
        c.execute(
            f"""
            CREATE TABLE {table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                respondent_id INTEGER NOT NULL,
                {value_col} TEXT NOT NULL,
                FOREIGN KEY (respondent_id) REFERENCES respondents(respondent_id)
            )
            """
        )

    c.execute(
        """
        CREATE TABLE job_satisfaction_points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            respondent_id INTEGER NOT NULL,
            aspect TEXT NOT NULL,
            score REAL,
            FOREIGN KEY (respondent_id) REFERENCES respondents(respondent_id)
        )
        """
    )

    c.execute(
        """
        CREATE TABLE knowledge_self_assessment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            respondent_id INTEGER NOT NULL,
            knowledge_area TEXT NOT NULL,
            response TEXT,
            score INTEGER,
            FOREIGN KEY (respondent_id) REFERENCES respondents(respondent_id)
        )
        """
    )

    # ---- collect rows -----------------------------------------------------
    respondents_rows = []
    junction_rows = {table: [] for table in _JUNCTION_SQL}
    tech_rows = {
        f"{cat_prefix}_{var_suffix}": []
        for cat_prefix in TECH_CATEGORIES
        for _, var_suffix in VARIANTS
    }
    satpoint_rows = []
    knowledge_rows = []
    unmapped_likert = {}

    def _add_unique(rows, seen, key, payload):
        if key in seen:
            return
        seen.add(key)
        rows.append(payload)

    seen_emp, seen_dev, seen_learn, seen_code = set(), set(), set(), set()
    seen_tech = {tbl: set() for tbl in tech_rows}
    seen_sat, seen_know = set(), set()

    for idx, row in df.iterrows():
        rid = int(row["ResponseId"])

        respondents_rows.append(
            (
                rid,
                _clean_str(row["MainBranch"]),
                row["age_clean"],
                _clean_str(row["RemoteWork"]),
                _clean_str(row["EdLevel"]),
                row["years_code_clean"],
                row["years_code_pro_clean"],
                _clean_str(row["OrgSize"]),
                _clean_str(row["Country"]),
                row["comp_clean"],
                row["WorkExp"] if pd.notna(row["WorkExp"]) else None,
                row["JobSat"] if pd.notna(row["JobSat"]) else None,
                _clean_str(row["ICorPM"]),
                _clean_str(row["TBranch"]),
                _clean_str(row["Industry"]),
                _clean_str(row["OpSysPersonal use"]),
                _clean_str(row["OpSysProfessional use"]),
                _clean_str(row["SOVisitFreq"]),
                _clean_str(row["SOAccount"]),
                _clean_str(row["SOPartFreq"]),
                _clean_str(row["SOComm"]),
                _clean_str(row["AISelect"]),
                _clean_str(row["AISent"]),
                _clean_str(row["AIBen"]),
                _clean_str(row["AIAcc"]),
                _clean_str(row["AIComplex"]),
                _clean_str(row["AIThreat"]),
                _clean_str(row["AIEthics"]),
                _clean_str(row["SurveyLength"]),
                _clean_str(row["SurveyEase"]),
            )
        )

        for value in split_multi(row["Employment"]):
            _add_unique(junction_rows["respondent_employment"], seen_emp, (rid, value), (rid, value))
        for value in split_multi(row["DevType"]):
            _add_unique(junction_rows["respondent_devtype"], seen_dev, (rid, value), (rid, value))
        for value in split_multi(row["LearnCode"]):
            _add_unique(junction_rows["respondent_learn_code"], seen_learn, (rid, value), (rid, value))
        for value in split_multi(row["CodingActivities"]):
            _add_unique(junction_rows["respondent_coding_activities"], seen_code, (rid, value), (rid, value))

        for cat_prefix in TECH_CATEGORIES:
            for csv_var, var_suffix in VARIANTS:
                col = f"{cat_prefix}{csv_var}"
                if col not in df.columns:
                    continue
                table = f"{cat_prefix}_{var_suffix}"
                for tech_item in split_multi(row[col]):
                    _add_unique(tech_rows[table], seen_tech[table], (rid, tech_item), (rid, tech_item))

        for col, aspect in ASPECT_MAP.items():
            if col in df.columns and pd.notna(row[col]):
                _add_unique(satpoint_rows, seen_sat, (rid, aspect), (rid, aspect, float(row[col])))

        for k in range(1, 10):
            col = f"Knowledge_{k}"
            if col not in df.columns:
                continue
            val = row[col]
            if pd.notna(val):
                val_str = str(val).strip()
                score = LIKERT_MAP.get(val_str)
                if val_str not in LIKERT_MAP:
                    unmapped_likert[val_str] = unmapped_likert.get(val_str, 0) + 1
                _add_unique(knowledge_rows, seen_know, (rid, col), (rid, col, val_str, score))

        if verbose and (idx + 1) % 2000 == 0:
            print(f"  Processed {idx + 1}/{len(df)} rows...")

    if unmapped_likert:
        print(
            "  WARNING: unmapped Likert responses stored with score=NULL: "
            + ", ".join(f"{k!r} (x{v})" for k, v in sorted(unmapped_likert.items())),
            file=sys.stderr,
        )

    # ---- insert -----------------------------------------------------------
    placeholders = ",".join(["?"] * len(RESPONDENT_COLUMNS))
    if verbose:
        print(f"Inserting {len(respondents_rows)} respondents...")
    c.executemany(
        f"INSERT INTO respondents ({','.join(RESPONDENT_COLUMNS)}) VALUES ({placeholders})",
        respondents_rows,
    )
    for table, value_col in _JUNCTION_SQL.items():
        rows = junction_rows[table]
        if verbose:
            print(f"Inserting {len(rows)} rows into {table}...")
        if rows:
            c.executemany(
                f"INSERT INTO {table} (respondent_id, {value_col}) VALUES (?,?)", rows
            )
    for table, rows in tech_rows.items():
        if verbose:
            print(f"Inserting {len(rows)} rows into {table}...")
        if rows:
            c.executemany(
                f"INSERT INTO {table} (respondent_id, tech_name) VALUES (?,?)", rows
            )
    if verbose:
        print(f"Inserting {len(satpoint_rows)} satisfaction point rows...")
    if satpoint_rows:
        c.executemany(
            "INSERT INTO job_satisfaction_points (respondent_id, aspect, score) VALUES (?,?,?)",
            satpoint_rows,
        )
    if verbose:
        print(f"Inserting {len(knowledge_rows)} knowledge assessment rows...")
    if knowledge_rows:
        c.executemany(
            "INSERT INTO knowledge_self_assessment "
            "(respondent_id, knowledge_area, response, score) VALUES (?,?,?,?)",
            knowledge_rows,
        )

    # ---- indexes ----------------------------------------------------------
    if verbose:
        print("Creating indexes...")
    indexes = [
        "CREATE INDEX idx_respondents_country ON respondents(country)",
        "CREATE INDEX idx_respondents_age ON respondents(age_group)",
        "CREATE INDEX idx_respondents_remote ON respondents(remote_work)",
        "CREATE INDEX idx_respondents_comp ON respondents(converted_comp_yearly)",
        "CREATE INDEX idx_respondents_jobsat ON respondents(job_sat)",
        "CREATE INDEX idx_emp_rid ON respondent_employment(respondent_id)",
        "CREATE INDEX idx_devtype_rid ON respondent_devtype(respondent_id)",
        "CREATE INDEX idx_learn_rid ON respondent_learn_code(respondent_id)",
        "CREATE INDEX idx_coding_rid ON respondent_coding_activities(respondent_id)",
        "CREATE INDEX idx_satpoint_rid ON job_satisfaction_points(respondent_id)",
        "CREATE INDEX idx_knowledge_rid ON knowledge_self_assessment(respondent_id)",
    ]
    for tbl_name in sorted(tech_rows.keys()):
        indexes.append(f"CREATE INDEX idx_{tbl_name}_rid ON {tbl_name}(respondent_id)")
        indexes.append(f"CREATE INDEX idx_{tbl_name}_tech ON {tbl_name}(tech_name)")
    for idx_sql in indexes:
        c.execute(idx_sql)

    conn.commit()
    c.execute("ANALYZE")
    conn.close()

    counts = {
        "respondents": len(respondents_rows),
        "tech_rows": sum(len(v) for v in tech_rows.values()),
        "tables": 1 + len(tech_rows) + len(_JUNCTION_SQL) + 2,
    }
    if verbose:
        print(f"\nDatabase created successfully: {output_db}")
        print(
            f"Tables: respondents + {len(tech_rows)} per-category tech tables "
            f"(11 categories x 3 variants) + {len(_JUNCTION_SQL) + 2} junction tables "
            f"= {counts['tables']} tables total"
        )
    return counts


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--input", default=_default_input(), help="survey CSV path")
    parser.add_argument("--output", default=_default_output(), help="output SQLite path")
    parser.add_argument("-q", "--quiet", action="store_true", help="suppress progress output")
    args = parser.parse_args(argv)

    if not os.path.exists(args.input):
        parser.error(f"input CSV not found: {args.input}")
    build(args.input, args.output, verbose=not args.quiet)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
