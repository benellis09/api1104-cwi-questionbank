# API 1104 CWI Question Bank

API 1104–based Certified Welding Inspector (CWI) practice question bank (copyright-safe). Contains CSV batches Q001–Q800. Created by benellis09.

This repository contains Python scripts to generate and publish a portable question bank suitable for study tools, practice tests, or small APIs.

## Repository layout

```
.gitignore
README.md
csv/                      # generated batch CSVs: questions_batch_01.csv .. questions_batch_08.csv
scripts/
  generate_questions.py   # generates 8 batches of 100 questions each (800 total)
  csv_to_sqlite.py        # imports CSV batches into a single SQLite DB (data/questions.db)
app/
  main.py                 # FastAPI app to serve questions from the SQLite DB
```

## Quickstart

Prerequisites
- Python 3.8+

1. Clone the repository

```bash
git clone https://github.com/benellis09/api1104-cwi-questionbank.git
cd api1104-cwi-questionbank
```

2. (Optional) Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate   # on Windows: .venv\Scripts\activate
pip install --upgrade pip
```

3. Generate the CSV batches (if you want to re-generate)

> The repository already contains CSV batches in the `csv/` directory. Run this only if you want to regenerate them.

```bash
python3 scripts/generate_questions.py
```

4. Import CSV batches into a single SQLite DB

```bash
python3 scripts/csv_to_sqlite.py
```

This creates `data/questions.db` by default. Use `--csv-dir` and `--db` to change locations, and `--overwrite` to drop/recreate the questions table.

## Running the API (FastAPI)

Install FastAPI + Uvicorn

```bash
pip install fastapi uvicorn
```

Start the app

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API expects the SQLite DB at `data/questions.db` (the default path used by the importer and the app). If the DB is missing, the endpoints will return an error — run `scripts/csv_to_sqlite.py` first.

### Endpoints

- GET /questions/{id}
  - Returns a single question by its ID (e.g., `Q001`).
  - Example: `curl http://localhost:8000/questions/Q001`

- GET /questions?topic=...&limit=...&offset=...
  - Returns a list of questions. Filter by `topic` and paginate using `limit` and `offset`.
  - Example: `curl "http://localhost:8000/questions?topic=Metallurgy&limit=20"`

- GET /questions/random?n=10
  - Returns `n` random questions (default 10).
  - Example: `curl "http://localhost:8000/questions/random?n=5"`

### Response shape

The API returns JSON objects with the following fields (example):

```json
{
  "id": "Q001",
  "type": "MCQ",
  "topic": "Weld discontinuities",
  "difficulty": 2,
  "stem": "Which discontinuity is characterized by incomplete fusion between weld passes?",
  "choices": ["Slag inclusion","Lack of fusion","Porosity","Undercut"],
  "correct_answer": "B",
  "explanation": "Lack of fusion is ...",
  "tags": "",
  "source_reference": "API 1104 21st Edition",
  "created_by": "benellis09",
  "created_at": "2026-09-03",
  "reviewer": "",
  "reviewer_notes": ""
}
```

## Development suggestions / Next steps
- Add tests (pytest) and a GitHub Actions workflow for CI.
- Add a requirements.txt and a simple Dockerfile for containerized running.
- Add authentication / rate limiting for public deployments.

## License & credits
- Questions are generated programmatically by `scripts/generate_questions.py` and are intended to be copyright-safe practice material.
- Created by benellis09.
