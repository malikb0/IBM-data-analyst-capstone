"""End-to-end determinism test for the report generator.

Builds a database from the small committed sample, then runs
`generate_report.py` twice and asserts every output byte is identical.
"""

import hashlib
import os
import subprocess
import sys

import pytest

import build_database as bd
from conftest import REPO_ROOT, SAMPLE_CSV

pytest.importorskip("matplotlib")


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def test_report_is_idempotent(tmp_path):
    if not os.path.exists(SAMPLE_CSV):
        pytest.skip("committed sample not present")

    db_path = tmp_path / "sample.sqlite"
    bd.build(SAMPLE_CSV, str(db_path), verbose=False)

    out_dir = tmp_path / "out"
    script = os.path.join(REPO_ROOT, "src", "generate_report.py")

    def run_once():
        result = subprocess.run(
            [sys.executable, script, "--db", str(db_path), "--output-dir", str(out_dir)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
        files = sorted(p for p in out_dir.rglob("*") if p.is_file())
        assert files, "report generator produced no output"
        return {str(p.relative_to(out_dir)): _sha256(p) for p in files}

    first = run_once()
    second = run_once()
    assert first == second, "generate_report.py is not idempotent"

    report = out_dir / "analysis_report.md"
    assert report.exists()
    text = report.read_text(encoding="utf-8")
    assert "Generated artifact" in text
    assert "Stack Overflow" in text
