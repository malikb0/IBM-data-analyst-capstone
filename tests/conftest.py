"""Shared pytest fixtures / path setup.

Ensures the repository root is importable so tests can `import build_database`
without installing the project.
"""

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

SAMPLE_CSV = os.path.join(REPO_ROOT, "data", "sample", "so_survey_sample.csv")
