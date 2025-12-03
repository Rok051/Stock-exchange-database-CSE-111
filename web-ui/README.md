# Stock Exchange Management System - Web UI

A modern, full-featured web interface for managing your stock exchange database with a sleek dark mode design and comprehensive CRUD operations.

![Dashboard](https://img.shields.io/badge/Status-Ready-success)
![Tech Stack](https://img.shields.io/badge/Stack-Flask%20%2B%20Vanilla%20JS-blue)

## 🚀 Features

- **Dashboard**: Real-time statistics and insights
- **Users Management**: Create, view, and manage users
- **Accounts**: Brokerage account management with balance updates
- **Securities**: Browse, search, and add securities
- **Orders**: Place and manage buy/sell orders (Market & Limit)
- **Holdings**: Portfolio positions tracking
- **Watchlists**: Create and manage security watchlists
- **Analytics**: Advanced insights and portfolio analytics

## 🎨 Design

- Modern dark mode interface with glassmorphism effects
- Vibrant gradient accents and smooth animations
- Responsive layout that works on all screen sizes
- Interactive data tables with hover effects
- Modal dialogs for creating/editing records

## 📋 Prerequisites

- Python 3.7+
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Your existing SQLite database at `Phase 2/stock_exchange.db`

## 🛠️ Installation

### 1. Install Python Dependencies

```bash
cd web-ui/backend
pip install -r requirements.txt
```

Or install manually:
```bash
pip install Flask Flask-CORS
```

### 2. Verify Database Path

Make sure your database file exists at:
```
Phase 2/stock_exchange.db
```

The backend is configured to connect to this path relative to the backend directory.

## 🚀 Running the Application

### Start the Backend Server

```bash
cd web-ui/backend
python app.py
```

The API server will start on `http://localhost:5000`

### Open the Frontend

Simply open the HTML file in your browser:

**Option 1: Direct File**
```bash
cd web-ui/frontend
open index.html
```

**Option 2: Local Server (Recommended)**
```bash
cd web-ui/frontend
python -m http.server 8000
```
Then visit: `http://localhost:8000`

## 📖 Usage Guide

### Dashboard
View overview statistics including total users, accounts, securities, and orders. See recent activity and most traded securities.

### Users
- Click "Add User" to create new users
- View all users in a data table
- Delete users with the action buttons

### Accounts
- Create new brokerage accounts linked to users
- View account balances and status
- Use "Deposit" button to add funds to accounts

### Securities
- Browse all available securities
- Use the search bar to filter by ticker or name
- Add new securities with ticker, name, sector, and exchange

### Orders
- Place buy/sell orders (Market or Limit)
- Filter orders by status (Open, Filled, Canceled)
- Update order status with action buttons

### Holdings
- View all portfolio positions
- See quantity, average cost, and total value
- Add new holdings manually

### Watchlists
- Create watchlists for different users
- View watchlist details and securities
- Delete watchlists as needed

### Analytics
- View top holdings by value
- See portfolio values across accounts
- Identify accounts without holdings

## 🔧 API Endpoints

The backend provides comprehensive REST API endpoints:

### Users
- `GET /api/users` - List all users
- `POST /api/users` - Create user
- `DELETE /api/users/:id` - Delete user

### Accounts
- `GET /api/accounts` - List all accounts
- `POST /api/accounts` - Create account
- `PUT /api/accounts/:id/balance` - Update balance

### Securities
- `GET /api/securities` - List all securities
- `POST /api/securities` - Add security
- `GET /api/securities/search?q=` - Search securities

### Orders
- `GET /api/orders` - List all orders
- `POST /api/orders` - Create order
- `PUT /api/orders/:id/status` - Update order status

### Holdings
- `GET /api/holdings` - List all holdings
- `POST /api/holdings` - Add/update holding

### Watchlists
- `GET /api/watchlists` - List all watchlists
- `POST /api/watchlists` - Create watchlist
- `POST /api/watchlists/:id/items` - Add item to watchlist
- `DELETE /api/watchlists/:id` - Delete watchlist

### Analytics
- `GET /api/analytics/overview` - Dashboard statistics
- `GET /api/analytics/most-traded` - Most traded securities
- `GET /api/analytics/top-holdings` - Top holdings by value
- `GET /api/analytics/portfolio-value` - Portfolio values

## 🎯 Tech Stack

**Backend:**
- Flask - Python web framework
- SQLite - Database
- Flask-CORS - Cross-origin resource sharing

**Frontend:**
- Vanilla JavaScript - No frameworks needed
- Modern CSS3 - Glassmorphism, gradients, animations
- HTML5 - Semantic markup
- Inter Font - Clean, modern typography

## 📁 Project Structure

```
web-ui/
├── backend/
│   ├── app.py           # Flask API server
│   ├── database.py      # Database connection handler
│   └── requirements.txt # Python dependencies
└── frontend/
    ├── index.html       # Main HTML structure
    ├── styles.css       # Modern CSS styling
    └── app.js          # JavaScript application logic
```

## 🐛 Troubleshooting

**Backend won't start:**
- Ensure Flask and Flask-CORS are installed
- Check that database path is correct
- Verify Python version is 3.7+

**Frontend can't connect to backend:**
- Make sure backend server is running on port 5000
- Check browser console for CORS errors
- Verify API_BASE_URL in app.js is correct

**Database errors:**
- Ensure database file exists and is not locked
- Check that database schema matches expectations
- Verify you have read/write permissions

## 🎨 Customization

### Change Colors
Edit CSS variables in `styles.css`:
```css
:root {
    --accent-primary: #3b82f6;    /* Blue */
    --accent-secondary: #8b5cf6;  /* Purple */
    --accent-success: #10b981;    /* Green */
}
```

### Change API Port
Edit `app.py`:
```python
app.run(debug=True, port=5000)  # Change port here
```

And update `API_BASE_URL` in `app.js`.

## 📝 License

This project is part of the CSE 111 Stock Exchange Database assignment.

## 🤝 Contributing

This is an educational project. Feel free to extend and customize as needed!

---

**Built with ❤️ for CSE 111**
