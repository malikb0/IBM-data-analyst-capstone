"""Integration tests for build_database.build on a tiny synthetic survey.

These do NOT touch the 150 MB survey files: a minimal in-memory CSV with the
columns the pipeline actually reads is written to a tmp path.
"""

import sqlite3

import pandas as pd
import pytest

import build_database as bd


def _required_columns():
    cols = {
        "ResponseId",
        "MainBranch",
        "Age",
        "Employment",
        "RemoteWork",
        "CodingActivities",
        "EdLevel",
        "LearnCode",
        "YearsCode",
        "YearsCodePro",
        "DevType",
        "OrgSize",
        "Country",
        "WorkExp",
        "JobSat",
        "ICorPM",
        "TBranch",
        "Industry",
        "OpSysPersonal use",
        "OpSysProfessional use",
        "SOVisitFreq",
        "SOAccount",
        "SOPartFreq",
        "SOComm",
        "AISelect",
        "AISent",
        "AIBen",
        "AIAcc",
        "AIComplex",
        "AIThreat",
        "AIEthics",
        "SurveyLength",
        "SurveyEase",
        "ConvertedCompYearly",
    }
    cols |= {f"{cat}{csv_var}" for cat in bd.TECH_CATEGORIES for csv_var, _ in bd.VARIANTS}
    cols |= set(bd.ASPECT_MAP)
    cols |= {f"Knowledge_{k}" for k in range(1, 10)}
    return sorted(cols)


def _write_csv(path, rows):
    cols = _required_columns()
    df = pd.DataFrame(rows, columns=cols)
    df.to_csv(path, index=False)


def _base_row(rid, **overrides):
    row = {c: None for c in _required_columns()}
    row["ResponseId"] = rid
    row.update(overrides)
    return row


def test_build_deduplicates_participant_value_rows(tmp_path):
    csv_path = tmp_path / "mini.csv"
    db_path = tmp_path / "mini.sqlite"
    _write_csv(
        csv_path,
        [
            _base_row(
                1,
                Age="25-34 years old",
                LanguageHaveWorkedWith="Python;Python;SQL",
                Employment="Employed, full-time;Employed, full-time",
                Knowledge_1="Agree",
            )
        ],
    )

    counts = bd.build(str(csv_path), str(db_path), verbose=False)
    assert counts["respondents"] == 1

    conn = sqlite3.connect(db_path)
    langs = conn.execute(
        "SELECT tech_name, COUNT(*) FROM Language_have WHERE respondent_id=1 GROUP BY tech_name"
    ).fetchall()
    assert sorted(langs) == [("Python", 1), ("SQL", 1)]

    emp = conn.execute(
        "SELECT COUNT(*) FROM respondent_employment WHERE respondent_id=1"
    ).fetchone()[0]
    assert emp == 1

    # No duplicate (respondent, value) anywhere.
    for cat in bd.TECH_CATEGORIES:
        for _, var in bd.VARIANTS:
            dups = conn.execute(
                f"SELECT COUNT(*) FROM (SELECT respondent_id, tech_name, COUNT(*) c "
                f"FROM {cat}_{var} GROUP BY 1,2 HAVING c>1)"
            ).fetchone()[0]
            assert dups == 0
    conn.close()


def test_compensation_cap_applied_once(tmp_path):
    csv_path = tmp_path / "comp.csv"
    db_path = tmp_path / "comp.sqlite"
    rows = [_base_row(i + 1, ConvertedCompYearly=1000 * (i + 1)) for i in range(100)]
    rows.append(_base_row(999, ConvertedCompYearly=10_000_000))
    _write_csv(csv_path, rows)

    bd.build(str(csv_path), str(db_path), verbose=False)

    conn = sqlite3.connect(db_path)
    max_clean = conn.execute("SELECT MAX(converted_comp_yearly) FROM respondents").fetchone()[0]
    null_comp = conn.execute(
        "SELECT COUNT(*) FROM respondents WHERE converted_comp_yearly IS NULL"
    ).fetchone()[0]
    conn.close()

    q99 = pd.Series([1000 * (i + 1) for i in range(100)] + [10_000_000]).quantile(0.99)
    assert max_clean == pytest.approx(q99)
    assert max_clean < 10_000_000
    assert null_comp == 0


def test_nan_compensation_preserved_as_null(tmp_path):
    csv_path = tmp_path / "nan.csv"
    db_path = tmp_path / "nan.sqlite"
    _write_csv(
        csv_path,
        [
            _base_row(1, ConvertedCompYearly=50000),
            _base_row(2, ConvertedCompYearly=None),
        ],
    )
    bd.build(str(csv_path), str(db_path), verbose=False)
    conn = sqlite3.connect(db_path)
    null_comp = conn.execute(
        "SELECT COUNT(*) FROM respondents WHERE converted_comp_yearly IS NULL"
    ).fetchone()[0]
    conn.close()
    assert null_comp == 1


def test_unmapped_likert_stored_with_null_score(tmp_path):
    csv_path = tmp_path / "likert.csv"
    db_path = tmp_path / "likert.sqlite"
    _write_csv(
        csv_path,
        [
            _base_row(1, Knowledge_1="Agree"),
            _base_row(2, Knowledge_1="Totally agree"),
        ],
    )
    bd.build(str(csv_path), str(db_path), verbose=False)
    conn = sqlite3.connect(db_path)
    rows = dict(
        conn.execute(
            "SELECT response, score FROM knowledge_self_assessment WHERE knowledge_area='Knowledge_1'"
        ).fetchall()
    )
    conn.close()
    assert rows["Agree"] == 4
    assert rows["Totally agree"] is None


def test_build_is_idempotent(tmp_path):
    csv_path = tmp_path / "idem.csv"
    db_path = tmp_path / "idem.sqlite"
    _write_csv(csv_path, [_base_row(1, Country="Germany")])
    first = bd.build(str(csv_path), str(db_path), verbose=False)
    # Running again over an existing output must not raise.
    second = bd.build(str(csv_path), str(db_path), verbose=False)
    assert first == second
