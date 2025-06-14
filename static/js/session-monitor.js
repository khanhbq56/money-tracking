/**
 * Session Monitor - Activity Tracking and Timeout Handling
 * Handles user inactivity detection and session expiration
 */

class SessionMonitor {
    constructor() {
        this.IDLE_TIMEOUT = 30 * 60 * 1000; // 30 minutes
        this.WARNING_TIME = 5 * 60 * 1000;  // 5 minutes before timeout
        this.CHECK_INTERVAL = 60 * 1000;    // Check every minute
        
        this.lastActivity = Date.now();
        this.warningShown = false;
        this.timeoutTimer = null;
        this.checkTimer = null;
        
        this.init();
    }
    
    init() {
        // Skip for unauthenticated users
        if (!document.body.classList.contains('authenticated')) {
            return;
        }
        
        // Track activity events
        this.setupActivityTracking();
        
        // Start monitoring
        this.startMonitoring();
        
        // Handle visibility change (tab switching)
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                this.updateActivity();
            }
        });
    }
    
    setupActivityTracking() {
        const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
        
        events.forEach(event => {
            document.addEventListener(event, () => this.updateActivity(), true);
        });
    }
    
    updateActivity() {
        this.lastActivity = Date.now();
        this.warningShown = false;
        
        // Clear any existing warning
        this.hideWarning();
    }
    
    startMonitoring() {
        this.checkTimer = setInterval(() => {
            this.checkInactivity();
        }, this.CHECK_INTERVAL);
    }
    
    checkInactivity() {
        const now = Date.now();
        const inactiveTime = now - this.lastActivity;
        
        // Show warning before timeout
        if (inactiveTime >= (this.IDLE_TIMEOUT - this.WARNING_TIME) && !this.warningShown) {
            this.showInactivityWarning();
        }
        
        // Handle timeout
        if (inactiveTime >= this.IDLE_TIMEOUT) {
            this.handleTimeout();
        }
    }
    
    async showInactivityWarning() {
        this.warningShown = true;
        
        const remainingMinutes = Math.ceil((this.IDLE_TIMEOUT - (Date.now() - this.lastActivity)) / (60 * 1000));
        
        const extendSession = await showConfirmationDialog(
            window.i18n.t('session_timeout_warning').replace('{minutes}', remainingMinutes),
            {
                type: 'warning',
                confirmText: window.i18n.t('extend_session'),
                cancelText: window.i18n.t('logout_now')
            }
        );
        
        if (extendSession) {
            this.updateActivity();
            // Ping server to extend session
            this.pingServer();
        } else {
            // User chose to logout
            this.handleTimeout();
        }
    }
    
    hideWarning() {
        // Implementation would hide any active warning modal
        // This depends on your modal system
    }
    
    async pingServer() {
        try {
            await fetch('/api/ping', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
        } catch (error) {
            console.warn('Failed to ping server:', error);
        }
    }
    
    async handleTimeout() {
        // Stop monitoring
        if (this.checkTimer) {
            clearInterval(this.checkTimer);
        }
        
        showAlertDialog(window.i18n.t('session_expired'), { type: 'warning' });
        
        // Auto logout after showing message
        setTimeout(() => {
            if (window.authManager) {
                window.authManager.handleLogout();
            } else {
                // Fallback: reload page to trigger authentication
                window.location.reload();
            }
        }, 2000);
    }
    
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
    }
    
    // Method to manually extend session (called by user activity)
    extendSession() {
        this.updateActivity();
        this.pingServer();
    }
    
    // Cleanup method
    destroy() {
        if (this.checkTimer) {
            clearInterval(this.checkTimer);
        }
    }
}

// Initialize session monitor when DOM is ready
let sessionMonitor;
document.addEventListener('DOMContentLoaded', () => {
    // Wait for dependencies
    const initSessionMonitor = () => {
        if (window.i18n && window.showConfirmationDialog && window.showAlertDialog) {
            sessionMonitor = new SessionMonitor();
            window.sessionMonitor = sessionMonitor;
        } else {
            setTimeout(initSessionMonitor, 100);
        }
    };
    
    initSessionMonitor();
});

// Export for global access
window.sessionMonitor = null; 