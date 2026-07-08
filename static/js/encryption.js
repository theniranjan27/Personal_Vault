/**
 * PRIVATE VAULT - Encryption Module
 * Client-side encryption utilities
 */

(function () {
    'use strict';

    const Encryption = {
        /**
         * Encrypt text using Web Crypto API
         */
        encrypt: async function (text, key) {
            try {
                const encoder = new TextEncoder();
                const data = encoder.encode(text);

                // Generate IV
                const iv = crypto.getRandomValues(new Uint8Array(12));

                // Import key
                const cryptoKey = await this.importKey(key);

                // Encrypt
                const encrypted = await crypto.subtle.encrypt(
                    {
                        name: 'AES-GCM',
                        iv: iv
                    },
                    cryptoKey,
                    data
                );

                // Combine IV and encrypted data
                const combined = new Uint8Array(iv.length + encrypted.byteLength);
                combined.set(iv, 0);
                combined.set(new Uint8Array(encrypted), iv.length);

                return btoa(String.fromCharCode(...combined));
            } catch (error) {
                console.error('Encryption error:', error);
                return null;
            }
        },

        /**
         * Decrypt text using Web Crypto API
         */
        decrypt: async function (encryptedText, key) {
            try {
                const combined = Uint8Array.from(atob(encryptedText), c => c.charCodeAt(0));

                // Extract IV and data
                const iv = combined.slice(0, 12);
                const data = combined.slice(12);

                // Import key
                const cryptoKey = await this.importKey(key);

                // Decrypt
                const decrypted = await crypto.subtle.decrypt(
                    {
                        name: 'AES-GCM',
                        iv: iv
                    },
                    cryptoKey,
                    data
                );

                const decoder = new TextDecoder();
                return decoder.decode(decrypted);
            } catch (error) {
                console.error('Decryption error:', error);
                return null;
            }
        },

        /**
         * Generate encryption key
         */
        generateKey: async function () {
            const key = await crypto.subtle.generateKey(
                {
                    name: 'AES-GCM',
                    length: 256
                },
                true,
                ['encrypt', 'decrypt']
            );

            const exported = await crypto.subtle.exportKey('raw', key);
            return btoa(String.fromCharCode(...new Uint8Array(exported)));
        },

        /**
         * Import key from base64 string
         */
        importKey: async function (keyString) {
            const keyData = Uint8Array.from(atob(keyString), c => c.charCodeAt(0));

            return await crypto.subtle.importKey(
                'raw',
                keyData,
                {
                    name: 'AES-GCM',
                    length: 256
                },
                false,
                ['encrypt', 'decrypt']
            );
        },

        /**
         * Hash text using SHA-256
         */
        hash: async function (text) {
            const encoder = new TextEncoder();
            const data = encoder.encode(text);
            const hash = await crypto.subtle.digest('SHA-256', data);
            return btoa(String.fromCharCode(...new Uint8Array(hash)));
        },

        /**
         * Generate random string
         */
        generateRandomString: function (length = 32) {
            const array = new Uint8Array(length);
            crypto.getRandomValues(array);
            return btoa(String.fromCharCode(...array)).slice(0, length);
        },

        /**
         * Generate secure PIN
         */
        generatePIN: function (length = 6) {
            let pin = '';
            for (let i = 0; i < length; i++) {
                pin += Math.floor(Math.random() * 10);
            }
            return pin;
        },

        /**
         * Generate password
         */
        generatePassword: function (length = 16, options = {}) {
            const defaults = {
                uppercase: true,
                lowercase: true,
                numbers: true,
                symbols: true,
                excludeAmbiguous: false
            };

            const opts = { ...defaults, ...options };

            let chars = '';
            if (opts.uppercase) chars += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
            if (opts.lowercase) chars += 'abcdefghijklmnopqrstuvwxyz';
            if (opts.numbers) chars += '0123456789';
            if (opts.symbols) chars += '!@#$%^&*()_+-=[]{}|;:,.<>?';

            if (opts.excludeAmbiguous) {
                chars = chars.replace(/[0OIl1]/g, '');
            }

            if (chars.length === 0) {
                chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
            }

            let password = '';
            const array = new Uint32Array(length);
            crypto.getRandomValues(array);

            for (let i = 0; i < length; i++) {
                password += chars[array[i] % chars.length];
            }

            return password;
        },

        /**
         * Check password strength
         */
        checkPasswordStrength: function (password) {
            let score = 0;

            // Length
            if (password.length >= 8) score += 1;
            if (password.length >= 12) score += 1;
            if (password.length >= 16) score += 1;

            // Character types
            if (/[a-z]/.test(password)) score += 1;
            if (/[A-Z]/.test(password)) score += 1;
            if (/[0-9]/.test(password)) score += 1;
            if (/[^a-zA-Z0-9]/.test(password)) score += 1;

            // Additional checks
            if (/(.)\1{2,}/.test(password)) score -= 1; // Repeated characters
            if (/^[a-zA-Z]+$/.test(password)) score -= 1; // Only letters

            // Determine strength
            let strength = 'weak';
            let color = '#ef5350';

            if (score >= 7) {
                strength = 'strong';
                color = '#4caf50';
            } else if (score >= 5) {
                strength = 'good';
                color = '#ff9800';
            } else if (score >= 3) {
                strength = 'fair';
                color = '#ffc107';
            }

            return {
                score: Math.max(0, Math.min(10, score)),
                strength: strength,
                color: color,
                label: strength.charAt(0).toUpperCase() + strength.slice(1)
            };
        }
    };

    // Expose globally
    window.Encryption = Encryption;
})();