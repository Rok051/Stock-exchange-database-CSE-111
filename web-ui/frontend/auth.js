// Authentication and initialization additions for app.js
// Add these to the beginning of your existing app.js file

// ==================== AUTH ADDITIONS ====================

// Get auth token from localStorage
function getAuthToken() {
    return localStorage.getItem('token');
}

// Get current user from localStorage
function getCurrentUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
}

// Check if user is authenticated
function isAuthenticated() {
    return !!getAuthToken();
}

// Check if user is admin
function isAdmin() {
    const user = getCurrentUser();
    return user && user.role === 'ADMIN';
}

// Logout function
function logout() {
    const token = getAuthToken();

    //Call logout endpoint
    if (token) {
        fetch(`${API_BASE_URL}/auth/logout`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        }).catch(err => console.error('Logout error:', err));
    }

    // Clear local storage
    localStorage.removeItem('token');
    localStorage.removeItem('user');

    // Redirect to login
    window.location.href = '/login.html';
}

// Initialize auth on page load
function initAuth() {
    // Check if authenticated
    if (!isAuthenticated()) {
        window.location.href = '/login.html';
        return false;
    }

    // Load current user info
    const user = getCurrentUser();
    if (user) {
        document.getElementById('current-user-name').textContent = user.full_name;
        document.getElementById('current-user-role').textContent = user.role;

        // Show/hide admin panel based on role
        if (isAdmin()) {
            document.querySelectorAll('.admin-only').forEach(el => {
                el.style.display = '';
            });
        }
    }

    return true;
}

// Modified apiCall to include auth token
const originalApiCall = window.apiCall;
window.apiCall = async function (endpoint, method = 'GET', data = null) {
    const token = getAuthToken();

    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` })
        }
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, options);

    // Handle 401 - redirect to login
    if (response.status === 401) {
        logout();
        return;
    }

    let result;
    try {
        result = await response.json();
    } catch (e) {
        throw new Error(`Server returned invalid JSON: ${response.statusText}`);
    }

    if (!response.ok) {
        const errorMsg = result.error || result.message || `API request failed with status ${response.status}`;
        throw new Error(errorMsg);
    }

    return result;
};

// Admin functions
async function loadAdminStats() {
    try {
        const stats = await apiCall('/admin/stats');

        // Update stats
        const usersByRole = stats.users_by_role || {};
        document.getElementById('admin-stat-users').textContent = usersByRole.USER || 0;
        document.getElementById('admin-stat-admins').textContent = usersByRole.ADMIN || 0;

        const totalCash = stats.total_cash || 0;
        document.getElementById('admin-stat-cash').textContent = formatCurrency(totalCash);

        const accountsByStatus = stats.accounts_by_status || {};
        document.getElementById('admin-stat-active-accounts').textContent = accountsByStatus.ACTIVE || 0;

        // Load users table
        loadAdminUsers();

        // Load recent activity
        loadAdminActivity(stats.recent_activity || []);
    } catch (error) {
        console.error('Error loading admin stats:', error);
    }
}

async function loadAdminUsers() {
    try {
        const users = await apiCall('/admin/users');

        let html = '<table><thead><tr>';
        html += '<th>Name</th><th>Email</th><th>Role</th><th>Accounts</th><th>Actions</th>';
        html += '</tr></thead><tbody>';

        users.forEach(user => {
            html += `<tr>
                <td>${escapeHtml(user.full_name)}</td>
                <td>${escapeHtml(user.email)}</td>
                <td><span class="badge ${user.role === 'ADMIN' ? 'badge-success' : 'badge-info'}">${user.role}</span></td>
                <td>${user.account_count}</td>
                <td>
                    <button class="btn btn-sm btn-secondary" onclick="toggleUserRole('${user.user_id}', '${user.role}')">
                        ${user.role === 'ADMIN' ? 'Demote to User' : 'Promote to Admin'}
                    </button>
                </td>
            </tr>`;
        });

        html += '</tbody></table>';
        document.getElementById('admin-users-table').innerHTML = html;
    } catch (error) {
        console.error('Error loading admin users:', error);
    }
}

async function toggleUserRole(userId, currentRole) {
    const newRole = currentRole === 'ADMIN' ? 'USER' : 'ADMIN';

    if (!confirm(`Are you sure you want to change this user's role to ${newRole}?`)) {
        return;
    }

    try {
        await apiCall(`/admin/users/${userId}/role`, 'PUT', { role: newRole });
        showToast(`User role updated to ${newRole}`, 'success');
        loadAdminUsers();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

function loadAdminActivity(activities) {
    if (!activities || activities.length === 0) {
        document.getElementById('admin-recent-activity').innerHTML = '<p style="color: #94a3b8; text-align: center; padding: 2rem;">No recent activity</p>';
        return;
    }

    let html = '<div class="activity-list">';
    activities.forEach(activity => {
        html += `<div class="activity-item">
            <div><strong>${escapeHtml(activity.full_name)}</strong> ${activity.side} ${activity.quantity} ${escapeHtml(activity.ticker)}</div>
            <div class="activity-meta">${new Date(activity.placed_at).toLocaleString()} · <span class="badge badge-${activity.status.toLowerCase()}">${activity.status}</span></div>
        </div>`;
    });
    html += '</div>';
    document.getElementById('admin-recent-activity').innerHTML = html;
}

// Update the existing init() function to include auth
const originalInit = window.init || function () { };
window.init = async function () {
    // Initialize auth first
    if (!initAuth()) {
        return; // Will redirect to login
    }

    // Continue with original init
    await originalInit();

    // Set up navigation
    setupNavigation();

    // Load initial page
    showPage('dashboard');
};

// Enhanced showPage to load admin page
const originalShowPage = window.showPage;
window.showPage = function (pageName) {
    if (pageName === 'admin') {
        if (!isAdmin()) {
            showToast('Access denied: Admin privileges required', 'error');
            return;
        }
        loadAdminStats();
    }

    // Call original showPage
    if (originalShowPage) {
        originalShowPage(pageName);
    }
};

console.log('Auth module loaded');
