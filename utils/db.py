import sqlite3
from pathlib import Path
from typing import List

DB_PATH = Path("db") / "app.db"

def init_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chunk_index INTEGER,
        question TEXT
    )""")
    c.execute("""
    CREATE TABLE IF NOT EXISTS answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_id INTEGER,
        answer TEXT,
        score INTEGER,
        feedback TEXT,
        FOREIGN KEY(question_id) REFERENCES questions(id)
    )""")
    conn.commit()
    conn.close()

def save_questions(chunk_index: int, questions: List[str]) -> List[int]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    ids: List[int] = []
    for q in questions:
        c.execute(
            "INSERT INTO questions (chunk_index, question) VALUES (?, ?)",
            (chunk_index, q)
        )
        ids.append(c.lastrowid)
    conn.commit()
    conn.close()
    return ids

def save_answer(question_id: int, answer: str, score: int, feedback: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO answers (question_id, answer, score, feedback) VALUES (?, ?, ?, ?)",
        (question_id, answer, score, feedback)
    )
    conn.commit()
    conn.close()
