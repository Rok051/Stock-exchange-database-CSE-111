import sqlite3
import os
import uuid
import random
from datetime import datetime, timedelta

# Connect to database
DB_PATH = os.path.join(os.path.dirname(__file__), '../../Phase 2/stock_exchange.db')
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

def generate_uuid():
    return uuid.uuid4().hex

print("Populating 100+ stocks...")

# List of stocks from sample_big.sql
stocks = [
    # Technology Giants
    ('AAPL','Apple Inc','Technology','NASDAQ'),
    ('MSFT','Microsoft Corp','Technology','NASDAQ'),
    ('GOOGL','Alphabet Class A','Technology','NASDAQ'),
    ('META','Meta Platforms','Technology','NASDAQ'),
    ('AMZN','Amazon.com','Technology','NASDAQ'),
    ('TSLA','Tesla Inc','Automotive','NASDAQ'),
    ('NVDA','Nvidia','Technology','NASDAQ'),
    ('ORCL','Oracle','Technology','NYSE'),
    ('INTC','Intel','Technology','NASDAQ'),
    ('AMD','Advanced Micro Devices','Technology','NASDAQ'),
    ('CSCO','Cisco Systems','Technology','NASDAQ'),
    ('ADBE','Adobe','Technology','NASDAQ'),
    ('CRM','Salesforce','Technology','NYSE'),
    ('NFLX','Netflix','Entertainment','NASDAQ'),
    ('PYPL','PayPal','Technology','NASDAQ'),
    ('SQ','Block (Square)','Technology','NYSE'),
    ('SHOP','Shopify','Technology','NYSE'),
    ('SNOW','Snowflake','Technology','NYSE'),
    ('ZM','Zoom','Technology','NASDAQ'),
    ('DOCU','DocuSign','Technology','NASDAQ'),
    ('UBER','Uber Technologies','Technology','NYSE'),
    ('LYFT','Lyft','Technology','NASDAQ'),
    ('ABNB','Airbnb','Technology','NASDAQ'),
    ('SNAP','Snap Inc','Technology','NYSE'),
    ('TWTR','Twitter','Technology','NYSE'),
    ('RBLX','Roblox','Technology','NYSE'),
    ('SPOT','Spotify','Entertainment','NYSE'),
    ('ROKU','Roku','Technology','NASDAQ'),

    # Finance & Banking
    ('JPM','JPMorgan Chase','Financials','NYSE'),
    ('BAC','Bank of America','Financials','NYSE'),
    ('WFC','Wells Fargo','Financials','NYSE'),
    ('C','Citigroup','Financials','NYSE'),
    ('GS','Goldman Sachs','Financials','NYSE'),
    ('MS','Morgan Stanley','Financials','NYSE'),
    ('V','Visa','Financials','NYSE'),
    ('MA','Mastercard','Financials','NYSE'),
    ('AXP','American Express','Financials','NYSE'),
    ('BLK','BlackRock','Financials','NYSE'),
    ('SCHW','Charles Schwab','Financials','NYSE'),

    # Consumer & Retail
    ('WMT','Walmart','Consumer Staples','NYSE'),
    ('TGT','Target','Consumer Discretionary','NYSE'),
    ('COST','Costco Wholesale','Consumer Staples','NASDAQ'),
    ('HD','Home Depot','Consumer Discretionary','NYSE'),
    ('LOW','Lowes','Consumer Discretionary','NYSE'),
    ('MCD','McDonalds','Consumer Discretionary','NYSE'),
    ('SBUX','Starbucks','Consumer Discretionary','NASDAQ'),
    ('NKE','Nike','Consumer Discretionary','NYSE'),
    ('DIS','Disney','Entertainment','NYSE'),
    ('KO','Coca-Cola','Consumer Staples','NYSE'),
    ('PEP','PepsiCo','Consumer Staples','NASDAQ'),
    ('PG','Procter & Gamble','Consumer Staples','NYSE'),
    ('UL','Unilever','Consumer Staples','NYSE'),
    ('CL','Colgate-Palmolive','Consumer Staples','NYSE'),

    # Healthcare & Pharma
    ('JNJ','Johnson & Johnson','Healthcare','NYSE'),
    ('UNH','UnitedHealth Group','Healthcare','NYSE'),
    ('PFE','Pfizer','Healthcare','NYSE'),
    ('ABBV','AbbVie','Healthcare','NYSE'),
    ('TMO','Thermo Fisher','Healthcare','NYSE'),
    ('ABT','Abbott Labs','Healthcare','NYSE'),
    ('LLY','Eli Lilly','Healthcare','NYSE'),
    ('MRK','Merck','Healthcare','NYSE'),
    ('CVS','CVS Health','Healthcare','NYSE'),
    ('AMGN','Amgen','Healthcare','NASDAQ'),
    ('GILD','Gilead Sciences','Healthcare','NASDAQ'),
    ('MRNA','Moderna','Healthcare','NASDAQ'),

    # Energy & Utilities
    ('XOM','Exxon Mobil','Energy','NYSE'),
    ('CVX','Chevron','Energy','NYSE'),
    ('COP','ConocoPhillips','Energy','NYSE'),
    ('SLB','Schlumberger','Energy','NYSE'),
    ('BP','BP','Energy','NYSE'),
    ('SHEL','Shell','Energy','NYSE'),
    ('NEE','NextEra Energy','Utilities','NYSE'),
    ('DUK','Duke Energy','Utilities','NYSE'),

    # Telecom & Media
    ('VZ','Verizon','Communication Services','NYSE'),
    ('T','AT&T','Communication Services','NYSE'),
    ('TMUS','T-Mobile','Communication Services','NASDAQ'),
    ('CMCSA','Comcast','Communication Services','NASDAQ'),
    ('CHTR','Charter Communications','Communication Services','NASDAQ'),

    # Automotive & Transportation
    ('F','Ford','Automotive','NYSE'),
    ('GM','General Motors','Automotive','NYSE'),
    ('RIVN','Rivian','Automotive','NASDAQ'),
    ('LCID','Lucid Motors','Automotive','NASDAQ'),
    ('UPS','UPS','Industrials','NYSE'),
    ('FDX','FedEx','Industrials','NYSE'),

    # Aerospace & Defense
    ('BA','Boeing','Industrials','NYSE'),
    ('LMT','Lockheed Martin','Industrials','NYSE'),
    ('RTX','Raytheon Technologies','Industrials','NYSE'),
    ('NOC','Northrop Grumman','Industrials','NYSE'),
    ('GD','General Dynamics','Industrials','NYSE'),

    # Industrials & Materials
    ('CAT','Caterpillar','Industrials','NYSE'),
    ('DE','Deere & Company','Industrials','NYSE'),
    ('MMM','3M Company','Industrials','NYSE'),
    ('GE','General Electric','Industrials','NYSE'),
    ('HON','Honeywell','Industrials','NASDAQ'),

    # Semiconductors
    ('TSM','Taiwan Semiconductor','Technology','NYSE'),
    ('AVGO','Broadcom','Technology','NASDAQ'),
    ('QCOM','Qualcomm','Technology','NASDAQ'),
    ('TXN','Texas Instruments','Technology','NASDAQ'),
    ('MU','Micron Technology','Technology','NASDAQ'),
    ('ASML','ASML Holding','Technology','NASDAQ')
]

