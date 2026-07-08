/**
 * PRIVATE VAULT - Backup Module
 * Backup and restore functionality
 */

(function () {
    'use strict';

    const Backup = {
        /**
         * Create a new backup
         */
        create: function (options = {}) {
            const {
                password = null,
                includeFiles = true,
                includeSettings = true
            } = options;

            return fetch('/backup/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    password: password,
                    include_files: includeFiles,
                    include_settings: includeSettings
                })
            })
                .then(response => response.json());
        },

        /**
         * Get backup history
         */
        getHistory: function (page = 1, limit = 20) {
            return fetch(`/backup/history?page=${page}&limit=${limit}`)
                .then(response => response.json());
        },

        /**
         * Get backup details
         */
        getDetails: function (id) {
            return fetch(`/backup/details/${id}`)
                .then(response => response.json());
        },

        /**
         * Download backup
         */
        download: function (id) {
            window.location.href = `/backup/download/${id}`;
        },

        /**
         * Restore backup
         */
        restore: function (id) {
            return fetch(`/backup/restore/${id}`, {
                method: 'POST'
            })
                .then(response => response.json());
        },

        /**
         * Delete backup
         */
        delete: function (id) {
            return fetch(`/backup/delete/${id}`, {
                method: 'DELETE'
            })
                .then(response => response.json());
        },

        /**
         * Import backup from file
         */
        import: function (file, password = null) {
            const formData = new FormData();
            formData.append('file', file);
            if (password) {
                formData.append('password', password);
            }

            return fetch('/backup/import', {
                method: 'POST',
                body: formData
            })
                .then(response => response.json());
        },

        /**
         * Export data (selective)
         */
        exportSelective: function (categories, password = null) {
            return fetch('/backup/export', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    categories: categories,
                    password: password
                })
            })
                .then(response => response.blob());
        },

        /**
         * Get backup stats
         */
        getStats: function () {
            return fetch('/backup/stats')
                .then(response => response.json());
        },

        /**
         * Validate backup file
         */
        validateFile: function (file) {
            return new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.onload = function (e) {
                    try {
                        const data = JSON.parse(e.target.result);
                        resolve({
                            valid: true,
                            data: data,
                            type: data.type || 'unknown',
                            version: data.version || '1.0',
                            items: data.items ? data.items.length : 0,
                            timestamp: data.timestamp || null
                        });
                    } catch (error) {
                        reject({
                            valid: false,
                            error: 'Invalid backup file format'
                        });
                    }
                };
                reader.onerror = function () {
                    reject({
                        valid: false,
                        error: 'Failed to read file'
                    });
                };
                reader.readAsText(file);
            });
        },

        /**
         * Get download URL for export
         */
        getExportUrl: function () {
            return `/backup/export?t=${Date.now()}`;
        },

        /**
         * Schedule automatic backup
         */
        scheduleAutoBackup: function (interval = 'daily') {
            return fetch('/backup/schedule', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ interval: interval })
            })
                .then(response => response.json());
        },

        /**
         * Get auto-backup status
         */
        getAutoBackupStatus: function () {
            return fetch('/backup/auto-status')
                .then(response => response.json());
        },

        /**
         * Format backup size
         */
        formatSize: function (bytes) {
            if (!bytes || bytes === 0) return '0 B';
            if (bytes < 1024) return bytes + ' B';
            if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
            return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
        },

        /**
         * Format backup date
         */
        formatDate: function (dateString) {
            if (!dateString) return '-';
            const date = new Date(dateString);
            return date.toLocaleString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        },

        /**
         * Get backup status badge
         */
        getStatusBadge: function (status) {
            const badges = {
                'success': '<span class="badge badge-success">✅ Success</span>',
                'failed': '<span class="badge badge-danger">❌ Failed</span>',
                'in-progress': '<span class="badge badge-warning">⏳ In Progress</span>',
                'pending': '<span class="badge badge-info">⏳ Pending</span>'
            };
            return badges[status] || '<span class="badge badge-info">Unknown</span>';
        },

        /**
         * Render backup history table
         */
        renderHistory: function (backups, container) {
            if (!container) return;

            if (!backups || backups.length === 0) {
                container.innerHTML = `
                    <tr>
                        <td colspan="6" class="text-center text-muted">No backups found</td>
                    </tr>
                `;
                return;
            }

            container.innerHTML = backups.map(backup => `
                <tr>
                    <td>#${backup.id}</td>
                    <td>${this.formatDate(backup.created_at)}</td>
                    <td>${this.formatSize(backup.size)}</td>
                    <td>${backup.items || 0}</td>
                    <td>${this.getStatusBadge(backup.status)}</td>
                    <td>
                        <button class="btn-sm btn-primary" onclick="Backup.download(${backup.id})">📥</button>
                        <button class="btn-sm btn-success" onclick="Backup.restorePrompt(${backup.id})">🔄</button>
                        <button class="btn-sm btn-danger" onclick="Backup.deletePrompt(${backup.id})">🗑️</button>
                    </td>
                </tr>
            `).join('');
        },

        /**
         * Prompt for restore confirmation
         */
        restorePrompt: function (id) {
            if (confirm('⚠️ Restoring this backup will replace all current data. Continue?')) {
                this.restore(id)
                    .then(data => {
                        if (data.success) {
                            window.showNotification('Backup restored successfully!', 'success');
                            setTimeout(() => window.location.reload(), 1500);
                        } else {
                            window.showNotification('Error restoring backup: ' + data.error, 'error');
                        }
                    })
                    .catch(error => {
                        window.showNotification('Error restoring backup', 'error');
                        console.error('Error:', error);
                    });
            }
        },

        /**
         * Prompt for delete confirmation
         */
        deletePrompt: function (id) {
            if (confirm('Are you sure you want to delete this backup?')) {
                this.delete(id)
                    .then(data => {
                        if (data.success) {
                            window.showNotification('Backup deleted successfully', 'success');
                            // Reload history if on backup page
                            if (window.BackupHistory) {
                                window.BackupHistory.load();
                            }
                        } else {
                            window.showNotification('Error deleting backup: ' + data.error, 'error');
                        }
                    })
                    .catch(error => {
                        window.showNotification('Error deleting backup', 'error');
                        console.error('Error:', error);
                    });
            }
        }
    };

    // Initialize backup page if present
    document.addEventListener('DOMContentLoaded', function () {
        if (document.querySelector('.backup-container')) {
            // Load backup history
            const historyContainer = document.querySelector('.backup-history tbody');
            if (historyContainer) {
                Backup.getHistory().then(data => {
                    Backup.renderHistory(data.backups, historyContainer);
                });
            }

            // Load backup stats
            Backup.getStats().then(data => {
                const stats = {
                    'totalBackups': data.total || 0,
                    'lastBackup': data.last ? Backup.formatDate(data.last) : 'Never',
                    'storageUsed': Backup.formatSize(data.storage || 0)
                };

                for (const [id, value] of Object.entries(stats)) {
                    const el = document.getElementById(id);
                    if (el) el.textContent = value;
                }
            });
        }
    });

    // Expose globally
    window.Backup = Backup;
})();