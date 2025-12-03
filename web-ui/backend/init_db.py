import sqlite3
import os

# Connect to database
DB_PATH = os.path.join(os.path.dirname(__file__), '../../Phase 2/stock_exchange.db')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), '../../Phase 2/tables.sql')

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print(f"Removed old database: {DB_PATH}")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

with open(SCHEMA_PATH, 'r') as f:
    schema = f.read()
    cursor.executescript(schema)

print("Database initialized successfully from tables.sql")
conn.close()
