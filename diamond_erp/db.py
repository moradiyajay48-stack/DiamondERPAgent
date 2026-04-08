"""
Diamond ERP Database Helper
Thread-safe SQLite connection management with context managers.
"""

import sqlite3
from contextlib import contextmanager
from typing import Any

from diamond_erp.config import DB_PATH


@contextmanager
def get_connection():
    """Context manager for thread-safe SQLite connections."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def execute_query(sql: str, params: tuple = ()) -> int:
    """Execute a write query (INSERT/UPDATE/DELETE). Returns lastrowid."""
    with get_connection() as conn:
        cursor = conn.execute(sql, params)
        return cursor.lastrowid


def execute_read(sql: str, params: tuple = ()) -> list[dict[str, Any]]:
    """Execute a read query. Returns list of dicts."""
    with get_connection() as conn:
        cursor = conn.execute(sql, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def execute_read_one(sql: str, params: tuple = ()) -> dict[str, Any] | None:
    """Execute a read query. Returns single dict or None."""
    with get_connection() as conn:
        cursor = conn.execute(sql, params)
        row = cursor.fetchone()
        return dict(row) if row else None
