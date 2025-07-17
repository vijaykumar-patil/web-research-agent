# history.py
import sqlite3
from datetime import datetime

DB_FILE = "qa_history.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS qa_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            question TEXT,
            answer TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_qa(question: str, answer: str):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO qa_history (timestamp, question, answer)
        VALUES (?, ?, ?)
    ''', (datetime.now().isoformat(timespec='seconds'), question, answer))
    conn.commit()
    conn.close()

def get_all_history():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT timestamp, question, answer FROM qa_history ORDER BY id DESC')
    rows = c.fetchall()
    conn.close()
    return rows
