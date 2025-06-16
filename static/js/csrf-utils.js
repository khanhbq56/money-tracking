/**
 * CSRF Token Utility - Centralized CSRF token management
 * This utility provides robust CSRF token retrieval for production environments
 * where secure cookies may not be accessible to JavaScript.
 */

/**
 * Get CSRF token using multiple fallback methods
 * Priority order:
 * 1. DOM input field (from forms)
 * 2. Meta tag (embedded in HTML template)
 * 3. Cookie (for local development)
 * 
 * @returns {string} CSRF token or empty string if not found
 */
function getCSRFToken() {
    // Method 1: Try to get from form input field
    const formToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    if (formToken) return formToken;
    
    // Method 2: Try to get from meta tag (most reliable for production)
    const metaToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    if (metaToken) return metaToken;
    
    // Method 3: Try to get from hidden input
    const hiddenInput = document.querySelector('input[name="csrfmiddlewaretoken"]')?.value;
    if (hiddenInput) return hiddenInput;
    
    // Method 4: Fallback to cookie (for development/localhost)
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return value;
        }
    }
    
    // Method 5: Log warning if no token found
    console.warn('CSRF token not found. This may cause API requests to fail.');
    return '';
}

/**
 * Get common headers for AJAX requests including CSRF token
 * @returns {Object} Headers object ready for fetch/AJAX requests
 */
function getCommonHeaders() {
    return {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken()
    };
}

/**
 * Validate CSRF token availability
 * @returns {boolean} True if CSRF token is available
 */
function validateCSRFToken() {
    const token = getCSRFToken();
    if (!token) {
        console.error('CSRF token validation failed. Requests may be rejected by server.');
        return false;
    }
    return true;
}

// Export functions for global use
window.getCSRFToken = getCSRFToken;
window.getCommonHeaders = getCommonHeaders;
window.validateCSRFToken = validateCSRFToken;

// Auto-validate on page load
document.addEventListener('DOMContentLoaded', function() {
    if (!validateCSRFToken()) {
        console.warn('⚠️ CSRF protection warning: Token not found. Please ensure template includes {% csrf_token %}');
    }
}); 