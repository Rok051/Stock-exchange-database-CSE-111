import sqlite3
import os
import uuid

# Database connection
DB_PATH = os.path.join(os.path.dirname(__file__), '../../Phase 2/stock_exchange.db')

# Additional securities (different from the first batch)
MORE_SECURITIES = [
    # Tech & Software
    ("UBER",  "Uber Technologies Inc.",           "Technology",        "NYSE"),
    ("LYFT",  "Lyft Inc.",                        "Technology",        "NASDAQ"),
    ("SNAP",  "Snap Inc.",                        "Technology",        "NYSE"),
    ("TWTR",  "Twitter Inc.",                     "Technology",        "NYSE"),
    ("SPOT",  "Spotify Technology SA",            "Technology",        "NYSE"),
    ("SQ",    "Block Inc.",                       "Technology",        "NYSE"),
    ("PYPL",  "PayPal Holdings Inc.",             "Technology",        "NASDAQ"),
    ("ROKU",  "Roku Inc.",                        "Technology",        "NASDAQ"),
    ("ZM",    "Zoom Video Communications Inc.",   "Technology",        "NASDAQ"),
    ("DOCU",  "DocuSign Inc.",                    "Technology",        "NASDAQ"),
    ("SNOW",  "Snowflake Inc.",                   "Technology",        "NYSE"),
    ("PLTR",  "Palantir Technologies Inc.",       "Technology",        "NYSE"),
    ("U",     "Unity Software Inc.",              "Technology",        "NYSE"),
    ("RBLX",  "Roblox Corporation",               "Technology",        "NYSE"),
    
    # Semiconductor & Hardware
    ("MU",    "Micron Technology Inc.",           "Technology",        "NASDAQ"),
    ("AMAT",  "Applied Materials Inc.",           "Technology",        "NASDAQ"),
    ("LRCX",  "Lam Research Corporation",         "Technology",        "NASDAQ"),
    ("KLAC",  "KLA Corporation",                  "Technology",        "NASDAQ"),
    ("MRVL",  "Marvell Technology Inc.",          "Technology",        "NASDAQ"),
    ("TXN",   "Texas Instruments Incorporated",   "Technology",        "NASDAQ"),
    
    # E-commerce & Retail
    ("BABA",  "Alibaba Group Holding Limited",   "Consumer Discretionary", "NYSE"),
    ("JD",    "JD.com Inc.",                      "Consumer Discretionary", "NASDAQ"),
    ("PDD",   "PDD Holdings Inc.",                "Consumer Discretionary", "NASDAQ"),
    ("EBAY",  "eBay Inc.",                        "Consumer Discretionary", "NASDAQ"),
    ("ETSY",  "Etsy Inc.",                        "Consumer Discretionary", "NASDAQ"),
    ("W",     "Wayfair Inc.",                     "Consumer Discretionary", "NYSE"),
    
    # Automotive & EV
    ("NIO",   "NIO Inc.",                         "Consumer Discretionary", "NYSE"),
    ("RIVN",  "Rivian Automotive Inc.",           "Consumer Discretionary", "NASDAQ"),
    ("LCID",  "Lucid Group Inc.",                 "Consumer Discretionary", "NASDAQ"),
    
    # Financial Services & Fintech
    ("COIN",  "Coinbase Global Inc.",             "Financials",        "NASDAQ"),
    ("SOFI",  "SoFi Technologies Inc.",           "Financials",        "NASDAQ"),
    ("HOOD",  "Robinhood Markets Inc.",           "Financials",        "NASDAQ"),
    ("AFRM",  "Affirm Holdings Inc.",             "Financials",        "NASDAQ"),
    
    # Healthcare & Biotech
    ("GILD",  "Gilead Sciences Inc.",             "Health Care",       "NASDAQ"),
    ("MRNA",  "Moderna Inc.",                     "Health Care",       "NASDAQ"),
    ("BNTX",  "BioNTech SE",                      "Health Care",       "NASDAQ"),
    ("ISRG",  "Intuitive Surgical Inc.",          "Health Care",       "NASDAQ"),
    ("VRTX",  "Vertex Pharmaceuticals Inc.",      "Health Care",       "NASDAQ"),
    ("REGN",  "Regeneron Pharmaceuticals Inc.",   "Health Care",       "NASDAQ"),
    ("BIIB",  "Biogen Inc.",                      "Health Care",       "NASDAQ"),
    ("AMGN",  "Amgen Inc.",                       "Health Care",       "NASDAQ"),
    
    # Consumer Brands
    ("SBUX",  "Starbucks Corporation",            "Consumer Discretionary", "NASDAQ"),
    ("CMG",   "Chipotle Mexican Grill Inc.",      "Consumer Discretionary", "NYSE"),
    ("YUM",   "Yum! Brands Inc.",                 "Consumer Discretionary", "NYSE"),
    ("LULU",  "Lululemon Athletica Inc.",         "Consumer Discretionary", "NASDAQ"),
    ("ULTA",  "Ulta Beauty Inc.",                 "Consumer Discretionary", "NASDAQ"),
    
    # Media & Entertainment
    ("PARA",  "Paramount Global",                 "Communication Services", "NASDAQ"),
    ("WBD",   "Warner Bros. Discovery Inc.",      "Communication Services", "NASDAQ"),
    ("SONY",  "Sony Group Corporation",           "Communication Services", "NYSE"),
    
    # Energy & Utilities
    ("NEE",   "NextEra Energy Inc.",              "Utilities",         "NYSE"),
    ("DUK",   "Duke Energy Corporation",          "Utilities",         "NYSE"),
    ("SO",    "The Southern Company",             "Utilities",         "NYSE"),
    
    # Industrial & Aerospace
    ("LMT",   "Lockheed Martin Corporation",      "Industrials",       "NYSE"),
    ("NOC",   "Northrop Grumman Corporation",     "Industrials",       "NYSE"),
    ("HON",   "Honeywell International Inc.",     "Industrials",       "NASDAQ"),
    ("MMM",   "3M Company",                       "Industrials",       "NYSE"),
    ("DE",    "Deere & Company",                  "Industrials",       "NYSE"),
    
    # Real Estate & REITs
    ("AMT",   "American Tower Corporation",       "Real Estate",       "NYSE"),
    ("PLD",   "Prologis Inc.",                    "Real Estate",       "NYSE"),
    ("SPG",   "Simon Property Group Inc.",        "Real Estate",       "NYSE"),
    
    # Materials & Chemicals
    ("DD",    "DuPont de Nemours Inc.",           "Materials",         "NYSE"),
    ("DOW",   "Dow Inc.",                         "Materials",         "NYSE"),
    ("APD",   "Air Products and Chemicals Inc.",  "Materials",         "NYSE"),
    
    # Telecommunications
    ("TMUS",  "T-Mobile US Inc.",                 "Communication Services", "NASDAQ"),
    
    # Retail
    ("TGT",   "Target Corporation",               "Consumer Staples",  "NYSE"),
    ("LOW",   "Lowe's Companies Inc.",            "Consumer Discretionary", "NYSE"),
    ("BBY",   "Best Buy Co Inc.",                 "Consumer Discretionary", "NYSE"),
    
    # Luxury & Apparel
    ("LVMUY", "LVMH Moët Hennessy Louis Vuitton", "Consumer Discretionary", "OTC"),
    
    # Gaming
    ("EA",    "Electronic Arts Inc.",             "Technology",        "NASDAQ"),
    ("TTWO",  "Take-Two Interactive Software",    "Technology",        "NASDAQ"),
    ("ATVI",  "Activision Blizzard Inc.",         "Technology",        "NASDAQ"),
]

def main():
    """
    Add more securities to the database.
    Skips any tickers that already exist.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    inserted_count = 0
    skipped_count = 0
    
    try:
        for ticker, name, sector, exchange in MORE_SECURITIES:
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
