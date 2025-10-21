
-- CSE 111 — Stock Exchange Database
-- schema.sql (SQLite dialect)
-- Run with:  sqlite3 stockdb.sqlite < schema.sql

PRAGMA foreign_keys = ON;

-- ==========================
-- DROP (for idempotent setup)
-- ==========================
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS watchlist;
DROP TABLE IF EXISTS holdings;
DROP TABLE IF EXISTS stocks;
DROP TABLE IF EXISTS markets;
DROP TABLE IF EXISTS companies;
DROP TABLE IF EXISTS user_portfolios;
DROP TABLE IF EXISTS portfolios;
DROP TABLE IF EXISTS users;

-- ================
-- CORE ENTITIES
-- ================

CREATE TABLE users (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    name           TEXT NOT NULL,
    email          TEXT NOT NULL UNIQUE,
    password_hash  TEXT NOT NULL,
    cash_balance   NUMERIC NOT NULL DEFAULT 0 CHECK (cash_balance >= 0),
    created_at     TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE portfolios (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    label       TEXT NOT NULL,
    created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Resolves User ⟷ Portfolio (M:N)
CREATE TABLE user_portfolios (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL,
    portfolio_id  INTEGER NOT NULL,
    role          TEXT NOT NULL DEFAULT 'owner', -- owner / viewer
    added_at      TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, portfolio_id),
    FOREIGN KEY (user_id)      REFERENCES users(id)      ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE companies (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    name   TEXT NOT NULL,
    sector TEXT
);

CREATE TABLE markets (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name     TEXT NOT NULL,
    country  TEXT,
    timezone TEXT
);

CREATE TABLE stocks (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol       TEXT NOT NULL UNIQUE,      -- e.g., AAPL
    name         TEXT NOT NULL,             -- e.g., Apple Inc.
    company_id   INTEGER NOT NULL,
    market_id    INTEGER NOT NULL,
    current_price NUMERIC NOT NULL CHECK (current_price >= 0),
    FOREIGN KEY (company_id) REFERENCES companies(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (market_id)  REFERENCES markets(id)   ON UPDATE CASCADE ON DELETE RESTRICT
);

-- Resolves Portfolio ⟷ Stock (M:N)
CREATE TABLE holdings (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    portfolio_id  INTEGER NOT NULL,
    stock_id      INTEGER NOT NULL,
    shares        NUMERIC NOT NULL DEFAULT 0 CHECK (shares >= 0), -- use DECIMAL-like via NUMERIC
    UNIQUE (portfolio_id, stock_id),
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (stock_id)     REFERENCES stocks(id)     ON UPDATE CASCADE ON DELETE CASCADE
);

-- Resolves User ⟷ Stock (M:N) for watchlist
CREATE TABLE watchlist (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id   INTEGER NOT NULL,
    stock_id  INTEGER NOT NULL,
    added_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, stock_id),
    FOREIGN KEY (user_id)  REFERENCES users(id)  ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (stock_id) REFERENCES stocks(id) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Immutable record of trades
CREATE TABLE transactions (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL,
    portfolio_id  INTEGER NOT NULL,
    stock_id      INTEGER NOT NULL,
    type          TEXT NOT NULL CHECK (type IN ('BUY','SELL')),
    qty           NUMERIC NOT NULL CHECK (qty > 0),
    price         NUMERIC NOT NULL CHECK (price >= 0), -- trade price per share
    ts            TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)      REFERENCES users(id)      ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (stock_id)     REFERENCES stocks(id)     ON UPDATE CASCADE ON DELETE RESTRICT
);

-- ==============
-- USEFUL INDEXES
-- ==============
CREATE INDEX idx_user_portfolios_user   ON user_portfolios(user_id);
CREATE INDEX idx_user_portfolios_port   ON user_portfolios(portfolio_id);

CREATE INDEX idx_stocks_company         ON stocks(company_id);
CREATE INDEX idx_stocks_market          ON stocks(market_id);

CREATE INDEX idx_holdings_portfolio     ON holdings(portfolio_id);
CREATE INDEX idx_holdings_stock         ON holdings(stock_id);

CREATE INDEX idx_watchlist_user         ON watchlist(user_id);
CREATE INDEX idx_watchlist_stock        ON watchlist(stock_id);

CREATE INDEX idx_tx_user                ON transactions(user_id);
CREATE INDEX idx_tx_portfolio           ON transactions(portfolio_id);
CREATE INDEX idx_tx_stock               ON transactions(stock_id);
CREATE INDEX idx_tx_ts                  ON transactions(ts);


