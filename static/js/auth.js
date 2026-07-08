/**
 * PRIVATE VAULT - Authentication Module
 * Login, logout, and session management
 */

(function () {
    'use strict';

    const Auth = {
        /**
         * Login with master password
         */
        login: function (masterPassword, pin) {
            return fetch('/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    master_password: masterPassword,
                    pin: pin
                })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        window.location.href = data.redirect || '/dashboard';
                    }
                    return data;
                });
        },

        /**
         * Verify master password (step 1)
         */
        verifyMaster: function (password) {
            return fetch('/auth/verify-master', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ master_password: password })
            })
                .then(response => response.json());
        },

        /**
         * Verify PIN (step 2)
         */
        verifyPin: function (pin) {
            return fetch('/auth/verify-pin', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ pin: pin })
            })
                .then(response => response.json());
        },

        /**
         * Logout
         */
        logout: function () {
            return fetch('/auth/logout', {
                method: 'POST'
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        window.location.href = '/auth/login';
                    }
                    return data;
                });
        },

        /**
         * Check session validity
         */
        checkSession: function () {
            return fetch('/auth/check-session')
                .then(response => response.json());
        },

        /**
         * Change password
         */
        changePassword: function (currentPassword, newPassword) {
            return fetch('/auth/change-password', {
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
            return fetch('/auth/change-pin', {
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
         * Request password reset
         */
        requestReset: function (email) {
            return fetch('/auth/request-reset', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email: email })
            })
                .then(response => response.json());
        },

        /**
         * Reset password with token
         */
        resetPassword: function (token, newPassword) {
            return fetch('/auth/reset-password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    token: token,
                    new_password: newPassword
                })
            })
                .then(response => response.json());
        }
    };

    // Expose globally
    window.Auth = Auth;

    // Auto-logout if session expired
    if (document.querySelector('.app-wrapper')) {
        Auth.checkSession()
            .then(data => {
                if (!data.valid) {
                    window.location.href = '/auth/login?expired=1';
                }
            })
            .catch(() => {
                window.location.href = '/auth/login';
            });
    }

    // Handle logout clicks
    document.addEventListener('click', function (e) {
        const logoutBtn = e.target.closest('.logout-link, #logoutBtn');
        if (logoutBtn) {
            e.preventDefault();
            if (confirm('Are you sure you want to logout?')) {
                Auth.logout();
            }
        }
    });
})();