import sqlite3
import os
import uuid

# Database connection
DB_PATH = os.path.join(os.path.dirname(__file__), '../../Phase 2/stock_exchange.db')

# List of new securities to add (ticker, name, sector, exchange)
NEW_SECURITIES = [
    ("AAPL",  "Apple Inc.",                        "Technology",        "NASDAQ"),
    ("MSFT",  "Microsoft Corporation",             "Technology",        "NASDAQ"),
    ("GOOGL", "Alphabet Inc. (Class A)",           "Technology",        "NASDAQ"),
    ("AMZN",  "Amazon.com Inc.",                   "Consumer Discretionary", "NASDAQ"),
    ("TSLA",  "Tesla Inc.",                        "Consumer Discretionary", "NASDAQ"),
    ("NVDA",  "NVIDIA Corporation",                "Technology",        "NASDAQ"),
    ("META",  "Meta Platforms Inc.",               "Technology",        "NASDAQ"),
    ("NFLX",  "Netflix Inc.",                      "Communication Services", "NASDAQ"),

    ("JPM",   "JPMorgan Chase & Co.",              "Financials",        "NYSE"),
    ("BAC",   "Bank of America Corporation",       "Financials",        "NYSE"),
    ("V",     "Visa Inc.",                         "Financials",        "NYSE"),
    ("MA",    "Mastercard Incorporated",           "Financials",        "NYSE"),

    ("DIS",   "The Walt Disney Company",           "Communication Services", "NYSE"),
    ("PEP",   "PepsiCo Inc.",                      "Consumer Staples",  "NASDAQ"),
    ("KO",    "The Coca-Cola Company",             "Consumer Staples",  "NYSE"),

    ("INTC",  "Intel Corporation",                 "Technology",        "NASDAQ"),
    ("AMD",   "Advanced Micro Devices Inc.",       "Technology",        "NASDAQ"),
    ("TSM",   "Taiwan Semiconductor Mfg. Co.",     "Technology",        "NYSE"),

    ("XOM",   "Exxon Mobil Corporation",           "Energy",            "NYSE"),
    ("CVX",   "Chevron Corporation",               "Energy",            "NYSE"),

    ("WMT",   "Walmart Inc.",                      "Consumer Staples",  "NYSE"),
    ("COST",  "Costco Wholesale Corporation",      "Consumer Staples",  "NASDAQ"),
    ("HD",    "The Home Depot Inc.",               "Consumer Discretionary", "NYSE"),
    ("MCD",   "McDonald's Corporation",            "Consumer Discretionary", "NYSE"),
    ("NKE",   "NIKE Inc.",                         "Consumer Discretionary", "NYSE"),

    ("T",     "AT&T Inc.",                         "Communication Services", "NYSE"),
    ("VZ",    "Verizon Communications Inc.",       "Communication Services", "NYSE"),

    ("UNH",   "UnitedHealth Group Incorporated",   "Health Care",       "NYSE"),
    ("PFE",   "Pfizer Inc.",                       "Health Care",       "NYSE"),
    ("MRK",   "Merck & Co. Inc.",                  "Health Care",       "NYSE"),
    ("ABBV",  "AbbVie Inc.",                       "Health Care",       "NYSE"),
    ("JNJ",   "Johnson & Johnson",                 "Health Care",       "NYSE"),
    ("LLY",   "Eli Lilly and Company",             "Health Care",       "NYSE"),

    ("ORCL",  "Oracle Corporation",                "Technology",        "NYSE"),
    ("CRM",   "Salesforce Inc.",                   "Technology",        "NYSE"),
    ("ADBE",  "Adobe Inc.",                        "Technology",        "NASDAQ"),
    ("CSCO",  "Cisco Systems Inc.",                "Technology",        "NASDAQ"),
    ("IBM",   "International Business Machines",   "Technology",        "NYSE"),
    ("QCOM",  "QUALCOMM Incorporated",             "Technology",        "NASDAQ"),
    ("AVGO",  "Broadcom Inc.",                     "Technology",        "NASDAQ"),

    ("SHOP",  "Shopify Inc.",                      "Technology",        "NYSE"),
    ("LIN",   "Linde plc",                         "Materials",         "NYSE"),

    ("RTX",   "RTX Corporation",                   "Industrials",       "NYSE"),
    ("BA",    "The Boeing Company",                "Industrials",       "NYSE"),
    ("CAT",   "Caterpillar Inc.",                  "Industrials",       "NYSE"),
    ("GE",    "General Electric Company",          "Industrials",       "NYSE"),

    ("GM",    "General Motors Company",            "Consumer Discretionary", "NYSE"),
    ("F",     "Ford Motor Company",                "Consumer Discretionary", "NYSE"),

    ("UPS",   "United Parcel Service Inc.",        "Industrials",       "NYSE"),
    ("FDX",   "FedEx Corporation",                 "Industrials",       "NYSE"),

    ("BLK",   "BlackRock Inc.",                    "Financials",        "NYSE"),
    ("SPGI",  "S&P Global Inc.",                   "Financials",        "NYSE"),
    ("MS",    "Morgan Stanley",                    "Financials",        "NYSE"),
    ("GS",    "The Goldman Sachs Group Inc.",      "Financials",        "NYSE"),
    ("C",     "Citigroup Inc.",                    "Financials",        "NYSE"),
    ("BK",    "The Bank of New York Mellon Corp.", "Financials",        "NYSE"),
    ("SCHW",  "The Charles Schwab Corporation",    "Financials",        "NYSE"),
]

def main():
    """
    Add new securities to the database.
    Skips any tickers that already exist.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    inserted_count = 0
    skipped_count = 0
    
    try:
        for ticker, name, sector, exchange in NEW_SECURITIES:
            # Check if ticker already exists
            cursor.execute(
                'SELECT security_id FROM Security WHERE ticker = ?',
                (ticker,)
            )
            existing = cursor.fetchone()
            
            if existing:
                print(f"⏭️  Skipping {ticker} – already exists")
                skipped_count += 1
            else:
                # Insert new security
                security_id = uuid.uuid4().hex
                cursor.execute(
                    '''
                    INSERT INTO Security (security_id, ticker, name, sector, exchange)
                    VALUES (?, ?, ?, ?, ?)
                    ''',
                    (security_id, ticker, name, sector, exchange)
                )
                print(f"✅ Inserted {ticker} – {name}")
                inserted_count += 1
        
        # Commit all changes
        conn.commit()
        
        # Print summary
        print("\n" + "=" * 50)
        print(f"📊 Summary:")
        print(f"   Inserted: {inserted_count} new securities")
        print(f"   Skipped:  {skipped_count} existing securities")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
