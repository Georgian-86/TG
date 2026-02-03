import sqlite3
import bcrypt

DB_PATH = "data/users.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password_hash BLOB
    )
    """)
    conn.commit()
    conn.close()

def create_user(email, password):
    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO users (email, password_hash) VALUES (?, ?)",
            (email, pw_hash)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(email, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT password_hash FROM users WHERE email=?", (email,))
    row = c.fetchone()
    conn.close()

    if not row:
        return False

    return bcrypt.checkpw(password.encode(), row[0])
