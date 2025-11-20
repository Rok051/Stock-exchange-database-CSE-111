-- ============================================================
-- checkpoint2_queries.sql
-- CSE 111 – Stock Exchange Database (Checkpoint 2)
-- 30 example SQL queries for demo (SQLite)
-- Assumes tables.sql + sample_big.sql have been loaded.
-- ============================================================

PRAGMA foreign_keys = ON;

---------------------------------------------------------------
-- 1) List all users in the system
---------------------------------------------------------------
SELECT user_id, full_name, email, created_at
FROM User
ORDER BY created_at;

---------------------------------------------------------------
-- 2) List all accounts with their owners
---------------------------------------------------------------
SELECT a.account_id,
       a.name AS account_name,
       a.cash_balance,
       a.status,
       u.full_name AS owner_name
FROM Account a
JOIN User u ON u.user_id = a.user_id
ORDER BY owner_name;

---------------------------------------------------------------
-- 3) Count how many accounts each user owns
---------------------------------------------------------------
SELECT u.full_name,
       COUNT(a.account_id) AS num_accounts
FROM User u
LEFT JOIN Account a ON u.user_id = a.user_id
GROUP BY u.user_id
ORDER BY num_accounts DESC, u.full_name;

---------------------------------------------------------------
-- 4) List some tradeable securities (first 20)
---------------------------------------------------------------
SELECT ticker, name, sector, exchange
FROM Security
ORDER BY ticker
LIMIT 20;

---------------------------------------------------------------
-- 5) How many securities per sector?
---------------------------------------------------------------
SELECT sector,
       COUNT(*) AS num_securities
FROM Security
GROUP BY sector
ORDER BY num_securities DESC;

---------------------------------------------------------------
-- 6) Insert a new user (fake data) and show the result
---------------------------------------------------------------
INSERT INTO User (user_id, full_name, email, created_at)
VALUES (
  lower(hex(randomblob(16))),
  'Test User',
  'testuser'  hex(randomblob(3))  '@example.com',
  datetime('now')
);

-- Show the most recently created Test User
SELECT user_id, full_name, email, created_at
FROM User
WHERE full_name = 'Test User'
ORDER BY created_at DESC
LIMIT 1;
---------------------------------------------------------------
-- 7) Open a new account for Ajay (guaranteed user exists)
---------------------------------------------------------------
INSERT OR IGNORE INTO Account (account_id, user_id, name, cash_balance)
SELECT lower(hex(randomblob(16))), user_id,
       'Ajay Extra Brokerage', 20000.00
FROM User
WHERE full_name = 'Ajay Grewal'
LIMIT 1;

SELECT account_id, name, cash_balance, status, opened_at
FROM Account
WHERE user_id = (SELECT user_id FROM User WHERE full_name='Ajay Grewal');



---------------------------------------------------------------
-- 8) Add a new stock (SNOW) if it does not already exist
---------------------------------------------------------------
INSERT OR IGNORE INTO Security (security_id, ticker, name, sector, exchange)
VALUES (lower(hex(randomblob(16))), 'SNOW', 'Snowflake Inc', 'Technology', 'NYSE');

SELECT ticker, name, sector, exchange
FROM Security
WHERE ticker='SNOW';


---------------------------------------------------------------
-- 9) Add a new daily price for TSLA on a future date
-- (Safe unique date so it never conflicts with seed data)
---------------------------------------------------------------
INSERT OR IGNORE INTO DailyPrice (price_id, security_id, price_date, open, high, low, close, volume)
SELECT lower(hex(randomblob(16))), security_id,
       '2025-02-01', 250, 260, 245, 255, 32000000
FROM Security WHERE ticker='TSLA';

SELECT * FROM DailyPrice
WHERE security_id = (SELECT security_id FROM Security WHERE ticker='TSLA')
ORDER BY price_date DESC LIMIT 1;


---------------------------------------------------------------
-- 10) Create a new watchlist for the second user
---------------------------------------------------------------
INSERT OR IGNORE INTO Watchlist (watchlist_id, user_id, name)
SELECT lower(hex(randomblob(16))), user_id, 'Growth Watchlist'
FROM User WHERE full_name='Ajay Grewal';

SELECT watchlist_id, name
FROM Watchlist
WHERE name='Growth Watchlist';


