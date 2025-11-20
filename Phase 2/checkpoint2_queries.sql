PRAGMA foreign_keys = ON;

---------------------------------------------------------------
-- 1) List users
---------------------------------------------------------------
SELECT * FROM User;

---------------------------------------------------------------
-- 2) Accounts per specific user
---------------------------------------------------------------
SELECT * FROM Account
WHERE user_id = (SELECT user_id FROM User ORDER BY created_at LIMIT 1);

---------------------------------------------------------------
-- 3) Count accounts per user
---------------------------------------------------------------
SELECT u.full_name, COUNT(a.account_id) AS num_accounts
FROM User u
LEFT JOIN Account a ON a.user_id = u.user_id
GROUP BY u.user_id;

---------------------------------------------------------------
-- 4) All securities
---------------------------------------------------------------
SELECT ticker, name, sector, exchange
FROM Security;

---------------------------------------------------------------
-- 5) AAPL 10-day price history
---------------------------------------------------------------
SELECT dp.price_date, dp.close
FROM DailyPrice dp
JOIN Security s ON s.security_id = dp.security_id
WHERE s.ticker='AAPL'
ORDER BY dp.price_date DESC LIMIT 10;

---------------------------------------------------------------
-- 6) Insert a fully valid NEW user
---------------------------------------------------------------
INSERT INTO User (user_id, full_name, email)
VALUES (lower(hex(randomblob(16))), 'Demo User', 'demo_' || hex(randomblob(3)) || '@mail.com');

---------------------------------------------------------------
-- 7) Create a NEW account under most recent real user
---------------------------------------------------------------
INSERT INTO Account (account_id, user_id, name, cash_balance)
SELECT lower(hex(randomblob(16))), user_id, 'New Account', 5000.00
FROM User WHERE user_id IS NOT NULL
ORDER BY created_at DESC LIMIT 1;

---------------------------------------------------------------
-- 8) Insert TSLA if missing
---------------------------------------------------------------
INSERT OR IGNORE INTO Security (security_id, ticker, name, sector, exchange)
VALUES (lower(hex(randomblob(16))), 'TSLA', 'Tesla Motors', 'Automotive', 'NASDAQ');

---------------------------------------------------------------
-- 9) Insert TSLA price sample
---------------------------------------------------------------
INSERT OR IGNORE INTO DailyPrice (price_id, security_id, price_date, close)
SELECT lower(hex(randomblob(16))), security_id, '2025-01-11', 250.00
FROM Security WHERE ticker='TSLA';

---------------------------------------------------------------
-- 10) Make a watchlist for last real user
---------------------------------------------------------------
INSERT INTO Watchlist (watchlist_id, user_id, name)
SELECT lower(hex(randomblob(16))), user_id, 'My Watchlist'
FROM User WHERE user_id IS NOT NULL
ORDER BY created_at DESC LIMIT 1;

---------------------------------------------------------------
-- 11) Add AAPL to newest watchlist
---------------------------------------------------------------
INSERT OR IGNORE INTO WatchlistItem (watchlist_id, security_id)
SELECT w.watchlist_id, s.security_id
FROM Watchlist w, Security s
WHERE s.ticker='AAPL'
ORDER BY w.created_at DESC LIMIT 1;

---------------------------------------------------------------
-- 12) Market BUY order
---------------------------------------------------------------
INSERT INTO "Order" (order_id, account_id, security_id, side, type, quantity)
SELECT lower(hex(randomblob(16))), a.account_id, s.security_id,
       'BUY','MARKET',10
FROM Account a, Security s
WHERE s.ticker='AAPL'
ORDER BY a.created_at DESC LIMIT 1;

---------------------------------------------------------------
-- 13) Sell limit order
---------------------------------------------------------------
INSERT INTO "Order" (order_id, account_id, security_id, side, type, quantity, limit_price)
SELECT lower(hex(randomblob(16))), a.account_id, s.security_id,
       'SELL','LIMIT',5,300.00
FROM Account a, Security s
WHERE s.ticker='AAPL'
ORDER BY a.created_at DESC LIMIT 1;

---------------------------------------------------------------
-- 14) Update email of newest user
---------------------------------------------------------------
UPDATE User
SET email='update_' || hex(randomblob(2)) || '@gmail.com'
WHERE user_id = (SELECT user_id FROM User WHERE user_id IS NOT NULL ORDER BY created_at DESC LIMIT 1);

