/**
 * Centralized CSRF Token Utility
 * Provides robust, cross-browser CSRF token extraction for Django applications
 * Follows DRY principles and professional error handling
 */
class CSRFTokenManager {
    constructor() {
        this.tokenCache = null;
        this.tokenTimestamp = null;
        this.CACHE_DURATION = 300000; // 5 minutes cache
        this.MIN_TOKEN_LENGTH = 32;
    }

    /**
     * Get CSRF token with caching and multiple fallback methods
     * @returns {string} Valid CSRF token or empty string
     */
    getToken() {
        // Return cached token if still valid
        if (this.isTokenCacheValid()) {
            return this.tokenCache;
        }

        // Extract fresh token
        const token = this.extractToken();
        
        // Cache valid token
        if (this.isValidToken(token)) {
            this.cacheToken(token);
            return token;
        }

        this.logTokenError();
        return '';
    }

    /**
     * Check if cached token is still valid
     * @returns {boolean}
     */
    isTokenCacheValid() {
        return this.tokenCache && 
               this.tokenTimestamp && 
               (Date.now() - this.tokenTimestamp) < this.CACHE_DURATION;
    }

    /**
     * Extract token using multiple fallback methods
     * @returns {string} Token or empty string
     */
    extractToken() {
        const extractors = [
            this.extractFromMetaTag.bind(this),
            this.extractFromFormInput.bind(this),
            this.extractFromCookie.bind(this)
        ];

        for (const extractor of extractors) {
            const token = extractor();
            if (this.isValidToken(token)) {
                return token;
            }
        }

        return '';
    }

    /**
     * Extract token from meta tag (most reliable)
     * @returns {string}
     */
    extractFromMetaTag() {
        const metaElement = document.querySelector('meta[name="csrf-token"]');
        return metaElement?.getAttribute('content') || '';
    }

    /**
     * Extract token from form input
     * @returns {string}
     */
    extractFromFormInput() {
        const inputElement = document.querySelector('[name="csrfmiddlewaretoken"]');
        return inputElement?.value || '';
    }

    /**
     * Extract token from cookie with proper decoding
     * @returns {string}
     */
    extractFromCookie() {
        const cookies = document.cookie.split(';');
        
        for (const cookie of cookies) {
            const trimmed = cookie.trim();
            if (trimmed.startsWith('csrftoken=')) {
                const encodedToken = trimmed.substring('csrftoken='.length);
                try {
                    return decodeURIComponent(encodedToken);
                } catch (error) {
                    console.warn('Failed to decode CSRF token from cookie:', error);
                    return encodedToken; // Fallback to raw token
                }
            }
        }

        return '';
    }

    /**
     * Validate token format and length
     * @param {string} token
     * @returns {boolean}
     */
    isValidToken(token) {
        return typeof token === 'string' && 
               token.length >= this.MIN_TOKEN_LENGTH &&
               /^[A-Za-z0-9]{32,}$/.test(token);
    }

    /**
     * Cache token with timestamp
     * @param {string} token
     */
    cacheToken(token) {
        this.tokenCache = token;
        this.tokenTimestamp = Date.now();
    }

    /**
     * Clear token cache
     */
    clearCache() {
        this.tokenCache = null;
        this.tokenTimestamp = null;
    }

    /**
     * Log token extraction error
     */
    logTokenError() {
        if (console && console.warn) {
            console.warn('CSRFTokenManager: No valid CSRF token found. ' +
                        'Check Django configuration and template setup.');
        }
    }

    /**
     * Refresh token (force re-extraction)
     * @returns {string}
     */
    refreshToken() {
        this.clearCache();
        return this.getToken();
    }
}

// Global instance
window.csrfTokenManager = new CSRFTokenManager();

/**
 * Global utility function for backward compatibility
 * @returns {string} CSRF token
 */
window.getCSRFToken = function() {
    return window.csrfTokenManager.getToken();
};

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CSRFTokenManager;
} 