---------------------------------------------------------------
-- 11) Add AAPL and TSLA to that watchlist
---------------------------------------------------------------
INSERT OR IGNORE INTO WatchlistItem (watchlist_id, security_id)
SELECT w.watchlist_id, s.security_id
FROM Watchlist w
JOIN User u ON u.user_id = w.user_id
JOIN Security s ON s.ticker IN ('AAPL','TSLA')
WHERE w.name = 'Growth Watchlist';

-- preview 
SELECT w.name, s.ticker
FROM WatchlistItem wi
JOIN Watchlist w ON w.watchlist_id = wi.watchlist_id
JOIN Security s ON s.security_id = wi.security_id
WHERE w.name='Growth Watchlist';



---------------------------------------------------------------
-- 12) Show all watchlists and how many stocks they contain
---------------------------------------------------------------
SELECT u.full_name,
       w.name AS watchlist_name,
       COUNT(wi.security_id) AS num_items
FROM Watchlist w
JOIN User u ON u.user_id = w.user_id
LEFT JOIN WatchlistItem wi ON wi.watchlist_id = w.watchlist_id
GROUP BY w.watchlist_id
ORDER BY u.full_name, w.name;

---------------------------------------------------------------
-- 13) Show recent price history for AAPL (5 latest days)
---------------------------------------------------------------
SELECT s.ticker,
       dp.price_date,
       dp.open,
       dp.close,
       dp.volume
FROM DailyPrice dp
JOIN Security s ON s.security_id = dp.security_id
WHERE s.ticker = 'AAPL'
ORDER BY dp.price_date DESC
LIMIT 5;

---------------------------------------------------------------
-- 14) Show portfolio holdings for the first account
---------------------------------------------------------------
SELECT a.name AS account_name,
       s.ticker,
       h.quantity,
       h.avg_cost,
       (h.quantity * h.avg_cost) AS total_cost
FROM Holding h
JOIN Account a ON a.account_id = h.account_id
JOIN Security s ON s.security_id = h.security_id
WHERE a.account_id = (SELECT account_id FROM Account ORDER BY opened_at LIMIT 1)
ORDER BY total_cost DESC;

---------------------------------------------------------------
-- 15) Total market value per account (using latest close)
---------------------------------------------------------------
SELECT a.account_id,
       a.name AS account_name,
       SUM(h.quantity * dp.close) AS market_value
FROM Holding h
JOIN Account a ON a.account_id = h.account_id
JOIN DailyPrice dp
  ON dp.security_id = h.security_id
 AND dp.price_date = (
       SELECT MAX(price_date)
       FROM DailyPrice d2
       WHERE d2.security_id = h.security_id
     )
GROUP BY a.account_id
ORDER BY market_value DESC;

---------------------------------------------------------------
-- 16) Place a LIMIT BUY order for NVDA on the first account (ajay)
---------------------------------------------------------------
INSERT INTO "Order" (order_id, account_id, security_id, side, type, quantity, limit_price, status)
SELECT lower(hex(randomblob(16))),
       a.account_id,
       s.security_id,
       'BUY','LIMIT',10,150.00,'OPEN'
FROM Account a
JOIN Security s ON s.ticker='NVDA'
JOIN User u ON u.user_id = a.user_id AND u.full_name='Ajay Grewal'
LIMIT 1;


---------------------------------------------------------------
-- 17) Place a MARKET SELL order for TSLA on the first account
---------------------------------------------------------------
INSERT INTO "Order" (order_id, account_id, security_id, side, type, quantity, status)
SELECT lower(hex(randomblob(16))),
       a.account_id,
       s.security_id,
       'SELL','MARKET',5,'OPEN'
FROM Account a
JOIN Security s ON s.ticker='TSLA'
JOIN User u ON u.user_id = a.user_id AND u.full_name='Ajay Grewal'
LIMIT 1;
---------------------------------------------------------------
-- 18) List all orders with stock ticker and side
---------------------------------------------------------------
SELECT o.order_id, a.name AS account_name, s.ticker,
       o.side, o.type, o.quantity, o.limit_price, o.status, o.placed_at
FROM "Order" o
JOIN Account a ON a.account_id=o.account_id
JOIN Security s ON s.security_id=o.security_id
ORDER BY o.placed_at DESC;


