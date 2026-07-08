/**
 * PRIVATE VAULT - Main Application
 * Core application initialization and global utilities
 */

(function () {
    'use strict';

    // Application namespace
    window.Vault = {
        version: '1.0.0',
        initialized: false,
        config: {
            sessionTimeout: 15 * 60 * 1000, // 15 minutes
            maxLoginAttempts: 5,
            lockoutDuration: 30 * 60 * 1000 // 30 minutes
        }
    };

    /**
     * Initialize the application
     */
    function init() {
        if (Vault.initialized) return;

        // Set up CSRF protection
        setupCSRF();

        // Set up session management
        setupSessionManagement();

        // Set up keyboard shortcuts
        setupKeyboardShortcuts();

        // Set up click outside handlers
        setupClickOutsideHandlers();

        Vault.initialized = true;
        console.log(`🔐 Private Vault v${Vault.version} initialized`);
    }

    /**
     * Set up CSRF token for all fetch requests
     */
    function setupCSRF() {
        const tokenMeta = document.querySelector('meta[name="csrf-token"]');
        if (tokenMeta) {
            const token = tokenMeta.content;
            const originalFetch = window.fetch;

            window.fetch = function (url, options = {}) {
                if (!options.headers) {
                    options.headers = {};
                }
                if (!options.headers['X-CSRFToken'] && !options.headers['X-CSRF-Token']) {
                    options.headers['X-CSRFToken'] = token;
                }
                return originalFetch(url, options);
            };
        }
    }

    /**
     * Set up session management with inactivity timeout
     */
    function setupSessionManagement() {
        let inactivityTimer = null;
        const timeout = Vault.config.sessionTimeout;

        function resetInactivityTimer() {
            if (inactivityTimer) {
                clearTimeout(inactivityTimer);
            }
            inactivityTimer = setTimeout(() => {
                // Check if user is on a protected page
                if (document.querySelector('.app-wrapper')) {
                    fetch('/auth/logout', { method: 'POST' })
                        .then(() => {
                            window.location.href = '/auth/login?timeout=1';
                        })
                        .catch(() => {
                            window.location.href = '/auth/login?timeout=1';
                        });
                }
            }, timeout);
        }

        // Reset timer on user activity
        const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
        events.forEach(event => {
            document.addEventListener(event, resetInactivityTimer);
        });

        // Initial timer start
        resetInactivityTimer();

        // Periodic session check
        setInterval(function () {
            if (document.querySelector('.app-wrapper')) {
                fetch('/auth/check-session')
                    .then(response => response.json())
                    .then(data => {
                        if (!data.valid) {
                            window.location.href = '/auth/login?expired=1';
                        }
                    })
                    .catch(() => {
                        window.location.href = '/auth/login';
                    });
            }
        }, 60000); // Check every minute
    }

    /**
     * Set up keyboard shortcuts
     */
    function setupKeyboardShortcuts() {
        document.addEventListener('keydown', function (e) {
            // Ctrl+K or Cmd+K for search
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                const searchInput = document.querySelector('.header-search-input, #globalSearch, .search-container input');
                if (searchInput) {
                    searchInput.focus();
                    searchInput.select();
                }
            }

            // Escape to close modals
            if (e.key === 'Escape') {
                const modals = document.querySelectorAll('.modal-overlay.show, .modal.show');
                modals.forEach(modal => {
                    if (modal.classList.contains('show')) {
                        modal.classList.remove('show');
                        modal.style.display = 'none';
                    }
                });
                // Close dropdowns
                document.querySelectorAll('.user-dropdown.show').forEach(el => {
                    el.classList.remove('show');
                });
            }

            // Ctrl+S to save forms
            if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                const form = document.querySelector('form[data-auto-save]');
                if (form) {
                    e.preventDefault();
                    form.dispatchEvent(new Event('submit'));
                }
            }
        });
    }

    /**
     * Set up click outside handlers for dropdowns
     */
    function setupClickOutsideHandlers() {
        document.addEventListener('click', function (e) {
            // Close user dropdown
            if (!e.target.closest('.header-user')) {
                document.querySelectorAll('.user-dropdown.show').forEach(el => {
                    el.classList.remove('show');
                });
            }

            // Close sidebar on mobile
            if (!e.target.closest('.sidebar') && !e.target.closest('.menu-toggle')) {
                const sidebar = document.querySelector('.sidebar');
                const overlay = document.querySelector('.sidebar-overlay');
                if (sidebar && sidebar.classList.contains('mobile-open')) {
                    sidebar.classList.remove('mobile-open');
                    if (overlay) overlay.classList.remove('show');
                    document.body.style.overflow = '';
                }
            }
        });
    }

    /**
     * Handle navigation to protected routes
     */
    function requireAuth() {
        const userId = getUserId();
        if (!userId) {
            window.location.href = '/auth/login';
            return false;
        }
        return true;
    }

    /**
     * Get current user ID from session
     */
    function getUserId() {
        return document.querySelector('meta[name="user-id"]')?.content || null;
    }

    /**
     * Get CSRF token
     */
    function getCSRFToken() {
        return document.querySelector('meta[name="csrf-token"]')?.content || '';
    }

    /**
     * Safe JSON parse with error handling
     */
    function safeJSONParse(str, fallback = null) {
        try {
            return JSON.parse(str);
        } catch (e) {
            return fallback;
        }
    }

    /**
     * Generate a unique ID
     */
    function generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2, 5);
    }

    /**
     * Sleep/delay function
     */
    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Get URL parameter
     */
    function getUrlParam(name) {
        const params = new URLSearchParams(window.location.search);
        return params.get(name);
    }

    /**
     * Update URL without reload
     */
    function updateUrl(params, replace = true) {
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
    }

    /**
     * Get all form data as object
     */
    function getFormData(formElement) {
        const formData = new FormData(formElement);
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
    }

    /**
     * Validate email format
     */
    function isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    /**
     * Validate URL format
     */
    function isValidUrl(url) {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    }

    /**
     * Get file extension
     */
    function getFileExtension(filename) {
        return filename.split('.').pop().toLowerCase();
    }

    /**
     * Truncate text
     */
    function truncateText(text, maxLength = 100, suffix = '...') {
        if (!text) return '';
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + suffix;
    }

    /**
     * Escape HTML
     */
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Expose utilities globally
    window.VaultUtils = {
        getUserId,
        getCSRFToken,
        safeJSONParse,
        generateId,
        sleep,
        getUrlParam,
        updateUrl,
        getFormData,
        isValidEmail,
        isValidUrl,
        getFileExtension,
        truncateText,
        escapeHtml,
        requireAuth
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();