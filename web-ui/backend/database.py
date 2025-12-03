import sqlite3
import os
from contextlib import contextmanager

# Path to the database file
DB_PATH = os.path.join(os.path.dirname(__file__), '../../Phase 2/stock_exchange.db')

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name
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
    Execute a SQL query and return results
    
    Args:
        query: SQL query string
        params: Query parameters (optional)
        fetch_one: If True, return only first row
        
    Returns:
        List of dictionaries or single dictionary if fetch_one=True
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if query.strip().upper().startswith('SELECT'):
            if fetch_one:
                row = cursor.fetchone()
                return dict(row) if row else None
            else:
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        else:
            # For INSERT/UPDATE/DELETE, return affected rows
            return {'affected_rows': cursor.rowcount, 'lastrowid': cursor.lastrowid}

def generate_uuid():
    """Generate a UUID in SQLite format (32-character hex string without hyphens)"""
    import uuid
    # Generate UUID and remove hyphens to match SQLite's lower(hex(randomblob(16))) format
    return uuid.uuid4().hex
