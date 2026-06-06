import sqlite3
import pandas as pd
import numpy as np

CSV_PATH = "survey_data_updated.csv"
DB_PATH = "survey_cleaned.sqlite"

df = pd.read_csv(CSV_PATH)

YEARS_CODE_MAP = {"Less than 1 year": 0.5, "More than 50 years": 55}
def clean_years(val):
    if pd.isna(val):
        return None
    val = str(val).strip()
    if val in YEARS_CODE_MAP:
        return YEARS_CODE_MAP[val]
    try:
        return float(val)
    except:
        return None

df["years_code_clean"] = df["YearsCode"].apply(clean_years)
df["years_code_pro_clean"] = df["YearsCodePro"].apply(clean_years)

p99 = df["ConvertedCompYearly"].quantile(0.99)
df["comp_clean"] = df["ConvertedCompYearly"].clip(upper=p99)
df["comp_clean"] = df["comp_clean"].where(df["ConvertedCompYearly"].notna())

age_map_clean = {
    "Under 18 years old": "Under 18",
    "18-24 years old": "18-24",
    "25-34 years old": "25-34",
    "35-44 years old": "35-44",
    "45-54 years old": "45-54",
    "55-64 years old": "55-64",
    "65 years or older": "65+",
    "Prefer not to say": None,
}
df["age_clean"] = df["Age"].map(age_map_clean)

LIKERT_MAP = {
    "Strongly disagree": 1,
    "Disagree": 2,
    "Neither agree nor disagree": 3,
    "Agree": 4,
    "Strongly agree": 5,
}

# 11 category definitions: (csv_prefix, table_suffix)
TECH_CATEGORIES = [
    ("Language", "language"),
    ("Database", "database"),
    ("Platform", "platform"),
    ("Webframe", "webframe"),
    ("Embedded", "embedded"),
    ("MiscTech", "misctech"),
    ("ToolsTech", "toolstech"),
    ("NEWCollabTools", "collabtools"),
    ("OfficeStackAsync", "officestackasync"),
    ("OfficeStackSync", "officestacksync"),
    ("AISearchDev", "aistack"),
]

VARIANTS = [("HaveWorkedWith", "have"), ("WantToWorkWith", "want"), ("Admired", "admired")]

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

c.executescript("""
PRAGMA journal_mode=WAL;
PRAGMA synchronous=OFF;
PRAGMA foreign_keys=ON;
""")

c.execute("""
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
""")

# Create all 33 per-category tech tables
for cat_suffix, _ in TECH_CATEGORIES:
    for _, var_suffix in VARIANTS:
        tbl = f"{cat_suffix}_{var_suffix}"
        c.execute(f"""
        CREATE TABLE {tbl} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            respondent_id INTEGER NOT NULL,
            tech_name TEXT NOT NULL,
            FOREIGN KEY (respondent_id) REFERENCES respondents(respondent_id)
        )
        """)

# Existing junction tables
c.execute("""
CREATE TABLE respondent_employment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    respondent_id INTEGER NOT NULL,
    employment_type TEXT NOT NULL,
    FOREIGN KEY (respondent_id) REFERENCES respondents(respondent_id)
)
""")

c.execute("""
CREATE TABLE respondent_devtype (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    respondent_id INTEGER NOT NULL,
    dev_type TEXT NOT NULL,
    FOREIGN KEY (respondent_id) REFERENCES respondents(respondent_id)
)
""")

c.execute("""
CREATE TABLE respondent_learn_code (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    respondent_id INTEGER NOT NULL,
    learning_source TEXT NOT NULL,
    FOREIGN KEY (respondent_id) REFERENCES respondents(respondent_id)
)
""")

c.execute("""
CREATE TABLE respondent_coding_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    respondent_id INTEGER NOT NULL,
    activity TEXT NOT NULL,
    FOREIGN KEY (respondent_id) REFERENCES respondents(respondent_id)
)
""")

c.execute("""
CREATE TABLE job_satisfaction_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    respondent_id INTEGER NOT NULL,
    aspect TEXT NOT NULL,
    score REAL,
    FOREIGN KEY (respondent_id) REFERENCES respondents(respondent_id)
)
""")

c.execute("""
CREATE TABLE knowledge_self_assessment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    respondent_id INTEGER NOT NULL,
    knowledge_area TEXT NOT NULL,
    response TEXT,
    score INTEGER,
    FOREIGN KEY (respondent_id) REFERENCES respondents(respondent_id)
)
""")

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

# Pre-build dict of lists per table
respondent_rows = []
employment_rows = []
devtype_rows = []
learncode_rows = []
codingact_rows = []
satpoint_rows = []
knowledge_rows = []

# For tech tables: dict of table_name -> list of (respondent_id, tech_name)
tech_rows = {}
for cat_prefix, _ in TECH_CATEGORIES:
    for _, var_suffix in VARIANTS:
        tbl = f"{cat_prefix}_{var_suffix}"
        tech_rows[tbl] = []

