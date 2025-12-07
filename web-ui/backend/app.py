from flask import Flask, request, jsonify
from flask_cors import CORS
from database import execute_query, generate_uuid
from datetime import datetime
import os
from auth import hash_password, create_session, get_session, delete_session, require_auth, require_admin

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*", "allow_headers": ["Content-Type", "Authorization"]}})  # Enable CORS with auth headers

# Order fulfillment stuff - handles when orders get filled

def process_order_fulfillment(order_id):
    # When an order is marked FILLED, update the holdings and cash balance
    # Returns True/False and a message
    
    # Grab order details from database
    order_query = '''
        SELECT o.*, a.cash_balance, a.user_id
        FROM "Order" o
        JOIN Account a ON a.account_id = o.account_id
        WHERE o.order_id = ?
    '''
    order = execute_query(order_query, (order_id,), fetch_one=True)
    
    if not order:
        return False, "Order not found"
    
    # double check it's not already filled
    if order['status'] == 'FILLED':
        return False, "Order is already filled"
    
    # need a price to calculate stuff
    price = None
    order_type = (order.get('type') or '').upper()

    if order_type == 'LIMIT':
        # use the stored limit price
        price = order.get('limit_price')
    elif order_type == 'MARKET':
        # use the most recent close price from DailyPrice
        price_row = execute_query(
            '''
            SELECT close
            FROM DailyPrice
            WHERE security_id = ?
            ORDER BY price_date DESC
            LIMIT 1
            ''',
            (order['security_id'],),
            fetch_one=True
        )
        if price_row:
            price = price_row['close']

    if not price or price <= 0:
        return False, "Order must have a valid price to be filled"

    # send to buy or sell function depending on order side
    try:
        if order['side'].upper() == 'BUY':
            return _process_buy_order(order, price)
        elif order['side'].upper() == 'SELL':
            return _process_sell_order(order, price)
        else:
            return False, f"Invalid order side: {order['side']}"
    except Exception as e:
        return False, f"Fulfillment failed: {str(e)}"


def _process_buy_order(order, price):
    # Handle buying shares
    # Check if enough cash, then update holdings and subtract cash
    total_cost = order['quantity'] * price
    
    # make sure they have enough money
    if order['cash_balance'] < total_cost:
        return False, f"Insufficient funds. Need ${total_cost:.2f}, have ${order['cash_balance']:.2f}"
    
    # check if they already own this stock
    holding_query = '''
        SELECT holding_id, quantity, avg_cost
        FROM Holding
        WHERE account_id = ? AND security_id = ?
    '''
    existing_holding = execute_query(
        holding_query,
        (order['account_id'], order['security_id']),
        fetch_one=True
    )
    
    # calculate new average cost
    if existing_holding:
        old_qty = existing_holding['quantity']
        old_avg = existing_holding['avg_cost']
        new_qty = old_qty + order['quantity']
        # weighted average formula
        new_avg_cost = ((old_qty * old_avg) + (order['quantity'] * price)) / new_qty
        
        # update their existing holding
        update_holding_query = '''
            UPDATE Holding
            SET quantity = ?, avg_cost = ?, updated_at = CURRENT_TIMESTAMP
            WHERE holding_id = ?
        '''
        execute_query(update_holding_query, (new_qty, new_avg_cost, existing_holding['holding_id']))
    else:
        # make a new holding if they don't have this stock yet
        holding_id = generate_uuid()
        create_holding_query = '''
            INSERT INTO Holding (holding_id, account_id, security_id, quantity, avg_cost)
            VALUES (?, ?, ?, ?, ?)
        '''
        execute_query(create_holding_query, (
            holding_id,
            order['account_id'],
            order['security_id'],
            order['quantity'],
            price
        ))
    
    # take money out of their account
    update_cash_query = '''
        UPDATE Account
        SET cash_balance = cash_balance - ?
        WHERE account_id = ?
    '''
    execute_query(update_cash_query, (total_cost, order['account_id']))
    
    return True, f"BUY order filled: {order['quantity']} shares at ${price:.2f} (total: ${total_cost:.2f})"


