/**
 * Session Monitor - Tracks session status and demo account expiration
 */
class SessionMonitor {
    constructor() {
        this.checkInterval = 60000; // Check every minute
        this.warningShown = false;
        this.init();
    }

    init() {
        // Only monitor if user is authenticated
        if (!document.body.classList.contains('authenticated')) {
            return;
        }

        // Start monitoring
        this.startMonitoring();
        
        // Monitor page visibility to refresh session when user returns
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                this.checkSessionStatus();
            }
        });
    }

    startMonitoring() {
        setInterval(() => {
            this.checkSessionStatus();
        }, this.checkInterval);
    }

    async checkSessionStatus() {
        try {
            const response = await fetch('/auth/session/status/', {
                method: 'GET',
                credentials: 'same-origin',
                headers: {
                    'X-CSRFToken': getCSRFToken()
                }
            });

            if (response.status === 401) {
                // Session expired
                this.handleSessionExpired();
                return;
            }

            if (response.ok) {
                const data = await response.json();
                
                if (data.is_demo && data.demo_expires_at) {
                    this.checkDemoExpiration(data.demo_expires_at);
                }
            }
        } catch (error) {
            console.warn('Session status check failed:', error);
        }
    }

    checkDemoExpiration(expiresAt) {
        const now = new Date().getTime();
        const expiry = new Date(expiresAt).getTime();
        const timeLeft = expiry - now;

        // Show warning 5 minutes before expiration
        if (timeLeft < 5 * 60 * 1000 && timeLeft > 0 && !this.warningShown) {
            this.showDemoExpirationWarning(Math.floor(timeLeft / 60000));
            this.warningShown = true;
        }

        // Handle expiration
        if (timeLeft <= 0) {
            this.handleDemoExpired();
        }
    }

    showDemoExpirationWarning(minutesLeft) {
        if (typeof showAlertDialog === 'function') {
            showAlertDialog(
                window.i18n.t('demo_expiring_soon').replace('{minutes}', minutesLeft),
                { 
                    type: 'warning',
                    persistent: true 
                }
            );
        }
    }

    handleSessionExpired() {
        if (typeof showAlertDialog === 'function') {
            showAlertDialog(window.i18n.t('session_expired'), { 
                type: 'error',
                onClose: () => {
                    window.location.reload();
                }
            });
        } else {
            window.location.reload();
        }
    }

    handleDemoExpired() {
        if (typeof showAlertDialog === 'function') {
            showAlertDialog(window.i18n.t('demo_session_expired'), { 
                type: 'warning',
                onClose: () => {
                    window.location.href = '/?demo_expired=true';
                }
            });
        } else {
            window.location.href = '/?demo_expired=true';
        }
    }
}

// Initialize session monitor when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Wait for dependencies
    const initSessionMonitor = () => {
        if (window.i18n) {
            window.sessionMonitor = new SessionMonitor();
        } else {
            setTimeout(initSessionMonitor, 100);
        }
    };
    
    initSessionMonitor();
}); 