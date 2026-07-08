/**
 * PRIVATE VAULT - Dashboard Module
 * Dashboard functionality and data loading
 */

(function () {
    'use strict';

    const Dashboard = {
        /**
         * Load dashboard data
         */
        loadDashboard: function () {
            this.loadCounts();
            this.loadRecentItems();
            this.loadFavoriteItems();
            this.loadRecentActivity();
            this.loadSecurityStatus();
            this.loadStorageUsage();
        },

        /**
         * Load vault counts
         */
        loadCounts: function () {
            fetch('/dashboard/counts')
                .then(response => response.json())
                .then(data => {
                    const mapping = {
                        'identityCount': 'identity',
                        'bankingCount': 'banking',
                        'passwordCount': 'passwords',
                        'notesCount': 'notes',
                        'documentsCount': 'documents',
                        'assetsCount': 'assets'
                    };

                    for (const [elementId, key] of Object.entries(mapping)) {
                        const el = document.getElementById(elementId);
                        if (el) el.textContent = data[key] || 0;
                    }
                })
                .catch(error => {
                    console.error('Error loading counts:', error);
                });
        },

        /**
         * Load recent items
         */
        loadRecentItems: function () {
            fetch('/dashboard/recent')
                .then(response => response.json())
                .then(data => {
                    const container = document.getElementById('recentItemsList');
                    if (!container) return;

                    if (data.items && data.items.length > 0) {
                        container.innerHTML = data.items.map(item => `
                            <div class="item-entry" onclick="VaultUtils?.navigateTo('/vault/view/${item.id}')">
                                <div class="item-info">
                                    <span class="item-icon">${this.getCategoryIcon(item.category)}</span>
                                    <span class="item-label">${item.label}</span>
                                    <span class="item-value">${this.maskValue(item.value)}</span>
                                </div>
                                <div class="item-actions">
                                    <button class="btn-sm btn-primary" onclick="event.stopPropagation(); window.VaultUtils?.copyText('${item.value}')">📋</button>
                                </div>
                            </div>
                        `).join('');
                    } else {
                        container.innerHTML = '<p class="text-muted">No recent items</p>';
                    }
                })
                .catch(error => {
                    console.error('Error loading recent items:', error);
                });
        },

        /**
         * Load favorite items
         */
        loadFavoriteItems: function () {
            fetch('/dashboard/favorites')
                .then(response => response.json())
                .then(data => {
                    const container = document.getElementById('favoriteItemsList');
                    if (!container) return;

                    if (data.items && data.items.length > 0) {
                        container.innerHTML = data.items.map(item => `
                            <div class="item-entry" onclick="VaultUtils?.navigateTo('/vault/view/${item.id}')">
                                <div class="item-info">
                                    <span class="item-icon">${this.getCategoryIcon(item.category)}</span>
                                    <span class="item-label">${item.label}</span>
                                    <span class="item-value">${this.maskValue(item.value)}</span>
                                </div>
                                <div class="item-actions">
                                    <button class="btn-sm btn-primary" onclick="event.stopPropagation(); window.VaultUtils?.copyText('${item.value}')">📋</button>
                                </div>
                            </div>
                        `).join('');
                    } else {
                        container.innerHTML = '<p class="text-muted">No favorite items</p>';
                    }
                })
                .catch(error => {
                    console.error('Error loading favorite items:', error);
                });
        },

        /**
         * Load recent activity
         */
        loadRecentActivity: function () {
            fetch('/dashboard/activity')
                .then(response => response.json())
                .then(data => {
                    const container = document.getElementById('recentActivityList');
                    if (!container) return;

                    if (data.activities && data.activities.length > 0) {
                        container.innerHTML = data.activities.map(activity => `
                            <div class="activity-entry">
                                <span class="activity-icon">${this.getActivityIcon(activity.action)}</span>
                                <div class="activity-content">
                                    <div class="activity-text">${activity.description || activity.action}</div>
                                    <div class="activity-time">${this.formatRelativeTime(activity.timestamp)}</div>
                                </div>
                            </div>
                        `).join('');
                    } else {
                        container.innerHTML = '<p class="text-muted">No recent activity</p>';
                    }
                })
                .catch(error => {
                    console.error('Error loading activity:', error);
                });
        },

        /**
         * Load security status
         */
        loadSecurityStatus: function () {
            fetch('/dashboard/security-status')
                .then(response => response.json())
                .then(data => {
                    const elements = {
                        'sessionTimeout': data.session_timeout || '15 min',
                        'loginAttempts': data.login_attempts || '5 attempts',
                        'lastLogin': data.last_login || '-'
                    };

                    for (const [id, value] of Object.entries(elements)) {
                        const el = document.getElementById(id);
                        if (el) el.textContent = value;
                    }
                })
                .catch(error => {
                    console.error('Error loading security status:', error);
                });
        },

        /**
         * Load storage usage
         */
        loadStorageUsage: function () {
            fetch('/dashboard/storage')
                .then(response => response.json())
                .then(data => {
                    const used = data.used || 0;
                    const total = data.total || 52428800;
                    const percentage = Math.min((used / total) * 100, 100);

                    const fill = document.getElementById('storageFill');
                    if (fill) fill.style.width = percentage + '%';

                    const usedEl = document.getElementById('storageUsed');
                    if (usedEl) usedEl.textContent = this.formatSize(used);

                    const totalEl = document.getElementById('storageTotal');
                    if (totalEl) totalEl.textContent = this.formatSize(total);

                    const itemsEl = document.getElementById('storageItems');
                    if (itemsEl) itemsEl.textContent = data.items || 0;

                    const filesEl = document.getElementById('storageFiles');
                    if (filesEl) filesEl.textContent = data.files || 0;

                    const backupsEl = document.getElementById('storageBackups');
                    if (backupsEl) backupsEl.textContent = data.backups || 0;
                })
                .catch(error => {
                    console.error('Error loading storage:', error);
                });
        },

        /**
         * Get category icon
         */
        getCategoryIcon: function (category) {
            const icons = {
                'identity': '🪪',
                'banking': '🏦',
                'passwords': '🔑',
                'notes': '📝',
                'documents': '📄',
                'emergency': '🚨',
                'digital_assets': '💻'
            };
            return icons[category] || '📦';
        },

        /**
         * Get activity icon
         */
        getActivityIcon: function (action) {
            const icons = {
                'login': '🔓',
                'logout': '🔒',
                'add': '➕',
                'edit': '✏️',
                'delete': '🗑️',
                'view': '👁️',
                'copy': '📋',
                'reveal': '👀',
                'upload': '📤',
                'download': '📥',
                'backup': '💾',
                'restore': '🔄',
                'security': '🛡️',
                'settings': '⚙️'
            };
            return icons[action] || '📌';
        },

        /**
         * Mask sensitive values
         */
        maskValue: function (value) {
            if (!value) return '';
            if (value.length <= 4) return '•'.repeat(value.length);
            return '•'.repeat(value.length - 4) + value.slice(-4);
        },

        /**
         * Format relative time
         */
        formatRelativeTime: function (timestamp) {
            if (!timestamp) return '';
            const now = new Date();
            const time = new Date(timestamp);
            const diff = Math.floor((now - time) / 1000);

            if (diff < 60) return 'Just now';
            if (diff < 3600) return Math.floor(diff / 60) + 'm ago';
            if (diff < 86400) return Math.floor(diff / 3600) + 'h ago';
            if (diff < 604800) return Math.floor(diff / 86400) + 'd ago';
            if (diff < 2592000) return Math.floor(diff / 604800) + 'w ago';
            if (diff < 31536000) return Math.floor(diff / 2592000) + 'mo ago';
            return Math.floor(diff / 31536000) + 'y ago';
        },

        /**
         * Format file size
         */
        formatSize: function (bytes) {
            if (!bytes || bytes === 0) return '0 B';
            if (bytes < 1024) return bytes + ' B';
            if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
            return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
        }
    };

    // Initialize dashboard when DOM is ready
    if (document.querySelector('.dashboard-container')) {
        document.addEventListener('DOMContentLoaded', function () {
            Dashboard.loadDashboard();
        });
    }

    // Expose globally
    window.Dashboard = Dashboard;
})();