def _process_sell_order(order, price):
    # Handle selling shares
    # Check if they have enough shares, update holdings, add cash
    total_proceeds = order['quantity'] * price
    
    # Get existing holding
    holding_query = '''
        SELECT holding_id, quantity, avg_cost
        FROM Holding
        WHERE account_id = ? AND security_id = ?
    '''
    holding = execute_query(
        holding_query,
        (order['account_id'], order['security_id']),
        fetch_one=True
    )
    
    if not holding:
        return False, "No shares to sell - holding does not exist"
    
    if holding['quantity'] < order['quantity']:
        return False, f"Insufficient shares. Need {order['quantity']}, have {holding['quantity']}"
    
    # either update quantity or delete holding if they sold everything
    remaining_shares = holding['quantity'] - order['quantity']
    
    if remaining_shares == 0:
        # sold all shares, delete the holding
        delete_holding_query = 'DELETE FROM Holding WHERE holding_id = ?'
        execute_query(delete_holding_query, (holding['holding_id'],))
    else:
        # still have some shares left, just update quantity
        update_holding_query = '''
            UPDATE Holding
            SET quantity = ?, updated_at = CURRENT_TIMESTAMP
            WHERE holding_id = ?
        '''
        execute_query(update_holding_query, (remaining_shares, holding['holding_id']))
    
    # give them the money from selling
    update_cash_query = '''
        UPDATE Account
        SET cash_balance = cash_balance + ?
        WHERE account_id = ?
    '''
    execute_query(update_cash_query, (total_proceeds, order['account_id']))
    
    return True, f"SELL order filled: {order['quantity']} shares at ${price:.2f} (total: ${total_proceeds:.2f})"

# ==================== AUTHENTICATION ====================

@app.route('/api/auth/login', methods=['POST'])
def login():
    # basically just login stuff
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
    # logout the user
    auth_header = request.headers.get('Authorization', '')
    token = auth_header.replace('Bearer ', '')
    delete_session(token)
    return jsonify({'message': 'Logged out successfully'}), 200


@app.route('/api/auth/me', methods=['GET'])
@require_auth
def get_current_user():
    # like get whoever is logged in right now
    return jsonify({'user': request.current_user}), 200


# ==================== USERS ====================

@app.route('/api/users', methods=['GET'])
@require_admin
def get_users():
    # get list of all users - only admins can do this
    users = execute_query('SELECT user_id, full_name, email, role, created_at FROM "User" ORDER BY created_at DESC')
    return jsonify(users)


@app.route('/api/users/<user_id>', methods=['GET'])
@require_auth
def get_user(user_id):
    # get one user's info
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
    # delete a user from the system (admin only)
    execute_query('DELETE FROM "User" WHERE user_id = ?', (user_id,))
    return jsonify({'message': 'User deleted successfully'}), 200

# ==================== ACCOUNTS ====================

@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    # get all the bank accounts with owner info
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
    # get info for one account
    query = 'SELECT * FROM Account WHERE account_id = ?'
    account = execute_query(query, (account_id,), fetch_one=True)
    if account:
        return jsonify(account)
    return jsonify({'error': 'Account not found'}), 404

@app.route('/api/users/<user_id>/accounts', methods=['GET'])
def get_user_accounts(user_id):
    # get all accounts that belong to one user
    query = 'SELECT * FROM Account WHERE user_id = ? ORDER BY opened_at DESC'
    accounts = execute_query(query, (user_id,))
    return jsonify(accounts)

@app.route('/api/users/<user_id>/holdings', methods=['GET'])
def get_user_holdings(user_id):
    # like get all stocks a user owns across their accounts
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
    # get all orders from one user
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
    # shows what the user's portfolio looks like - total accounts, holdings value, etc
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
    # makes a new account
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
@require_auth
def update_balance(account_id):
    """
    Admin-only: adjust account cash_balance.
    - Only ADMIN can call this
    - ADMIN can deposit into any account
    """
    current = request.current_user
    if current['role'] != 'ADMIN':
        return jsonify({'error': 'Only admins can modify account balances'}), 403

    data = request.get_json() or {}
    amount = data.get('amount')

    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid amount'}), 400

    if amount <= 0:
        return jsonify({'error': 'Amount must be positive'}), 400

    # Make sure account exists
    account = execute_query(
        '''
        SELECT account_id
        FROM Account
        WHERE account_id = ?
        ''',
        (account_id,),
        fetch_one=True
    )
    if not account:
        return jsonify({'error': 'Account not found'}), 404

    # Apply deposit
    execute_query(
        'UPDATE Account SET cash_balance = cash_balance + ? WHERE account_id = ?',
        (amount, account_id)
    )

    return jsonify({'message': 'Balance updated successfully'})

