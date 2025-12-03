from flask import Flask, request, jsonify
from flask_cors import CORS
from database import execute_query, generate_uuid
from datetime import datetime
import os
from auth import hash_password, create_session, get_session, delete_session, require_auth, require_admin

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*", "allow_headers": ["Content-Type", "Authorization"]}})  # Enable CORS with auth headers

# ==================== AUTHENTICATION ====================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.json or {}
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        # Hash the incoming password
        password_hash = hash_password(password)

        # Find user with matching email + hashed password
        query = '''
            SELECT user_id, full_name, email, role
            FROM "User"
            WHERE email = ? AND password = ?
        '''
        user = execute_query(query, (email, password_hash), fetch_one=True)

        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401

        # Create session (stored in memory by auth.py)
        token = create_session(
            user['user_id'],
            user['email'],
            user['full_name'],
            user['role']
        )

        return jsonify({
            'token': token,
            'user': {
                'user_id': user['user_id'],
                'full_name': user['full_name'],
                'email': user['email'],
                'role': user['role']
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/logout', methods=['POST'])
@require_auth
def logout():
    """User logout endpoint"""
    auth_header = request.headers.get('Authorization', '')
    token = auth_header.replace('Bearer ', '')
    delete_session(token)
    return jsonify({'message': 'Logged out successfully'}), 200


@app.route('/api/auth/me', methods=['GET'])
@require_auth
def get_current_user():
    """Get current authenticated user (from session)"""
    return jsonify({'user': request.current_user}), 200


# ==================== USERS ====================

@app.route('/api/users', methods=['GET'])
@require_admin
def get_users():
    """Get all users (admin only)"""
    users = execute_query('SELECT user_id, full_name, email, role, created_at FROM "User" ORDER BY created_at DESC')
    return jsonify(users)


@app.route('/api/users/<user_id>', methods=['GET'])
@require_auth
def get_user(user_id):
    """Get a specific user (self or admin)"""
    current = request.current_user

    # Non-admins can only see themselves
    if current['role'] != 'ADMIN' and current['user_id'] != user_id:
        return jsonify({'error': 'Forbidden'}), 403

    user = execute_query(
        'SELECT user_id, full_name, email, role, created_at FROM "User" WHERE user_id = ?',
        (user_id,),
        fetch_one=True
    )
    if user:
        return jsonify(user)
    return jsonify({'error': 'User not found'}), 404


@app.route('/api/users', methods=['POST'])
@require_admin
def create_user():
    """
    Create a new user (admin only).
    Expects: full_name, email, password, optional role ('USER'/'ADMIN')
    """
    try:
        data = request.json or {}
        full_name = data.get('full_name')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'USER').upper()

        if not full_name or not email or not password:
            return jsonify({'error': 'full_name, email, and password are required'}), 400

        if role not in ['USER', 'ADMIN']:
            return jsonify({'error': 'role must be USER or ADMIN'}), 400

        user_id = generate_uuid()
        password_hash = hash_password(password)

        query = '''
            INSERT INTO "User" (user_id, full_name, email, password, role)
            VALUES (?, ?, ?, ?, ?)
        '''
        execute_query(query, (user_id, full_name, email, password_hash, role))

        return jsonify({
            'user_id': user_id,
            'message': 'User created successfully'
        }), 201

    except Exception as e:
        error_msg = str(e)
        if 'UNIQUE constraint failed' in error_msg or 'unique' in error_msg.lower():
            return jsonify({'error': 'A user with this email already exists'}), 400
        elif 'NOT NULL constraint failed' in error_msg:
            return jsonify({'error': 'Missing required field'}), 400
        else:
            return jsonify({'error': f'Failed to create user: {error_msg}'}), 500


@app.route('/api/users/<user_id>', methods=['PUT'])
@require_auth
def update_user(user_id):
    """
    Update user information.
    - User can update their own full_name/email
    - Admin can also update role
    """
    current = request.current_user
    data = request.json or {}

    # Non-admins can only update themselves
    if current['role'] != 'ADMIN' and current['user_id'] != user_id:
        return jsonify({'error': 'Forbidden'}), 403

    full_name = data.get('full_name')
    email = data.get('email')
    role = data.get('role')  # only admin uses this

    # Build dynamic update
    fields = []
    params = []

    if full_name:
        fields.append('full_name = ?')
        params.append(full_name)
    if email:
        fields.append('email = ?')
        params.append(email)
    if role and current['role'] == 'ADMIN':
        role = role.upper()
        if role not in ['USER', 'ADMIN']:
            return jsonify({'error': 'role must be USER or ADMIN'}), 400
        fields.append('role = ?')
        params.append(role)

    if not fields:
        return jsonify({'error': 'No fields to update'}), 400

    params.append(user_id)
    query = f'UPDATE "User" SET {", ".join(fields)} WHERE user_id = ?'
    execute_query(query, tuple(params))

    return jsonify({'message': 'User updated successfully'}), 200


@app.route('/api/users/<user_id>', methods=['DELETE'])
@require_admin
def delete_user(user_id):
    """Delete a user (admin only)"""
    execute_query('DELETE FROM "User" WHERE user_id = ?', (user_id,))
    return jsonify({'message': 'User deleted successfully'}), 200

# ==================== ACCOUNTS ====================

@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    """Get all accounts with user information"""
    query = '''
        SELECT a.*, u.full_name, u.email 
        FROM Account a
        JOIN User u ON u.user_id = a.user_id
        ORDER BY a.opened_at DESC
    '''
    accounts = execute_query(query)
    return jsonify(accounts)

@app.route('/api/accounts/<account_id>', methods=['GET'])
def get_account(account_id):
    """Get a specific account"""
    query = 'SELECT * FROM Account WHERE account_id = ?'
    account = execute_query(query, (account_id,), fetch_one=True)
    if account:
        return jsonify(account)
    return jsonify({'error': 'Account not found'}), 404

@app.route('/api/users/<user_id>/accounts', methods=['GET'])
def get_user_accounts(user_id):
    """Get all accounts for a specific user"""
    query = 'SELECT * FROM Account WHERE user_id = ? ORDER BY opened_at DESC'
    accounts = execute_query(query, (user_id,))
    return jsonify(accounts)

@app.route('/api/users/<user_id>/holdings', methods=['GET'])
def get_user_holdings(user_id):
    """Get all holdings for a specific user across all accounts"""
    query = '''
        SELECT h.*, s.ticker, s.name, a.name as account_name,
               (h.quantity * h.avg_cost) as total_cost
        FROM Holding h
        JOIN Security s ON s.security_id = h.security_id
        JOIN Account a ON a.account_id = h.account_id
        WHERE a.user_id = ?
        ORDER BY h.updated_at DESC
    '''
    holdings = execute_query(query, (user_id,))
    return jsonify(holdings)

@app.route('/api/users/<user_id>/orders', methods=['GET'])
def get_user_orders(user_id):
    """Get all orders for a specific user"""
    query = '''
        SELECT o.*, s.ticker, s.name, a.name as account_name
        FROM "Order" o
        JOIN Security s ON s.security_id = o.security_id
        JOIN Account a ON a.account_id = o.account_id
        WHERE a.user_id = ?
        ORDER BY o.placed_at DESC
    '''
    orders = execute_query(query, (user_id,))
    return jsonify(orders)

@app.route('/api/users/<user_id>/portfolio-summary', methods=['GET'])
def get_user_portfolio_summary(user_id):
    """Get portfolio summary for a specific user"""
    query = '''
        SELECT 
            COUNT(DISTINCT a.account_id) as total_accounts,
            SUM(a.cash_balance) as total_cash,
            COUNT(DISTINCT h.security_id) as unique_holdings,
            COALESCE(SUM(h.quantity * h.avg_cost), 0) as holdings_value,
            SUM(a.cash_balance) + COALESCE(SUM(h.quantity * h.avg_cost), 0) as total_value
        FROM Account a
        LEFT JOIN Holding h ON h.account_id = a.account_id
        WHERE a.user_id = ?
    '''
    summary = execute_query(query, (user_id,), fetch_one=True)
    return jsonify(summary)


@app.route('/api/accounts', methods=['POST'])
def create_account():
    """Create a new account"""
    try:
        data = request.json
        account_id = generate_uuid()
        query = 'INSERT INTO Account (account_id, user_id, name, cash_balance, status) VALUES (?, ?, ?, ?, ?)'
        execute_query(query, (account_id, data['user_id'], data['name'], 
                              data.get('cash_balance', 0.0), data.get('status', 'ACTIVE')))
        return jsonify({'account_id': account_id, 'message': 'Account created successfully'}), 201
    except Exception as e:
        error_msg = str(e)
        if 'FOREIGN KEY constraint' in error_msg:
            return jsonify({'error': 'Invalid user ID - user does not exist'}), 400
        elif 'NOT NULL constraint' in error_msg:
            return jsonify({'error': 'Missing required field'}), 400
        else:
            return jsonify({'error': f'Failed to create account: {error_msg}'}), 500

@app.route('/api/accounts/<account_id>/balance', methods=['PUT'])
def update_balance(account_id):
    """Update account balance"""
    data = request.json
    amount = data.get('amount', 0)
    query = 'UPDATE Account SET cash_balance = cash_balance + ? WHERE account_id = ?'
    execute_query(query, (amount, account_id))
    return jsonify({'message': 'Balance updated successfully'})

@app.route('/api/accounts/<account_id>/status', methods=['PUT'])
def update_account_status(account_id):
    """Update account status"""
    data = request.json
    query = 'UPDATE Account SET status = ? WHERE account_id = ?'
    execute_query(query, (data['status'], account_id))
    return jsonify({'message': 'Account status updated successfully'})

# ==================== SECURITIES ====================

@app.route('/api/securities', methods=['GET'])
def get_securities():
    """Get all securities"""
    securities = execute_query('SELECT * FROM Security ORDER BY ticker')
    return jsonify(securities)

@app.route('/api/securities/<security_id>', methods=['GET'])
def get_security(security_id):
    """Get a specific security"""
    security = execute_query('SELECT * FROM Security WHERE security_id = ?', 
                            (security_id,), fetch_one=True)
    if security:
        return jsonify(security)
    return jsonify({'error': 'Security not found'}), 404

@app.route('/api/securities/ticker/<ticker>', methods=['GET'])
def get_security_by_ticker(ticker):
    """Get security by ticker symbol"""
    security = execute_query('SELECT * FROM Security WHERE ticker = ?', 
                            (ticker.upper(),), fetch_one=True)
    if security:
        return jsonify(security)
    return jsonify({'error': 'Security not found'}), 404

@app.route('/api/securities', methods=['POST'])
def create_security():
    """Create a new security"""
    try:
        data = request.json
        security_id = generate_uuid()
        query = 'INSERT INTO Security (security_id, ticker, name, sector, exchange) VALUES (?, ?, ?, ?, ?)'
        execute_query(query, (security_id, data['ticker'].upper(), data['name'], 
                              data.get('sector'), data.get('exchange', 'NYSE')))
        return jsonify({'security_id': security_id, 'message': 'Security created successfully'}), 201
    except Exception as e:
        error_msg = str(e)
        if 'UNIQUE constraint failed' in error_msg or 'unique' in error_msg.lower():
            return jsonify({'error': 'A security with this ticker symbol already exists'}), 400
        elif 'NOT NULL constraint' in error_msg:
            return jsonify({'error': 'Missing required field (ticker or name)'}), 400
        else:
            return jsonify({'error': f'Failed to create security: {error_msg}'}), 500

@app.route('/api/securities/search', methods=['GET'])
def search_securities():
    """Search securities by ticker or name"""
    query_param = request.args.get('q', '')
    query = '''
        SELECT * FROM Security 
        WHERE ticker LIKE ? OR name LIKE ?
        ORDER BY ticker
    '''
    pattern = f'%{query_param}%'
    securities = execute_query(query, (pattern, pattern))
    return jsonify(securities)

# ==================== DAILY PRICES ====================

@app.route('/api/prices', methods=['GET'])
def get_prices():
    """Get daily prices with optional filters"""
    ticker = request.args.get('ticker')
    limit = request.args.get('limit', 100)
    
    if ticker:
        query = '''
            SELECT dp.*, s.ticker, s.name
            FROM DailyPrice dp
            JOIN Security s ON s.security_id = dp.security_id
            WHERE s.ticker = ?
            ORDER BY dp.price_date DESC
            LIMIT ?
        '''
        prices = execute_query(query, (ticker.upper(), limit))
    else:
        query = '''
            SELECT dp.*, s.ticker, s.name
            FROM DailyPrice dp
            JOIN Security s ON s.security_id = dp.security_id
            ORDER BY dp.price_date DESC
            LIMIT ?
        '''
        prices = execute_query(query, (limit,))
    
    return jsonify(prices)

@app.route('/api/securities/<security_id>/prices', methods=['GET'])
def get_security_prices(security_id):
    """Get price history for a specific security"""
    query = '''
        SELECT * FROM DailyPrice 
        WHERE security_id = ?
        ORDER BY price_date DESC
        LIMIT 100
    '''
    prices = execute_query(query, (security_id,))
    return jsonify(prices)

@app.route('/api/prices', methods=['POST'])
def create_price():
    """Add a new daily price"""
    data = request.json
    price_id = generate_uuid()
    query = '''
        INSERT INTO DailyPrice (price_id, security_id, price_date, open, high, low, close, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    '''
    execute_query(query, (price_id, data['security_id'], data['price_date'],
                          data['open'], data['high'], data['low'], 
                          data['close'], data['volume']))
    return jsonify({'price_id': price_id, 'message': 'Price added successfully'}), 201

# ==================== ORDERS ====================

@app.route('/api/orders', methods=['GET'])
def get_orders():
    """Get all orders with account and security info"""
    status = request.args.get('status')
    
    base_query = '''
        SELECT o.*, s.ticker, s.name, a.name as account_name
        FROM "Order" o
        JOIN Security s ON s.security_id = o.security_id
        JOIN Account a ON a.account_id = o.account_id
    '''
    
    if status:
        query = base_query + ' WHERE o.status = ? ORDER BY o.placed_at DESC'
        orders = execute_query(query, (status.upper(),))
    else:
        query = base_query + ' ORDER BY o.placed_at DESC'
        orders = execute_query(query)
    
    return jsonify(orders)

@app.route('/api/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    """Get a specific order"""
    query = 'SELECT * FROM "Order" WHERE order_id = ?'
    order = execute_query(query, (order_id,), fetch_one=True)
    if order:
        return jsonify(order)
    return jsonify({'error': 'Order not found'}), 404

@app.route('/api/orders', methods=['POST'])
def create_order():
    """Create a new order"""
    try:
        data = request.json
        order_id = generate_uuid()
        query = '''
            INSERT INTO "Order" (order_id, account_id, security_id, side, type, quantity, limit_price, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        execute_query(query, (order_id, data['account_id'], data['security_id'],
                              data['side'].upper(), data['type'].upper(), 
                              data['quantity'], data.get('limit_price'),
                              data.get('status', 'OPEN')))
        return jsonify({'order_id': order_id, 'message': 'Order created successfully'}), 201
    except Exception as e:
        error_msg = str(e)
        if 'FOREIGN KEY constraint' in error_msg:
            return jsonify({'error': 'Invalid account or security ID'}), 400
        elif 'NOT NULL constraint' in error_msg:
            return jsonify({'error': 'Missing required field'}), 400
        else:
            return jsonify({'error': f'Failed to create order: {error_msg}'}), 500

@app.route('/api/orders/<order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """Update order status"""
    data = request.json
    query = 'UPDATE "Order" SET status = ? WHERE order_id = ?'
    execute_query(query, (data['status'].upper(), order_id))
    return jsonify({'message': 'Order status updated successfully'})

# ==================== HOLDINGS ====================

@app.route('/api/holdings', methods=['GET'])
def get_holdings():
    """Get all holdings with security info"""
    query = '''
        SELECT h.*, s.ticker, s.name, a.name as account_name,
               (h.quantity * h.avg_cost) as total_cost
        FROM Holding h
        JOIN Security s ON s.security_id = h.security_id
        JOIN Account a ON a.account_id = h.account_id
        ORDER BY h.updated_at DESC
    '''
    holdings = execute_query(query)
    return jsonify(holdings)

@app.route('/api/accounts/<account_id>/holdings', methods=['GET'])
def get_account_holdings(account_id):
    """Get holdings for a specific account"""
    query = '''
        SELECT h.*, s.ticker, s.name,
               (h.quantity * h.avg_cost) as total_cost
        FROM Holding h
        JOIN Security s ON s.security_id = h.security_id
        WHERE h.account_id = ?
        ORDER BY h.updated_at DESC
    '''
    holdings = execute_query(query, (account_id,))
    return jsonify(holdings)

@app.route('/api/holdings', methods=['POST'])
def create_holding():
    """Create or update a holding"""
    try:
        data = request.json
        holding_id = generate_uuid()
        query = '''
            INSERT INTO Holding (holding_id, account_id, security_id, quantity, avg_cost)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(account_id, security_id) DO UPDATE SET
                quantity = excluded.quantity,
                avg_cost = excluded.avg_cost,
                updated_at = CURRENT_TIMESTAMP
        '''
        execute_query(query, (holding_id, data['account_id'], data['security_id'],
                              data['quantity'], data['avg_cost']))
        return jsonify({'holding_id': holding_id, 'message': 'Holding updated successfully'}), 201
    except Exception as e:
        error_msg = str(e)
        if 'FOREIGN KEY constraint' in error_msg:
            return jsonify({'error': 'Invalid account or security ID'}), 400
        elif 'NOT NULL constraint' in error_msg:
            return jsonify({'error': 'Missing required field'}), 400
        else:
            return jsonify({'error': f'Failed to create holding: {error_msg}'}), 500

# ==================== WATCHLISTS ====================

@app.route('/api/watchlists', methods=['GET'])
def get_watchlists():
    """Get all watchlists with item count"""
    query = '''
        SELECT w.*, u.full_name, COUNT(wi.security_id) as item_count
        FROM Watchlist w
        JOIN User u ON u.user_id = w.user_id
        LEFT JOIN WatchlistItem wi ON wi.watchlist_id = w.watchlist_id
        GROUP BY w.watchlist_id
        ORDER BY w.created_at DESC
    '''
    watchlists = execute_query(query)
    return jsonify(watchlists)

@app.route('/api/watchlists/<watchlist_id>', methods=['GET'])
def get_watchlist(watchlist_id):
    """Get a specific watchlist with its items"""
    watchlist = execute_query('SELECT * FROM Watchlist WHERE watchlist_id = ?', 
                             (watchlist_id,), fetch_one=True)
    if not watchlist:
        return jsonify({'error': 'Watchlist not found'}), 404
    
    items_query = '''
        SELECT wi.*, s.ticker, s.name, s.sector
        FROM WatchlistItem wi
        JOIN Security s ON s.security_id = wi.security_id
        WHERE wi.watchlist_id = ?
        ORDER BY wi.added_at DESC
    '''
    items = execute_query(items_query, (watchlist_id,))
    watchlist['items'] = items
    
    return jsonify(watchlist)

@app.route('/api/watchlists', methods=['POST'])
def create_watchlist():
    """Create a new watchlist"""
    try:
        data = request.json
        watchlist_id = generate_uuid()
        query = 'INSERT INTO Watchlist (watchlist_id, user_id, name) VALUES (?, ?, ?)'
        execute_query(query, (watchlist_id, data['user_id'], data['name']))
        return jsonify({'watchlist_id': watchlist_id, 'message': 'Watchlist created successfully'}), 201
    except Exception as e:
        error_msg = str(e)
        if 'FOREIGN KEY constraint' in error_msg:
            return jsonify({'error': 'Invalid user ID - user does not exist'}), 400
        elif 'NOT NULL constraint' in error_msg:
            return jsonify({'error': 'Missing required field'}), 400
        else:
            return jsonify({'error': f'Failed to create watchlist: {error_msg}'}), 500

@app.route('/api/watchlists/<watchlist_id>/items', methods=['POST'])
def add_watchlist_item(watchlist_id):
    """Add a security to a watchlist"""
    data = request.json
    query = 'INSERT OR IGNORE INTO WatchlistItem (watchlist_id, security_id) VALUES (?, ?)'
    execute_query(query, (watchlist_id, data['security_id']))
    return jsonify({'message': 'Item added to watchlist'}), 201

@app.route('/api/watchlists/<watchlist_id>/items/<security_id>', methods=['DELETE'])
def remove_watchlist_item(watchlist_id, security_id):
    """Remove a security from a watchlist"""
    query = 'DELETE FROM WatchlistItem WHERE watchlist_id = ? AND security_id = ?'
    execute_query(query, (watchlist_id, security_id))
    return jsonify({'message': 'Item removed from watchlist'})

@app.route('/api/watchlists/<watchlist_id>', methods=['DELETE'])
def delete_watchlist(watchlist_id):
    """Delete a watchlist"""
    execute_query('DELETE FROM Watchlist WHERE watchlist_id = ?', (watchlist_id,))
    return jsonify({'message': 'Watchlist deleted successfully'})

# ==================== ANALYTICS ====================

@app.route('/api/analytics/overview', methods=['GET'])
def get_overview():
    """Get dashboard overview statistics"""
    stats = {}
    
    # Total users
    result = execute_query('SELECT COUNT(*) as count FROM User', fetch_one=True)
    stats['total_users'] = result['count']
    
    # Total accounts
    result = execute_query('SELECT COUNT(*) as count FROM Account', fetch_one=True)
    stats['total_accounts'] = result['count']
    
    # Total securities
    result = execute_query('SELECT COUNT(*) as count FROM Security', fetch_one=True)
    stats['total_securities'] = result['count']
    
    # Open orders
    result = execute_query('SELECT COUNT(*) as count FROM "Order" WHERE status = "OPEN"', fetch_one=True)
    stats['open_orders'] = result['count']
    
    # Total orders
    result = execute_query('SELECT COUNT(*) as count FROM "Order"', fetch_one=True)
    stats['total_orders'] = result['count']
    
    return jsonify(stats)

@app.route('/api/analytics/most-traded', methods=['GET'])
def get_most_traded():
    """Get most traded securities"""
    query = '''
        SELECT s.ticker, s.name, COUNT(*) as trade_count
        FROM "Order" o
        JOIN Security s ON s.security_id = o.security_id
        GROUP BY s.security_id
        ORDER BY trade_count DESC
        LIMIT 10
    '''
    results = execute_query(query)
    return jsonify(results)

@app.route('/api/analytics/top-holdings', methods=['GET'])
def get_top_holdings():
    """Get top holdings by value"""
    query = '''
        SELECT s.ticker, s.name, 
               SUM(h.quantity) as total_shares,
               SUM(h.quantity * h.avg_cost) as total_value
        FROM Holding h
        JOIN Security s ON s.security_id = h.security_id
        GROUP BY s.security_id
        ORDER BY total_value DESC
        LIMIT 10
    '''
    results = execute_query(query)
    return jsonify(results)

@app.route('/api/analytics/accounts-without-holdings', methods=['GET'])
def get_accounts_without_holdings():
    """Get accounts without any holdings"""
    query = '''
        SELECT a.account_id, a.name, a.cash_balance, u.full_name
        FROM Account a
        JOIN User u ON u.user_id = a.user_id
        LEFT JOIN Holding h ON h.account_id = a.account_id
        WHERE h.account_id IS NULL
    '''
    results = execute_query(query)
    return jsonify(results)

@app.route('/api/analytics/portfolio-value', methods=['GET'])
def get_portfolio_values():
    """Get total portfolio value per account"""
    query = '''
        SELECT a.account_id, a.name, u.full_name,
               a.cash_balance,
               COALESCE(SUM(h.quantity * h.avg_cost), 0) as holdings_value,
               a.cash_balance + COALESCE(SUM(h.quantity * h.avg_cost), 0) as total_value
        FROM Account a
        JOIN User u ON u.user_id = a.user_id
        LEFT JOIN Holding h ON h.account_id = a.account_id
        GROUP BY a.account_id
        ORDER BY total_value DESC
    '''
    results = execute_query(query)
    return jsonify(results)

# ==================== ADMIN ====================

@app.route('/api/admin/users', methods=['GET'])
@require_admin
def admin_get_all_users():
    """Get all users with their roles (admin only)"""
    query = '''
        SELECT u.user_id, u.full_name, u.email, u.role, u.created_at,
               COUNT(DISTINCT a.account_id) as account_count
        FROM User u
        LEFT JOIN Account a ON a.user_id = u.user_id
        GROUP BY u.user_id
        ORDER BY u.created_at DESC
    '''
    users = execute_query(query)
    return jsonify(users)

@app.route('/api/admin/users/<user_id>/role', methods=['PUT'])
@require_admin
def admin_update_user_role(user_id):
    """Update user role (admin only)"""
    try:
        data = request.json
        new_role = data.get('role')
        
        if new_role not in ['USER', 'ADMIN']:
            return jsonify({'error': 'Role must be USER or ADMIN'}), 400
        
        query = 'UPDATE User SET role = ? WHERE user_id = ?'
        execute_query(query, (new_role, user_id))
        return jsonify({'message': 'User role updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/stats', methods=['GET'])
@require_admin
def admin_get_stats():
    """Get system statistics (admin only)"""
    stats = {}
    
    # Total users by role
    result = execute_query('SELECT role, COUNT(*) as count FROM User GROUP BY role')
    stats['users_by_role'] = {row['role']: row['count'] for row in result}
    
    # Total accounts and status
    result = execute_query('SELECT status, COUNT(*) as count FROM Account GROUP BY status')
    stats['accounts_by_status'] = {row['status']: row['count'] for row in result}
    
    # Order statistics
    result = execute_query('SELECT status, COUNT(*) as count FROM "Order" GROUP BY status')
    stats['orders_by_status'] = {row['status']: row['count'] for row in result}
    
    # Total cash in system
    result = execute_query('SELECT SUM(cash_balance) as total FROM Account', fetch_one=True)
    stats['total_cash'] = result['total'] or 0
    
    # Recent activity (last 10 orders)
    recent_orders = execute_query('''
        SELECT o.placed_at, u.full_name, s.ticker, o.side, o.quantity, o.status
        FROM "Order" o
        JOIN Account a ON a.account_id = o.account_id
        JOIN User u ON u.user_id = a.user_id
        JOIN Security s ON s.security_id = o.security_id
        ORDER BY o.placed_at DESC
        LIMIT 10
    ''')
    stats['recent_activity'] = recent_orders
    
    return jsonify(stats)

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("Starting Stock Exchange API Server...")
    print("Database path:", os.path.abspath(os.path.join(os.path.dirname(__file__), '../../Phase 2/stock_exchange.db')))
    print("=" * 60)
    print("IMPORTANT: Running on PORT 5001 (not 5000) to avoid macOS AirPlay conflict")
    print("=" * 60)
    app.run(debug=True, port=5001)
