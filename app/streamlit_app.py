"""Streamlit app for API 1104 CWI Question Bank

Run:
  pip install -r requirements.txt
  python3 scripts/csv_to_sqlite.py  # if data/questions.db not present
  streamlit run app/streamlit_app.py

Authentication:
- The app checks environment variable STREAMLIT_PASSWORD. If not set, it falls back to the default password "changeme" (not secure).
- Set STREAMLIT_PASSWORD before running to secure the app: export STREAMLIT_PASSWORD=yourpassword

Features:
- Simple password login
- Browse questions by topic, search by text
- View individual questions and check answers
- Start a random quiz (n questions) with scoring
- Export selected questions to CSV/JSONL
"""
from __future__ import annotations
import json
import os
import random
import sqlite3
from typing import List, Optional

import pandas as pd
import streamlit as st

DB_PATH = os.path.join("data", "questions.db")
DEFAULT_PASSWORD = os.getenv("STREAMLIT_PASSWORD", "changeme")

st.set_page_config(page_title="API1104 CWI Question Bank", layout="wide")

# --- Utilities ---
@st.cache_data
def load_questions_from_db(db_path: str = DB_PATH) -> pd.DataFrame:
    if not os.path.exists(db_path):
        return pd.DataFrame()
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM questions ORDER BY id", conn)
    conn.close()
    # normalize choices column to lists
    def parse_choices(x):
        if not x:
            return []
        if isinstance(x, list):
            return x
        try:
            parsed = json.loads(x)
            if isinstance(parsed, list):
                return parsed
            return [str(parsed)]
        except Exception:
            return [str(x)]

    if "choices" in df.columns:
        df["choices_parsed"] = df["choices"].apply(parse_choices)
    else:
        df["choices_parsed"] = [[] for _ in range(len(df))]
    return df


def get_topics(df: pd.DataFrame) -> List[str]:
    if df.empty:
        return []
    topics = df["topic"].fillna("").unique().tolist()
    topics = [t for t in topics if t]
    topics.sort()
    return topics


def get_question_by_id(df: pd.DataFrame, qid: str) -> Optional[dict]:
    if df.empty:
        return None
    row = df[df["id"] == qid]
    if row.empty:
        return None
    r = row.iloc[0].to_dict()
    r["choices_parsed"] = r.get("choices_parsed", [])
    return r


def get_random_questions(df: pd.DataFrame, n: int) -> List[dict]:
    if df.empty:
        return []
    sampled = df.sample(n=min(n, len(df))).to_dict(orient="records")
    for s in sampled:
        s["choices_parsed"] = s.get("choices_parsed", [])
    return sampled


# --- Authentication ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

with st.sidebar:
    st.title("API1104 CWI — Login")
    if not st.session_state.authenticated:
        pwd = st.text_input("Password", type="password")
        if st.button("Login"):
            if pwd == DEFAULT_PASSWORD:
                st.session_state.authenticated = True
                st.experimental_rerun()
            else:
                st.error("Incorrect password")
        if DEFAULT_PASSWORD == "changeme":
            st.warning("Using default password 'changeme'. Set STREAMLIT_PASSWORD env var to secure the app.")
    else:
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.experimental_rerun()

# Halt if not authenticated
if not st.session_state.authenticated:
    st.write("\nPlease log in to continue.")
    st.stop()

# --- Load data ---
df = load_questions_from_db()
if df.empty:
    st.error(f"No DB found at {DB_PATH} or DB contains no questions. Run scripts/csv_to_sqlite.py to create the DB.")

# Layout: sidebar controls and main area
with st.sidebar:
    st.header("Controls")
    st.markdown(f"**DB:** {DB_PATH}")
    total = len(df)
    st.markdown(f"**Questions:** {total}")
    topics = get_topics(df)
    topic_filter = st.multiselect("Filter by topic", options=["All"] + topics, default=["All"])
    search_text = st.text_input("Search in stem/tags", value="")
    difficulty_filter = st.selectbox("Difficulty", options=["Any", 1, 2, 3], index=0)

    st.markdown("---")
    st.header("Quiz")
    quiz_size = st.number_input("Quiz size", min_value=1, max_value=100, value=10)
    if st.button("Start Random Quiz"):
        st.session_state.quiz = get_random_questions(df, quiz_size)
        st.session_state.quiz_index = 0
        st.session_state.quiz_score = 0
        st.experimental_rerun()

    if st.button("Reload DB"):
        load_questions_from_db.clear()
        st.experimental_rerun()

    st.markdown("---")
    st.header("Export")
    if st.button("Export visible to CSV"):
        # prepare filtered df
        filtered = df.copy()
        if "All" not in topic_filter:
            filtered = filtered[filtered["topic"].isin(topic_filter)]
        if search_text:
            filtered = filtered[filtered["stem"].str.contains(search_text, case=False, na=False) | filtered.get("tags", "").str.contains(search_text, case=False, na=False)]
        st.download_button("Download CSV", filtered.to_csv(index=False), file_name="questions_export.csv", mime="text/csv")