@app.route('/api/accounts/<account_id>/status', methods=['PUT'])
def update_account_status(account_id):
    # change account status to like ACTIVE or CLOSED
    data = request.json
    query = 'UPDATE Account SET status = ? WHERE account_id = ?'
    execute_query(query, (data['status'], account_id))
    return jsonify({'message': 'Account status updated successfully'})

# ==================== SECURITIES ====================

@app.route('/api/securities', methods=['GET'])
def get_securities():
    # get all the stocks/securities
    securities = execute_query('SELECT * FROM Security ORDER BY ticker')
    return jsonify(securities)

@app.route('/api/securities/<security_id>', methods=['GET'])
def get_security(security_id):
    # get one specific stock
    security = execute_query('SELECT * FROM Security WHERE security_id = ?', 
                            (security_id,), fetch_one=True)
    if security:
        return jsonify(security)
    return jsonify({'error': 'Security not found'}), 404

@app.route('/api/securities/ticker/<ticker>', methods=['GET'])
def get_security_by_ticker(ticker):
    # find a stock by its ticker
    security = execute_query('SELECT * FROM Security WHERE ticker = ?', 
                            (ticker.upper(),), fetch_one=True)
    if security:
        return jsonify(security)
    return jsonify({'error': 'Security not found'}), 404

@app.route('/api/securities', methods=['POST'])
def create_security():
    # add a new stock to the system
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
    # search for stocks
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
    # this gets like the daily price data
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
    # basically price history for one stock
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
    # add a new price
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
    # get all the orders
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
    # get details for one order
    query = 'SELECT * FROM "Order" WHERE order_id = ?'
    order = execute_query(query, (order_id,), fetch_one=True)
    if order:
        return jsonify(order)
    return jsonify({'error': 'Order not found'}), 404

@app.route('/api/orders', methods=['POST'])
def create_order():
    # place a new order
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
    """
    Update order status.
    When status is changed to FILLED, automatically processes the order
    by updating holdings and account balances.
    """
    try:
        data = request.json
        new_status = data.get('status', '').upper()
        
        if not new_status:
            return jsonify({'error': 'Status is required'}), 400
        
        # If status is being set to FILLED, process the order fulfillment
        if new_status == 'FILLED':
            success, message = process_order_fulfillment(order_id)
            
            if not success:
                return jsonify({'error': message}), 400
            
            # Update the order status to FILLED
            query = 'UPDATE "Order" SET status = ? WHERE order_id = ?'
            execute_query(query, ('FILLED', order_id))
            
            return jsonify({
                'message': 'Order filled successfully',
                'details': message
            }), 200
        else:
            # For non-FILLED statuses, just update the status
            query = 'UPDATE "Order" SET status = ? WHERE order_id = ?'
            execute_query(query, (new_status, order_id))
            return jsonify({'message': f'Order status updated to {new_status}'}), 200
            
    except Exception as e:
        return jsonify({'error': f'Failed to update order status: {str(e)}'}), 500


# ==================== HOLDINGS ====================

@app.route('/api/holdings', methods=['GET'])
def get_holdings():
    # get what stocks everyone owns with security details
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
    # see what stocks one account has
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
    # add a new holding or update existing one
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
@require_auth
def get_watchlists():
    # Show user their own watchlists, or all of them if they're admin
    current = request.current_user
    
    if current['role'] == 'ADMIN':
        # admins can see everyone's watchlists
        query = '''
            SELECT w.*, u.full_name, COUNT(wi.security_id) as item_count
            FROM Watchlist w
            JOIN User u ON u.user_id = w.user_id
            LEFT JOIN WatchlistItem wi ON wi.watchlist_id = w.watchlist_id
            GROUP BY w.watchlist_id
            ORDER BY w.created_at DESC
        '''
        watchlists = execute_query(query)
    else:
        # regular users only see their own stuff
        query = '''
            SELECT w.*, u.full_name, COUNT(wi.security_id) as item_count
            FROM Watchlist w
            JOIN User u ON u.user_id = w.user_id
            LEFT JOIN WatchlistItem wi ON wi.watchlist_id = w.watchlist_id
            WHERE w.user_id = ?
            GROUP BY w.watchlist_id
            ORDER BY w.created_at DESC
        '''
        watchlists = execute_query(query, (current['user_id'],))
    
    return jsonify(watchlists)

