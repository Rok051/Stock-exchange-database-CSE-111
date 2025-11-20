-- ============================================================
-- sample_seed_big.sql  (50 stocks + 10 days price history)
-- ============================================================

PRAGMA foreign_keys = ON;

---------------------------------------------------------------
-- 1) Insert Users
---------------------------------------------------------------
INSERT INTO User (user_id, full_name, email) VALUES
  (lower(hex(randomblob(16))), 'Rohit Kumar', 'rohit@example.com'),
  (lower(hex(randomblob(16))), 'Ajay Grewal', 'ajay@example.com'),
  (lower(hex(randomblob(16))), 'Arshdeep Dhaliwal', 'arsh@example.com');

---------------------------------------------------------------
-- 2) Create Accounts for each user
---------------------------------------------------------------
INSERT INTO Account (account_id, user_id, name, cash_balance)
SELECT lower(hex(randomblob(16))), user_id, full_name || ' Brokerage', 15000.00
FROM User;

---------------------------------------------------------------
-- 3) Insert 50 Popular Stocks
---------------------------------------------------------------
INSERT INTO Security (security_id, ticker, name, sector, exchange) VALUES
(lower(hex(randomblob(16))), 'AAPL','Apple Inc','Technology','NASDAQ'),
(lower(hex(randomblob(16))), 'MSFT','Microsoft Corp','Technology','NASDAQ'),
(lower(hex(randomblob(16))), 'AMZN','Amazon.com','Consumer Discretionary','NASDAQ'),
(lower(hex(randomblob(16))), 'GOOGL','Alphabet Class A','Communication Services','NASDAQ'),
(lower(hex(randomblob(16))), 'META','Meta Platforms','Communication Services','NASDAQ'),
(lower(hex(randomblob(16))), 'TSLA','Tesla Motors','Automotive','NASDAQ'),
(lower(hex(randomblob(16))), 'NFLX','Netflix','Communication Services','NASDAQ'),
(lower(hex(randomblob(16))), 'NVDA','Nvidia','Technology','NASDAQ'),
(lower(hex(randomblob(16))), 'ORCL','Oracle','Technology','NYSE'),
(lower(hex(randomblob(16))), 'INTC','Intel','Technology','NASDAQ'),
(lower(hex(randomblob(16))), 'AMD','Advanced Micro Devices','Technology','NASDAQ'),
(lower(hex(randomblob(16))), 'Lun','Lun','Technology','NYSE'),
(lower(hex(randomblob(16))), 'ADBE','Adobe','Technology','NASDAQ'),
(lower(hex(randomblob(16))), 'CRM','Salesforce','Technology','NYSE'),
(lower(hex(randomblob(16))), 'UBER','Uber Technologies','Technology','NYSE'),
(lower(hex(randomblob(16))), 'LYFT','Lyft','Technology','NASDAQ'),
(lower(hex(randomblob(16))), 'DIS','Disney','Consumer Discretionary','NYSE'),
(lower(hex(randomblob(16))), 'WMT','Walmart','Consumer Staples','NYSE'),
(lower(hex(randomblob(16))), 'HD','Home Depot','Consumer Discretionary','NYSE'),
(lower(hex(randomblob(16))), 'LOW','Lowe''s','Consumer Discretionary','NYSE'),
(lower(hex(randomblob(16))), 'COST','Costco Wholesale','Consumer Staples','NASDAQ'),
(lower(hex(randomblob(16))), 'KO','Coca-Cola','Consumer Staples','NYSE'),
(lower(hex(randomblob(16))), 'PEP','PepsiCo','Consumer Staples','NASDAQ'),
(lower(hex(randomblob(16))), 'MCD','McDonald''s','Consumer Discretionary','NYSE'),
(lower(hex(randomblob(16))), 'SBUX','Starbucks','Consumer Discretionary','NASDAQ'),
(lower(hex(randomblob(16))), 'NKE','Nike','Consumer Discretionary','NYSE'),
(lower(hex(randomblob(16))), 'V','Visa','Financials','NYSE'),
(lower(hex(randomblob(16))), 'MA','Mastercard','Financials','NYSE'),
(lower(hex(randomblob(16))), 'JPM','JPMorgan Chase','Financials','NYSE'),
(lower(hex(randomblob(16))), 'BAC','Bank of America','Financials','NYSE'),
(lower(hex(randomblob(16))), 'C','Citigroup','Financials','NYSE'),
(lower(hex(randomblob(16))), 'GS','Goldman Sachs','Financials','NYSE'),
(lower(hex(randomblob(16))), 'XOM','Exxon Mobil','Energy','NYSE'),
(lower(hex(randomblob(16))), 'CVX','Chevron','Energy','NYSE'),
(lower(hex(randomblob(16))), 'BP','BP Oil','Energy','NYSE'),
(lower(hex(randomblob(16))), 'VZ','Verizon','Communication Services','NYSE'),
(lower(hex(randomblob(16))), 'T','AT&T','Communication Services','NYSE'),
(lower(hex(randomblob(16))), 'TMUS','T-Mobile','Communication Services','NASDAQ'),
(lower(hex(randomblob(16))), 'F','Ford','Automotive','NYSE'),
(lower(hex(randomblob(16))), 'GM','General Motors','Automotive','NYSE'),
(lower(hex(randomblob(16))), 'AIR','Airbus','Industrials','NYSE'),
(lower(hex(randomblob(16))), 'BA','Boeing','Industrials','NYSE'),
(lower(hex(randomblob(16))), 'CAT','Caterpillar','Industrials','NYSE'),
(lower(hex(randomblob(16))), 'MMM','3M Company','Industrials','NYSE'),
(lower(hex(randomblob(16))), 'GE','General Electric','Industrials','NYSE'),
(lower(hex(randomblob(16))), 'UPS','UPS','Industrials','NYSE'),
(lower(hex(randomblob(16))), 'FDX','FedEx','Industrials','NYSE'),
(lower(hex(randomblob(16))), 'LMT','Lockheed Martin','Industrials','NYSE');