# --- Main ---
st.title("API1104 CWI Question Bank")

# Show topics summary
col1, col2 = st.columns([1, 3])
with col1:
    st.subheader("Topics")
    if topics:
        for t in topics:
            count = int((df["topic"] == t).sum())
            st.write(f"- {t} ({count})")
    else:
        st.write("(no topics)")

with col2:
    st.subheader("Browse Questions")
    # filter df based on sidebar controls
    filtered = df.copy()
    if "All" not in topic_filter and topic_filter:
        filtered = filtered[filtered["topic"].isin(topic_filter)]
    if difficulty_filter != "Any":
        filtered = filtered[filtered["difficulty"] == difficulty_filter]
    if search_text:
        filtered = filtered[filtered["stem"].str.contains(search_text, case=False, na=False) | filtered["tags"].fillna("").str.contains(search_text, case=False, na=False)]

    st.write(f"Showing {len(filtered)} questions")

    # selection UI
    qids = filtered["id"].tolist()
    selected_id = st.selectbox("Select question ID", options=[""] + qids, index=0)

    if selected_id:
        q = get_question_by_id(df, selected_id)
        if q:
            st.markdown(f"### {q['id']}: {q.get('topic','')} (difficulty: {q.get('difficulty')})")
            st.write(q.get("stem"))
            choices = q.get("choices_parsed") or []
            if choices:
                choice = st.radio("Choices", choices, key=f"choice_{q['id']}")
                if st.button("Check Answer", key=f"check_{q['id']}"):
                    correct = q.get("correct_answer")
                    is_correct = False
                    # handle letter answers
                    if isinstance(correct, str) and len(correct) == 1 and correct.upper() in "ABCDE":
                        idx = ord(correct.upper()) - ord("A")
                        try:
                            is_correct = (choices[idx] == choice)
                        except Exception:
                            is_correct = False
                    else:
                        # compare normalized text
                        is_correct = (str(correct).strip().lower() == str(choice).strip().lower())

                    if is_correct:
                        st.success("Correct!")
                    else:
                        st.error("Incorrect")
                    st.info(f"Answer: {correct}")
                    if q.get("explanation"):
                        st.write("**Explanation:**")
                        st.write(q.get("explanation"))
            else:
                st.write("(no choices available)")
                if st.button("Show answer"):
                    st.info(f"Answer: {q.get('correct_answer')}")
                    if q.get("explanation"):
                        st.write(q.get("explanation"))

# --- Quiz mode ---
if st.session_state.get("quiz"):
    st.markdown("---")
    st.header("Quiz")
    quiz = st.session_state.quiz
    idx = st.session_state.get("quiz_index", 0)
    score = st.session_state.get("quiz_score", 0)

    if idx >= len(quiz):
        st.success(f"Quiz complete — Score: {score} / {len(quiz)}")
        if st.button("Retake"):
            st.session_state.pop("quiz")
            st.experimental_rerun()
    else:
        current = quiz[idx]
        st.subheader(f"Question {idx+1} / {len(quiz)}: {current.get('id')}")
        st.write(current.get("stem"))
        choices = current.get("choices_parsed", [])
        if choices:
            choice_key = f"quiz_choice_{idx}"
            selected = st.radio("Choices", choices, key=choice_key)
            if st.button("Submit", key=f"submit_{idx}"):
                correct = current.get("correct_answer")
                is_correct = False
                if isinstance(correct, str) and len(correct) == 1 and correct.upper() in "ABCDE":
                    ci = ord(correct.upper()) - ord("A")
                    try:
                        is_correct = (choices[ci] == selected)
                    except Exception:
                        is_correct = False
                else:
                    is_correct = (str(correct).strip().lower() == str(selected).strip().lower())

                if is_correct:
                    st.success("Correct!")
                    st.session_state.quiz_score = st.session_state.get("quiz_score", 0) + 1
                else:
                    st.error("Incorrect")
                    st.info(f"Answer: {correct}")
                if current.get("explanation"):
                    st.write("**Explanation:**")
                    st.write(current.get("explanation"))
                # advance
                st.session_state.quiz_index = st.session_state.get("quiz_index", 0) + 1
                st.experimental_rerun()
        else:
            st.write("(no choices)")
            if st.button("Show answer and next"):
                st.session_state.quiz_index = st.session_state.get("quiz_index", 0) + 1
                st.experimental_rerun()

# Footer
st.markdown("---")
st.caption("Built with Streamlit — data from csv/questions_batch_01.csv .. 08.csv")
