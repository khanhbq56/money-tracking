/**
 * Bank Integration Management
 * Handles TPBank and future bank integration features
 */
class BankIntegrationManager {
    constructor() {
        this.initializeComponents();
        this.checkGmailPermissionStatus();
    }

    initializeComponents() {
        // Initialize bank status
        this.refreshBankStatuses();
        
        // Set up event listeners
        document.addEventListener('DOMContentLoaded', () => {
            this.setupEventListeners();
        });
    }

    setupEventListeners() {
        // Gmail permission status check
        this.checkGmailPermissionStatus();
    }

    /**
     * Toggle bank integration on/off
     */
    async toggleBankIntegration(bankCode) {
        const toggle = document.getElementById(`bank-toggle-${bankCode}`);
        const isEnabled = toggle.checked;
        

        
        try {
            if (isEnabled) {
                // User wants to enable bank integration
                await this.enableBankIntegration(bankCode);
            } else {
                // User wants to disable bank integration
                await this.disableBankIntegration(bankCode);
            }
        } catch (error) {
            console.error('Bank integration toggle error:', error);
            // Revert toggle state
            toggle.checked = !isEnabled;
            
            if (typeof showAlertDialog === 'function') {
                showAlertDialog(
                    window.i18n.t('error_occurred'),
                    { type: 'error' }
                );
            }
        }
    }

    /**
     * Toggle Gmail permission
     */
    async toggleGmailPermission() {
        const toggle = document.getElementById('gmail-permission-toggle');
        const isEnabled = toggle.checked;
        
        try {
            if (isEnabled) {
                // User wants to grant Gmail permission
                await this.requestGmailPermission();
            } else {
                // User wants to revoke Gmail permission
                await this.revokeGmailPermission();
            }
        } catch (error) {
            console.error('Gmail permission toggle error:', error);
            // Revert toggle state
            toggle.checked = !isEnabled;
            
            if (typeof showAlertDialog === 'function') {
                showAlertDialog(
                    window.i18n.t('error_occurred'),
                    { type: 'error' }
                );
            }
        }
    }

    /**
     * Revoke Gmail permission
     */
    async revokeGmailPermission() {
        const confirmed = await showConfirmationDialog(
            window.i18n.t('revoke_gmail_permission_confirm'),
            {
                title: window.i18n.t('revoke_gmail_permission'),
                confirmText: window.i18n.t('revoke'),
                cancelText: window.i18n.t('cancel'),
                type: 'warning'
            }
        );
        
        if (!confirmed) {
            return false;
        }
        
        const response = await fetch('/auth/gmail-oauth/revoke/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to revoke Gmail permission');
        }
        
        // Update UI
        this.updateGmailPermissionUI(false);
        
        if (typeof showAlertDialog === 'function') {
            showAlertDialog(
                window.i18n.t('gmail_permission_revoked'),
                { type: 'info' }
            );
        }
        
