/**
 * PRIVATE VAULT - Vault Module
 * CRUD operations for vault items
 */

(function () {
    'use strict';

    const Vault = {
        /**
         * Get all items for a category
         */
        getItems: function (category) {
            return fetch(`/${category}/list`)
                .then(response => response.json());
        },

        /**
         * Get single item
         */
        getItem: function (id) {
            return fetch(`/vault/view/${id}`)
                .then(response => response.json());
        },

        /**
         * Create new item
         */
        createItem: function (data) {
            return fetch('/vault/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
                .then(response => response.json());
        },

        /**
         * Update item
         */
        updateItem: function (id, data) {
            return fetch(`/vault/update/${id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
                .then(response => response.json());
        },

        /**
         * Delete item
         */
        deleteItem: function (id) {
            return fetch(`/vault/delete/${id}`, {
                method: 'DELETE'
            })
                .then(response => response.json());
        },

        /**
         * Toggle favorite
         */
        toggleFavorite: function (id, category) {
            const url = category ? `/${category}/favorite/${id}` : `/vault/favorite/${id}`;
            return fetch(url, {
                method: 'POST'
            })
                .then(response => response.json());
        },

        /**
         * Copy item value
         */
        copyValue: function (id) {
            return fetch(`/vault/copy/${id}`)
                .then(response => response.json());
        },

        /**
         * Search items
         */
        search: function (query, category = null) {
            const url = category
                ? `/${category}/search?q=${encodeURIComponent(query)}`
                : `/dashboard/search?q=${encodeURIComponent(query)}`;
            return fetch(url)
                .then(response => response.json());
        },

        /**
         * Export items
         */
        exportItems: function (category) {
            return fetch(`/${category}/export`)
                .then(response => response.blob());
        },

        /**
         * Get item categories
         */
        getCategories: function () {
            return {
                'identity': 'Identity',
                'banking': 'Banking',
                'passwords': 'Passwords',
                'notes': 'Notes',
                'documents': 'Documents',
                'emergency': 'Emergency',
                'digital_assets': 'Digital Assets'
            };
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
         * Get category fields
         */
        getCategoryFields: function (category) {
            const fields = {
                'identity': ['type', 'number'],
                'banking': ['bank_name', 'account_number', 'ifsc', 'upi', 'account_holder'],
                'passwords': ['username', 'url', 'password_hint'],
                'notes': ['category', 'tags'],
                'emergency': ['contact_name', 'phone', 'relationship', 'address'],
                'digital_assets': ['asset_type', 'asset_url', 'provider']
            };
            return fields[category] || [];
        },

        /**
         * Mask sensitive value
         */
        maskValue: function (value, visibleChars = 4) {
            if (!value) return '';
            if (value.length <= visibleChars) return '•'.repeat(value.length);
            return '•'.repeat(value.length - visibleChars) + value.slice(-visibleChars);
        },

        /**
         * Validate item data
         */
        validateItem: function (data) {
            const errors = {};

            if (!data.label || data.label.trim() === '') {
                errors.label = 'Label is required';
            }

            if (!data.value || data.value.trim() === '') {
                errors.value = 'Value is required';
            }

            if (!data.category) {
                errors.category = 'Category is required';
            }

            return {
                valid: Object.keys(errors).length === 0,
                errors: errors
            };
        }
    };

    // Expose globally
    window.Vault = Vault;
})();