import sqlite3
import sys
import os

# Connect to database  
DB_PATH = os.path.join(os.path.dirname(__file__), '../../Phase 2/stock_exchange.db')
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    # Get demo user ID
    cursor.execute("SELECT user_id FROM User WHERE email = 'demo@stockex.com'")
    demo_user = cursor.fetchone()
    if not demo_user:
        print("Demo user not found!")
        sys.exit(1)
    demo_user_id = demo_user[0]
    print(f"Demo user ID: {demo_user_id}")
    
    # Create accounts for demo user
    import uuid
    
    # Account 1: Trading Account
    account1_id = uuid.uuid4().hex
    cursor.execute("""
        INSERT INTO Account (account_id, user_id, name, cash_balance, status)
        VALUES (?, ?, 'Trading Account', 50000.00, 'ACTIVE')
    """, (account1_id, demo_user_id))
    print(f"Created Trading Account: {account1_id}")
    
    # Account 2: Savings Account
    account2_id = uuid.uuid4().hex
    cursor.execute("""
        INSERT INTO Account (account_id, user_id, name, cash_balance, status)
        VALUES (?, ?, 'Savings Account', 25000.00, 'ACTIVE')
    """, (account2_id, demo_user_id))
    print(f"Created Savings Account: {account2_id}")
    
    # Check if securities exist, if not create some
    cursor.execute("SELECT COUNT(*) FROM Security")
    sec_count = cursor.fetchone()[0]
    
    if sec_count == 0:
        print("Creating securities...")
        securities = [
            ('AAPL', 'Apple Inc.', 'Technology', 'NASDAQ'),
            ('GOOGL', 'Alphabet Inc.', 'Technology', 'NASDAQ'),
            ('MSFT', 'Microsoft Corporation', 'Technology', 'NASDAQ'),
            ('TSLA', 'Tesla Inc.', 'Automotive', 'NASDAQ'),
            ('AMZN', 'Amazon.com Inc.', 'E-commerce', 'NASDAQ'),
        ]
        
        for ticker, name, sector, exchange in securities:
            sec_id = uuid.uuid4().hex
            cursor.execute("""
                INSERT INTO Security (security_id, ticker, name, sector, exchange)
                VALUES (?, ?, ?, ?, ?)
            """, (sec_id, ticker, name, sector, exchange))
            print(f"Created security: {ticker}")
    
    # Get some security IDs for holdings
    cursor.execute("SELECT security_id, ticker FROM Security LIMIT 3")
    securities = cursor.fetchall()
    
    # Create holdings for demo user
    holdings_data = [
        (securities[0][0], 100, 150.00),  # 100 shares at $150 avg cost
        (securities[1][0], 50, 2800.00),   # 50 shares at $2800 avg cost
        (securities[2][0], 75, 380.00),    # 75 shares at $380 avg cost
    ]
    
    for sec_id, qty, avg_cost in holdings_data:
        holding_id = uuid.uuid4().hex
        cursor.execute("""
            INSERT INTO Holding (holding_id, account_id, security_id, quantity, avg_cost)
            VALUES (?, ?, ?, ?, ?)
        """, (holding_id, account1_id, sec_id, qty, avg_cost))
        cursor.execute("SELECT ticker FROM Security WHERE security_id = ?", (sec_id,))
        ticker = cursor.fetchone()[0]
        print(f"Created holding: {qty} shares of {ticker} @ ${avg_cost}")
    
    # Create some orders
    order_id1 = uuid.uuid4().hex
    cursor.execute("""
        INSERT INTO "Order" (order_id, account_id, security_id, side, type, quantity, status)
        VALUES (?, ?, ?, 'BUY', 'MARKET', 10, 'FILLED')
    """, (order_id1, account1_id, securities[0][0]))
    print("Created sample order")
    
    conn.commit()
    print("\n✅ Successfully created test data for demo user!")
    print(f"   - 2 accounts with ${50000 + 25000:,.2f} total cash")
    print(f"   - 3 stock holdings")
    print(f"   - 1 order")
    
except Exception as e:
    conn.rollback()
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    conn.close()
