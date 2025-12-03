-- tables.sql
-- Schema for CSE 111 Stock Exchange Database (SQLite)

PRAGMA foreign_keys = ON;

-- Drop tables if they already exist
DROP TABLE IF EXISTS Holding;
DROP TABLE IF EXISTS "Order";
DROP TABLE IF EXISTS WatchlistItem;
DROP TABLE IF EXISTS Watchlist;
DROP TABLE IF EXISTS DailyPrice;
DROP TABLE IF EXISTS Security;
DROP TABLE IF EXISTS Account;
DROP TABLE IF EXISTS "User";

-----------------------------------------------------
-- Users of the app
-----------------------------------------------------
CREATE TABLE "User" (
  user_id    TEXT PRIMARY KEY,          -- provide UUID manually or in seed script
  full_name  TEXT NOT NULL,
  email      TEXT NOT NULL UNIQUE,
  password   TEXT NOT NULL,             -- hashed password (SHA256 in auth.py)
  role       TEXT NOT NULL DEFAULT 'USER', -- USER or ADMIN
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-----------------------------------------------------
-- Brokerage accounts (each belongs to one user)
-----------------------------------------------------
CREATE TABLE Account (
  account_id   TEXT PRIMARY KEY,
  user_id      TEXT NOT NULL,
  name         TEXT NOT NULL,
  cash_balance REAL NOT NULL DEFAULT 0.0,
  status       TEXT NOT NULL DEFAULT 'ACTIVE',     -- ACTIVE, CLOSED, FROZEN
  opened_at    TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES "User"(user_id) ON DELETE CASCADE
);

-----------------------------------------------------
-- Tradeable securities (stocks / ETFs)
-----------------------------------------------------
CREATE TABLE Security (
  security_id TEXT PRIMARY KEY,
  ticker      TEXT NOT NULL UNIQUE,
  name        TEXT NOT NULL,
  sector      TEXT,
  exchange    TEXT NOT NULL DEFAULT 'NYSE'
);

-----------------------------------------------------
-- Static daily prices (1D OHLCV)
-----------------------------------------------------
CREATE TABLE DailyPrice (
  price_id    TEXT PRIMARY KEY,
  security_id TEXT NOT NULL,
  price_date  TEXT NOT NULL,         -- YYYY-MM-DD
  open        REAL NOT NULL,
  high        REAL NOT NULL,
  low         REAL NOT NULL,
  close       REAL NOT NULL,
  volume      INTEGER NOT NULL,
  FOREIGN KEY (security_id) REFERENCES Security(security_id) ON DELETE CASCADE,
  UNIQUE (security_id, price_date)
);

-----------------------------------------------------
-- User watchlists
-----------------------------------------------------
CREATE TABLE Watchlist (
  watchlist_id TEXT PRIMARY KEY,
  user_id      TEXT NOT NULL,
  name         TEXT NOT NULL,
  created_at   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES "User"(user_id) ON DELETE CASCADE
);

-----------------------------------------------------
-- Items in a watchlist (M:N between Watchlist and Security)
-----------------------------------------------------
CREATE TABLE WatchlistItem (
  watchlist_id TEXT NOT NULL,
  security_id  TEXT NOT NULL,
  added_at     TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (watchlist_id, security_id),
  FOREIGN KEY (watchlist_id) REFERENCES Watchlist(watchlist_id) ON DELETE CASCADE,
  FOREIGN KEY (security_id)  REFERENCES Security(security_id) ON DELETE CASCADE
);

-----------------------------------------------------
-- Orders placed by accounts
-----------------------------------------------------
CREATE TABLE "Order" (
  order_id    TEXT PRIMARY KEY,
  account_id  TEXT NOT NULL,
  security_id TEXT NOT NULL,
  side        TEXT NOT NULL,     -- BUY or SELL
  type        TEXT NOT NULL,     -- MARKET or LIMIT
  quantity    INTEGER NOT NULL,
  limit_price REAL,
  status      TEXT NOT NULL DEFAULT 'OPEN',    -- OPEN, FILLED, CANCELED
  placed_at   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (account_id)  REFERENCES Account(account_id) ON DELETE CASCADE,
  FOREIGN KEY (security_id) REFERENCES Security(security_id) ON DELETE CASCADE
);

-----------------------------------------------------
-- Current holdings for accounts
-----------------------------------------------------
CREATE TABLE Holding (
  holding_id  TEXT PRIMARY KEY,
  account_id  TEXT NOT NULL,
  security_id TEXT NOT NULL,
  quantity    INTEGER NOT NULL DEFAULT 0,
  avg_cost    REAL NOT NULL DEFAULT 0.0,
  updated_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (account_id)  REFERENCES Account(account_id) ON DELETE CASCADE,
  FOREIGN KEY (security_id) REFERENCES Security(security_id) ON DELETE CASCADE,
  UNIQUE (account_id, security_id)
);
