-- ==================================================
-- CSE 111 - Stock Exchange DB Demo Queries
-- ==================================================
-- Usage (SQLite):
--   .headers on
--   .mode column
--   .read demo_queries.sql
-- ==================================================

-- ==================================================
-- 1. SIMPLE SELECT
-- ==================================================
-- List all registered users
SELECT user_id, full_name, email, role 
FROM User 
LIMIT 5;

-- List first 5 stocks in the system
SELECT ticker, name, sector, exchange 
FROM Security 
LIMIT 5;

-- ==================================================
-- 2. SELECT + WHERE
-- ==================================================
-- Find a specific user by email (partial match)
SELECT * 
FROM User 
WHERE email LIKE '%demo%';

-- Find all Tech stocks on NASDAQ
SELECT * 
FROM Security 
WHERE sector = 'Technology' AND exchange = 'NASDAQ'
LIMIT 5;

-- ==================================================
-- 3. JOINS (Users / Accounts / Orders / Securities)
-- ==================================================
-- Show User names and their Account names
SELECT u.full_name, a.name AS account_name, a.cash_balance
FROM User u
JOIN Account a ON u.user_id = a.user_id
LIMIT 5;

-- Show specifics of Orders (who bought what)
SELECT a.name AS account, o.type, o.quantity, s.ticker, o.status
FROM "Order" o
JOIN Account a ON o.account_id = a.account_id
JOIN Security s ON o.security_id = s.security_id
ORDER BY o.placed_at DESC
LIMIT 5;

-- ==================================================
-- 4. GROUP BY / ORDER BY
-- ==================================================
-- Count how many accounts each user has
SELECT u.full_name, COUNT(a.account_id) AS account_count
FROM User u
LEFT JOIN Account a ON u.user_id = a.user_id
GROUP BY u.user_id
ORDER BY account_count DESC
LIMIT 5;

-- Find the most traded stock (by number of orders)
SELECT s.ticker, COUNT(o.order_id) AS order_total
FROM "Order" o
JOIN Security s ON o.security_id = s.security_id
GROUP BY s.ticker
ORDER BY order_total DESC
LIMIT 1;

-- ==================================================
-- 5. "ONE-TO-ONE" STYLE QUERY
-- ==================================================
-- Show the LATEST daily price for each security (effectively 1-to-1 view)
SELECT s.ticker, dp.close, dp.price_date
FROM Security s
JOIN DailyPrice dp ON s.security_id = dp.security_id
WHERE dp.price_date = (
    SELECT MAX(price_date) 
    FROM DailyPrice 
    WHERE security_id = s.security_id
)
LIMIT 5;

-- ==================================================
-- 6. USE-CASE: VIEW PORTFOLIO
-- ==================================================
-- Show current holdings for a specific account (Active users)
SELECT a.name as account_name, s.ticker, h.quantity, h.avg_cost
FROM Holding h
JOIN Account a ON h.account_id = a.account_id
JOIN Security s ON h.security_id = s.security_id
ORDER BY h.quantity DESC
LIMIT 5;

-- ==================================================
-- 7. INSERT EXAMPLES
-- ==================================================
-- RUN THIS ONLY IF YOU WANT TO ADD DATA
-- Insert a new watchlist for a (random) user
INSERT INTO Watchlist (watchlist_id, user_id, name)
SELECT lower(hex(randomblob(16))), user_id, 'Demo Watchlist'
FROM User ORDER BY created_at DESC LIMIT 1;

-- Add a stock (TSLA) to that watchlist
INSERT OR IGNORE INTO WatchlistItem (watchlist_id, security_id)
SELECT w.watchlist_id, s.security_id
FROM Watchlist w, Security s
WHERE w.name = 'Demo Watchlist' AND s.ticker = 'TSLA';

-- ==================================================
-- 8. UPDATE EXAMPLES
-- ==================================================
-- RUN THIS ONLY IF YOU WANT TO MODIFY DATA
-- Deposit huge cash into the most recent account
UPDATE Account
SET cash_balance = cash_balance + 20000.00
WHERE account_id = (SELECT account_id FROM Account ORDER BY created_at DESC LIMIT 1);

-- ==================================================
-- 9. DELETE EXAMPLES
-- ==================================================
-- RUN THIS ONLY IF YOU WANT TO DELETE DATA
-- Remove the empty "Demo Watchlist" we just made
DELETE FROM Watchlist
WHERE name = 'Demo Watchlist';
