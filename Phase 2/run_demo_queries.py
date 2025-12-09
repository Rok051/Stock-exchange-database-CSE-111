import sqlite3
import os

# Connect to the database
DB_PATH = "stock_exchange.db"

if not os.path.exists(DB_PATH):
    print(f"Error: Could not find database at {DB_PATH}")
    exit(1)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

def run_query(label, sql, params=()):
    print(f"\n{'='*60}")
    print(f"QUERY: {label}")
    print(f"{'-'*60}")
    print(f"SQL: {sql.strip()}")
    print(f"{'-'*60}")
    
    try:
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        if not rows:
            print("(No results found)")
            return

        # Get column names
        col_names = [description[0] for description in cursor.description]
        
        # Calculate column widths
        widths = [len(c) for c in col_names]
        for row in rows:
            for i, val in enumerate(row):
                widths[i] = max(widths[i], len(str(val)))
        
        # Print Header
        header = " | ".join(f"{col_names[i]:<{widths[i]}}" for i in range(len(col_names)))
        print(header)
        print("-" * len(header))
        
        # Print Rows
        for row in rows:
            print(" | ".join(f"{str(val):<{widths[i]}}" for i, val in enumerate(row)))
            
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

# ==================================================
# DEMO QUERIES
# ==================================================

# 1. Simple Select
run_query("1. List Users (Simple SELECT)", 
    "SELECT user_id, full_name, email, role FROM User LIMIT 5;")

# 2. Join Query
run_query("2. Recent Orders (JOIN Users/Accounts/Securities)", 
    """
    SELECT a.name AS account, o.type, o.quantity, s.ticker, o.status, o.placed_at
    FROM "Order" o
    JOIN Account a ON o.account_id = a.account_id
    JOIN Security s ON o.security_id = s.security_id
    ORDER BY o.placed_at DESC
    LIMIT 5;
    """)

# 3. Aggregation
run_query("3. Most Traded Stocks (GROUP BY / ORDER BY)", 
    """
    SELECT s.ticker, COUNT(o.order_id) AS order_total
    FROM "Order" o
    JOIN Security s ON o.security_id = s.security_id
    GROUP BY s.ticker
    ORDER BY order_total DESC
    LIMIT 5;
    """)

# 4. Use Case
run_query("4. View User Portfolio (Complex Join)", 
    """
    SELECT a.name as account_name, s.ticker, h.quantity, h.avg_cost
    FROM Holding h
    JOIN Account a ON h.account_id = a.account_id
    JOIN Security s ON h.security_id = s.security_id
    ORDER BY h.quantity DESC
    LIMIT 5;
    """)

conn.close()
input("\nPress Enter to exit...")
