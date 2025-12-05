-- ============================================================
-- sample_big.sql - Enhanced with 100+ stocks + 30 days history
-- ============================================================

PRAGMA foreign_keys = ON;

---------------------------------------------------------------
-- 1) Insert Users
---------------------------------------------------------------
INSERT INTO User (user_id, full_name, email, password, role) VALUES
  (lower(hex(randomblob(16))), 'Rohit Kumar', 'rohit@example.com', 'd3ad9315b7be5dd53b31a273b3b3aba5defe700808305aa16a3062b76658a791', 'USER'),
  (lower(hex(randomblob(16))), 'Ajay Grewal', 'ajay@example.com', 'd3ad9315b7be5dd53b31a273b3b3aba5defe700808305aa16a3062b76658a791', 'USER'),
  (lower(hex(randomblob(16))), 'Arshdeep Dhaliwal', 'arsh@example.com', 'd3ad9315b7be5dd53b31a273b3b3aba5defe700808305aa16a3062b76658a791', 'USER'),
  (lower(hex(randomblob(16))), 'Sarah Chen', 'sarah@example.com', 'd3ad9315b7be5dd53b31a273b3b3aba5defe700808305aa16a3062b76658a791', 'USER'),
  (lower(hex(randomblob(16))), 'Marcus Johnson', 'marcus@example.com', 'd3ad9315b7be5dd53b31a273b3b3aba5defe700808305aa16a3062b76658a791', 'USER'),
  (lower(hex(randomblob(16))), 'Emily Rodriguez', 'emily@example.com', 'd3ad9315b7be5dd53b31a273b3b3aba5defe700808305aa16a3062b76658a791', 'USER'),
  (lower(hex(randomblob(16))), 'David Park', 'david@example.com', 'd3ad9315b7be5dd53b31a273b3b3aba5defe700808305aa16a3062b76658a791', 'USER');

---------------------------------------------------------------
-- 2) Create Accounts for each user
---------------------------------------------------------------
INSERT INTO Account (account_id, user_id, name, cash_balance)
SELECT lower(hex(randomblob(16))), user_id, full_name || ' Main Account', 25000.00
FROM User;

INSERT INTO Account (account_id, user_id, name, cash_balance)
SELECT lower(hex(randomblob(16))), user_id, full_name || ' Trading Account', 50000.00
FROM User
LIMIT 3;

---------------------------------------------------------------
-- 3) Insert 100+ Popular Stocks (Tech, Finance, Consumer, Healthcare, Energy, etc.)
---------------------------------------------------------------
INSERT INTO Security (security_id, ticker, name, sector, exchange) VALUES
-- Technology Giants
(lower(hex(randomblob(16))), 'AAPL','Apple Inc','Technology','NASDAQ'),
(lower(hex(randomblob(16))), 'MSFT','Microsoft Corp','Technology','NASDAQ'),
(lower(hex(randomblob(16))), 'GOOGL','Alphabet Class A','Technology','NASDAQ'),
(lower(hex(randomblob(16))), 'META','Meta Platforms','Technology','NASDAQ'),
(lower(hex(randomblob(16))), 'AMZN','Amazon.com','Technology','NASDAQ'),
(lower(hex(randomblob(16))), 'TSLA','Tesla Inc','Automotive','NASDAQ'),
(lower(hex(randomblob(16))), 'NVDA','Nvidia','Technology','NASDAQ'),
(lower(hex(randomblob(16))), 'ORCL','Oracle','Technology','NYSE'),
(lower(hex(randomblob(16))), 'INTC','Intel','Technology','NASDAQ'),
(lower(hex(randomblob(16))), 'AMD','Advanced Micro Devices','Technology','NASDAQ'),
(lower(hex(randomblob(16))), 'CSCO','Cisco Systems','Technology','NASDAQ'),
(lower(hex(randomblob(16))), 'ADBE','Adobe','Technology','NASDAQ'),
(lower(hex(randomblob(16))), 'CRM','Salesforce','Technology','NYSE'),
(lower(hex(randomblob(16))), 'NFLX','Netflix','Entertainment','NASDAQ'),
(lower(hex(randomblob(16))), 'PYPL','PayPal','Technology','NASDAQ'),
(lower(hex(randomblob(16))), 'SQ','Block (Square)','Technology','NYSE'),
(lower(hex(randomblob(16))), 'SHOP','Shopify','Technology','NYSE'),
(lower(hex(randomblob(16))), 'SNOW','Snowflake','Technology','NYSE'),
(lower(hex(randomblob(16))), 'ZM','Zoom','Technology','NASDAQ'),
(lower(hex(randomblob(16))), 'DOCU','DocuSign','Technology','NASDAQ'),
(lower(hex(randomblob(16))), 'UBER','Uber Technologies','Technology','NYSE'),
(lower(hex(randomblob(16))), 'LYFT','Lyft','Technology','NASDAQ'),
(lower(hex(randomblob(16))), 'ABNB','Airbnb','Technology','NASDAQ'),
(lower(hex(randomblob(16))), 'SNAP','Snap Inc','Technology','NYSE'),
(lower(hex(randomblob(16))), 'TWTR','Twitter','Technology','NYSE'),
(lower(hex(randomblob(16))), 'RBLX','Roblox','Technology','NYSE'),
(lower(hex(randomblob(16))), 'SPOT','Spotify','Entertainment','NYSE'),
(lower(hex(randomblob(16))), 'ROKU','Roku','Technology','NASDAQ'),

