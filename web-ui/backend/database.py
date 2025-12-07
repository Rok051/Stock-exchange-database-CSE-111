import sqlite3
import os
from contextlib import contextmanager

# Absolute path to the SQLite database file
# (Phase 2/stock_exchange.db relative to this backend folder)
DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../Phase 2/stock_exchange.db")
)


def _ensure_db_exists():
    # Make sure the database file actually exists
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            f"Database file not found at: {DB_PATH}\n"
            "Make sure you created stock_exchange.db using tables.sql + seed scripts."
        )


@contextmanager
def get_db_connection():
    # Opens a connection to the database
    # Commits on success, rolls back if there's an error
    _ensure_db_exists()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def execute_query(query, params=None, fetch_one=False):
    # Run a SQL query and return the results
    # For SELECT: returns list of dicts (or single dict if fetch_one=True)
    # For INSERT/UPDATE/DELETE: returns affected rows + lastrowid
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
    # Generate a UUID the same way SQLite does it (32-char hex, no hyphens)
    import uuid

    return uuid.uuid4().hex
