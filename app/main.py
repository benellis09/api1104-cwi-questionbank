from __future__ import annotations
import json
import os
import sqlite3
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

DB_PATH_DEFAULT = os.path.join("data", "questions.db")

app = FastAPI(title="API 1104 CWI Question Bank")


class Question(BaseModel):
    id: str
    type: Optional[str]
    topic: Optional[str]
    difficulty: Optional[int]
    stem: Optional[str]
    choices: Optional[List[str]]
    correct_answer: Optional[str]
    explanation: Optional[str]
    tags: Optional[str]
    source_reference: Optional[str]
    created_by: Optional[str]
    created_at: Optional[str]
    reviewer: Optional[str]
    reviewer_notes: Optional[str]


def get_db_connection(db_path: str = DB_PATH_DEFAULT) -> sqlite3.Connection:
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"DB file not found: {db_path}. Run scripts/csv_to_sqlite.py first.")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def row_to_question(row: sqlite3.Row) -> Question:
    # Parse choices JSON if possible
    choices_raw = row.get("choices")
    choices = None
    if choices_raw:
        try:
            parsed = json.loads(choices_raw)
            # ensure list of strings
            if isinstance(parsed, list):
                choices = [str(x) for x in parsed]
            else:
                choices = [str(parsed)]
        except Exception:
            # fallback: return raw string in a single-element list
            choices = [choices_raw]

    return Question(
        id=row.get("id"),
        type=row.get("type"),
        topic=row.get("topic"),
        difficulty=row.get("difficulty"),
        stem=row.get("stem"),
        choices=choices,
        correct_answer=row.get("correct_answer"),
        explanation=row.get("explanation"),
        tags=row.get("tags"),
        source_reference=row.get("source_reference"),
        created_by=row.get("created_by"),
        created_at=row.get("created_at"),
        reviewer=row.get("reviewer"),
        reviewer_notes=row.get("reviewer_notes"),
    )


@app.get("/questions/{question_id}", response_model=Question)
def get_question(question_id: str, db_path: str = DB_PATH_DEFAULT):
    """Get a single question by ID (e.g., Q001)"""
    conn = get_db_connection(db_path)
    cur = conn.execute("SELECT * FROM questions WHERE id = ?", (question_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Question not found")
    return row_to_question(row)


@app.get("/questions", response_model=List[Question])
def list_questions(
    topic: Optional[str] = Query(None, description="Filter by topic"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum number of results to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db_path: str = DB_PATH_DEFAULT,
):
    """List questions, optionally filtered by topic. Pagination via limit & offset."""
    conn = get_db_connection(db_path)
    params = []
    sql = "SELECT * FROM questions"
    if topic:
        sql += " WHERE topic = ?"
        params.append(topic)
    sql += " ORDER BY id LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cur = conn.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return [row_to_question(r) for r in rows]


@app.get("/questions/random", response_model=List[Question])
def random_questions(n: int = Query(10, ge=1, le=100, description="Number of random questions"), db_path: str = DB_PATH_DEFAULT):
    """Return n random questions."""
    conn = get_db_connection(db_path)
    cur = conn.execute("SELECT * FROM questions ORDER BY RANDOM() LIMIT ?", (n,))
    rows = cur.fetchall()
    conn.close()
    return [row_to_question(r) for r in rows]