-- Finance & Banking
(lower(hex(randomblob(16))), 'JPM','JPMorgan Chase','Financials','NYSE'),
(lower(hex(randomblob(16))), 'BAC','Bank of America','Financials','NYSE'),
(lower(hex(randomblob(16))), 'WFC','Wells Fargo','Financials','NYSE'),
(lower(hex(randomblob(16))), 'C','Citigroup','Financials','NYSE'),
(lower(hex(randomblob(16))), 'GS','Goldman Sachs','Financials','NYSE'),
(lower(hex(randomblob(16))), 'MS','Morgan Stanley','Financials','NYSE'),
(lower(hex(randomblob(16))), 'V','Visa','Financials','NYSE'),
(lower(hex(randomblob(16))), 'MA','Mastercard','Financials','NYSE'),
(lower(hex(randomblob(16))), 'AXP','American Express','Financials','NYSE'),
(lower(hex(randomblob(16))), 'BLK','BlackRock','Financials','NYSE'),
(lower(hex(randomblob(16))), 'SCHW','Charles Schwab','Financials','NYSE'),

-- Consumer & Retail
(lower(hex(randomblob(16))), 'WMT','Walmart','Consumer Staples','NYSE'),
(lower(hex(randomblob(16))), 'TGT','Target','Consumer Discretionary','NYSE'),
(lower(hex(randomblob(16))), 'COST','Costco Wholesale','Consumer Staples','NASDAQ'),
(lower(hex(randomblob(16))), 'HD','Home Depot','Consumer Discretionary','NYSE'),
(lower(hex(randomblob(16))), 'LOW','Lowes','Consumer Discretionary','NYSE'),
(lower(hex(randomblob(16))), 'MCD','McDonalds','Consumer Discretionary','NYSE'),
(lower(hex(randomblob(16))), 'SBUX','Starbucks','Consumer Discretionary','NASDAQ'),
(lower(hex(randomblob(16))), 'NKE','Nike','Consumer Discretionary','NYSE'),
(lower(hex(randomblob(16))), 'DIS','Disney','Entertainment','NYSE'),
(lower(hex(randomblob(16))), 'KO','Coca-Cola','Consumer Staples','NYSE'),
(lower(hex(randomblob(16))), 'PEP','PepsiCo','Consumer Staples','NASDAQ'),
(lower(hex(randomblob(16))), 'PG','Procter & Gamble','Consumer Staples','NYSE'),
(lower(hex(randomblob(16))), 'UL','Unilever','Consumer Staples','NYSE'),
(lower(hex(randomblob(16))), 'CL','Colgate-Palmolive','Consumer Staples','NYSE'),

-- Healthcare & Pharma
(lower(hex(randomblob(16))), 'JNJ','Johnson & Johnson','Healthcare','NYSE'),
(lower(hex(randomblob(16))), 'UNH','UnitedHealth Group','Healthcare','NYSE'),
(lower(hex(randomblob(16))), 'PFE','Pfizer','Healthcare','NYSE'),
(lower(hex(randomblob(16))), 'ABBV','AbbVie','Healthcare','NYSE'),
(lower(hex(randomblob(16))), 'TMO','Thermo Fisher','Healthcare','NYSE'),
(lower(hex(randomblob(16))), 'ABT','Abbott Labs','Healthcare','NYSE'),
(lower(hex(randomblob(16))), 'LLY','Eli Lilly','Healthcare','NYSE'),
(lower(hex(randomblob(16))), 'MRK','Merck','Healthcare','NYSE'),
(lower(hex(randomblob(16))), 'CVS','CVS Health','Healthcare','NYSE'),
(lower(hex(randomblob(16))), 'AMGN','Amgen','Healthcare','NASDAQ'),
(lower(hex(randomblob(16))), 'GILD','Gilead Sciences','Healthcare','NASDAQ'),
(lower(hex(randomblob(16))), 'MRNA','Moderna','Healthcare','NASDAQ'),