        return true;
    }

    /**
     * Enable bank integration - assumes Gmail permission already granted
     */
    async enableBankIntegration(bankCode) {
        // Step 1: Check if Gmail permission is already granted
        const hasPermission = await this.checkGmailPermission();
        
        if (!hasPermission) {
            // Redirect user to grant Gmail permission first
            if (typeof showAlertDialog === 'function') {
                showAlertDialog(
                    window.i18n.t('gmail_permission_required'),
                    { type: 'warning' }
                );
            }
            return;
        }
        
        // Step 2: Enable bank integration
        const response = await fetch('/api/bank-integration/enable/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            body: JSON.stringify({
                bank_code: bankCode
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to enable bank integration');
        }
        
        const result = await response.json();
        
        // Create custom alert to avoid dialog conflicts
        this.showBankMessage(
            window.i18n.t('bank_integration_enabled', { bank: bankCode.toUpperCase() }),
            'success'
        );
        
        // Update UI
        this.updateBankStatus(bankCode, true, result);
    }

    /**
     * Disable bank integration
     */
    async disableBankIntegration(bankCode) {
        const response = await fetch('/api/bank-integration/disable/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            body: JSON.stringify({
                bank_code: bankCode
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to disable bank integration');
        }
        
        // Create custom alert to avoid dialog conflicts
        this.showBankMessage(
            window.i18n.t('bank_integration_disabled', { bank: bankCode.toUpperCase() }),
            'info'
        );
        
        // Update UI
        this.updateBankStatus(bankCode, false);
    }

    /**
     * Check if user has Gmail permission
     */
    async checkGmailPermission() {
        try {
            const response = await fetch('/api/bank-integration/gmail-status/', {
                method: 'GET',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                }
            });
            
            if (!response.ok) {
                return false;
            }
            
            const result = await response.json();
            return result.has_permission;
        } catch (error) {
            console.error('Gmail permission check error:', error);
            return false;
        }
    }

    /**
     * Check Gmail permission status and update UI
     */
    async checkGmailPermissionStatus() {
        const hasPermission = await this.checkGmailPermission();
        this.updateGmailPermissionUI(hasPermission);
    }

    /**
     * Request Gmail permission via separate OAuth flow
     */
    async requestGmailPermission() {
        // Use standard confirmation dialog system from app.js
        if (typeof showConfirmationDialog === 'function') {
            const confirmed = await showConfirmationDialog(
                window.i18n.t('gmail_permission_required_message'),
                {
                    title: window.i18n.t('gmail_permission_required_title'),
                    confirmText: window.i18n.t('grant_permission'),
                    cancelText: window.i18n.t('cancel'),
                    type: 'info'
                }
            );
            
            if (confirmed) {
                // Redirect to separate Gmail OAuth flow with bank parameter
                window.location.href = '/auth/gmail-oauth/initiate/?bank=tpbank';
                return false; // Will be determined on return
            } else {
                return false;
            }
        } else {
            // Fallback without dialog
            window.location.href = '/auth/gmail-oauth/initiate/';
            return false;
        }
    }

    /**
     * Update Gmail permission status in UI
     */
    updateGmailPermissionUI(hasPermission) {
        const statusElement = document.querySelector('.gmail-permission-status');
        const toggle = document.getElementById('gmail-permission-toggle');
        
        if (statusElement) {
            const badge = statusElement.querySelector('.badge') || statusElement.querySelector('span');
            if (badge) {
                if (hasPermission) {
                    badge.className = 'badge success';
                    badge.textContent = `✅ ${window.i18n.t('connected')}`;
                } else {
                    badge.className = 'badge warning';
                    badge.textContent = `⚠️ ${window.i18n.t('not_connected')}`;
                }
            }
        }
        
        if (toggle) {
            toggle.checked = hasPermission;
        }
    }

    /**
     * Update bank status in UI
     */
    updateBankStatus(bankCode, isEnabled, data = {}) {
        const toggle = document.getElementById(`bank-toggle-${bankCode}`);
        const detailsDiv = document.getElementById(`${bankCode}-details`);
        const lastSyncSpan = document.getElementById(`${bankCode}-last-sync`);
        
        if (toggle) {
            toggle.checked = isEnabled;
        }
        
        if (detailsDiv) {
            if (isEnabled) {
                detailsDiv.classList.remove('hidden');
            } else {
                detailsDiv.classList.add('hidden');
            }
        }
        
        if (lastSyncSpan && data.last_sync) {
            lastSyncSpan.textContent = new Date(data.last_sync).toLocaleString();
        }
    }

    /**
     * Manual sync for a specific bank
     */
    async manualSync(bankCode) {
        if (typeof showAlertDialog === 'function') {
            showAlertDialog(
                'Manual sync functionality will be implemented in Phase 2-3',
                { type: 'info' }
            );
        }
    }

    /**
     * Show sync history for a bank
     */
    async showSyncHistory(bankCode) {
        if (typeof showAlertDialog === 'function') {
            showAlertDialog(
                'Sync history functionality will be implemented in Phase 2-3',
                { type: 'info' }
            );
        }
    }

    /**
     * Show bank-specific message dialog
     */
    showBankMessage(message, type) {
        // Create simple modal manually to avoid conflicts
        const modalId = 'bank-message-' + Date.now();
        const modal = document.createElement('div');
        modal.id = modalId;
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm z-[60] flex items-center justify-center';
        modal.style.display = 'flex';
        
        const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : type === 'warning' ? '⚠️' : 'ℹ️';
        const title = type === 'success' ? window.i18n.t('success') : 
                      type === 'error' ? window.i18n.t('error') : 
                      type === 'warning' ? window.i18n.t('warning') : 
                      window.i18n.t('notice');
        
        modal.innerHTML = `
            <div class="bg-white rounded-xl shadow-2xl max-w-md w-full mx-4 overflow-hidden" onclick="event.stopPropagation()">
                <!-- Header -->
                <div class="bg-gradient-to-r from-purple-600 to-pink-600 px-6 py-4 text-white">
                    <h3 class="text-lg font-semibold">${title}</h3>
                </div>
                
                <!-- Content -->
                <div class="p-6 text-center">
                    <div class="mb-4 text-4xl">
                        ${icon}
                    </div>
                    <p class="text-gray-700 mb-6 leading-relaxed">${message}</p>
                    
                    <!-- Actions -->
                    <div class="flex justify-center">
                        <button id="${modalId}-ok" class="btn btn--primary">
                            OK
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Add event listeners
        const okBtn = document.getElementById(`${modalId}-ok`);
        if (okBtn) {
            okBtn.addEventListener('click', () => {
                modal.remove();
            });
        }
        
        // Handle outside click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
        
        // Handle ESC key
        const handleEsc = (e) => {
            if (e.key === 'Escape') {
                modal.remove();
                document.removeEventListener('keydown', handleEsc);
            }
        };
        document.addEventListener('keydown', handleEsc);
    }

    /**
     * Refresh all bank statuses
     */
    async refreshBankStatuses() {
        try {
            const response = await fetch('/api/bank-integration/status/', {
                method: 'GET',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                }
            });
            
            if (!response.ok) {
                return;
            }
            
            const statuses = await response.json();
            
            // Update UI for each bank
            Object.entries(statuses).forEach(([bankCode, status]) => {
                this.updateBankStatus(bankCode, status.enabled, status);
            });
            
        } catch (error) {
            console.error('Failed to refresh bank statuses:', error);
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Wait for i18n to be ready
    const initBankIntegration = () => {
        if (window.i18n && typeof window.i18n.t === 'function') {
            window.bankIntegrationManager = new BankIntegrationManager();
        } else {
            setTimeout(initBankIntegration, 100);
        }
    };
    
    initBankIntegration();
});

// Export for global access
window.BankIntegrationManager = BankIntegrationManager; 