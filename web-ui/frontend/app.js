// ==================== CONFIGURATION ====================
const API_BASE_URL = 'http://localhost:5001/api';

// ==================== STATE MANAGEMENT ====================
let currentPage = 'dashboard';
let cachedData = {
    users: [],
    accounts: [],
    securities: [],
    orders: [],
    holdings: [],
    watchlists: []
};

// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    loadDashboard();
});

// ==================== NAVIGATION ====================
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const page = item.dataset.page;
            navigateTo(page);
        });
    });
}

function navigateTo(page) {
    // Update nav active state
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`[data-page="${page}"]`).classList.add('active');

    // Update page visibility
    document.querySelectorAll('.page').forEach(p => {
        p.classList.remove('active');
    });
    document.getElementById(`${page}-page`).classList.add('active');

    currentPage = page;

    // Load page data
    switch (page) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'users':
            loadUsers();
            break;
        case 'accounts':
            loadAccounts();
            break;
        case 'securities':
            loadSecurities();
            break;
        case 'orders':
            loadOrders();
            break;
        case 'holdings':
            loadHoldings();
            break;
        case 'watchlists':
            loadWatchlists();
            break;
        case 'analytics':
            loadAnalytics();
            break;
    }
}

// ==================== API CALLS ====================
async function apiCall(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json'
            }
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);

        // Try to parse JSON response
        let result;
        try {
            result = await response.json();
        } catch (e) {
            throw new Error(`Server returned invalid JSON: ${response.statusText}`);
        }

        if (!response.ok) {
            // Show detailed error from backend if available
            const errorMsg = result.error || result.message || `API request failed with status ${response.status}`;
            throw new Error(errorMsg);
        }

        return result;
    } catch (error) {
        console.error('API Error:', error);
        showToast(error.message, 'error');
        throw error;
    }
}

// ==================== DASHBOARD ====================
async function loadDashboard() {
    try {
        const stats = await apiCall('/analytics/overview');

        document.getElementById('stat-users').textContent = stats.total_users || 0;
        document.getElementById('stat-accounts').textContent = stats.total_accounts || 0;
        document.getElementById('stat-securities').textContent = stats.total_securities || 0;
        document.getElementById('stat-orders').textContent = stats.total_orders || 0;

        // Load recent orders
        const orders = await apiCall('/orders?limit=5');
        displayRecentOrders(orders.slice(0, 5));

        // Load most traded
        const mostTraded = await apiCall('/analytics/most-traded');
        displayMostTraded(mostTraded);
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

function displayRecentOrders(orders) {
    const container = document.getElementById('recent-orders');
    if (!orders || orders.length === 0) {
        container.innerHTML = '<p style="color: var(--text-secondary);">No recent orders</p>';
        return;
    }

    container.innerHTML = orders.map(order => `
        <div class="recent-item">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong style="color: var(--text-primary);">${order.ticker}</strong>
                    <span style="margin-left: 0.5rem; color: ${order.side === 'BUY' ? 'var(--accent-success)' : 'var(--accent-danger)'};">
                        ${order.side}
                    </span>
                </div>
                <span class="badge badge-${order.status.toLowerCase()}">${order.status}</span>
            </div>
            <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.25rem;">
                ${order.quantity} shares • ${order.type}
            </div>
        </div>
    `).join('');
}

function displayMostTraded(securities) {
    const container = document.getElementById('most-traded');
    if (!securities || securities.length === 0) {
        container.innerHTML = '<p style="color: var(--text-secondary);">No data available</p>';
        return;
    }

    container.innerHTML = securities.map((sec, index) => `
        <div class="recent-item">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong style="color: var(--text-primary);">${index + 1}. ${sec.ticker}</strong>
                    <div style="font-size: 0.875rem; color: var(--text-secondary);">${sec.name}</div>
                </div>
                <span style="color: var(--accent-primary); font-weight: 600;">${sec.trade_count} trades</span>
            </div>
        </div>
    `).join('');
}

// ==================== USERS ====================
async function loadUsers() {
    try {
        const users = await apiCall('/users');
        cachedData.users = users;
        displayUsers(users);
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

function displayUsers(users) {
    const container = document.getElementById('users-table');
    if (!users || users.length === 0) {
        container.innerHTML = '<p style="color: var(--text-secondary); padding: 2rem; text-align: center;">No users found</p>';
        return;
    }

    container.innerHTML = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>Full Name</th>
                    <th>Email</th>
                    <th>Created At</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                ${users.map(user => `
                    <tr>
                        <td style="color: var(--text-primary); font-weight: 600;">${escapeHtml(user.full_name)}</td>
                        <td>${escapeHtml(user.email)}</td>
                        <td>${formatDate(user.created_at)}</td>
                        <td>
                            <button class="btn btn-sm btn-danger" onclick="deleteUser('${user.user_id}')">Delete</button>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

async function showCreateUserModal() {
    showModal('create-user-modal');
}

async function createUser(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = {
        full_name: formData.get('full_name'),
        email: formData.get('email')
    };

    try {
        await apiCall('/users', 'POST', data);
        showToast('User created successfully!', 'success');
        closeModal();
        loadUsers();
    } catch (error) {
        showToast('Failed to create user', 'error');
    }
}

async function deleteUser(userId) {
    if (!confirm('Are you sure you want to delete this user?')) return;

    try {
        await apiCall(`/users/${userId}`, 'DELETE');
        showToast('User deleted successfully!', 'success');
        loadUsers();
    } catch (error) {
        showToast('Failed to delete user', 'error');
    }
}

// ==================== ACCOUNTS ====================
async function loadAccounts() {
    try {
        const accounts = await apiCall('/accounts');
        cachedData.accounts = accounts;
        displayAccounts(accounts);
    } catch (error) {
        console.error('Error loading accounts:', error);
    }
}

function displayAccounts(accounts) {
    const container = document.getElementById('accounts-table');
    if (!accounts || accounts.length === 0) {
        container.innerHTML = '<p style="color: var(--text-secondary); padding: 2rem; text-align: center;">No accounts found</p>';
        return;
    }

    container.innerHTML = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>Account Name</th>
                    <th>Owner</th>
                    <th>Cash Balance</th>
                    <th>Status</th>
                    <th>Opened</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                ${accounts.map(account => `
                    <tr>
                        <td style="color: var(--text-primary); font-weight: 600;">${escapeHtml(account.name)}</td>
                        <td>${escapeHtml(account.full_name)}</td>
                        <td style="color: var(--accent-success); font-weight: 600;">$${formatNumber(account.cash_balance)}</td>
                        <td><span class="badge badge-${account.status.toLowerCase()}">${account.status}</span></td>
                        <td>${formatDate(account.opened_at)}</td>
                        <td>
                            <button class="btn btn-sm btn-primary" onclick="showDepositModal('${account.account_id}')">Deposit</button>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

async function showCreateAccountModal() {
    const users = await apiCall('/users');
    const select = document.getElementById('account-user-select');
    select.innerHTML = users.map(user =>
        `<option value="${user.user_id}">${escapeHtml(user.full_name)} (${escapeHtml(user.email)})</option>`
    ).join('');
    showModal('create-account-modal');
}

async function createAccount(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = {
        user_id: formData.get('user_id'),
        name: formData.get('name'),
        cash_balance: parseFloat(formData.get('cash_balance'))
    };

    try {
        await apiCall('/accounts', 'POST', data);
        showToast('Account created successfully!', 'success');
        closeModal();
        loadAccounts();
    } catch (error) {
        showToast('Failed to create account', 'error');
    }
}

function showDepositModal(accountId) {
    const amount = prompt('Enter deposit amount:');
    if (amount && !isNaN(amount)) {
        updateBalance(accountId, parseFloat(amount));
    }
}

async function updateBalance(accountId, amount) {
    try {
        await apiCall(`/accounts/${accountId}/balance`, 'PUT', { amount });
        showToast('Balance updated successfully!', 'success');
        loadAccounts();
    } catch (error) {
        showToast('Failed to update balance', 'error');
    }
}

// ==================== SECURITIES ====================
async function loadSecurities() {
    try {
        const securities = await apiCall('/securities');
        cachedData.securities = securities;
        displaySecurities(securities);
    } catch (error) {
        console.error('Error loading securities:', error);
    }
}

function displaySecurities(securities) {
    const container = document.getElementById('securities-table');
    if (!securities || securities.length === 0) {
        container.innerHTML = '<p style="color: var(--text-secondary); padding: 2rem; text-align: center;">No securities found</p>';
        return;
    }

    container.innerHTML = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>Ticker</th>
                    <th>Name</th>
                    <th>Sector</th>
                    <th>Exchange</th>
                </tr>
            </thead>
            <tbody>
                ${securities.map(security => `
                    <tr>
                        <td style="color: var(--accent-primary); font-weight: 700; font-size: 1rem;">${escapeHtml(security.ticker)}</td>
                        <td style="color: var(--text-primary); font-weight: 600;">${escapeHtml(security.name)}</td>
                        <td>${escapeHtml(security.sector || 'N/A')}</td>
                        <td>${escapeHtml(security.exchange)}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

async function searchSecurities() {
    const query = document.getElementById('security-search').value;
    if (!query) {
        displaySecurities(cachedData.securities);
        return;
    }

    try {
        const results = await apiCall(`/securities/search?q=${encodeURIComponent(query)}`);
        displaySecurities(results);
    } catch (error) {
        console.error('Error searching securities:', error);
    }
}

async function showCreateSecurityModal() {
    showModal('create-security-modal');
}

async function createSecurity(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = {
        ticker: formData.get('ticker').toUpperCase(),
        name: formData.get('name'),
        sector: formData.get('sector'),
        exchange: formData.get('exchange')
    };

    try {
        await apiCall('/securities', 'POST', data);
        showToast('Security added successfully!', 'success');
        closeModal();
        loadSecurities();
    } catch (error) {
        showToast('Failed to add security', 'error');
    }
}

// ==================== ORDERS ====================
async function loadOrders() {
    const status = document.getElementById('order-status-filter')?.value || '';
    try {
        const endpoint = status ? `/orders?status=${status}` : '/orders';
        const orders = await apiCall(endpoint);
        cachedData.orders = orders;
        displayOrders(orders);
    } catch (error) {
        console.error('Error loading orders:', error);
    }
}

function displayOrders(orders) {
    const container = document.getElementById('orders-table');
    if (!orders || orders.length === 0) {
        container.innerHTML = '<p style="color: var(--text-secondary); padding: 2rem; text-align: center;">No orders found</p>';
        return;
    }

    container.innerHTML = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>Ticker</th>
                    <th>Account</th>
                    <th>Side</th>
                    <th>Type</th>
                    <th>Quantity</th>
                    <th>Limit Price</th>
                    <th>Status</th>
                    <th>Placed At</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                ${orders.map(order => `
                    <tr>
                        <td style="color: var(--accent-primary); font-weight: 700;">${escapeHtml(order.ticker)}</td>
                        <td>${escapeHtml(order.account_name)}</td>
                        <td style="color: ${order.side === 'BUY' ? 'var(--accent-success)' : 'var(--accent-danger)'}; font-weight: 600;">
                            ${order.side}
                        </td>
                        <td>${order.type}</td>
                        <td>${order.quantity}</td>
                        <td>${order.limit_price ? '$' + formatNumber(order.limit_price) : 'N/A'}</td>
                        <td><span class="badge badge-${order.status.toLowerCase()}">${order.status}</span></td>
                        <td>${formatDate(order.placed_at)}</td>
                        <td>
                            ${order.status === 'OPEN' ? `
                                <button class="btn btn-sm btn-success" onclick="updateOrderStatus('${order.order_id}', 'FILLED')">Fill</button>
                                <button class="btn btn-sm btn-danger" onclick="updateOrderStatus('${order.order_id}', 'CANCELED')">Cancel</button>
                            ` : ''}
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

async function showCreateOrderModal() {
    const [accounts, securities] = await Promise.all([
        apiCall('/accounts'),
        apiCall('/securities')
    ]);

    document.getElementById('order-account-select').innerHTML = accounts.map(account =>
        `<option value="${account.account_id}">${escapeHtml(account.name)} (${escapeHtml(account.full_name)})</option>`
    ).join('');

    document.getElementById('order-security-select').innerHTML = securities.map(security =>
        `<option value="${security.security_id}">${escapeHtml(security.ticker)} - ${escapeHtml(security.name)}</option>`
    ).join('');

    showModal('create-order-modal');
}

function toggleLimitPrice() {
    const orderType = document.getElementById('order-type').value;
    const limitPriceGroup = document.getElementById('limit-price-group');
    limitPriceGroup.style.display = orderType === 'LIMIT' ? 'block' : 'none';
}

async function createOrder(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = {
        account_id: formData.get('account_id'),
        security_id: formData.get('security_id'),
        side: formData.get('side'),
        type: formData.get('type'),
        quantity: parseInt(formData.get('quantity')),
        limit_price: formData.get('limit_price') ? parseFloat(formData.get('limit_price')) : null
    };

    try {
        await apiCall('/orders', 'POST', data);
        showToast('Order placed successfully!', 'success');
        closeModal();
        loadOrders();
    } catch (error) {
        showToast('Failed to place order', 'error');
    }
}

async function updateOrderStatus(orderId, status) {
    try {
        await apiCall(`/orders/${orderId}/status`, 'PUT', { status });
        showToast(`Order ${status.toLowerCase()} successfully!`, 'success');
        loadOrders();
    } catch (error) {
        showToast('Failed to update order status', 'error');
    }
}

// ==================== HOLDINGS ====================
async function loadHoldings() {
    try {
        const holdings = await apiCall('/holdings');
        cachedData.holdings = holdings;
        displayHoldings(holdings);
    } catch (error) {
        console.error('Error loading holdings:', error);
    }
}

function displayHoldings(holdings) {
    const container = document.getElementById('holdings-table');
    if (!holdings || holdings.length === 0) {
        container.innerHTML = '<p style="color: var(--text-secondary); padding: 2rem; text-align: center;">No holdings found</p>';
        return;
    }

    container.innerHTML = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>Ticker</th>
                    <th>Name</th>
                    <th>Account</th>
                    <th>Quantity</th>
                    <th>Avg Cost</th>
                    <th>Total Cost</th>
                    <th>Updated</th>
                </tr>
            </thead>
            <tbody>
                ${holdings.map(holding => `
                    <tr>
                        <td style="color: var(--accent-primary); font-weight: 700;">${escapeHtml(holding.ticker)}</td>
                        <td style="color: var(--text-primary);">${escapeHtml(holding.name)}</td>
                        <td>${escapeHtml(holding.account_name)}</td>
                        <td style="font-weight: 600;">${holding.quantity}</td>
                        <td>$${formatNumber(holding.avg_cost)}</td>
                        <td style="color: var(--accent-success); font-weight: 600;">$${formatNumber(holding.total_cost)}</td>
                        <td>${formatDate(holding.updated_at)}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

async function showCreateHoldingModal() {
    const [accounts, securities] = await Promise.all([
        apiCall('/accounts'),
        apiCall('/securities')
    ]);

    document.getElementById('holding-account-select').innerHTML = accounts.map(account =>
        `<option value="${account.account_id}">${escapeHtml(account.name)} (${escapeHtml(account.full_name)})</option>`
    ).join('');

    document.getElementById('holding-security-select').innerHTML = securities.map(security =>
        `<option value="${security.security_id}">${escapeHtml(security.ticker)} - ${escapeHtml(security.name)}</option>`
    ).join('');

    showModal('create-holding-modal');
}

async function createHolding(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = {
        account_id: formData.get('account_id'),
        security_id: formData.get('security_id'),
        quantity: parseInt(formData.get('quantity')),
        avg_cost: parseFloat(formData.get('avg_cost'))
    };

    try {
        await apiCall('/holdings', 'POST', data);
        showToast('Holding added successfully!', 'success');
        closeModal();
        loadHoldings();
    } catch (error) {
        showToast('Failed to add holding', 'error');
    }
}

// ==================== WATCHLISTS ====================
async function loadWatchlists() {
    try {
        const watchlists = await apiCall('/watchlists');
        cachedData.watchlists = watchlists;
        displayWatchlists(watchlists);
    } catch (error) {
        console.error('Error loading watchlists:', error);
    }
}

function displayWatchlists(watchlists) {
    const container = document.getElementById('watchlists-container');
    if (!watchlists || watchlists.length === 0) {
        container.innerHTML = '<p style="color: var(--text-secondary); padding: 2rem; text-align: center;">No watchlists found</p>';
        return;
    }

    container.innerHTML = `
        <div class="watchlists-grid">
            ${watchlists.map(watchlist => `
                <div class="watchlist-card">
                    <div class="watchlist-header">
                        <div>
                            <h3 style="margin-bottom: 0.25rem;">${escapeHtml(watchlist.name)}</h3>
                            <p style="color: var(--text-secondary); font-size: 0.875rem;">
                                ${escapeHtml(watchlist.full_name)} • ${watchlist.item_count} items
                            </p>
                        </div>
                        <button class="btn btn-sm btn-danger" onclick="deleteWatchlist('${watchlist.watchlist_id}')">Delete</button>
                    </div>
                    <button class="btn btn-sm btn-primary" onclick="viewWatchlistDetails('${watchlist.watchlist_id}', '${escapeHtml(watchlist.name)}')">
                        View Details
                    </button>
                </div>
            `).join('')}
        </div>
    `;
}

async function showCreateWatchlistModal() {
    const users = await apiCall('/users');
    document.getElementById('watchlist-user-select').innerHTML = users.map(user =>
        `<option value="${user.user_id}">${escapeHtml(user.full_name)} (${escapeHtml(user.email)})</option>`
    ).join('');
    showModal('create-watchlist-modal');
}

async function createWatchlist(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = {
        user_id: formData.get('user_id'),
        name: formData.get('name')
    };

    try {
        await apiCall('/watchlists', 'POST', data);
        showToast('Watchlist created successfully!', 'success');
        closeModal();
        loadWatchlists();
    } catch (error) {
        showToast('Failed to create watchlist', 'error');
    }
}

async function viewWatchlistDetails(watchlistId, name) {
    try {
        const watchlist = await apiCall(`/watchlists/${watchlistId}`);
        alert(`Watchlist: ${name}\n\nItems:\n${watchlist.items.map(item => `• ${item.ticker} - ${item.name}`).join('\n') || 'No items'}`);
    } catch (error) {
        showToast('Failed to load watchlist details', 'error');
    }
}

async function deleteWatchlist(watchlistId) {
    if (!confirm('Are you sure you want to delete this watchlist?')) return;

    try {
        await apiCall(`/watchlists/${watchlistId}`, 'DELETE');
        showToast('Watchlist deleted successfully!', 'success');
        loadWatchlists();
    } catch (error) {
        showToast('Failed to delete watchlist', 'error');
    }
}

// ==================== ANALYTICS ====================
async function loadAnalytics() {
    try {
        const [topHoldings, portfolioValues, emptyAccounts] = await Promise.all([
            apiCall('/analytics/top-holdings'),
            apiCall('/analytics/portfolio-value'),
            apiCall('/analytics/accounts-without-holdings')
        ]);

        displayTopHoldings(topHoldings);
        displayPortfolioValues(portfolioValues);
        displayEmptyAccounts(emptyAccounts);
    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

function displayTopHoldings(holdings) {
    const container = document.getElementById('top-holdings');
    if (!holdings || holdings.length === 0) {
        container.innerHTML = '<p style="color: var(--text-secondary);">No data available</p>';
        return;
    }

    container.innerHTML = holdings.map((holding, index) => `
        <div class="analytics-item">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong style="color: var(--text-primary);">${index + 1}. ${escapeHtml(holding.ticker)}</strong>
                    <div style="font-size: 0.875rem; color: var(--text-secondary);">${escapeHtml(holding.name)}</div>
                </div>
                <div style="text-align: right;">
                    <div style="color: var(--accent-success); font-weight: 600;">$${formatNumber(holding.total_value)}</div>
                    <div style="font-size: 0.875rem; color: var(--text-secondary);">${formatNumber(holding.total_shares)} shares</div>
                </div>
            </div>
        </div>
    `).join('');
}

function displayPortfolioValues(portfolios) {
    const container = document.getElementById('portfolio-values');
    if (!portfolios || portfolios.length === 0) {
        container.innerHTML = '<p style="color: var(--text-secondary);">No data available</p>';
        return;
    }

    container.innerHTML = portfolios.map(portfolio => `
        <div class="analytics-item">
            <div>
                <strong style="color: var(--text-primary);">${escapeHtml(portfolio.name)}</strong>
                <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.25rem;">
                    ${escapeHtml(portfolio.full_name)}
                </div>
                <div style="display: flex; gap: 1rem; margin-top: 0.5rem; font-size: 0.875rem;">
                    <span>Cash: <strong style="color: var(--accent-success);">$${formatNumber(portfolio.cash_balance)}</strong></span>
                    <span>Holdings: <strong>$${formatNumber(portfolio.holdings_value)}</strong></span>
                    <span>Total: <strong style="color: var(--accent-primary);">$${formatNumber(portfolio.total_value)}</strong></span>
                </div>
            </div>
        </div>
    `).join('');
}

function displayEmptyAccounts(accounts) {
    const container = document.getElementById('empty-accounts');
    if (!accounts || accounts.length === 0) {
        container.innerHTML = '<p style="color: var(--text-secondary);">All accounts have holdings!</p>';
        return;
    }

    container.innerHTML = accounts.map(account => `
        <div class="analytics-item">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong style="color: var(--text-primary);">${escapeHtml(account.name)}</strong>
                    <div style="font-size: 0.875rem; color: var(--text-secondary);">${escapeHtml(account.full_name)}</div>
                </div>
                <span style="color: var(--accent-success); font-weight: 600;">$${formatNumber(account.cash_balance)}</span>
            </div>
        </div>
    `).join('');
}

// ==================== MODAL MANAGEMENT ====================
function showModal(modalId) {
    document.getElementById('modal-overlay').classList.add('active');
    document.getElementById(modalId).classList.add('active');
}

function closeModal() {
    document.getElementById('modal-overlay').classList.remove('active');
    document.querySelectorAll('.modal').forEach(modal => {
        modal.classList.remove('active');
    });
    // Reset forms
    document.querySelectorAll('form').forEach(form => form.reset());
}

// ==================== NOTIFICATIONS ====================
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.add('show');

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// ==================== UTILITY FUNCTIONS ====================
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function formatNumber(number) {
    if (!number && number !== 0) return '0.00';
    return parseFloat(number).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
