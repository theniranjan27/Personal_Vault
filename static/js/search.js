/**
 * PRIVATE VAULT - Search Module
 * Global search functionality
 */

(function () {
    'use strict';

    const Search = {
        /**
         * Perform search
         */
        search: function (query, options = {}) {
            const {
                category = null,
                page = 1,
                limit = 50,
                filters = {}
            } = options;

            const params = new URLSearchParams({
                q: query,
                page: page,
                limit: limit,
                ...filters
            });

            if (category) {
                params.append('category', category);
            }

            return fetch(`/dashboard/search?${params}`)
                .then(response => response.json());
        },

        /**
         * Search with debounce
         */
        debouncedSearch: function (query, callback, delay = 300) {
            clearTimeout(this._searchTimeout);
            this._searchTimeout = setTimeout(() => {
                this.search(query).then(callback);
            }, delay);
        },

        /**
         * Render search results
         */
        renderResults: function (results, container) {
            if (!container) return;

            if (!results || results.items.length === 0) {
                container.innerHTML = `
                    <div class="search-empty">
                        <span class="icon">🔍</span>
                        <p>No results found</p>
                    </div>
                `;
                return;
            }

            container.innerHTML = results.items.map(item => `
                <div class="search-result" onclick="window.location.href='/vault/view/${item.id}'">
                    <div class="result-icon">${this.getCategoryIcon(item.category)}</div>
                    <div class="result-content">
                        <div class="result-title">${this.highlightText(item.label, results.query)}</div>
                        <div class="result-subtitle">${this.highlightText(this.maskValue(item.value), results.query)}</div>
                        <div class="result-meta">
                            <span class="result-category">${item.category}</span>
                            ${item.is_favorite ? '<span class="result-favorite">⭐</span>' : ''}
                        </div>
                    </div>
                </div>
            `).join('');
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
         * Mask sensitive values
         */
        maskValue: function (value) {
            if (!value) return '';
            if (value.length <= 4) return '•'.repeat(value.length);
            return '•'.repeat(value.length - 4) + value.slice(-4);
        },

        /**
         * Highlight matching text
         */
        highlightText: function (text, query) {
            if (!text || !query) return text || '';
            const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
            return text.replace(regex, '<mark>$1</mark>');
        },

        /**
         * Initialize search input
         */
        initSearchInput: function (inputElement, resultsContainer, options = {}) {
            const {
                minChars = 2,
                delay = 300,
                onSearch = null,
                onSelect = null
            } = options;

            if (!inputElement || !resultsContainer) return;

            let currentQuery = '';

            inputElement.addEventListener('input', function () {
                const query = this.value.trim();
                currentQuery = query;

                if (query.length < minChars) {
                    resultsContainer.classList.add('hidden');
                    return;
                }

                clearTimeout(this._searchTimeout);
                this._searchTimeout = setTimeout(() => {
                    Search.search(query).then(data => {
                        if (query === currentQuery) {
                            Search.renderResults(data, resultsContainer);
                            resultsContainer.classList.remove('hidden');

                            if (onSearch) onSearch(data);
                        }
                    });
                }, delay);
            });

            // Close results on click outside
            document.addEventListener('click', function (e) {
                if (!e.target.closest('.search-container')) {
                    resultsContainer.classList.add('hidden');
                }
            });

            // Handle result selection
            resultsContainer.addEventListener('click', function (e) {
                const result = e.target.closest('.search-result');
                if (result) {
                    const id = result.dataset.id;
                    if (onSelect) {
                        onSelect(id);
                    } else {
                        window.location.href = `/vault/view/${id}`;
                    }
                }
            });
        },

        /**
         * Keyboard shortcuts for search
         */
        initKeyboardShortcuts: function (inputElement) {
            if (!inputElement) return;

            document.addEventListener('keydown', function (e) {
                // Ctrl+K or Cmd+K
                if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                    e.preventDefault();
                    inputElement.focus();
                    inputElement.select();
                }

                // Escape to clear search
                if (e.key === 'Escape' && document.activeElement === inputElement) {
                    inputElement.value = '';
                    inputElement.blur();
                    const results = document.querySelector('.search-results');
                    if (results) results.classList.add('hidden');
                }
            });
        },

        /**
         * Advanced search with filters
         */
        advancedSearch: function (filters) {
            const params = new URLSearchParams();

            for (const [key, value] of Object.entries(filters)) {
                if (value !== null && value !== undefined && value !== '') {
                    params.append(key, value);
                }
            }

            return fetch(`/dashboard/advanced-search?${params}`)
                .then(response => response.json());
        }
    };

    // Initialize global search
    document.addEventListener('DOMContentLoaded', function () {
        const searchInput = document.querySelector('.header-search-input, #globalSearch');
        const searchResults = document.getElementById('searchResults');

        if (searchInput && searchResults) {
            Search.initSearchInput(searchInput, searchResults);
            Search.initKeyboardShortcuts(searchInput);
        }
    });

    // Expose globally
    window.Search = Search;
})();