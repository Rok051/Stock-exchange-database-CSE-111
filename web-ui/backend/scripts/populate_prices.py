#!/usr/bin/env python3
"""
Populate DailyPrice table with sample price data for all securities.
This allows MARKET orders to be filled.
"""

import sys
sys.path.insert(0, '.')
from database import execute_query, generate_uuid
from datetime import datetime, timedelta
import random

def populate_daily_prices():
    print("Populating DailyPrice table with sample data...")
    
    # Get all securities
    securities = execute_query('SELECT security_id, ticker FROM Security ORDER BY ticker')
    print(f"Found {len(securities)} securities")
    
    # Check which ones already have price data
    existing_prices = execute_query('SELECT DISTINCT security_id FROM DailyPrice')
    existing_ids = {p['security_id'] for p in existing_prices}
    
    securities_to_populate = [s for s in securities if s['security_id'] not in existing_ids]
    print(f"{len(securities_to_populate)} securities need price data")
    
    if not securities_to_populate:
        print("All securities already have price data!")
        return
    
    # Generate price data for the last 30 days
    today = datetime.now().date()
    date_range = [(today - timedelta(days=i)) for i in range(30, -1, -1)]
    
    total_inserted = 0
    for security in securities_to_populate:
        ticker = security['ticker']
        security_id = security['security_id']
        
        # Start with a random base price between $10-$500
        base_price = random.uniform(10, 500)
        
        for date in date_range:
            # Simulate daily price movement (+/- 5%)
            daily_change = random.uniform(-0.05, 0.05)
            open_price = base_price * (1 + random.uniform(-0.02, 0.02))
            close_price = open_price * (1 + daily_change)
            high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.03))
            low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.03))
            volume = random.randint(1000000, 50000000)
            
            # Insert the price data
            price_id = generate_uuid()
            execute_query(
                '''
                INSERT INTO DailyPrice (price_id, security_id, price_date, open, high, low, close, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (price_id, security_id, date, open_price, high_price, low_price, close_price, volume)
            )
            
            # Update base price for next day
            base_price = close_price
        
        total_inserted += len(date_range)
        print(f"  ✓ {ticker}: {len(date_range)} days of price data")
    
    print(f"\n✅ Successfully populated {total_inserted} price records for {len(securities_to_populate)} securities")

if __name__ == '__main__':
    populate_daily_prices()
