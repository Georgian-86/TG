import sqlite3
from datetime import datetime

DB_PATH = "data/usage.db"

def init_usage_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        topic TEXT,
        level TEXT,
        duration INTEGER,
        quiz_enabled INTEGER,
        ppt INTEGER,
        pdf INTEGER,
        timestamp TEXT
    )
    """)
    conn.commit()
    conn.close()

def log_usage(email, state):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO usage 
        (email, topic, level, duration, quiz_enabled, ppt, pdf, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        email,
        state.get("topic"),
        state.get("level"),
        state.get("duration"),
        int(state.get("include_quiz", False)),
        int("ppt_path" in state),
        int("pdf_path" in state),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()

def get_user_history(email):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT topic, level, duration, quiz_enabled, ppt, pdf, timestamp
        FROM usage WHERE email=? ORDER BY id DESC
    """, (email,))
    rows = c.fetchall()
    conn.close()
    return rows
