// Auth.js - Admin Panel Helpers
// Note: Core auth logic (login/logout/tokens) is handled in app.js

// Format currency helper (wraps app.js formatNumber)
function formatCurrency(amount) {
    // Check if formatNumber exists in global scope (from app.js)
    if (typeof formatNumber === 'function') {
        return '$' + formatNumber(amount || 0);
    }
    return '$' + (parseFloat(amount) || 0).toFixed(2);
}

// ==================== ADMIN PANEL FUNCTIONS ====================

async function loadAdminPanel() {
    await loadAdminStats();
}

async function loadAdminStats() {
    try {
        const stats = await apiCall('/admin/stats');

        // Update stats
        const usersByRole = stats.users_by_role || {};
        const userCountEl = document.getElementById('admin-stat-users');
        const adminCountEl = document.getElementById('admin-stat-admins');

        if (userCountEl) userCountEl.textContent = usersByRole.USER || 0;
        if (adminCountEl) adminCountEl.textContent = usersByRole.ADMIN || 0;

        const totalCash = stats.total_cash || 0;
        const cashEl = document.getElementById('admin-stat-cash');
        if (cashEl) cashEl.textContent = formatCurrency(totalCash);

        const accountsByStatus = stats.accounts_by_status || {};
        const activeAccountsEl = document.getElementById('admin-stat-active-accounts');
        if (activeAccountsEl) activeAccountsEl.textContent = accountsByStatus.ACTIVE || 0;

        // Load users table
        loadAdminUsers();

        // Load recent activity
        loadAdminActivity(stats.recent_activity || []);
    } catch (error) {
        console.error('Error loading admin stats:', error);
        showToast('Failed to load admin stats', 'error');
    }
}

async function loadAdminUsers() {
    try {
        const users = await apiCall('/admin/users');

        let html = '<table><thead><tr>';
        html += '<th>Name</th><th>Email</th><th>Role</th><th>Accounts</th><th>Actions</th>';
        html += '</tr></thead><tbody>';

        users.forEach(user => {
            // Use global escapeHtml if available, otherwise simple fallback
            const safeName = typeof escapeHtml === 'function' ? escapeHtml(user.full_name) : user.full_name;
            const safeEmail = typeof escapeHtml === 'function' ? escapeHtml(user.email) : user.email;

            html += `<tr>
                <td>${safeName}</td>
                <td>${safeEmail}</td>
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
        const tableEl = document.getElementById('admin-users-table');
        if (tableEl) tableEl.innerHTML = html;
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
        showToast(error.message || 'Failed to update role', 'error');
    }
}

function loadAdminActivity(activities) {
    const activityEl = document.getElementById('admin-recent-activity');
    if (!activityEl) return;

    if (!activities || activities.length === 0) {
        activityEl.innerHTML = '<p style="color: #94a3b8; text-align: center; padding: 2rem;">No recent activity</p>';
        return;
    }

    let html = '<div class="activity-list">';
    activities.forEach(activity => {
        const safeName = typeof escapeHtml === 'function' ? escapeHtml(activity.full_name) : activity.full_name;
        const safeTicker = typeof escapeHtml === 'function' ? escapeHtml(activity.ticker) : activity.ticker;

        html += `<div class="activity-item">
            <div><strong>${safeName}</strong> ${activity.side} ${activity.quantity} ${safeTicker}</div>
            <div class="activity-meta">${new Date(activity.placed_at).toLocaleString()} · <span class="badge badge-${activity.status.toLowerCase()}">${activity.status}</span></div>
        </div>`;
    });
    html += '</div>';
    activityEl.innerHTML = html;
}

console.log('Admin Auth module loaded');
