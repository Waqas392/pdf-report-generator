"""Database helpers: one SQLite file, two tables (orders + reports)."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "report.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS orders (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    customer   TEXT NOT NULL,
    product    TEXT NOT NULL,
    amount     REAL NOT NULL,
    created_at TEXT NOT NULL            -- YYYY-MM-DD
);
CREATE TABLE IF NOT EXISTS reports (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    path       TEXT,
    created_at TEXT NOT NULL            -- local ISO timestamp
);
"""


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn
