// ==================== CONFIGURATION ====================
const API_BASE_URL = 'http://localhost:5001/api';

// ==================== AUTH HELPERS (FRONTEND) ====================
function getToken() {
    return localStorage.getItem('token');
}

function clearToken() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
}

function setCurrentUser(user) {
    window.currentUser = user; // keep a global for convenience
    localStorage.setItem('user', JSON.stringify(user));
}

function getStoredUser() {
    const raw = localStorage.getItem('user');
    if (!raw) return null;
    try {
        return JSON.parse(raw);
    } catch {
        return null;
    }
}

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
    initApp();
});

async function initApp() {
    // Check if user has token
    const token = getToken();

    if (!token) {
        // No token - redirect to login page
        window.location.href = '/';
        return;
    }

    // Verify session with backend
    try {
        const data = await apiFetch('/auth/me');
        const user = data.user;

        // Store user info globally + in localStorage
        setCurrentUser(user);

        // Update UI with user info
        document.getElementById('current-user-name').textContent = user.full_name;
        document.getElementById('current-user-role').textContent = user.role;

        // Role-based UI setup and data loading
        if (user.role === 'ADMIN') {
            // Show admin navigation
            document.querySelectorAll('.admin-only').forEach(el => {
                el.style.display = '';
            });
            // Initialize navigation and load admin dashboard
            initNavigation();
            loadAdminDashboard();
        } else {
            // USER role - hide admin features and load user-specific dashboard
            document.querySelectorAll('.admin-only').forEach(el => {
                el.style.display = 'none';
            });
            initNavigation();
            loadUserDashboard(user.user_id);
        }

    } catch (error) {
        // Auth failed - clear and redirect to login
        console.error('Session verification failed:', error);
        clearToken();
        window.location.href = '/';
    }
}

// Logout function
function logout() {
    const token = getToken();

    // Call backend logout
    if (token) {
        apiFetch('/auth/logout', { method: 'POST' })
            .catch(err => console.error('Logout error:', err));
    }

    // Clear local data
    clearToken();

    // Redirect to login
    window.location.href = '/';
}


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
    const navItem = document.querySelector(`[data-page="${page}"]`);
    if (navItem) navItem.classList.add('active');

    // Update page visibility
    document.querySelectorAll('.page').forEach(p => {
        p.classList.remove('active');
    });
    const pageDiv = document.getElementById(`${page}-page`);
    if (pageDiv) pageDiv.classList.add('active');

    currentPage = page;

    // Load page data
    const user = window.currentUser;
    const isUser = user && user.role !== 'ADMIN';
    const userId = user ? user.user_id : null;

    switch (page) {
        case 'dashboard':
            if (isUser) {
                loadUserDashboard(userId);
            } else {
                loadAdminDashboard();
            }
            break;
        case 'users':
            // only admins can view all users
            if (!isUser) {
                loadUsers();
            }
            break;
        case 'accounts':
            if (isUser) {
                loadUserAccounts(userId);
            } else {
                loadAccounts();
            }
            break;
        case 'securities':
            loadSecurities();
            break;
        case 'orders':
            if (isUser) {
                loadUserOrders(userId);
            } else {
                loadOrders();
            }
            break;
        case 'holdings':
            if (isUser) {
                loadUserHoldings(userId);
            } else {
                loadHoldings();
            }
            break;
        case 'watchlists':
            loadWatchlists();
            break;
        case 'analytics':
            loadAnalytics();
            break;
        case 'admin':
            if (!isUser) {
                loadAdminPanel();
            }
            break;
    }
}

// ==================== API CALLS ====================
// ==================== API CALLS ====================
async function apiCall(endpoint, method = 'GET', data = null) {
    console.log(`[API] ${method} ${endpoint}`, data); // Debug log
    try {
        const token = getToken();

        const options = {
            method,
            headers: {
                'Content-Type': 'application/json'
            }
        };

        if (token) {
            options.headers['Authorization'] = `Bearer ${token}`;
        }

        if (data !== null && data !== undefined) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);

        // Handle 204 No Content or empty responses
        if (response.status === 204) {
            return {};
        }

        const text = await response.text();
        let result = {};
        try {
            if (text) {
                result = JSON.parse(text);
            }
        } catch (e) {
            console.error('[API] Failed to parse JSON response:', text);
            throw new Error(`Server returned invalid JSON: ${response.statusText}`);
        }

        if (!response.ok) {
            console.error('[API] Request failed:', response.status, result);
            const errorMsg = result.error || result.message || `API request failed with status ${response.status}`;
            throw new Error(errorMsg);
        }

        console.log(`[API] Success:`, result);
        return result;
    } catch (error) {
        console.error('[API] Error:', error);
        showToast(error.message, 'error');
        throw error;
    }
}

// Wrapper so we can call like apiFetch('/auth/me')
async function apiFetch(endpoint, options = {}) {
    const method = options.method || 'GET';
    const data = options.data || null;
    return apiCall(endpoint, method, data);
}

// ==================== DASHBOARD ====================

// Admin dashboard - shows all system data
async function loadAdminDashboard() {
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
        console.error('Error loading admin dashboard:', error);
    }
}

// User dashboard - shows only user's data
async function loadUserDashboard(userId) {
    console.log('Loading user dashboard for:', userId);
    try {
        // Fetch user portfolio summary
        const summary = await apiFetch(`/users/${userId}/portfolio-summary`);
        console.log('Portfolio summary:', summary);
        displayUserStats(summary);

        // Fetch recent holdings and accounts for dashboard widgets
        const [holdings, accounts] = await Promise.all([
            apiFetch(`/users/${userId}/holdings`),
            apiFetch(`/users/${userId}/accounts`)
        ]);
        console.log('Holdings:', holdings);
        console.log('Accounts:', accounts);

        // FIX: pass (accounts, holdings) in correct order
        displayUserPortfolio(accounts, holdings);
    } catch (error) {
        console.error('Error loading user dashboard:', error);
        showToast('Error loading your portfolio. Please try again.', 'error');
    }
}

function displayUserStats(summary) {
    // Show user-specific stats
    document.getElementById('stat-users').textContent = summary.total_accounts || 0;
    document.querySelector('#stat-users').parentElement.querySelector('p').textContent = 'My Accounts';

    document.getElementById('stat-accounts').textContent = `$${formatNumber(summary.total_cash || 0)}`;
    document.querySelector('#stat-accounts').parentElement.querySelector('p').textContent = 'Cash Balance';

    document.getElementById('stat-securities').textContent = summary.unique_holdings || 0;
    document.querySelector('#stat-securities').parentElement.querySelector('p').textContent = 'Stocks Owned';

    document.getElementById('stat-orders').textContent = `$${formatNumber(summary.total_value || 0)}`;
    document.querySelector('#stat-orders').parentElement.querySelector('p').textContent = 'Total Value';
}

function displayUserPortfolio(accounts, holdings, orders) {
    // Display user's accounts in the "Recent Orders" section
    const accountsContainer = document.getElementById('recent-orders');
    accountsContainer.parentElement.querySelector('h3').textContent = 'My Accounts';

    if (!accounts || accounts.length === 0) {
        accountsContainer.innerHTML = '<p style="color: var(--text-secondary);">No accounts found</p>';
    } else {
        accountsContainer.innerHTML = accounts.map(account => `
            <div class="recent-item">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="color: var(--text-primary);">${escapeHtml(account.name)}</strong>
                        <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.25rem;">
                            ${account.status}
                        </div>
                    </div>
                    <span style="color: var(--accent-success); font-weight: 600;">$${formatNumber(account.cash_balance)}</span>
                </div>
            </div>
        `).join('');
    }

    // Display user's holdings in the "Most Traded" section
    const holdingsContainer = document.getElementById('most-traded');
    holdingsContainer.parentElement.querySelector('h3').textContent = 'My Holdings';

    if (!holdings || holdings.length === 0) {
        holdingsContainer.innerHTML = '<p style="color: var(--text-secondary);">No holdings found</p>';
    } else {
        holdingsContainer.innerHTML = holdings.slice(0, 5).map(holding => `
            <div class="recent-item">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="color: var(--accent-primary);">${escapeHtml(holding.ticker)}</strong>
                        <div style="font-size: 0.875rem; color: var(--text-secondary);">${escapeHtml(holding.name)}</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="color: var(--text-primary); font-weight: 600;">${holding.quantity} shares</div>
                        <div style="font-size: 0.875rem; color: var(--text-secondary);">$${formatNumber(holding.total_cost)}</div>
                    </div>
                </div>
            </div>
        `).join('');
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

    // Backend now expects: full_name, email, password, role
    // Your modal only has full_name + email, so we default password + role
    const data = {
        full_name: formData.get('full_name'),
        email: formData.get('email'),
        password: formData.get('password') || 'demo123',
        role: (formData.get('role') || 'USER').toUpperCase()
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

async function loadUserAccounts(userId) {
    try {
        const accounts = await apiCall(`/users/${userId}/accounts`);
        cachedData.accounts = accounts;
        displayAccounts(accounts);
        // Hide "Owner" column for user view since it's redundant
        const table = document.querySelector('#accounts-table table');
        if (table) {
            // Hide header
            table.querySelector('th:nth-child(2)').style.display = 'none';
            // Hide cells
            table.querySelectorAll('td:nth-child(2)').forEach(td => td.style.display = 'none');
        }
    } catch (error) {
        console.error('Error loading user accounts:', error);
    }
}

function displayAccounts(accounts) {
    const container = document.getElementById('accounts-table');
    if (!accounts || accounts.length === 0) {
        container.innerHTML = '<p style="color: var(--text-secondary); padding: 2rem; text-align: center;">No accounts found</p>';
        return;
    }

    const isAdmin = window.currentUser && window.currentUser.role === 'ADMIN';

    container.innerHTML = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>Account Name</th>
                    <th>Owner</th>
                    <th>Cash Balance</th>
                    <th>Status</th>
                    <th>Opened</th>
                    ${isAdmin ? '<th>Actions</th>' : ''}
                </tr>
            </thead>
            <tbody>
                ${accounts.map(account => `
                    <tr>
                        <td style="color: var(--text-primary); font-weight: 600;">
                            ${escapeHtml(account.name)}
                        </td>
                        <td>${escapeHtml(account.full_name || 'Me')}</td>
                        <td style="color: var(--accent-success); font-weight: 600;">
                            $${formatNumber(account.cash_balance)}
                        </td>
                        <td>
                            <span class="badge badge-${account.status.toLowerCase()}">
                                ${account.status}
                            </span>
                        </td>
                        <td>${formatDate(account.opened_at)}</td>
                        ${isAdmin
            ? `<td>
                                       <button class="btn btn-sm btn-primary"
                                               onclick="showDepositModal('${account.account_id}')">
                                           Deposit
                                       </button>
                                   </td>`
            : ''
        }
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;

    // If not admin, hide the "Owner" column (same as before)
    if (!isAdmin) {
        const table = container.querySelector('table');
        if (table) {
            table.querySelector('th:nth-child(2)').style.display = 'none';
            table.querySelectorAll('td:nth-child(2)').forEach(td => td.style.display = 'none');
        }
    }
}

async function showCreateAccountModal() {
    const user = window.currentUser;
    const select = document.getElementById('account-user-select');

    if (user.role === 'ADMIN') {
        const users = await apiCall('/users');
        select.innerHTML = users.map(u =>
            `<option value="${u.user_id}">${escapeHtml(u.full_name)} (${escapeHtml(u.email)})</option>`
        ).join('');
        select.disabled = false;
        select.parentElement.style.display = 'block';
    } else {
        // For regular users, pre-select themselves and hide the dropdown
        select.innerHTML = `<option value="${user.user_id}" selected>${user.full_name}</option>`;
        select.disabled = true;
        select.parentElement.style.display = 'none';
    }

    showModal('create-account-modal');
}

async function createAccount(event) {
    event.preventDefault();
    const formData = new FormData(event.target);

    // If user select was disabled (for regular users), we need to manually get the user_id
    let userId = formData.get('user_id');
    if (!userId) {
        userId = document.getElementById('account-user-select').value;
    }

    const data = {
        user_id: userId,
        name: formData.get('name'),
        cash_balance: parseFloat(formData.get('cash_balance'))
    };

    try {
        await apiCall('/accounts', 'POST', data);
        showToast('Account created successfully!', 'success');
        closeModal();

        // Reload correct list
        if (window.currentUser.role === 'ADMIN') {
            loadAccounts();
        } else {
            loadUserAccounts(window.currentUser.user_id);
        }
    } catch (error) {
        showToast('Failed to create account', 'error');
    }
}

function showDepositModal(accountId) {
    const raw = prompt('Enter deposit amount:');
    if (raw === null) return; // user clicked cancel

    const amount = parseFloat(raw);
    if (isNaN(amount) || amount <= 0) {
        showToast('Please enter a valid positive amount', 'error');
        return;
    }

    updateBalance(accountId, amount);
}

async function updateBalance(accountId, amount) {
    try {
        await apiCall(`/accounts/${accountId}/balance`, 'PUT', { amount });

        showToast('Balance updated successfully!', 'success');

        // Reload correct list
        if (window.currentUser.role === 'ADMIN') {
            loadAccounts();
        } else {
            loadUserAccounts(window.currentUser.user_id);
        }
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
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                ${securities.map(security => `
                    <tr>
                        <td style="color: var(--accent-primary); font-weight: 700; font-size: 1rem;">${escapeHtml(security.ticker)}</td>
                        <td style="color: var(--text-primary); font-weight: 600;">${escapeHtml(security.name)}</td>
                        <td>${escapeHtml(security.sector || 'N/A')}</td>
                        <td>${escapeHtml(security.exchange)}</td>
                        <td>
                            <button class="btn btn-sm btn-secondary" onclick="openAddToWatchlistModal('${security.security_id}', '${escapeHtml(security.ticker)}')">
                                + Watchlist
                            </button>
                        </td>
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

async function loadUserOrders(userId) {
    const status = document.getElementById('order-status-filter')?.value || '';
    try {
        const orders = await apiCall(`/users/${userId}/orders`);

        let filteredOrders = orders;
        if (status) {
            filteredOrders = orders.filter(o => o.status === status);
        }

        cachedData.orders = filteredOrders;
        displayOrders(filteredOrders);
    } catch (error) {
        console.error('Error loading user orders:', error);
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
    const user = window.currentUser;
    let accounts = [];

    if (user.role === 'ADMIN') {
        accounts = await apiCall('/accounts');
    } else {
        accounts = await apiCall(`/users/${user.user_id}/accounts`);
    }

    const securities = await apiCall('/securities');

    document.getElementById('order-account-select').innerHTML = accounts.map(account =>
        `<option value="${account.account_id}">${escapeHtml(account.name)} ($${formatNumber(account.cash_balance)})</option>`
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

// Handle order status filter change based on user role
function handleOrderStatusFilterChange() {
    const user = window.currentUser;
    if (!user) return;

    const isUser = user.role !== 'ADMIN';
    if (isUser) {
        loadUserOrders(user.user_id);
    } else {
        loadOrders();
    }
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

        // Reload correct list
        if (window.currentUser.role === 'ADMIN') {
            loadOrders();
        } else {
            loadUserOrders(window.currentUser.user_id);
        }
    } catch (error) {
        showToast('Failed to place order', 'error');
    }
}

async function updateOrderStatus(orderId, status) {
    try {
        await apiCall(`/orders/${orderId}/status`, 'PUT', { status });
        showToast(`Order ${status.toLowerCase()} successfully!`, 'success');

        // Reload correct list
        if (window.currentUser.role === 'ADMIN') {
            loadOrders();
        } else {
            loadUserOrders(window.currentUser.user_id);
        }
    } catch (error) {
        showToast(error.message || 'Failed to update order status', 'error');
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

async function loadUserHoldings(userId) {
    try {
        const holdings = await apiCall(`/users/${userId}/holdings`);
        cachedData.holdings = holdings;
        displayHoldings(holdings);
    } catch (error) {
        console.error('Error loading user holdings:', error);
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
    const user = window.currentUser;
    let accounts = [];

    if (user.role === 'ADMIN') {
        accounts = await apiCall('/accounts');
    } else {
        accounts = await apiCall(`/users/${user.user_id}/accounts`);
    }

    const securities = await apiCall('/securities');

    document.getElementById('holding-account-select').innerHTML = accounts.map(account =>
        `<option value="${account.account_id}">${escapeHtml(account.name)} (${escapeHtml(account.full_name || 'Me')})</option>`
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

        // Reload correct list
        if (window.currentUser.role === 'ADMIN') {
            loadHoldings();
        } else {
            loadUserHoldings(window.currentUser.user_id);
        }
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

    const currentUserId = window.currentUser.user_id; // Fix: Ensure we compare with stored user ID
    const isAdmin = window.currentUser.role === 'ADMIN';

    container.innerHTML = `
        <div class="watchlists-grid">
            ${watchlists.map(watchlist => {
        const canDelete = isAdmin || watchlist.user_id === currentUserId;
        return `
                <div class="watchlist-card">
                    <div class="watchlist-header">
                        <div>
                            <h3 style="margin-bottom: 0.25rem;">${escapeHtml(watchlist.name)}</h3>
                            <p style="color: var(--text-secondary); font-size: 0.875rem;">
                                ${escapeHtml(watchlist.full_name)} • ${watchlist.item_count} items
                            </p>
                        </div>
                        ${canDelete ? `<button class="btn btn-sm btn-danger" onclick="deleteWatchlist('${watchlist.watchlist_id}')">Delete</button>` : ''}
                    </div>
                    <button class="btn btn-sm btn-primary" onclick="viewWatchlistDetails('${watchlist.watchlist_id}', '${escapeHtml(watchlist.name)}')">
                        View Details
                    </button>
                </div>
            `;
    }).join('')}
        </div>
    `;
}

async function showCreateWatchlistModal() {
    // Watchlists are always created for the current logged-in user.
    // We don't need to pick a user in the UI anymore.
    showModal('create-watchlist-modal');
}

async function createWatchlist(event) {
    event.preventDefault();
    const formData = new FormData(event.target);

    // backend handles the user_id automatically, just send the name
    const data = {
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
        const modalTitle = document.getElementById('view-watchlist-title');
        const modalContent = document.getElementById('view-watchlist-content');

        modalTitle.textContent = `Details: ${name}`;

        if (!watchlist.items || watchlist.items.length === 0) {
            modalContent.innerHTML = '<p style="color: var(--text-secondary); text-align: center; padding: 1rem;">No items in this watchlist</p>';
        } else {
            modalContent.innerHTML = `
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Ticker</th>
                            <th>Name</th>
                            <th>Sector</th>
                            <th>Added</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${watchlist.items.map(item => `
                            <tr>
                                <td style="font-weight: 600; color: var(--accent-primary);">${escapeHtml(item.ticker)}</td>
                                <td>${escapeHtml(item.name)}</td>
                                <td>${escapeHtml(item.sector || '-')}</td>
                                <td>${new Date(item.added_at).toLocaleDateString()}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        }

        showModal('view-watchlist-modal');
    } catch (error) {
        console.error(error);
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
        console.error('Delete failed:', error);
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

// ==================== WATCHLIST HELPERS ====================

async function openAddToWatchlistModal(securityId, ticker) {
    document.getElementById('add-watchlist-security-id').value = securityId;
    document.getElementById('add-watchlist-ticker').textContent = ticker;

    // Load watchlists for dropdown
    const select = document.getElementById('add-watchlist-select');
    select.innerHTML = '<option>Loading...</option>';

    try {
        const watchlists = await apiCall('/watchlists');
        if (watchlists.length === 0) {
            select.innerHTML = '<option value="" disabled selected>No watchlists found - Create one first!</option>';
        } else {
            select.innerHTML = watchlists.map(w =>
                `<option value="${w.watchlist_id}">${escapeHtml(w.name)}</option>`
            ).join('');
        }
    } catch (error) {
        select.innerHTML = '<option value="" disabled>Error loading watchlists</option>';
    }

    showModal('add-to-watchlist-modal');
}

async function addToWatchlist(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const watchlistId = formData.get('watchlist_id');
    const securityId = formData.get('security_id');

    if (!watchlistId) {
        showToast('Please select a watchlist', 'error');
        return;
    }

    try {
        await apiCall(`/watchlists/${watchlistId}/items`, 'POST', { security_id: securityId });
        showToast('Added to watchlist successfully!', 'success');
        closeModal();
        // Optional: reload watchlists if currently on that page
        if (currentPage === 'watchlists') {
            loadWatchlists();
        }
    } catch (error) {
        showToast(error.message || 'Failed to add to watchlist', 'error');
    }
}
