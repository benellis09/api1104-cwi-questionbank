#!/usr/bin/env python3
"""
csv_to_sqlite.py

Create a single SQLite database from the CSV batches in csv/

Usage:
  python3 scripts/csv_to_sqlite.py [--csv-dir csv] [--db data/questions.db] [--overwrite]

The script will:
 - create the destination directory for the DB (default: data/)
 - create a `questions` table (if not exists) with appropriate columns
 - read all files matching `questions_batch_*.csv` in the csv directory sorted by name
 - import rows, skipping duplicates by `id` (primary key)
 - report counts per file and a final summary

No external dependencies required (uses Python stdlib only).
"""

from __future__ import annotations
import argparse
import csv
import glob
import json
import os
import sqlite3
import sys
from typing import Dict, List, Optional, Tuple

SQL_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS questions (
    id TEXT PRIMARY KEY,
    type TEXT,
    topic TEXT,
    difficulty INTEGER,
    stem TEXT,
    choices TEXT, -- JSON string
    correct_answer TEXT,
    explanation TEXT,
    tags TEXT,
    source_reference TEXT,
    created_by TEXT,
    created_at TEXT,
    reviewer TEXT,
    reviewer_notes TEXT
);
"""

SQL_INSERT = """
INSERT OR IGNORE INTO questions (
    id, type, topic, difficulty, stem, choices, correct_answer, explanation, tags,
    source_reference, created_by, created_at, reviewer, reviewer_notes
) VALUES (
    :id, :type, :topic, :difficulty, :stem, :choices, :correct_answer, :explanation, :tags,
    :source_reference, :created_by, :created_at, :reviewer, :reviewer_notes
)
"""

DEFAULT_DB = os.path.join("data", "questions.db")
DEFAULT_CSV_DIR = "csv"


def find_csv_files(csv_dir: str) -> List[str]:
    pattern = os.path.join(csv_dir, "questions_batch_*.csv")
    files = sorted(glob.glob(pattern))
    return files


def ensure_parent_dir(path: str) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)


def connect_db(db_path: str) -> sqlite3.Connection:
    ensure_parent_dir(db_path)
    conn = sqlite3.connect(db_path)
    # pragmatic pragmas
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.row_factory = sqlite3.Row
    return conn


def create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SQL_CREATE_TABLE)


def parse_row(row: Dict[str, str]) -> Dict[str, Optional[str]]:
    # Normalize fields and types; assume CSV header matches expected column names
    out: Dict[str, Optional[str]] = {}
    out["id"] = row.get("id")
    out["type"] = row.get("type")
    out["topic"] = row.get("topic")

    difficulty = row.get("difficulty")
    if difficulty is None or difficulty == "":
        out["difficulty"] = None
    else:
        try:
            out["difficulty"] = int(difficulty)
        except ValueError:
            out["difficulty"] = None

    out["stem"] = row.get("stem")

    # choices column may contain JSON or a Python-like repr; try to keep as valid JSON string
    choices_raw = row.get("choices")
    if choices_raw:
        # if it already looks like JSON (starts with [), keep as-is
        choices = choices_raw
        # Try to ensure it is valid JSON: replace doubled single quotes etc.
        try:
            # If it's already valid JSON, load/dump to normalize spacing
            parsed = json.loads(choices_raw)
            choices = json.dumps(parsed, ensure_ascii=False)
        except Exception:
            # fallback: wrap as single-element list
            try:
                # attempt to eval-like parsing (safe-ish): replace single quotes with double
                guess = choices_raw.strip()
                if guess.startswith("[") and "'" in guess and '"' not in guess:
                    guess = guess.replace("'", '"')
                parsed = json.loads(guess)
                choices = json.dumps(parsed, ensure_ascii=False)
            except Exception:
                # last resort: store raw string
                choices = choices_raw
        out["choices"] = choices
    else:
        out["choices"] = json.dumps([])

    out["correct_answer"] = row.get("correct_answer")
    out["explanation"] = row.get("explanation")
    out["tags"] = row.get("tags")
    out["source_reference"] = row.get("source_reference")
    out["created_by"] = row.get("created_by")
    out["created_at"] = row.get("created_at")
    out["reviewer"] = row.get("reviewer")
    out["reviewer_notes"] = row.get("reviewer_notes")

    return out


def import_file(conn: sqlite3.Connection, csv_path: str) -> Tuple[int, int]:
    """Import a single CSV file into the DB.

    Returns (inserted, ignored)
    """
    inserted = 0
    ignored = 0
    with open(csv_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        to_insert = []
        for raw_row in reader:
            parsed = parse_row(raw_row)
            to_insert.append(parsed)

        cur = conn.cursor()
        cur.execute("BEGIN")
        try:
            for r in to_insert:
                cur.execute(SQL_INSERT, r)
                if cur.rowcount == 1:
                    inserted += 1
                else:
                    ignored += 1
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    return inserted, ignored


def import_all(csv_dir: str, db_path: str, overwrite: bool = False) -> None:
    files = find_csv_files(csv_dir)
    if not files:
        print(f"No files found in {csv_dir} matching questions_batch_*.csv", file=sys.stderr)
        return

    if os.path.exists(db_path) and overwrite:
        print(f"Overwriting existing DB at {db_path} (dropping questions table)")
        conn = connect_db(db_path)
        conn.execute("DROP TABLE IF EXISTS questions")
        create_schema(conn)
    else:
        conn = connect_db(db_path)
        create_schema(conn)

    total_inserted = 0
    total_ignored = 0
    for path in files:
        print(f"Importing {os.path.basename(path)}...", end=" ")
        inserted, ignored = import_file(conn, path)
        total_inserted += inserted
        total_ignored += ignored
        print(f"inserted={inserted} ignored={ignored}")

    conn.close()
    print("\nImport complete.")
    print(f"Total inserted: {total_inserted}")
    print(f"Total ignored (duplicates/skipped): {total_ignored}")
    print(f"DB file: {os.path.abspath(db_path)}")


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Import CSV question batches into a single SQLite DB")
    p.add_argument("--csv-dir", default=DEFAULT_CSV_DIR, help="Directory containing questions_batch_*.csv (default: csv)")
    p.add_argument("--db", default=DEFAULT_DB, help=f"Path to output SQLite DB (default: {DEFAULT_DB})")
    p.add_argument("--overwrite", action="store_true", help="If set, drop existing questions table and re-import")
    return p.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    print("csv_to_sqlite.py — import CSV batches into SQLite")
    print(f"CSV dir: {args.csv_dir}")
    print(f"DB path: {args.db}")
    print(f"Overwrite: {args.overwrite}")

    try:
        import_all(args.csv_dir, args.db, overwrite=args.overwrite)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