---------------------------------------------------------------
-- 19) Mark the oldest OPEN order as FILLED
---------------------------------------------------------------
UPDATE "Order"
SET status = 'FILLED'
WHERE order_id = (
  SELECT order_id
  FROM "Order"
  WHERE status = 'OPEN'
  ORDER BY placed_at
  LIMIT 1
);

---------------------------------------------------------------
-- 20) Cancel all remaining OPEN orders
---------------------------------------------------------------
UPDATE "Order" SET status='CANCELED'
WHERE status='OPEN';

---------------------------------------------------------------
-- 21) Delete any empty watchlists (no items)
---------------------------------------------------------------
DELETE FROM Watchlist
WHERE watchlist_id IN (
  SELECT w.watchlist_id
  FROM Watchlist w
  LEFT JOIN WatchlistItem wi ON wi.watchlist_id=w.watchlist_id
  GROUP BY w.watchlist_id
  HAVING COUNT(wi.security_id)=0
);


---------------------------------------------------------------
-- 22) Find the top 5 most traded stocks by number of orders
---------------------------------------------------------------
SELECT s.ticker, COUNT(o.order_id) AS num_orders
FROM "Order" o
JOIN Security s ON s.security_id=o.security_id
GROUP BY s.security_id
ORDER BY num_orders DESC LIMIT 5;

---------------------------------------------------------------
-- 23) Stocks whose latest close is above 200
---------------------------------------------------------------
SELECT s.ticker, dp.close AS latest_close
FROM Security s
JOIN DailyPrice dp ON dp.security_id=s.security_id
WHERE dp.price_date=(SELECT MAX(price_date) FROM DailyPrice WHERE security_id=s.security_id)
AND dp.close > 200
ORDER BY latest_close DESC;


---------------------------------------------------------------
-- 24) Users who currently have no accounts
---------------------------------------------------------------
SELECT u.user_id, u.full_name, u.email
FROM User u
LEFT JOIN Account a ON a.user_id=u.user_id
WHERE a.user_id IS NULL;

---------------------------------------------------------------
-- 25) Securities that appear in watchlists but not in holdings
---------------------------------------------------------------
SELECT DISTINCT s.ticker
FROM Security s
JOIN WatchlistItem wi ON wi.security_id = s.security_id
LEFT JOIN Holding h ON h.security_id = s.security_id
WHERE h.security_id IS NULL
ORDER BY s.ticker;
---------------------------------------------------------------
-- 26) Top 5 lowest closing prices based on each stock's
--     most recent price date
---------------------------------------------------------------
SELECT s.ticker,
       dp.close AS latest_close
FROM Security s
JOIN DailyPrice dp
  ON dp.security_id = s.security_id
 AND dp.price_date = (
       SELECT MAX(price_date)
       FROM DailyPrice d2
       WHERE d2.security_id = s.security_id
     )
ORDER BY latest_close ASC
LIMIT 5;


---------------------------------------------------------------
-- 27) Top 10 largest holdings by quantity
---------------------------------------------------------------
SELECT u.full_name, a.name AS account_name, s.ticker, h.quantity
FROM Holding h
JOIN Account a ON a.account_id=h.account_id
JOIN User u ON u.user_id=a.user_id
JOIN Security s ON s.security_id=h.security_id
ORDER BY h.quantity DESC
LIMIT 10;

---------------------------------------------------------------
-- 28) Delete all canceled orders
---------------------------------------------------------------
DELETE FROM "Order" WHERE status='CANCELED';


---------------------------------------------------------------
-- 29) Average daily volume per security
---------------------------------------------------------------
SELECT s.ticker,
       ROUND(AVG(dp.volume)) AS avg_daily_volume
FROM DailyPrice dp
JOIN Security s ON s.security_id = dp.security_id
GROUP BY s.security_id
ORDER BY avg_daily_volume DESC
LIMIT 10;

---------------------------------------------------------------
-- 30) Full view: user → account → holding → security
---------------------------------------------------------------
SELECT u.full_name AS user_name,
       a.name      AS account_name,
       s.ticker,
       h.quantity,
       h.avg_cost
FROM User u
JOIN Account a ON a.user_id = u.user_id
JOIN Holding h ON h.account_id = a.account_id
JOIN Security s ON s.security_id = h.security_id
ORDER BY u.full_name, a.name, s.ticker;