---------------------------------------------------------------
-- 4) Generate 10 days of price history for all 50 stocks
---------------------------------------------------------------
INSERT INTO DailyPrice (
  price_id, security_id, price_date, open, high, low, close, volume
)
SELECT 
  lower(hex(randomblob(16))),
  s.security_id,
  date('2025-01-01', '+' || x || ' day'),
  ROUND(50 + (abs(random()) % 150), 2),
  ROUND(60 + (abs(random()) % 150), 2),
  ROUND(40 + (abs(random()) % 150), 2),
  ROUND(50 + (abs(random()) % 150), 2),
  1000000 + (abs(random()) % 5000000)
FROM Security s,
     (SELECT 0 AS x UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION
      SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9);

---------------------------------------------------------------
-- 5) Create watchlists
---------------------------------------------------------------
INSERT INTO Watchlist (watchlist_id, user_id, name)
SELECT lower(hex(randomblob(16))), user_id, 'Tech Favorites'
FROM User;

INSERT INTO Watchlist (watchlist_id, user_id, name)
SELECT lower(hex(randomblob(16))), user_id, 'Blue Chips'
FROM User;

---------------------------------------------------------------
-- 6) Add watchlist items (5 stocks per list)
---------------------------------------------------------------
INSERT INTO WatchlistItem (watchlist_id, security_id)
SELECT w.watchlist_id, s.security_id
FROM Watchlist w
JOIN Security s ON s.ticker IN ('AAPL','MSFT','NVDA','META','AMZN');

INSERT INTO WatchlistItem (watchlist_id, security_id)
SELECT w.watchlist_id, s.security_id
FROM Watchlist w
JOIN Security s ON s.ticker IN ('JPM','CVX','KO','PEP','DIS');

---------------------------------------------------------------
-- 7) Give each account some holdings
---------------------------------------------------------------
INSERT INTO Holding (holding_id, account_id, security_id, quantity, avg_cost)
SELECT lower(hex(randomblob(16))), a.account_id, s.security_id,
       (abs(random()) % 20) + 1,
       ROUND(50 + (abs(random()) % 200), 2)
FROM Account a
JOIN Security s ON s.ticker IN ('AAPL','AMZN','TSLA','NVDA','MSFT');

---------------------------------------------------------------
-- 8) Insert 10 sample BUY and SELL orders
---------------------------------------------------------------
INSERT INTO "Order" (
  order_id, account_id, security_id, side, type, quantity, limit_price, status
)
SELECT 
  lower(hex(randomblob(16))),
  a.account_id,
  s.security_id,
  CASE WHEN abs(random()) % 2 = 0 THEN 'BUY' ELSE 'SELL' END,
  'LIMIT',
  (abs(random()) % 10) + 1,
  ROUND(50 + (abs(random()) % 300), 2),
  'FILLED'
FROM Account a, Security s
LIMIT 10;