for idx, row in df.iterrows():
    rid = int(row["ResponseId"])

    respondent_rows.append((
        rid,
        str(row["MainBranch"]) if pd.notna(row["MainBranch"]) else None,
        row["age_clean"],
        str(row["RemoteWork"]) if pd.notna(row["RemoteWork"]) else None,
        str(row["EdLevel"]) if pd.notna(row["EdLevel"]) else None,
        row["years_code_clean"],
        row["years_code_pro_clean"],
        str(row["OrgSize"]) if pd.notna(row["OrgSize"]) else None,
        str(row["Country"]) if pd.notna(row["Country"]) else None,
        row["comp_clean"],
        row["WorkExp"] if pd.notna(row["WorkExp"]) else None,
        row["JobSat"] if pd.notna(row["JobSat"]) else None,
        str(row["ICorPM"]) if pd.notna(row["ICorPM"]) else None,
        str(row["TBranch"]) if pd.notna(row["TBranch"]) else None,
        str(row["Industry"]) if pd.notna(row["Industry"]) else None,
        str(row["OpSysPersonal use"]) if pd.notna(row["OpSysPersonal use"]) else None,
        str(row["OpSysProfessional use"]) if pd.notna(row["OpSysProfessional use"]) else None,
        str(row["SOVisitFreq"]) if pd.notna(row["SOVisitFreq"]) else None,
        str(row["SOAccount"]) if pd.notna(row["SOAccount"]) else None,
        str(row["SOPartFreq"]) if pd.notna(row["SOPartFreq"]) else None,
        str(row["SOComm"]) if pd.notna(row["SOComm"]) else None,
        str(row["AISelect"]) if pd.notna(row["AISelect"]) else None,
        str(row["AISent"]) if pd.notna(row["AISent"]) else None,
        str(row["AIBen"]) if pd.notna(row["AIBen"]) else None,
        str(row["AIAcc"]) if pd.notna(row["AIAcc"]) else None,
        str(row["AIComplex"]) if pd.notna(row["AIComplex"]) else None,
        str(row["AIThreat"]) if pd.notna(row["AIThreat"]) else None,
        str(row["AIEthics"]) if pd.notna(row["AIEthics"]) else None,
        str(row["SurveyLength"]) if pd.notna(row["SurveyLength"]) else None,
        str(row["SurveyEase"]) if pd.notna(row["SurveyEase"]) else None,
    ))

    if pd.notna(row["Employment"]):
        for emp in str(row["Employment"]).split(";"):
            emp = emp.strip()
            if emp:
                employment_rows.append((rid, emp))

    if pd.notna(row["DevType"]):
        for dt in str(row["DevType"]).split(";"):
            dt = dt.strip()
            if dt:
                devtype_rows.append((rid, dt))

    if pd.notna(row["LearnCode"]):
        for lc in str(row["LearnCode"]).split(";"):
            lc = lc.strip()
            if lc:
                learncode_rows.append((rid, lc))

    if pd.notna(row["CodingActivities"]):
        for ca in str(row["CodingActivities"]).split(";"):
            ca = ca.strip()
            if ca:
                codingact_rows.append((rid, ca))

    # Populate per-category tech tables
    for cat_prefix, _ in TECH_CATEGORIES:
        for csv_var, var_suffix in VARIANTS:
            col = f"{cat_prefix}{csv_var}"
            val = row.get(col)
            if pd.notna(val):
                tbl = f"{cat_prefix}_{var_suffix}"
                for tech_item in str(val).split(";"):
                    tech_item = tech_item.strip()
                    if tech_item:
                        tech_rows[tbl].append((rid, tech_item))

    for col, aspect in ASPECT_MAP.items():
        val = row.get(col)
        if pd.notna(val):
            satpoint_rows.append((rid, aspect, float(val)))

    for k in range(1, 10):
        col = f"Knowledge_{k}"
        val = row.get(col)
        if pd.notna(val):
            val_str = str(val).strip()
            score = LIKERT_MAP.get(val_str, None)
            knowledge_rows.append((rid, col, val_str, score))

    if (idx + 1) % 2000 == 0:
        print(f"  Processed {idx+1}/{len(df)} rows...")

print(f"\nInserting {len(respondent_rows)} respondents...")
c.executemany("INSERT INTO respondents VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", respondent_rows)

print(f"Inserting {len(employment_rows)} employment rows...")
c.executemany("INSERT INTO respondent_employment (respondent_id, employment_type) VALUES (?,?)", employment_rows)

print(f"Inserting {len(devtype_rows)} devtype rows...")
c.executemany("INSERT INTO respondent_devtype (respondent_id, dev_type) VALUES (?,?)", devtype_rows)

print(f"Inserting {len(learncode_rows)} learncode rows...")
c.executemany("INSERT INTO respondent_learn_code (respondent_id, learning_source) VALUES (?,?)", learncode_rows)

print(f"Inserting {len(codingact_rows)} coding activity rows...")
c.executemany("INSERT INTO respondent_coding_activities (respondent_id, activity) VALUES (?,?)", codingact_rows)

for tbl, rows in tech_rows.items():
    if rows:
        print(f"  Inserting {len(rows)} rows into {tbl}...")
        c.executemany(f"INSERT INTO {tbl} (respondent_id, tech_name) VALUES (?,?)", rows)

print(f"Inserting {len(satpoint_rows)} satisfaction point rows...")
c.executemany("INSERT INTO job_satisfaction_points (respondent_id, aspect, score) VALUES (?,?,?)", satpoint_rows)

print(f"Inserting {len(knowledge_rows)} knowledge assessment rows...")
c.executemany("INSERT INTO knowledge_self_assessment (respondent_id, knowledge_area, response, score) VALUES (?,?,?,?)", knowledge_rows)

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

print("\nDatabase created successfully: survey_cleaned.sqlite")
print("Tables: respondents, 33 per-category tech tables (11 categories × 3 variants) + 6 junction tables")