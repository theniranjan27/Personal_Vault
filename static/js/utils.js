/**
 * PRIVATE VAULT - Utility Functions
 * Common utility functions used throughout the application
 */

(function () {
    'use strict';

    const Utils = {
        /**
         * Format date
         */
        formatDate: function (dateString, format = 'short') {
            if (!dateString) return '-';
            const date = new Date(dateString);

            if (format === 'short') {
                return date.toLocaleDateString('en-US', {
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric'
                });
            }

            if (format === 'long') {
                return date.toLocaleString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit'
                });
            }

            if (format === 'relative') {
                return this.relativeTime(date);
            }

            return date.toLocaleString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        },

        /**
         * Get relative time string
         */
        relativeTime: function (date) {
            const now = new Date();
            const diff = Math.floor((now - date) / 1000);

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
        formatFileSize: function (bytes) {
            if (!bytes || bytes === 0) return '0 B';
            const units = ['B', 'KB', 'MB', 'GB', 'TB'];
            const k = 1024;
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + units[i];
        },

        /**
         * Mask sensitive value
         */
        maskValue: function (value, visibleChars = 4, maskChar = '•') {
            if (!value) return '';
            if (value.length <= visibleChars) return maskChar.repeat(value.length);
            return maskChar.repeat(value.length - visibleChars) + value.slice(-visibleChars);
        },

        /**
         * Truncate text
         */
        truncate: function (text, maxLength = 100, suffix = '...') {
            if (!text) return '';
            if (text.length <= maxLength) return text;
            return text.substring(0, maxLength) + suffix;
        },

        /**
         * Escape HTML
         */
        escapeHtml: function (text) {
            if (!text) return '';
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        },

        /**
         * Unescape HTML
         */
        unescapeHtml: function (html) {
            if (!html) return '';
            const div = document.createElement('div');
            div.innerHTML = html;
            return div.textContent;
        },

        /**
         * Debounce function
         */
        debounce: function (func, wait = 300) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },

        /**
         * Throttle function
         */
        throttle: function (func, limit = 300) {
            let inThrottle;
            return function (...args) {
                if (!inThrottle) {
                    func(...args);
                    inThrottle = true;
                    setTimeout(() => inThrottle = false, limit);
                }
            };
        },

        /**
         * Generate random ID
         */
        generateId: function () {
            return Date.now().toString(36) + Math.random().toString(36).substr(2, 5);
        },

        /**
         * Get URL parameter
         */
        getUrlParam: function (name) {
            const params = new URLSearchParams(window.location.search);
            return params.get(name);
        },

        /**
         * Update URL parameters
         */
        updateUrlParams: function (params, replace = true) {
            const url = new URL(window.location);
            for (const [key, value] of Object.entries(params)) {
                if (value !== null && value !== undefined) {
                    url.searchParams.set(key, value);
                } else {
                    url.searchParams.delete(key);
                }
            }
            if (replace) {
                window.history.replaceState({}, '', url);
            } else {
                window.history.pushState({}, '', url);
            }
        },

        /**
         * Get form data as object
         */
        getFormData: function (form) {
            const formData = new FormData(form);
            const data = {};
            for (const [key, value] of formData.entries()) {
                if (data[key] !== undefined) {
                    if (!Array.isArray(data[key])) {
                        data[key] = [data[key]];
                    }
                    data[key].push(value);
                } else {
                    data[key] = value;
                }
            }
            return data;
        },

        /**
         * Validate email
         */
        isValidEmail: function (email) {
            return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
        },

        /**
         * Validate URL
         */
        isValidUrl: function (url) {
            try {
                new URL(url);
                return true;
            } catch {
                return false;
            }
        },

        /**
         * Validate phone number
         */
        isValidPhone: function (phone) {
            return /^\+?[\d\s-]{10,15}$/.test(phone);
        },

        /**
         * Get file extension
         */
        getFileExtension: function (filename) {
            if (!filename) return '';
            return filename.split('.').pop().toLowerCase();
        },

        /**
         * Check if file is allowed
         */
        isAllowedFile: function (filename, allowedExtensions) {
            const ext = this.getFileExtension(filename);
            return allowedExtensions.includes(ext);
        },

        /**
         * Get color for category
         */
        getCategoryColor: function (category) {
            const colors = {
                'identity': '#4a85ff',
                'banking': '#4caf50',
                'passwords': '#ff9800',
                'notes': '#ffc107',
                'documents': '#ce93d8',
                'emergency': '#ef5350',
                'digital_assets': '#4dd0e1'
            };
            return colors[category] || '#7b96c0';
        },

        /**
         * Get icon for category
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
         * Get status badge HTML
         */
        getStatusBadge: function (status) {
            const badges = {
                'active': '<span class="badge badge-success">Active</span>',
                'inactive': '<span class="badge badge-danger">Inactive</span>',
                'pending': '<span class="badge badge-warning">Pending</span>',
                'success': '<span class="badge badge-success">Success</span>',
                'failed': '<span class="badge badge-danger">Failed</span>',
                'in-progress': '<span class="badge badge-warning">In Progress</span>'
            };
            return badges[status] || '<span class="badge badge-info">Unknown</span>';
        },

        /**
         * Sleep/delay
         */
        sleep: function (ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        },

        /**
         * Copy text to clipboard
         */
        copyText: async function (text) {
            try {
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    await navigator.clipboard.writeText(text);
                    return true;
                }

                // Fallback
                const textarea = document.createElement('textarea');
                textarea.value = text;
                textarea.style.position = 'fixed';
                textarea.style.opacity = '0';
                document.body.appendChild(textarea);
                textarea.select();
                const success = document.execCommand('copy');
                document.body.removeChild(textarea);
                return success;
            } catch (error) {
                console.error('Copy error:', error);
                return false;
            }
        },

        /**
         * Download blob as file
         */
        downloadBlob: function (blob, filename) {
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        },

        /**
         * Get browser info
         */
        getBrowserInfo: function () {
            const ua = navigator.userAgent;
            let browser = 'Unknown';
            let os = 'Unknown';

            if (ua.includes('Chrome')) browser = 'Chrome';
            else if (ua.includes('Firefox')) browser = 'Firefox';
            else if (ua.includes('Safari')) browser = 'Safari';
            else if (ua.includes('Edge')) browser = 'Edge';
            else if (ua.includes('MSIE')) browser = 'Internet Explorer';

            if (ua.includes('Windows')) os = 'Windows';
            else if (ua.includes('Mac')) os = 'macOS';
            else if (ua.includes('Linux')) os = 'Linux';
            else if (ua.includes('Android')) os = 'Android';
            else if (ua.includes('iOS')) os = 'iOS';

            return { browser, os };
        }
    };

    // Expose globally
    window.Utils = Utils;
    window.VaultUtils = Utils;
})();