-- Energy & Utilities
(lower(hex(randomblob(16))), 'XOM','Exxon Mobil','Energy','NYSE'),
(lower(hex(randomblob(16))), 'CVX','Chevron','Energy','NYSE'),
(lower(hex(randomblob(16))), 'COP','ConocoPhillips','Energy','NYSE'),
(lower(hex(randomblob(16))), 'SLB','Schlumberger','Energy','NYSE'),
(lower(hex(randomblob(16))), 'BP','BP','Energy','NYSE'),
(lower(hex(randomblob(16))), 'SHEL','Shell','Energy','NYSE'),
(lower(hex(randomblob(16))), 'NEE','NextEra Energy','Utilities','NYSE'),
(lower(hex(randomblob(16))), 'DUK','Duke Energy','Utilities','NYSE'),

-- Telecom & Media
(lower(hex(randomblob(16))), 'VZ','Verizon','Communication Services','NYSE'),
(lower(hex(randomblob(16))), 'T','AT&T','Communication Services','NYSE'),
(lower(hex(randomblob(16))), 'TMUS','T-Mobile','Communication Services','NASDAQ'),
(lower(hex(randomblob(16))), 'CMCSA','Comcast','Communication Services','NASDAQ'),
(lower(hex(randomblob(16))), 'CHTR','Charter Communications','Communication Services','NASDAQ'),

-- Automotive & Transportation
(lower(hex(randomblob(16))), 'F','Ford','Automotive','NYSE'),
(lower(hex(randomblob(16))), 'GM','General Motors','Automotive','NYSE'),
(lower(hex(randomblob(16))), 'RIVN','Rivian','Automotive','NASDAQ'),
(lower(hex(randomblob(16))), 'LCID','Lucid Motors','Automotive','NASDAQ'),
(lower(hex(randomblob(16))), 'UPS','UPS','Industrials','NYSE'),
(lower(hex(randomblob(16))), 'FDX','FedEx','Industrials','NYSE'),

-- Aerospace & Defense
(lower(hex(randomblob(16))), 'BA','Boeing','Industrials','NYSE'),
(lower(hex(randomblob(16))), 'LMT','Lockheed Martin','Industrials','NYSE'),
(lower(hex(randomblob(16))), 'RTX','Raytheon Technologies','Industrials','NYSE'),
(lower(hex(randomblob(16))), 'NOC','Northrop Grumman','Industrials','NYSE'),
(lower(hex(randomblob(16))), 'GD','General Dynamics','Industrials','NYSE'),

-- Industrials & Materials
(lower(hex(randomblob(16))), 'CAT','Caterpillar','Industrials','NYSE'),
(lower(hex(randomblob(16))), 'DE','Deere & Company','Industrials','NYSE'),
(lower(hex(randomblob(16))), 'MMM','3M Company','Industrials','NYSE'),
(lower(hex(randomblob(16))), 'GE','General Electric','Industrials','NYSE'),
(lower(hex(randomblob(16))), 'HON','Honeywell','Industrials','NASDAQ'),

-- Semiconductors
(lower(hex(randomblob(16))), 'TSM','Taiwan Semiconductor','Technology','NYSE'),
(lower(hex(randomblob(16))), 'AVGO','Broadcom','Technology','NASDAQ'),
(lower(hex(randomblob(16))), 'QCOM','Qualcomm','Technology','NASDAQ'),
(lower(hex(randomblob(16))), 'TXN','Texas Instruments','Technology','NASDAQ'),
(lower(hex(randomblob(16))), 'MU','Micron Technology','Technology','NASDAQ'),
(lower(hex(randomblob(16))), 'ASML','ASML Holding','Technology','NASDAQ'),

-- Real Estate & REITs
(lower(hex(randomblob(16))), 'AMT','American Tower','Real Estate','NYSE'),
(lower(hex(randomblob(16))), 'PLD','Prologis','Real Estate','NYSE'),
(lower(hex(randomblob(16))), 'CCI','Crown Castle','Real Estate','NYSE'),
(lower(hex(randomblob(16))), 'EQIX','Equinix','Real Estate','NASDAQ'),
(lower(hex(randomblob(16))), 'SPG','Simon Property','Real Estate','NYSE');

