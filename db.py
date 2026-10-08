import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            favourite_moment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def email_exists(email):
    conn = get_connection()
    row = conn.execute(
        "SELECT 1 FROM subscribers WHERE email = ?", (email,)
    ).fetchone()
    conn.close()
    return row is not None


def add_subscriber(name, email, moment):
    conn = get_connection()
    conn.execute(
        "INSERT INTO subscribers (name, email, favourite_moment) VALUES (?, ?, ?)",
        (name, email, moment),
    )
    conn.commit()
    conn.close()


def count_subscribers():
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM subscribers").fetchone()[0]
    conn.close()
    return total


def get_all_subscribers():
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, name, email, favourite_moment, created_at "
        "FROM subscribers ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]