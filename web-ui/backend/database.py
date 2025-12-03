import sqlite3
import os
from contextlib import contextmanager

# Absolute path to the SQLite database file
# (Phase 2/stock_exchange.db relative to this backend folder)
DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../Phase 2/stock_exchange.db")
)


def _ensure_db_exists():
    """
    Make sure the database file exists.
    If it doesn't, raise a clear error instead of a cryptic sqlite3 error.
    """
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            f"Database file not found at: {DB_PATH}\n"
            "Make sure you created stock_exchange.db using tables.sql + seed scripts."
        )


@contextmanager
def get_db_connection():
    """
    Context manager for database connections.

    - Opens connection to DB_PATH
    - Sets row_factory so we can access columns by name
    - Commits on success, rolls back on error
    """
    _ensure_db_exists()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def execute_query(query, params=None, fetch_one=False):
    """
    Execute a SQL query and return results.

    Args:
        query (str): SQL query string
        params (tuple or list): Query parameters (optional)
        fetch_one (bool): If True, return only a single row dict

    Returns:
        - For SELECT: list[dict] or dict (if fetch_one=True)
        - For INSERT/UPDATE/DELETE: dict with affected_rows and lastrowid
    """
    with get_db_connection() as conn:
        cur = conn.cursor()

        if params is not None:
            cur.execute(query, params)
        else:
            cur.execute(query)

        first_word = query.strip().split()[0].upper()

        if first_word == "SELECT":
            if fetch_one:
                row = cur.fetchone()
                return dict(row) if row else None
            else:
                rows = cur.fetchall()
                return [dict(r) for r in rows]
        else:
            return {
                "affected_rows": cur.rowcount,
                "lastrowid": cur.lastrowid,
            }


def generate_uuid():
    """
    Generate a UUID in the same format as lower(hex(randomblob(16))) in SQLite:
    a 32-character hex string without hyphens.
    """
    import uuid

    return uuid.uuid4().hex
