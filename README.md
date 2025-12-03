# Stock Exchange Database (CSE 111 Project)

This is our Robinhood-style stock trading database system for the CSE 111 project.

**Team Members:** Ajay, Arsh, Rohit

---

## About this project
We built a simplified version of a stock trading platform like Robinhood. Basically, users can sign up, look at stocks, add them to a watchlist, and "buy" or "sell" them using fake money.

**Our Goals:**
- Make a database that actually makes sense for trading (normalized).
- Show that we know how to use many-to-many and one-to-many relationships.
- Build a backend and frontend so you can actually interact with it.

---

## Tech Stack
We used these tools to build it:

- **Frontend:** React.js (for the website part)
- **Backend:** Python with Flask (handles the logic)
- **Database:** MySQL (stores all the user and stock data)
- **Tools:** GitHub, VS Code, Draw.io

---

## Database Design
We built a comprehensive database with over **30 tables** to handle all the stock trading features. The main entities include users, accounts, securities, orders, holdings, transactions, portfolios, and watchlists, along with supporting tables for daily prices, market data, and relationships.

**Core Tables:**
`User`, `Account`, `Security`, `DailyPrice`, `Order`, `Holding`, `Watchlist`, `WatchlistItem`

**Key Relationships:**
- Users can have multiple Accounts (One-to-Many)
- Accounts hold Securities through Holdings (Many-to-Many)
- Users track Securities via Watchlists (Many-to-Many)
- Orders link Accounts and Securities (Many-to-Many)
- Daily prices track Security performance over time (One-to-Many)

---

## Features

**User Management:**
- User registration and authentication
- Role-based access (regular users vs admins)
- Secure password hashing

**Account Management:**
- Create multiple brokerage accounts per user
- Track cash balances
- Manage account status (active, frozen, closed)

**Trading:**
- Browse available securities
- Place market and limit orders
- Buy/sell stocks
- Track order history and status

**Portfolio:**
- View current holdings across all accounts
- See total portfolio value
- Average cost tracking per security

**Watchlists:**
- Create custom watchlists
- Add/remove securities to track
- Monitor multiple stocks at once

**Analytics:**
- Dashboard with key stats
- Most traded securities
- Portfolio performance tracking
- Account summaries

---

## What We Learned

While building this project, we got hands-on experience with:

- **Database Normalization**: Making sure our tables were properly normalized to avoid redundancy
- **Complex Relationships**: Implementing many-to-many relationships using junction tables
- **Foreign Keys**: Using constraints to maintain data integrity
- **API Design**: Creating RESTful endpoints that make sense
- **Authentication**: Implementing session-based auth from scratch
- **Frontend-Backend Integration**: Getting the web UI to talk to our Flask API
- **SQL Queries**: Writing complex JOIN queries for analytics

---

## Challenges We Faced

**Port Conflicts**: macOS kept blocking port 5000 because of AirPlay, so we had to move the backend to port 5001.

**UUID Format Issues**: SQLite wanted UUIDs without hyphens, but we were generating them with hyphens. Took a while to figure that out.

**Error Handling**: Initially our error messages were super vague ("Failed to create user"). We had to go back and add proper try-catch blocks everywhere.

**CORS Issues**: Getting the frontend to actually talk to the backend was a pain at first. Had to configure Flask-CORS properly.

---

## Future Improvements

If we had more time, we'd add:
- Real-time stock prices (maybe using an API)
- Charts and graphs for price history
- Email notifications for filled orders
- Mobile app version
- Transaction history with better filtering
- Tax reporting features
- Social features (following other traders)

---

## How to Run It
Once you have everything set up:

```bash
# Clone our repo
git clone https://github.com/Rok051/Stock-exchange-database-CSE-111.git
cd Stock-exchange-database-CSE-111

# Load the database schema
mysql -u root -p < sql/schema.sql
```
