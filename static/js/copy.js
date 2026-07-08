/**
 * PRIVATE VAULT - Copy Module
 * Copy to clipboard functionality
 */

(function () {
    'use strict';

    const Copy = {
        /**
         * Copy text to clipboard
         */
        copyText: function (text, options = {}) {
            const {
                successMessage = 'Copied to clipboard!',
                errorMessage = 'Failed to copy',
                autoHide = true,
                duration = 2000
            } = options;

            if (!text) {
                this.showNotification('Nothing to copy', 'warning');
                return false;
            }

            // Try modern clipboard API first
            if (navigator.clipboard && navigator.clipboard.writeText) {
                return navigator.clipboard.writeText(text)
                    .then(() => {
                        this.showNotification(successMessage, 'success', autoHide, duration);
                        return true;
                    })
                    .catch(() => {
                        return this.fallbackCopy(text, successMessage, errorMessage);
                    });
            }

            // Fallback for older browsers
            return this.fallbackCopy(text, successMessage, errorMessage);
        },

        /**
         * Fallback copy method using textarea
         */
        fallbackCopy: function (text, successMessage, errorMessage) {
            try {
                const textarea = document.createElement('textarea');
                textarea.value = text;
                textarea.style.position = 'fixed';
                textarea.style.opacity = '0';
                textarea.style.left = '-9999px';
                textarea.style.top = '-9999px';
                document.body.appendChild(textarea);
                textarea.select();

                const success = document.execCommand('copy');
                document.body.removeChild(textarea);

                if (success) {
                    this.showNotification(successMessage || 'Copied to clipboard!', 'success');
                    return true;
                } else {
                    this.showNotification(errorMessage || 'Failed to copy', 'error');
                    return false;
                }
            } catch (error) {
                console.error('Copy error:', error);
                this.showNotification(errorMessage || 'Failed to copy', 'error');
                return false;
            }
        },

        /**
         * Copy to clipboard with element reference
         */
        copyFromElement: function (elementId, options = {}) {
            const element = document.getElementById(elementId);
            if (!element) {
                console.error('Element not found:', elementId);
                return false;
            }

            const text = element.textContent || element.value || '';
            return this.copyText(text, options);
        },

        /**
         * Copy to clipboard with value and show feedback on button
         */
        copyWithFeedback: function (text, buttonElement, options = {}) {
            const {
                successMessage = '✅ Copied!',
                resetMessage = '📋 Copy',
                duration = 2000
            } = options;

            const originalText = buttonElement.innerHTML;

            this.copyText(text, {
                successMessage: '',
                errorMessage: ''
            }).then(success => {
                if (success) {
                    buttonElement.innerHTML = successMessage;
                    buttonElement.classList.add('copied');

                    setTimeout(() => {
                        buttonElement.innerHTML = resetMessage;
                        buttonElement.classList.remove('copied');
                    }, duration);
                } else {
                    buttonElement.innerHTML = '❌ Failed';
                    setTimeout(() => {
                        buttonElement.innerHTML = resetMessage;
                    }, duration);
                }
            });
        },

        /**
         * Copy JSON data as formatted string
         */
        copyJSON: function (data, options = {}) {
            try {
                const text = typeof data === 'string' ? data : JSON.stringify(data, null, 2);
                return this.copyText(text, options);
            } catch (error) {
                console.error('JSON copy error:', error);
                return false;
            }
        },

        /**
         * Copy multiple values as formatted list
         */
        copyList: function (items, options = {}) {
            const text = items.map(item => {
                if (typeof item === 'object') {
                    return Object.entries(item)
                        .map(([key, value]) => `${key}: ${value}`)
                        .join('\n');
                }
                return String(item);
            }).join('\n\n');

            return this.copyText(text, options);
        },

        /**
         * Show notification
         */
        showNotification: function (message, type = 'info', autoHide = true, duration = 2000) {
            // Use global notification if available
            if (window.showNotification) {
                window.showNotification(message, type, duration);
                return;
            }

            // Fallback notification
            const notification = document.createElement('div');
            notification.className = `notification ${type}`;
            notification.textContent = message;
            document.body.appendChild(notification);

            if (autoHide) {
                setTimeout(() => {
                    notification.style.opacity = '0';
                    notification.style.transform = 'translateY(-20px)';
                    setTimeout(() => notification.remove(), 300);
                }, duration);
            }
        },

        /**
         * Initialize copy buttons on page
         */
        init: function () {
            document.querySelectorAll('[data-copy]').forEach(button => {
                const target = button.dataset.copy;
                const value = button.dataset.value;

                button.addEventListener('click', function (e) {
                    e.preventDefault();

                    if (value) {
                        Copy.copyWithFeedback(value, this);
                    } else if (target) {
                        const element = document.getElementById(target);
                        if (element) {
                            Copy.copyWithFeedback(element.textContent || element.value, this);
                        }
                    }
                });
            });
        }
    };

    // Initialize on page load
    document.addEventListener('DOMContentLoaded', function () {
        Copy.init();
    });

    // Expose globally
    window.Copy = Copy;
})();