try:
    # 1. Insert Stocks
    count = 0
    for ticker, name, sector, exchange in stocks:
        # Check if exists first
        cursor.execute("SELECT security_id FROM Security WHERE ticker = ?", (ticker,))
        if not cursor.fetchone():
            sec_id = generate_uuid()
            cursor.execute("""
                INSERT INTO Security (security_id, ticker, name, sector, exchange)
                VALUES (?, ?, ?, ?, ?)
            """, (sec_id, ticker, name, sector, exchange))
            count += 1
            
            # 2. Generate 30 days of price history for each new stock
            base_price = random.uniform(50, 400)
            start_date = datetime.now() - timedelta(days=30)
            
            for i in range(30):
                price_date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
                variation = random.uniform(-0.05, 0.05) # +/- 5%
                close_price = base_price * (1 + variation)
                open_price = close_price * (1 + random.uniform(-0.02, 0.02))
                high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.03))
                low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.03))
                volume = int(random.uniform(500000, 10000000))
                
                cursor.execute("""
                    INSERT INTO DailyPrice (price_id, security_id, price_date, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (generate_uuid(), sec_id, price_date, round(open_price, 2), 
                      round(high_price, 2), round(low_price, 2), round(close_price, 2), volume))
                
                base_price = close_price # Next day starts from here

    conn.commit()
    print(f"✅ Successfully added {count} new stocks with price history!")

except Exception as e:
    conn.rollback()
    print(f"❌ Error: {e}")
finally:
    conn.close()
