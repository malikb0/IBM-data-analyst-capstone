#!/usr/bin/env python3
"""query.py — run a read-only SQL query against the survey SQLite database.

Usage:
    python scripts/query.py "SELECT COUNT(*) FROM respondents"
    python scripts/query.py --db demo.sqlite "SELECT name FROM sqlite_master WHERE type='table'"
    python scripts/query.py --list-tables
    python scripts/query.py --schema respondents

Safety: only read-only statements (`SELECT`, `WITH`, `PRAGMA` that returns rows) are
allowed. Anything else is rejected before execution.
"""

from __future__ import annotations

import argparse
import os
import re
import sqlite3
import sys

DEFAULT_DB = os.environ.get("SURVEY_DB", "survey_cleaned.sqlite")
_READ_ONLY = re.compile(r"^\s*(SELECT|WITH|PRAGMA|EXPLAIN)\b", re.IGNORECASE)


def _fmt(value):
    if value is None:
        return "NULL"
    if isinstance(value, float):
        return f"{value:,.2f}"
    if isinstance(value, int):
        return f"{value:,}"
    return str(value)


def run(db_path: str, sql: str) -> int:
    if not _READ_ONLY.match(sql):
        print("refused: only read-only SELECT/WITH/PRAGMA/EXPLAIN statements are allowed", file=sys.stderr)
        return 2
    if not os.path.exists(db_path):
        print(f"database not found: {db_path}", file=sys.stderr)
        return 2

    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        cursor = conn.execute(sql)
        if cursor.description is None:
            print("(no rows returned)")
            return 0
        headers = [d[0] for d in cursor.description]
        rows = cursor.fetchall()
        widths = [
            max(len(str(h)), *(len(_fmt(r[i])) for r in rows)) if rows else len(str(h))
            for i, h in enumerate(headers)
        ]
        print(" | ".join(str(h).ljust(widths[i]) for i, h in enumerate(headers)))
        print("-+-".join("-" * w for w in widths))
        for row in rows:
            print(" | ".join(_fmt(v).ljust(widths[i]) for i, v in enumerate(row)))
        print(f"\n({len(rows)} row{'s' if len(rows) != 1 else ''})")
    finally:
        conn.close()
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("sql", nargs="?", help="read-only SQL statement")
    parser.add_argument("--db", default=DEFAULT_DB, help="SQLite database (default: %(default)s)")
    parser.add_argument("--list-tables", action="store_true", help="list tables and exit")
    parser.add_argument("--schema", metavar="TABLE", help="print the schema for a table")
    args = parser.parse_args(argv)

    if args.list_tables:
        return run(
            args.db,
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name NOT LIKE 'sqlite_%' ORDER BY name",
        )
    if args.schema:
        return run(args.db, f"PRAGMA table_info({args.schema})")
    if not args.sql:
        parser.error("provide a SQL statement, or use --list-tables / --schema")
    return run(args.db, args.sql)


if __name__ == "__main__":
    raise SystemExit(main())
