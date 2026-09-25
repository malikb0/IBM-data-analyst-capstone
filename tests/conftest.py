"""Shared pytest fixtures / path setup.

Ensures `src/` is importable so tests can `import build_database` without
installing the project.
"""

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(REPO_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

SAMPLE_CSV = os.path.join(REPO_ROOT, "data", "sample", "so_survey_sample.csv")