---------------------------------------------------------------
-- 15) Deposit +500 into latest account
---------------------------------------------------------------
UPDATE Account
SET cash_balance=cash_balance+500
WHERE account_id=(SELECT account_id FROM Account ORDER BY created_at DESC LIMIT 1);

---------------------------------------------------------------
-- 16) Mark latest order FILLED
---------------------------------------------------------------
UPDATE "Order"
SET status='FILLED'
WHERE order_id=(SELECT order_id FROM "Order" ORDER BY placed_at DESC LIMIT 1);

---------------------------------------------------------------
-- 17) Delete oldest watchlist (cleanup)
---------------------------------------------------------------
DELETE FROM Watchlist
WHERE watchlist_id IN (SELECT watchlist_id FROM Watchlist ORDER BY created_at LIMIT 1);

---------------------------------------------------------------
-- 18) Remove AAPL from watchlists
---------------------------------------------------------------
DELETE FROM WatchlistItem
WHERE security_id=(SELECT security_id FROM Security WHERE ticker='AAPL');

---------------------------------------------------------------
-- 19) Holdings for newest account
---------------------------------------------------------------
SELECT s.ticker, h.quantity, h.avg_cost
FROM Holding h
JOIN Security s ON s.security_id=h.security_id
WHERE account_id=(SELECT account_id FROM Account ORDER BY created_at DESC LIMIT 1);

---------------------------------------------------------------
-- 20) Most traded stock
---------------------------------------------------------------
SELECT s.ticker, COUNT(*) AS trade_count
FROM "Order" o
JOIN Security s ON s.security_id=o.security_id
GROUP BY s.security_id
ORDER BY trade_count DESC LIMIT 1;

---------------------------------------------------------------
-- 21) Open orders
---------------------------------------------------------------
SELECT * FROM "Order"
WHERE status='OPEN';

---------------------------------------------------------------
-- 22) Max close price per stock
---------------------------------------------------------------
SELECT ticker, MAX(close) AS highest_close
FROM Security s
JOIN DailyPrice dp ON dp.security_id=s.security_id
GROUP BY s.security_id
ORDER BY highest_close DESC;

---------------------------------------------------------------
-- 23) Top gainers 1/1 → 1/10
---------------------------------------------------------------
SELECT s.ticker, dp1.close, dp2.close
FROM DailyPrice dp1
JOIN DailyPrice dp2 ON dp1.security_id=dp2.security_id
JOIN Security s ON s.security_id=dp1.security_id
WHERE dp1.price_date='2025-01-01'
AND dp2.price_date='2025-01-10'
AND dp2.close > dp1.close;

---------------------------------------------------------------
-- 24) Watchlist item count
---------------------------------------------------------------
SELECT w.name, COUNT(wi.security_id) AS watch_count
FROM Watchlist w
LEFT JOIN WatchlistItem wi ON wi.watchlist_id=w.watchlist_id
GROUP BY w.watchlist_id;

---------------------------------------------------------------
-- 25) Orders for TSLA
---------------------------------------------------------------
SELECT * FROM "Order"
WHERE security_id = (SELECT security_id FROM Security WHERE ticker='TSLA');

---------------------------------------------------------------
-- 26) Accounts without holdings
---------------------------------------------------------------
SELECT a.account_id, a.name
FROM Account a
LEFT JOIN Holding h ON h.account_id=a.account_id
WHERE h.account_id IS NULL;

---------------------------------------------------------------
-- 27) Upsert holding (fixed!)
---------------------------------------------------------------
INSERT INTO Holding (holding_id, account_id, security_id, quantity, avg_cost)
SELECT lower(hex(randomblob(16))), a.account_id, s.security_id, 1, 100
FROM Account a, Security s
LIMIT 1
ON CONFLICT(account_id,security_id) DO UPDATE SET
  quantity = excluded.quantity + 1;

---------------------------------------------------------------
-- 28) Delete canceled orders
---------------------------------------------------------------
DELETE FROM "Order"
WHERE status='CANCELED';

---------------------------------------------------------------
-- 29) Total portfolio value per account
---------------------------------------------------------------
SELECT a.account_id, a.name,
SUM(h.quantity * dp.close) AS market_value
FROM Holding h
JOIN Account a ON a.account_id=h.account_id
JOIN DailyPrice dp ON dp.security_id=h.security_id
GROUP BY a.account_id;

---------------------------------------------------------------
-- 30) Users with no watchlists
---------------------------------------------------------------
SELECT u.user_id, u.full_name
FROM User u
LEFT JOIN Watchlist w ON w.user_id=u.user_id
WHERE w.user_id IS NULL;