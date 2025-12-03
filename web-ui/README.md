# Stock Exchange Web UI

This is the web interface we built for the database project. It uses a dark mode design and lets you actually use the database to trade stocks.

## What it does

- **Dashboard**: Shows you stats about the market.
- **Users**: You can add and delete users.
- **Accounts**: Manage brokerage accounts and money.
- **Securities**: Search for stocks and add new ones.
- **Orders**: Buy and sell stocks (Market & Limit orders).
- **Holdings**: See what stocks you own.
- **Watchlists**: Keep track of stocks you like.
- **Analytics**: See who owns what and how portfolios are doing.

## How it looks

We tried to make it look modern with a dark theme and some glass effects so it's not just a boring database table view. It should work on mobile too.

## Prerequisites

You need Python 3.7+ and a browser.
Also make sure the database file is at `Phase 2/stock_exchange.db`.

## How to Install

### 1. Get the Python stuff
Go to the backend folder and install the requirements:

```bash
cd web-ui/backend
pip install -r requirements.txt
```

### 2. Check the Database
Just make sure `Phase 2/stock_exchange.db` is there. The backend looks for it there.

## How to Run It

### Start the Backend
Open a terminal and run:

```bash
cd web-ui/backend
python app.py
```
It runs on port 5000.

### Start the Frontend
You can just open `index.html` in Chrome, or run a simple server:

```bash
cd web-ui/frontend
python -m http.server 8000
```
Then go to `http://localhost:8000`.

## How to use it

- **Dashboard**: Check the stats.
- **Users**: Add a user to start.
- **Accounts**: Give that user an account and some money.
- **Securities**: Find a stock (like AAPL).
- **Orders**: Buy some shares.
- **Holdings**: Check your portfolio.

## Tech Stack

**Backend:** Python (Flask) + SQLite
**Frontend:** Just HTML, CSS, and JS (no React/Angular needed for this part)

## Project Structure

```
web-ui/
├── backend/
│   ├── app.py           # The API
│   ├── database.py      # Database stuff
│   └── requirements.txt
└── frontend/
    ├── index.html
    ├── styles.css
    └── app.js
```

## Troubleshooting

- If the backend won't start, check if you installed the requirements.
- If the frontend can't talk to the backend, make sure the backend is running on port 5000.
- If the database errors out, check if the file exists.

## Customization

You can change the colors in `styles.css` if you want.
To change the port, look at `app.py`.




