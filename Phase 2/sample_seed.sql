-- sample_seed.sql
-- Inserts sample data into the Stock Exchange DB

PRAGMA foreign_keys = ON;

---------------------------------------------------
-- Insert Users
---------------------------------------------------
INSERT INTO User (user_id, full_name, email)
VALUES
  (lower(hex(randomblob(16))), 'Rohit Kumar', 'rohit@example.com'),
  (lower(hex(randomblob(16))), 'Ajay Grewal', 'ajay@example.com'),
  (lower(hex(randomblob(16))), 'Arshdeep Dhaliwal', 'arsh@example.com');

---------------------------------------------------
-- Insert Accounts for each user
---------------------------------------------------
INSERT INTO Account (account_id, user_id, name, cash_balance)
SELECT lower(hex(randomblob(16))), user_id, full_name || ' Brokerage', 5000.00
FROM User;

---------------------------------------------------
-- Insert Securities (Stocks)
---------------------------------------------------
INSERT INTO Security (security_id, ticker, name, sector, exchange) VALUES
  (lower(hex(randomblob(16))), 'AAPL', 'Apple Inc', 'Technology', 'NASDAQ'),
  (lower(hex(randomblob(16))), 'TSLA', 'Tesla Motors', 'Automotive', 'NASDAQ'),
  (lower(hex(randomblob(16))), 'MSFT', 'Microsoft Corp', 'Technology', 'NASDAQ'),
  (lower(hex(randomblob(16))), 'AMZN', 'Amazon.com Inc', 'E-Commerce', 'NASDAQ'),
  (lower(hex(randomblob(16))), 'JPM', 'JP Morgan Chase', 'Finance', 'NYSE');

---------------------------------------------------
-- Insert Daily Prices for each stock
---------------------------------------------------
INSERT INTO DailyPrice (
  price_id, security_id, price_date, open, high, low, close, volume
)
SELECT lower(hex(randomblob(16))), security_id, '2025-01-15', 100, 110, 98, 108, 5000000
FROM Security;

---------------------------------------------------
-- Insert Watchlists for each User
---------------------------------------------------
INSERT INTO Watchlist (watchlist_id, user_id, name)
SELECT lower(hex(randomblob(16))), user_id, full_name || ' Main Watchlist'
FROM User;

---------------------------------------------------
-- Insert Watchlist Items (each watchlist gets 2 stocks)
---------------------------------------------------
INSERT INTO WatchlistItem (watchlist_id, security_id)
SELECT w.watchlist_id, s.security_id
FROM Watchlist w
JOIN Security s ON s.ticker IN ('AAPL', 'TSLA');

---------------------------------------------------
-- Insert sample Orders (BUY/SELL)
---------------------------------------------------
INSERT INTO "Order" (
  order_id, account_id, security_id, side, type, quantity, limit_price, status
)
SELECT 
  lower(hex(randomblob(16))),
  a.account_id,
  s.security_id,
  'BUY',
  'LIMIT',
  10,
  100.00,
  'FILLED'
FROM Account a
JOIN Security s ON s.ticker = 'AAPL'
LIMIT 1;

INSERT INTO "Order" (
  order_id, account_id, security_id, side, type, quantity, status
)
SELECT 
  lower(hex(randomblob(16))),
  a.account_id,
  s.security_id,
  'SELL',
  'MARKET',
  5,
  'OPEN'
FROM Account a
JOIN Security s ON s.ticker = 'TSLA'
LIMIT 1;

---------------------------------------------------
-- Insert Holdings (positions)
---------------------------------------------------
INSERT INTO Holding (holding_id, account_id, security_id, quantity, avg_cost)
SELECT lower(hex(randomblob(16))), account_id, security_id, 10, 95.00
FROM Account
JOIN Security ON ticker = 'AAPL'
LIMIT 1;