@app.route('/api/watchlists/<watchlist_id>', methods=['GET'])
@require_auth
def get_watchlist(watchlist_id):
    # Get details for one watchlist
    current = request.current_user
    
    watchlist = execute_query('SELECT * FROM Watchlist WHERE watchlist_id = ?', 
                             (watchlist_id,), fetch_one=True)
    if not watchlist:
        return jsonify({'error': 'Watchlist not found'}), 404
    
    # make sure they own this watchlist (unless they're admin)
    if current['role'] != 'ADMIN' and watchlist['user_id'] != current['user_id']:
        return jsonify({'error': 'Forbidden - you can only access your own watchlists'}), 403
    
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
@require_auth
def create_watchlist():
    # Create new watchlist for whoever's logged in
    try:
        current = request.current_user
        data = request.json
        watchlist_id = generate_uuid()
        
        # always create for the current user
        query = 'INSERT INTO Watchlist (watchlist_id, user_id, name) VALUES (?, ?, ?)'
        execute_query(query, (watchlist_id, current['user_id'], data['name']))
        return jsonify({'watchlist_id': watchlist_id, 'message': 'Watchlist created successfully'}), 201
    except Exception as e:
        error_msg = str(e)
        if 'NOT NULL constraint' in error_msg:
            return jsonify({'error': 'Watchlist name is required'}), 400
        else:
            return jsonify({'error': f'Failed to create watchlist: {error_msg}'}), 500

@app.route('/api/watchlists/<watchlist_id>/items', methods=['POST'])
@require_auth
def add_watchlist_item(watchlist_id):
    # Add a stock to a watchlist (need to own it first)
    current = request.current_user
    
    # check if they own this watchlist
    watchlist = execute_query('SELECT user_id FROM Watchlist WHERE watchlist_id = ?', 
                             (watchlist_id,), fetch_one=True)
    if not watchlist:
        return jsonify({'error': 'Watchlist not found'}), 404
    
    if current['role'] != 'ADMIN' and watchlist['user_id'] != current['user_id']:
        return jsonify({'error': 'Forbidden - you can only modify your own watchlists'}), 403
    
    data = request.json
    query = 'INSERT OR IGNORE INTO WatchlistItem (watchlist_id, security_id) VALUES (?, ?)'
    execute_query(query, (watchlist_id, data['security_id']))
    return jsonify({'message': 'Item added to watchlist'}), 201

@app.route('/api/watchlists/<watchlist_id>/items/<security_id>', methods=['DELETE'])
@require_auth
def remove_watchlist_item(watchlist_id, security_id):
    # remove a stock from someone's watchlist (need to own it)
    current = request.current_user
    
    # Verify watchlist ownership
    watchlist = execute_query('SELECT user_id FROM Watchlist WHERE watchlist_id = ?', 
                             (watchlist_id,), fetch_one=True)
    if not watchlist:
        return jsonify({'error': 'Watchlist not found'}), 404
    
    if current['role'] != 'ADMIN' and watchlist['user_id'] != current['user_id']:
        return jsonify({'error': 'Forbidden - you can only modify your own watchlists'}), 403
    
    query = 'DELETE FROM WatchlistItem WHERE watchlist_id = ? AND security_id = ?'
    execute_query(query, (watchlist_id, security_id))
    return jsonify({'message': 'Item removed from watchlist'})

@app.route('/api/watchlists/<watchlist_id>', methods=['DELETE'])
@require_auth
def delete_watchlist(watchlist_id):
    # delete the whole watchlist (need to own it)
    current = request.current_user
    
    # Verify watchlist ownership
    watchlist = execute_query('SELECT user_id FROM Watchlist WHERE watchlist_id = ?', 
                             (watchlist_id,), fetch_one=True)
    if not watchlist:
        return jsonify({'error': 'Watchlist not found'}), 404
    
    if current['role'] != 'ADMIN' and watchlist['user_id'] != current['user_id']:
        return jsonify({'error': 'Forbidden - you can only delete your own watchlists'}), 403
    
    # 1) Delete all items in this watchlist (avoids FK issues)
    execute_query('DELETE FROM WatchlistItem WHERE watchlist_id = ?', (watchlist_id,))

    # 2) Delete the watchlist itself
    execute_query('DELETE FROM Watchlist WHERE watchlist_id = ?', (watchlist_id,))
    return jsonify({'message': 'Watchlist deleted successfully'})