---------------------------------------------------------------
-- 4) Generate 30 days of price history for all stocks
---------------------------------------------------------------
INSERT INTO DailyPrice (
  price_id, security_id, price_date, open, high, low, close, volume
)
SELECT 
  lower(hex(randomblob(16))),
  s.security_id,
  date('2024-12-01', '+' || x || ' day'),
  ROUND(50 + (abs(random()) % 300), 2),
  ROUND(55 + (abs(random()) % 310), 2),
  ROUND(45 + (abs(random()) % 290), 2),
  ROUND(50 + (abs(random()) % 300), 2),
  500000 + (abs(random()) % 10000000)
FROM Security s,
     (SELECT 0 AS x UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION
      SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION
      SELECT 10 UNION SELECT 11 UNION SELECT 12 UNION SELECT 13 UNION SELECT 14 UNION
      SELECT 15 UNION SELECT 16 UNION SELECT 17 UNION SELECT 18 UNION SELECT 19 UNION
      SELECT 20 UNION SELECT 21 UNION SELECT 22 UNION SELECT 23 UNION SELECT 24 UNION
      SELECT 25 UNION SELECT 26 UNION SELECT 27 UNION SELECT 28 UNION SELECT 29);

---------------------------------------------------------------
-- 5) Create watchlists
---------------------------------------------------------------
INSERT INTO Watchlist (watchlist_id, user_id, name)
SELECT lower(hex(randomblob(16))), user_id, 'Tech Favorites'
FROM User;

INSERT INTO Watchlist (watchlist_id, user_id, name)
SELECT lower(hex(randomblob(16))), user_id, 'Blue Chips'
FROM User;

INSERT INTO Watchlist (watchlist_id, user_id, name)
SELECT lower(hex(randomblob(16))), user_id, 'Growth Stocks'
FROM User
LIMIT 3;

---------------------------------------------------------------
-- 6) Add watchlist items (10+ stocks per watchlist)
---------------------------------------------------------------
INSERT INTO WatchlistItem (watchlist_id, security_id)
SELECT w.watchlist_id, s.security_id
FROM Watchlist w
JOIN Security s ON s.ticker IN ('AAPL','MSFT','NVDA','META','AMZN','GOOGL','TSLA','NFLX','AMD','ADBE')
WHERE w.name = 'Tech Favorites';

INSERT INTO WatchlistItem (watchlist_id, security_id)
SELECT w.watchlist_id, s.security_id
FROM Watchlist w
JOIN Security s ON s.ticker IN ('JPM','CVX','KO','PEP','DIS','JNJ','WMT','PG','V','MA')
WHERE w.name = 'Blue Chips';

INSERT INTO WatchlistItem (watchlist_id, security_id)
SELECT w.watchlist_id, s.security_id
FROM Watchlist w
JOIN Security s ON s.ticker IN ('SNOW','SHOP','RBLX','RIVN','ABNB','SPOT','ROKU','ZM','SQ','DOCU')
WHERE w.name = 'Growth Stocks';

---------------------------------------------------------------
-- 7) Give each account diverse holdings
---------------------------------------------------------------
INSERT INTO Holding (holding_id, account_id, security_id, quantity, avg_cost)
SELECT lower(hex(randomblob(16))), a.account_id, s.security_id,
       (abs(random()) % 50) + 5,
       ROUND(50 + (abs(random()) % 400), 2)
FROM Account a
JOIN Security s ON s.ticker IN ('AAPL','MSFT','GOOGL','AMZN','TSLA','NVDA','META','JPM','V','MA');

---------------------------------------------------------------
-- 8) Insert 50+ orders with various statuses
---------------------------------------------------------------
INSERT INTO "Order" (
  order_id, account_id, security_id, side, type, quantity, limit_price, status
)
SELECT 
  lower(hex(randomblob(16))),
  a.account_id,
  s.security_id,
  CASE WHEN abs(random()) % 2 = 0 THEN 'BUY' ELSE 'SELL' END,
  CASE WHEN abs(random()) % 3 = 0 THEN 'MARKET' ELSE 'LIMIT' END,
  (abs(random()) % 20) + 1,
  ROUND(50 + (abs(random()) % 400), 2),
  CASE (abs(random()) % 3)
    WHEN 0 THEN 'FILLED'
    WHEN 1 THEN 'OPEN'
    ELSE 'CANCELED'
  END
FROM Account a, Security s
LIMIT 50;
