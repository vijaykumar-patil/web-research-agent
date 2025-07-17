# history.py
import sqlite3
from datetime import datetime
from typing import Optional, List, Tuple

DB_FILE = "qa_history.db"

def _table_has_user_id(cur) -> bool:
    cur.execute("PRAGMA table_info(qa_history)")
    cols = [row[1] for row in cur.fetchall()]
    return "user_id" in cols

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS qa_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            user_id TEXT,
            question TEXT,
            answer TEXT
        )
    """)
    conn.commit()
    conn.close()

def log_qa(question: str, answer: str, user_id: Optional[str] = None):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    if not _table_has_user_id(cur):
        cur.execute("ALTER TABLE qa_history ADD COLUMN user_id TEXT")
    cur.execute(
        "INSERT INTO qa_history (timestamp, user_id, question, answer) VALUES (?, ?, ?, ?)",
        (datetime.now().isoformat(timespec="seconds"), user_id, question, answer)
    )
    conn.commit()
    conn.close()

def get_all_history(user_id: Optional[str] = None, limit: Optional[int] = None) -> List[Tuple[str, str, str, str]]:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    base = "SELECT timestamp, user_id, question, answer FROM qa_history"
    params = []

    if user_id:
        base += " WHERE user_id = ?"
        params.append(user_id)

    base += " ORDER BY id DESC"
    if limit:
        base += f" LIMIT {int(limit)}"

    if params:
        cur.execute(base, params)
    else:
        cur.execute(base)

    rows = cur.fetchall()
    conn.close()
    return rows
