/**
 * PRIVATE VAULT - Settings Module
 * Settings and preferences management
 */

(function () {
    'use strict';

    const Settings = {
        /**
         * Get all settings
         */
        getAll: function () {
            return fetch('/settings/all')
                .then(response => response.json());
        },

        /**
         * Update settings
         */
        update: function (settings) {
            return fetch('/settings/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(settings)
            })
                .then(response => response.json());
        },

        /**
         * Update security settings
         */
        updateSecurity: function (settings) {
            return fetch('/settings/security', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(settings)
            })
                .then(response => response.json());
        },

        /**
         * Update profile
         */
        updateProfile: function (data) {
            return fetch('/settings/profile', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
                .then(response => response.json());
        },

        /**
         * Change password
         */
        changePassword: function (currentPassword, newPassword) {
            return fetch('/settings/change-password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    current_password: currentPassword,
                    new_password: newPassword
                })
            })
                .then(response => response.json());
        },

        /**
         * Change PIN
         */
        changePin: function (currentPin, newPin) {
            return fetch('/settings/change-pin', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    current_pin: currentPin,
                    new_pin: newPin
                })
            })
                .then(response => response.json());
        },

        /**
         * Upload avatar
         */
        uploadAvatar: function (file) {
            const formData = new FormData();
            formData.append('avatar', file);

            return fetch('/settings/upload-avatar', {
                method: 'POST',
                body: formData
            })
                .then(response => response.json());
        },

        /**
         * Get security methods
         */
        getSecurityMethods: function () {
            return fetch('/settings/security-methods')
                .then(response => response.json());
        },

        /**
         * Toggle security method
         */
        toggleSecurityMethod: function (method, enabled) {
            return fetch('/settings/toggle-method', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    method: method,
                    enabled: enabled
                })
            })
                .then(response => response.json());
        },

        /**
         * Get trusted devices
         */
        getTrustedDevices: function () {
            return fetch('/settings/trusted-devices')
                .then(response => response.json());
        },

        /**
         * Remove trusted device
         */
        removeTrustedDevice: function (deviceId) {
            return fetch(`/settings/trusted-devices/${deviceId}`, {
                method: 'DELETE'
            })
                .then(response => response.json());
        },

        /**
         * Get activity logs
         */
        getActivityLogs: function (page = 1, limit = 50) {
            return fetch(`/settings/activity?page=${page}&limit=${limit}`)
                .then(response => response.json());
        },

        /**
         * Clear activity logs
         */
        clearActivityLogs: function () {
            return fetch('/settings/clear-activity', {
                method: 'POST'
            })
                .then(response => response.json());
        },

        /**
         * Export activity logs
         */
        exportActivityLogs: function () {
            window.location.href = '/settings/export-activity';
        },

        /**
         * Delete all data
         */
        deleteAllData: function () {
            return fetch('/settings/delete-all-data', {
                method: 'POST'
            })
                .then(response => response.json());
        },

        /**
         * Get backup settings
         */
        getBackupSettings: function () {
            return fetch('/settings/backup-settings')
                .then(response => response.json());
        },

        /**
         * Update backup settings
         */
        updateBackupSettings: function (settings) {
            return fetch('/settings/backup-settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(settings)
            })
                .then(response => response.json());
        },

        /**
         * Render security methods
         */
        renderSecurityMethods: function (methods, container) {
            if (!container) return;

            container.innerHTML = Object.entries(methods).map(([key, method]) => `
                <div class="method-item">
                    <div class="method-info">
                        <span class="method-icon">${method.icon || '🔒'}</span>
                        <div>
                            <div class="method-name">${method.name}</div>
                            <div class="method-description">${method.description || ''}</div>
                        </div>
                    </div>
                    <div class="method-control">
                        ${method.enabled !== undefined ? `
                            <label class="switch">
                                <input type="checkbox" ${method.enabled ? 'checked' : ''} 
                                    ${method.required ? 'disabled' : ''}
                                    onchange="Settings.toggleSecurityMethod('${key}', this.checked)">
                                <span class="slider"></span>
                            </label>
                        ` : `
                            <span class="badge badge-${method.status || 'info'}">${method.status || 'Active'}</span>
                        `}
                    </div>
                </div>
            `).join('');
        },

        /**
         * Render trusted devices
         */
        renderTrustedDevices: function (devices, container) {
            if (!container) return;

            if (!devices || devices.length === 0) {
                container.innerHTML = '<p class="text-muted">No trusted devices</p>';
                return;
            }

            container.innerHTML = devices.map(device => `
                <div class="device-item">
                    <div class="device-info">
                        <span class="device-icon">${device.type === 'mobile' ? '📱' : '💻'}</span>
                        <div>
                            <div class="device-name">${device.name}</div>
                            <div class="device-meta">
                                <span>${device.browser || ''}</span>
                                <span>${device.os || ''}</span>
                                <span class="device-time">${this.formatDate(device.last_used)}</span>
                            </div>
                        </div>
                    </div>
                    <div class="device-actions">
                        ${device.is_current ? '<span class="badge badge-success">Current</span>' : ''}
                        <button class="btn-sm btn-danger" onclick="Settings.removeTrustedDevicePrompt('${device.id}')">Remove</button>
                    </div>
                </div>
            `).join('');
        },

        /**
         * Prompt for device removal
         */
        removeTrustedDevicePrompt: function (deviceId) {
            if (confirm('Remove this trusted device?')) {
                this.removeTrustedDevice(deviceId)
                    .then(data => {
                        if (data.success) {
                            window.showNotification('Device removed successfully', 'success');
                            // Reload devices
                            if (window.SettingsUI) {
                                window.SettingsUI.loadTrustedDevices();
                            }
                        } else {
                            window.showNotification('Error removing device: ' + data.error, 'error');
                        }
                    })
                    .catch(error => {
                        window.showNotification('Error removing device', 'error');
                        console.error('Error:', error);
                    });
            }
        },

        /**
         * Format date
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
         * Validate settings
         */
        validateSettings: function (settings) {
            const errors = {};

            if (settings.session_timeout !== undefined) {
                const timeout = parseInt(settings.session_timeout);
                if (isNaN(timeout) || timeout < 1 || timeout > 1440) {
                    errors.session_timeout = 'Session timeout must be between 1 and 1440 minutes';
                }
            }

            if (settings.max_login_attempts !== undefined) {
                const attempts = parseInt(settings.max_login_attempts);
                if (isNaN(attempts) || attempts < 1 || attempts > 20) {
                    errors.max_login_attempts = 'Login attempts must be between 1 and 20';
                }
            }

            if (settings.lockout_duration !== undefined) {
                const duration = parseInt(settings.lockout_duration);
                if (isNaN(duration) || duration < 1 || duration > 1440) {
                    errors.lockout_duration = 'Lockout duration must be between 1 and 1440 minutes';
                }
            }

            return {
                valid: Object.keys(errors).length === 0,
                errors: errors
            };
        }
    };

    // Expose globally
    window.Settings = Settings;
})();