# ==================== ANALYTICS ====================

@app.route('/api/analytics/overview', methods=['GET'])
def get_overview():
    # get the main dashboard stats like total users, accounts, etc
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
@require_auth
def get_most_traded():
    # get which stocks get traded the most (user's own or all if admin)
    current = request.current_user
    
    if current['role'] == 'ADMIN':
        # Admin sees all trades
        query = '''
            SELECT s.ticker, s.name, COUNT(*) as trade_count
            FROM "Order" o
            JOIN Security s ON s.security_id = o.security_id
            GROUP BY s.security_id
            ORDER BY trade_count DESC
            LIMIT 10
        '''
        results = execute_query(query)
    else:
        # Regular users see their own trades only
        query = '''
            SELECT s.ticker, s.name, COUNT(*) as trade_count
            FROM "Order" o
            JOIN Security s ON s.security_id = o.security_id
            JOIN Account a ON a.account_id = o.account_id
            WHERE a.user_id = ?
            GROUP BY s.security_id
            ORDER BY trade_count DESC
            LIMIT 10
        '''
        results = execute_query(query, (current['user_id'],))
    
    return jsonify(results)

@app.route('/api/analytics/top-holdings', methods=['GET'])
@require_auth
def get_top_holdings():
    # top stocks by total value (user's own or all if admin)
    current = request.current_user
    
    if current['role'] == 'ADMIN':
        # Admin sees all holdings
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
    else:
        # Regular users see only their own holdings
        query = '''
            SELECT s.ticker, s.name, 
                   SUM(h.quantity) as total_shares,
                   SUM(h.quantity * h.avg_cost) as total_value
            FROM Holding h
            JOIN Security s ON s.security_id = h.security_id
            JOIN Account a ON a.account_id = h.account_id
            WHERE a.user_id = ?
            GROUP BY s.security_id
            ORDER BY total_value DESC
            LIMIT 10
        '''
        results = execute_query(query, (current['user_id'],))
    
    return jsonify(results)

@app.route('/api/analytics/accounts-without-holdings', methods=['GET'])
@require_auth
def get_accounts_without_holdings():
    # accounts that don't have any stocks (user's own or all if admin)
    current = request.current_user
    
    if current['role'] == 'ADMIN':
        # Admin sees all accounts
        query = '''
            SELECT a.account_id, a.name, a.cash_balance, u.full_name
            FROM Account a
            JOIN User u ON u.user_id = a.user_id
            LEFT JOIN Holding h ON h.account_id = a.account_id
            WHERE h.account_id IS NULL
        '''
        results = execute_query(query)
    else:
        # Regular users see only their own accounts
        query = '''
            SELECT a.account_id, a.name, a.cash_balance, u.full_name
            FROM Account a
            JOIN User u ON u.user_id = a.user_id
            LEFT JOIN Holding h ON h.account_id = a.account_id
            WHERE h.account_id IS NULL AND a.user_id = ?
        '''
        results = execute_query(query, (current['user_id'],))
    
    return jsonify(results)

@app.route('/api/analytics/portfolio-value', methods=['GET'])
@require_auth
def get_portfolio_values():
    # total value of each account's portfolio (user's own or all if admin)
    current = request.current_user
    
    if current['role'] == 'ADMIN':
        # Admin sees all accounts
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
    else:
        # Regular users see only their own accounts
        query = '''
            SELECT a.account_id, a.name, u.full_name,
                   a.cash_balance,
                   COALESCE(SUM(h.quantity * h.avg_cost), 0) as holdings_value,
                   a.cash_balance + COALESCE(SUM(h.quantity * h.avg_cost), 0) as total_value
            FROM Account a
            JOIN User u ON u.user_id = a.user_id
            LEFT JOIN Holding h ON h.account_id = a.account_id
            WHERE a.user_id = ?
            GROUP BY a.account_id
            ORDER BY total_value DESC
        '''
        results = execute_query(query, (current['user_id'],))
    
    return jsonify(results)

# ==================== ADMIN ====================

@app.route('/api/admin/users', methods=['GET'])
@require_admin
def admin_get_all_users():
    # list all users with their roles (admin only)
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
    # change someone's role like USER to ADMIN (admin only)
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
    # get system stats (admin only)
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
