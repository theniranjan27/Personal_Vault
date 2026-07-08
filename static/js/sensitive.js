/**
 * PRIVATE VAULT - Sensitive Data Module
 * Handling sensitive values with reveal/hide functionality
 */

(function () {
    'use strict';

    const Sensitive = {
        /**
         * Toggle reveal/hide sensitive value
         */
        toggleReveal: function (elementId, value) {
            const element = document.getElementById(elementId);
            if (!element) return;

            const isRevealed = element.dataset.revealed === 'true';

            if (isRevealed) {
                this.hideValue(elementId);
            } else {
                this.revealValue(elementId, value);
            }
        },

        /**
         * Reveal sensitive value
         */
        revealValue: function (elementId, value, duration = 5000) {
            const element = document.getElementById(elementId);
            if (!element) return;

            // Log reveal action
            this.logReveal(element.dataset.itemId);

            // Store original masked value
            const originalText = element.textContent;

            // Show actual value
            element.textContent = value;
            element.dataset.revealed = 'true';
            element.style.color = '#ffc107';
            element.style.fontWeight = '600';

            // Auto-hide after duration
            if (duration > 0) {
                const timer = setTimeout(() => {
                    this.hideValue(elementId, originalText);
                }, duration);

                // Store timer for cleanup
                element.dataset.timer = timer;
            }

            // Update button
            this.updateRevealButton(elementId, true);
        },

        /**
         * Hide sensitive value
         */
        hideValue: function (elementId, maskedValue = null) {
            const element = document.getElementById(elementId);
            if (!element) return;

            // Clear timer
            if (element.dataset.timer) {
                clearTimeout(parseInt(element.dataset.timer));
                delete element.dataset.timer;
            }

            // Restore masked value
            if (maskedValue) {
                element.textContent = maskedValue;
            } else if (element.dataset.masked) {
                element.textContent = element.dataset.masked;
            }

            element.dataset.revealed = 'false';
            element.style.color = '';
            element.style.fontWeight = '';

            // Update button
            this.updateRevealButton(elementId, false);
        },

        /**
         * Update reveal button state
         */
        updateRevealButton: function (elementId, isRevealed) {
            const button = document.querySelector(`[data-target="${elementId}"]`);
            if (!button) return;

            if (isRevealed) {
                button.innerHTML = '🔒 Hide';
                button.classList.add('active');
            } else {
                button.innerHTML = '👁️ Reveal';
                button.classList.remove('active');
            }
        },

        /**
         * Log reveal action to audit trail
         */
        logReveal: function (itemId) {
            if (!itemId) return;

            fetch(`/activity/log-reveal/${itemId}`, {
                method: 'POST'
            }).catch(error => {
                console.error('Error logging reveal:', error);
            });
        },

        /**
         * Confirm reveal for highly sensitive values
         */
        confirmReveal: function (elementId, value, message = 'This contains sensitive information. Are you sure you want to reveal it?') {
            if (confirm(message)) {
                this.revealValue(elementId, value);
            }
        },

        /**
         * Initialize sensitive elements on page load
         */
        init: function () {
            document.querySelectorAll('[data-sensitive]').forEach(element => {
                const value = element.dataset.value;
                const masked = this.maskValue(value);

                element.textContent = masked;
                element.dataset.masked = masked;
                element.dataset.revealed = 'false';

                // Add reveal button if not present
                if (!element.closest('.sensitive-container')?.querySelector('.reveal-btn')) {
                    const container = document.createElement('div');
                    container.className = 'sensitive-container';
                    element.parentNode.insertBefore(container, element);
                    container.appendChild(element);

                    const btn = document.createElement('button');
                    btn.className = 'btn-sm reveal-btn';
                    btn.dataset.target = element.id || 'sensitive-' + Date.now();
                    btn.innerHTML = '👁️ Reveal';
                    btn.onclick = function () {
                        Sensitive.toggleReveal(element.id || this.dataset.target, value);
                    };
                    container.appendChild(btn);
                }
            });
        },

        /**
         * Mask value
         */
        maskValue: function (value, visibleChars = 4) {
            if (!value) return '';
            if (value.length <= visibleChars) return '•'.repeat(value.length);
            return '•'.repeat(value.length - visibleChars) + value.slice(-visibleChars);
        },

        /**
         * Get value type label
         */
        getValueType: function (value) {
            if (/^\d{4}-\d{4}-\d{4}$/.test(value)) return 'Aadhaar';
            if (/^[A-Z]{5}[0-9]{4}[A-Z]{1}$/.test(value)) return 'PAN';
            if (/^[A-Z][0-9]{7}$/.test(value)) return 'Passport';
            if (/^\d{9,18}$/.test(value)) return 'Account Number';
            if (/^[A-Z]{4}0[A-Z0-9]{6}$/.test(value)) return 'IFSC';
            if (/^[a-zA-Z0-9._-]+@[a-zA-Z0-9]+$/.test(value)) return 'UPI';
            return 'Sensitive';
        }
    };

    // Initialize on page load
    document.addEventListener('DOMContentLoaded', function () {
        Sensitive.init();
    });

    // Expose globally
    window.Sensitive = Sensitive;
})();