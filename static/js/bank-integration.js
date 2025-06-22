/**
 * Bank Integration Management
 * Handles TPBank and future bank integration features
 */
class BankIntegrationManager {
    constructor() {
        this.isLoading = false;
        this.syncInProgress = false;
        this.initializeComponents();
        this.checkGmailPermissionStatus();
    }

    initializeComponents() {
        // Initialize bank status
        this.refreshBankStatuses();
        this.loadAllBankConfigs(); // Load custom banks too
        
        // Set up event listeners
        document.addEventListener('DOMContentLoaded', () => {
            this.setupEventListeners();
        });
    }

    setupEventListeners() {
        // Gmail permission status check
        this.checkGmailPermissionStatus();
    }

    // Debug logging to console
    debugLog(message, type = 'info') {
        // Try to log to settings page debug console
        if (typeof logToConsole === 'function') {
            logToConsole(message, type);
        } else {
            // Fallback to browser console
            console.log(`[BankSync] ${message}`);
        }
    }

    // Check sync status
    async checkSyncStatus() {
        try {
            this.debugLog('📊 Checking sync status...', 'info');
            
            const response = await fetch('/api/bank-integration/sync-status/', {
                method: 'GET',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                }
            });
            
            if (response.ok) {
                const result = await response.json();
                this.debugLog(`✅ Status: ${JSON.stringify(result.data, null, 2)}`, 'success');
                return result.data;
            } else {
                this.debugLog(`❌ Status check failed: ${response.status}`, 'error');
                return null;
            }
        } catch (error) {
            this.debugLog(`💥 Status check error: ${error.message}`, 'error');
            return null;
        }
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
     * Manual sync for a specific bank - shows advanced sync options
     */
    async manualSync(bankCode) {
        // Create sync options modal
        const syncModal = this.createSyncOptionsModal(bankCode);
        document.body.appendChild(syncModal);
        syncModal.style.display = 'flex';
    }

    /**
     * Create advanced sync options modal
     */
    createSyncOptionsModal(bankCode) {
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm z-50 flex items-center justify-center';
        modal.id = `sync-modal-${bankCode}`;
        
        const today = new Date();
        const todayStr = today.toISOString().split('T')[0];
        const lastMonthStr = new Date(today.getFullYear(), today.getMonth() - 1, today.getDate()).toISOString().split('T')[0];
        
        modal.innerHTML = `
            <div class="bg-white rounded-xl p-6 w-full max-w-md mx-4 shadow-2xl">
                <div class="flex items-center justify-between mb-4">
                    <h3 class="text-lg font-medium">🔄 ${window.i18n.t('sync_options')} - ${bankCode.toUpperCase()}</h3>
                    <button onclick="this.closest('.fixed').remove()" class="text-gray-400 hover:text-gray-600">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
                
                <form id="sync-options-form-${bankCode}" class="space-y-4">
                    <!-- Sync Type Selection -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">${window.i18n.t('sync_type')}</label>
                        <div class="space-y-2">
                            <label class="flex items-center">
                                <input type="radio" name="syncType" value="recent" class="mr-2" checked>
                                <span class="text-sm">📅 ${window.i18n.t('sync_recent_emails')} (${window.i18n.t('last_7_days')})</span>
                            </label>
                            <label class="flex items-center">
                                <input type="radio" name="syncType" value="specific_date" class="mr-2">
                                <span class="text-sm">📅 ${window.i18n.t('sync_specific_date')}</span>
                            </label>
                            <label class="flex items-center">
                                <input type="radio" name="syncType" value="specific_month" class="mr-2">
                                <span class="text-sm">📅 ${window.i18n.t('sync_specific_month')}</span>
                            </label>
                            <label class="flex items-center">
                                <input type="radio" name="syncType" value="date_range" class="mr-2">
                                <span class="text-sm">📅 ${window.i18n.t('sync_date_range')}</span>
                            </label>
                            <label class="flex items-center">
                                <input type="radio" name="syncType" value="all_emails" class="mr-2">
                                <span class="text-sm">📧 ${window.i18n.t('sync_all_emails')}</span>
                            </label>
                        </div>
                    </div>
                    
                    <!-- Specific Date Input -->
                    <div id="specific-date-${bankCode}" class="sync-option hidden">
                        <label class="block text-sm font-medium text-gray-700 mb-1">${window.i18n.t('select_date')}</label>
                        <input type="date" name="specificDate" class="w-full border border-gray-300 rounded-lg px-3 py-2" value="${todayStr}">
                    </div>
                    
                    <!-- Specific Month Input -->
                    <div id="specific-month-${bankCode}" class="sync-option hidden">
                        <label class="block text-sm font-medium text-gray-700 mb-1">${window.i18n.t('select_month')}</label>
                        <input type="month" name="specificMonth" class="w-full border border-gray-300 rounded-lg px-3 py-2" value="${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}">
                    </div>
                    
                    <!-- Date Range Inputs -->
                    <div id="date-range-${bankCode}" class="sync-option hidden">
                        <div class="grid grid-cols-2 gap-3">
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">${window.i18n.t('from_date')}</label>
                                <input type="date" name="fromDate" class="w-full border border-gray-300 rounded-lg px-3 py-2" value="${lastMonthStr}">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">${window.i18n.t('to_date')}</label>
                                <input type="date" name="toDate" class="w-full border border-gray-300 rounded-lg px-3 py-2" value="${todayStr}">
                            </div>
                        </div>
                    </div>
                    
                    <!-- Advanced Options -->
                    <div class="border-t pt-4">
                        <label class="flex items-center mb-2">
                            <input type="checkbox" name="forceRefresh" class="mr-2">
                            <span class="text-sm">${window.i18n.t('force_refresh')} (${window.i18n.t('reprocess_existing_emails')})</span>
                        </label>
                        <label class="flex items-center">
                            <input type="checkbox" name="notifyResults" class="mr-2" checked>
                            <span class="text-sm">${window.i18n.t('show_detailed_results')}</span>
                        </label>
                    </div>
                    
                    <!-- Action Buttons -->
                    <div class="flex space-x-3 pt-4">
                        <button type="button" id="preview-btn-${bankCode}" class="flex-1 bg-gradient-to-r from-blue-600 to-cyan-600 text-white px-4 py-2 rounded-lg font-medium hover:from-blue-700 hover:to-cyan-700 transition-all">
                            👀 ${window.i18n.t('preview_transactions')}
                        </button>
                        <button type="submit" class="flex-1 bg-gradient-to-r from-purple-600 to-pink-600 text-white px-4 py-2 rounded-lg font-medium hover:from-purple-700 hover:to-pink-700 transition-all">
                            🔄 ${window.i18n.t('start_sync')}
                        </button>
                        <button type="button" onclick="this.closest('.fixed').remove()" class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors">
                            ${window.i18n.t('cancel')}
                        </button>
                    </div>
                </form>
            </div>
        `;
        
        // Add event listeners for radio buttons
        const radioButtons = modal.querySelectorAll('input[name="syncType"]');
        const syncOptions = modal.querySelectorAll('.sync-option');
        
        radioButtons.forEach(radio => {
            radio.addEventListener('change', () => {
                // Hide all options
                syncOptions.forEach(option => option.classList.add('hidden'));
                
                // Show relevant option
                const selectedOption = modal.querySelector(`#${radio.value.replace('_', '-')}-${bankCode}`);
                if (selectedOption) {
                    selectedOption.classList.remove('hidden');
                }
            });
        });
        
        // Form submission
        const form = modal.querySelector(`#sync-options-form-${bankCode}`);
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.executeSyncWithOptions(bankCode, new FormData(form));
            modal.remove();
        });
        
        // Preview button
        const previewBtn = modal.querySelector(`#preview-btn-${bankCode}`);
        if (previewBtn) {
            previewBtn.addEventListener('click', async () => {
                console.log('Preview button clicked for bank:', bankCode);
                try {
                    await this.executeSyncPreview(bankCode, new FormData(form));
                } catch (error) {
                    console.error('Preview error:', error);
                    if (typeof showAlertDialog === 'function') {
                        showAlertDialog(`❌ Preview error: ${error.message}`, { type: 'error' });
                    }
                }
            });
        }
        
        return modal;
    }

    /**
     * Execute sync preview with specific options
     */
    async executeSyncPreview(bankCode, formData) {
        const syncType = formData.get('syncType');
        const forceRefresh = formData.get('forceRefresh') === 'on';
        
        // Build sync parameters (same as sync)
        const syncParams = {
            bank_code: bankCode,
            force_refresh: forceRefresh
        };
        
        // Add date parameters based on sync type
        switch (syncType) {
            case 'specific_date':
                syncParams.sync_date = formData.get('specificDate');
                break;
            case 'specific_month':
                const monthValue = formData.get('specificMonth');
                const [year, month] = monthValue.split('-');
                syncParams.sync_year = parseInt(year);
                syncParams.sync_month = parseInt(month);
                break;
            case 'date_range':
                syncParams.from_date = formData.get('fromDate');
                syncParams.to_date = formData.get('toDate');
                break;
            case 'all_emails':
                syncParams.sync_all = true;
                break;
        }
        
        // Show progress indicator
        this.showSyncProgress(bankCode, 'preview');
        
        try {
            console.log('👀 Starting sync preview with params:', syncParams);
            
            const response = await fetch('/api/bank-integration/sync-preview/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                },
                body: JSON.stringify(syncParams)
            });
            
            const result = await response.json();
            console.log('📊 Preview result:', result);
            
            // Hide progress
            this.hideSyncProgress();
            
            if (result.success) {
                // Close current modal
                document.querySelector('.fixed')?.remove();
                
                // Show preview modal
                this.showTransactionPreviewModal(bankCode, result);
            } else {
                throw new Error(result.error || 'Preview failed');
            }
            
        } catch (error) {
            console.error('💥 Preview error:', error);
            this.hideSyncProgress();
            
            if (typeof showAlertDialog === 'function') {
                showAlertDialog(
                    `❌ ${window.i18n.t('preview_failed')}: ${error.message}`,
                    { type: 'error' }
                );
            }
        }
    }

    /**
     * Execute sync with specific options
     */
    async executeSyncWithOptions(bankCode, formData) {
        const syncType = formData.get('syncType');
        const forceRefresh = formData.get('forceRefresh') === 'on';
        const notifyResults = formData.get('notifyResults') === 'on';
        
        // Build sync parameters
        const syncParams = {
            bank_code: bankCode,
            force_refresh: forceRefresh
        };
        
        // Add date parameters based on sync type
        switch (syncType) {
            case 'specific_date':
                syncParams.sync_date = formData.get('specificDate');
                break;
            case 'specific_month':
                const monthValue = formData.get('specificMonth');
                const [year, month] = monthValue.split('-');
                syncParams.sync_year = parseInt(year);
                syncParams.sync_month = parseInt(month);
                break;
            case 'date_range':
                syncParams.from_date = formData.get('fromDate');
                syncParams.to_date = formData.get('toDate');
                break;
            case 'all_emails':
                syncParams.sync_all = true;
                break;
            case 'recent':
            default:
                // Use default recent sync (last 7 days)
                break;
        }
        
        // Show progress indicator
        this.showSyncProgress(bankCode, 'sync');
        
        try {
            console.log('🚀 Starting bank sync request with params:', syncParams);
            this.debugLog('🚀 Starting bank sync request', 'info');
            this.debugLog(`📋 Params: ${JSON.stringify(syncParams)}`, 'info');
            
            // Add timeout wrapper for fetch
            const controller = new AbortController();
            const timeoutId = setTimeout(() => {
                console.error('⏰ Request timeout after 60 seconds');
                this.debugLog('⏰ Request timeout after 60 seconds', 'error');
                controller.abort();
            }, 60000); // 60 second timeout
            
            const response = await fetch('/api/bank-integration/sync/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                },
                body: JSON.stringify(syncParams),
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            console.log('📡 Response received:', response.status, response.statusText);
            this.debugLog(`📡 Response: ${response.status} ${response.statusText}`, 'success');
            
            const result = await response.json();
            console.log('📊 Sync result:', result);
            this.debugLog(`📊 Result: ${JSON.stringify(result, null, 2)}`, 'info');
            
            // Hide progress
            this.hideSyncProgress();
            
            if (result.success) {
                console.log('✅ Sync successful, updating UI');
                // Update UI with sync results
                this.updateBankSyncStatus(bankCode, result.data);
                
                if (notifyResults) {
                    console.log('📋 Showing detailed sync results');
                    this.showSyncResultsModal(bankCode, result.data);
                } else {
                    // Simple success notification
                    console.log('🎉 Showing simple success notification');
                    if (typeof showAlertDialog === 'function') {
                        showAlertDialog(
                            `✅ ${window.i18n.t('sync_completed_successfully')} ${bankCode.toUpperCase()}!`,
                            { type: 'success' }
                        );
                    }
                }
            } else {
                console.error('❌ Sync failed:', result.error);
                throw new Error(result.error || 'Sync failed');
            }
            
        } catch (error) {
            console.error('💥 Sync error:', error);
            this.debugLog(`💥 Sync error: ${error.message}`, 'error');
            
            let errorMessage = error.message;
            
            if (error.name === 'AbortError') {
                errorMessage = 'Sync timed out after 60 seconds. Please try again.';
                console.error('⏰ Sync request timed out');
                this.debugLog('⏰ Sync request timed out', 'error');
            } else if (error.message.includes('NetworkError') || error.message.includes('Failed to fetch')) {
                errorMessage = 'Network error. Please check your connection and try again.';
                console.error('🌐 Network error occurred');
                this.debugLog('🌐 Network error occurred', 'error');
            }
            
            if (typeof showAlertDialog === 'function') {
                showAlertDialog(
                    `❌ ${window.i18n.t('sync_failed')}: ${errorMessage}`,
                    { type: 'error' }
                );
            }
        }
    }

    /**
     * Show detailed sync results modal
     */
    showSyncResultsModal(bankCode, syncData) {
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm z-50 flex items-center justify-center';
        
        const details = syncData[0] || {}; // Get first bank result
        
        modal.innerHTML = `
            <div class="bg-white rounded-xl p-6 w-full max-w-lg mx-4 shadow-2xl">
                <div class="flex items-center justify-between mb-4">
                    <h3 class="text-lg font-medium">📊 ${window.i18n.t('sync_results')} - ${bankCode.toUpperCase()}</h3>
                    <button onclick="this.remove()" class="text-gray-400 hover:text-gray-600">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
                
                <div class="space-y-4">
                    <div class="bg-gray-50 rounded-lg p-4">
                        <div class="grid grid-cols-2 gap-4 text-sm">
                            <div>
                                <span class="font-medium text-gray-600">${window.i18n.t('emails_found')}:</span>
                                <span class="text-lg font-bold text-blue-600">${details.new_emails_count || 0}</span>
                            </div>
                            <div>
                                <span class="font-medium text-gray-600">${window.i18n.t('transactions_parsed')}:</span>
                                <span class="text-lg font-bold text-green-600">${details.parsed_transactions_count || 0}</span>
                            </div>
                            <div>
                                <span class="font-medium text-gray-600">${window.i18n.t('transactions_created')}:</span>
                                <span class="text-lg font-bold text-purple-600">${details.created_transactions_count || 0}</span>
                            </div>
                            <div>
                                <span class="font-medium text-gray-600">${window.i18n.t('last_sync')}:</span>
                                <span class="text-sm text-gray-700">${details.last_sync_at ? new Date(details.last_sync_at).toLocaleString() : window.i18n.t('never')}</span>
                            </div>
                        </div>
                    </div>
                    
                    ${details.created_transactions_count > 0 ? `
                        <div class="text-center">
                            <p class="text-sm text-gray-600 mb-2">${window.i18n.t('view_new_transactions')}</p>
                            <button onclick="window.location.href='/'; this.closest('.fixed').remove();" 
                                    class="bg-purple-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-purple-700 transition-colors">
                                📊 ${window.i18n.t('go_to_dashboard')}
                            </button>
                        </div>
                    ` : ''}
                    
                    <div class="text-center">
                        <button onclick="this.closest('.fixed').remove()" 
                                class="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg text-sm hover:bg-gray-300 transition-colors">
                            ${window.i18n.t('close')}
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        modal.style.display = 'flex';
        
        // Auto close after 10 seconds
        setTimeout(() => {
            if (modal.parentNode) {
                modal.remove();
            }
        }, 10000);
    }

    /**
     * Update bank sync status in UI
     */
    updateBankSyncStatus(bankCode, syncResults) {
        const lastSyncSpan = document.getElementById(`${bankCode}-last-sync`);
        if (lastSyncSpan && syncResults.length > 0) {
            const bankResult = syncResults[0];
            if (bankResult.last_sync_at) {
                lastSyncSpan.textContent = new Date(bankResult.last_sync_at).toLocaleString();
            }
        }
    }

    /**
     * Show sync history for a bank
     */
    async showSyncHistory(bankCode) {
        try {
            const response = await fetch(`/api/bank-integration/sync-history/?bank_code=${bankCode}`, {
                method: 'GET',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                }
            });
            
            if (!response.ok) {
                throw new Error('Failed to fetch sync history');
            }
            
            const historyData = await response.json();
            this.showSyncHistoryModal(bankCode, historyData);
            
        } catch (error) {
            console.error('Sync history error:', error);
            if (typeof showAlertDialog === 'function') {
                showAlertDialog(
                    `❌ ${window.i18n.t('failed_to_load_sync_history')}: ${error.message}`,
                    { type: 'error' }
                );
            }
        }
    }

    /**
     * Show sync history modal
     */
    showSyncHistoryModal(bankCode, historyData) {
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm z-50 flex items-center justify-center';
        
        const transactions = historyData.transactions || [];
        
        modal.innerHTML = `
            <div class="bg-white rounded-xl p-6 w-full max-w-4xl mx-4 shadow-2xl max-h-[90vh] overflow-hidden flex flex-col">
                <div class="flex items-center justify-between mb-4">
                    <h3 class="text-lg font-medium">📜 ${window.i18n.t('sync_history')} - ${bankCode.toUpperCase()}</h3>
                    <button onclick="this.closest('.fixed').remove()" class="text-gray-400 hover:text-gray-600">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
                
                <div class="flex-1 overflow-y-auto">
                    ${transactions.length > 0 ? `
                        <div class="space-y-3">
                            ${transactions.map(transaction => `
                                <div class="border rounded-lg p-4 ${transaction.is_processed ? 'bg-green-50 border-green-200' : 'bg-yellow-50 border-yellow-200'}">
                                    <div class="flex items-start justify-between">
                                        <div class="flex-1">
                                            <div class="flex items-center space-x-2 mb-2">
                                                <span class="text-sm font-medium text-gray-600">📧 ${transaction.email_subject || 'No subject'}</span>
                                                <span class="text-xs text-gray-500">${new Date(transaction.email_date).toLocaleString()}</span>
                                            </div>
                                            
                                            <div class="grid grid-cols-2 gap-4 text-sm">
                                                <div>
                                                    <span class="font-medium">${window.i18n.t('transaction_type')}:</span>
                                                    <span class="ml-1">${transaction.transaction_type}</span>
                                                </div>
                                                <div>
                                                    <span class="font-medium">${window.i18n.t('amount')}:</span>
                                                    <span class="ml-1 font-bold ${transaction.amount > 0 ? 'text-green-600' : 'text-red-600'}">
                                                        ${transaction.amount?.toLocaleString()}₫
                                                    </span>
                                                </div>
                                                <div>
                                                    <span class="font-medium">${window.i18n.t('description')}:</span>
                                                    <span class="ml-1">${transaction.description || 'N/A'}</span>
                                                </div>
                                                <div>
                                                    <span class="font-medium">${window.i18n.t('confidence')}:</span>
                                                    <span class="ml-1">${(transaction.ai_confidence * 100).toFixed(1)}%</span>
                                                </div>
                                            </div>
                                        </div>
                                        
                                        <div class="text-right">
                                            <div class="text-xs ${transaction.is_processed ? 'text-green-600' : 'text-yellow-600'} font-medium mb-1">
                                                ${transaction.is_processed ? '✅ ' + window.i18n.t('imported') : '⏳ ' + window.i18n.t('pending')}
                                            </div>
                                            ${transaction.transaction_id ? `
                                                <button onclick="window.location.href='/?highlight=${transaction.transaction_id}'" 
                                                        class="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded hover:bg-purple-200">
                                                    ${window.i18n.t('view_transaction')}
                                                </button>
                                            ` : ''}
                                        </div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    ` : `
                        <div class="text-center py-8">
                            <div class="text-6xl mb-4">📪</div>
                            <p class="text-gray-500">${window.i18n.t('no_sync_history_found')}</p>
                        </div>
                    `}
                </div>
                
                <div class="border-t pt-4 mt-4">
                    <div class="flex justify-between items-center">
                        <div class="text-sm text-gray-600">
                            ${window.i18n.t('total_records')}: <span class="font-bold">${transactions.length}</span> |
                            ${window.i18n.t('imported')}: <span class="font-bold text-green-600">${transactions.filter(t => t.is_processed).length}</span> |
                            ${window.i18n.t('pending')}: <span class="font-bold text-yellow-600">${transactions.filter(t => !t.is_processed).length}</span>
                        </div>
                        <button onclick="this.closest('.fixed').remove()" 
                                class="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg text-sm hover:bg-gray-300 transition-colors">
                            ${window.i18n.t('close')}
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        modal.style.display = 'flex';
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

    /**
     * Show add custom bank modal
     */
    showAddCustomBankModal() {
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm z-50 flex items-center justify-center';
        modal.id = 'add-custom-bank-modal';
        
        modal.innerHTML = `
            <div class="bg-white rounded-xl p-6 w-full max-w-md mx-4 shadow-2xl">
                <div class="flex items-center justify-between mb-4">
                    <h3 class="text-lg font-medium">➕ ${window.i18n.t('add_custom_bank')}</h3>
                    <button onclick="this.closest('.fixed').remove()" class="text-gray-400 hover:text-gray-600">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
                
                <form id="custom-bank-form" class="space-y-4">
                    <!-- Bank Name -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">${window.i18n.t('bank_name')}</label>
                        <input type="text" name="bankName" required 
                               class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                               placeholder="${window.i18n.t('bank_name_placeholder')}">
                        <p class="text-xs text-gray-500 mt-1">${window.i18n.t('bank_name_help')}</p>
                    </div>
                    
                    <!-- Sender Email Pattern -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">${window.i18n.t('sender_email_pattern')}</label>
                        <input type="email" name="senderPattern" required 
                               class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                               placeholder="${window.i18n.t('sender_email_placeholder')}">
                        <p class="text-xs text-gray-500 mt-1">${window.i18n.t('sender_email_help')}</p>
                    </div>
                    
                    <!-- Account Suffix (Optional) -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">${window.i18n.t('account_suffix')} (${window.i18n.t('optional')})</label>
                        <input type="text" name="accountSuffix" maxlength="10"
                               class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                               placeholder="${window.i18n.t('account_suffix_placeholder')}">
                        <p class="text-xs text-gray-500 mt-1">${window.i18n.t('account_suffix_help')}</p>
                    </div>
                    
                    <!-- Info Box -->
                    <div class="bg-blue-50 border border-blue-200 rounded-lg p-3">
                        <div class="flex items-start">
                            <div class="text-blue-600 mr-2">💡</div>
                            <div class="text-sm text-blue-800">
                                <p class="font-medium mb-1">${window.i18n.t('custom_bank_info_title')}</p>
                                <ul class="text-xs space-y-1">
                                    <li>• ${window.i18n.t('custom_bank_info_1')}</li>
                                    <li>• ${window.i18n.t('custom_bank_info_2')}</li>
                                    <li>• ${window.i18n.t('custom_bank_info_3')}</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Action Buttons -->
                    <div class="flex space-x-3 pt-4">
                        <button type="submit" class="flex-1 bg-gradient-to-r from-blue-500 to-purple-500 text-white px-4 py-2 rounded-lg font-medium hover:from-blue-600 hover:to-purple-600 transition-all">
                            ➕ ${window.i18n.t('create_bank')}
                        </button>
                        <button type="button" onclick="this.closest('.fixed').remove()" class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors">
                            ${window.i18n.t('cancel')}
                        </button>
                    </div>
                </form>
            </div>
        `;
        
        document.body.appendChild(modal);
        modal.style.display = 'flex';
        
        // Form submission
        const form = modal.querySelector('#custom-bank-form');
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            await this.createCustomBank(formData);
            modal.remove();
        });
    }

    /**
     * Create custom bank
     */
    async createCustomBank(formData) {
        const bankName = formData.get('bankName').trim();
        const senderPattern = formData.get('senderPattern').trim();
        const accountSuffix = formData.get('accountSuffix').trim();
        
        if (!bankName || !senderPattern) {
            if (typeof showAlertDialog === 'function') {
                showAlertDialog(
                    window.i18n.t('bank_name_and_sender_required'),
                    { type: 'error' }
                );
            }
            return;
        }
        
        try {
            const response = await fetch('/api/bank-integration/custom/create/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                },
                body: JSON.stringify({
                    bank_name: bankName,
                    sender_pattern: senderPattern,
                    account_suffix: accountSuffix || null
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Show success message
                if (typeof showAlertDialog === 'function') {
                    showAlertDialog(
                        `✅ ${window.i18n.t('custom_bank_created_success')}: ${bankName}`,
                        { type: 'success' }
                    );
                }
                
                // Refresh bank list
                await this.loadAllBankConfigs();
                
            } else {
                throw new Error(result.error || 'Failed to create custom bank');
            }
            
        } catch (error) {
            console.error('Custom bank creation error:', error);
            if (typeof showAlertDialog === 'function') {
                showAlertDialog(
                    `❌ ${window.i18n.t('custom_bank_creation_failed')}: ${error.message}`,
                    { type: 'error' }
                );
            }
        }
    }

    /**
     * Load all bank configurations (predefined + custom)
     */
    async loadAllBankConfigs() {
        try {
            const response = await fetch('/api/bank-integration/configs/', {
                method: 'GET',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                }
            });
            
            if (!response.ok) {
                throw new Error('Failed to load bank configurations');
            }
            
            const result = await response.json();
            
            if (result.success) {
                // Render custom banks
                this.renderCustomBanks(result.data.configured_banks.filter(bank => bank.is_custom));
                
                // Update predefined bank statuses
                result.data.configured_banks
                    .filter(bank => !bank.is_custom)
                    .forEach(bank => {
                        this.updateBankStatus(bank.bank_code, bank.is_enabled, {
                            last_sync: bank.last_sync
                        });
                    });
            }
            
        } catch (error) {
            console.error('Failed to load bank configurations:', error);
        }
    }

    /**
     * Render custom banks in the UI
     */
    renderCustomBanks(customBanks) {
        const container = document.getElementById('custom-banks-container');
        if (!container) return;
        
        if (customBanks.length === 0) {
            container.innerHTML = '';
            return;
        }
        
        const customBanksHTML = customBanks.map(bank => `
            <div class="bank-card border rounded-lg p-4 bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
                <div class="flex items-center justify-between">
                    <div class="bank-info">
                        <h4 class="font-medium flex items-center">
                            <span class="bg-gradient-to-r from-blue-500 to-purple-500 text-white px-2 py-1 rounded text-xs mr-2">CUSTOM</span>
                            🏛️ ${bank.bank_name}
                        </h4>
                        <p class="text-sm text-gray-600">${bank.sender_pattern}</p>
                        ${bank.account_suffix ? `<p class="text-xs text-gray-500">Account: ***${bank.account_suffix}</p>` : ''}
                    </div>
                    <div class="bank-toggle">
                        <label class="relative inline-flex items-center cursor-pointer">
                            <input type="checkbox" 
                                   id="bank-toggle-${bank.bank_code}" 
                                   class="sr-only peer"
                                   ${bank.is_enabled ? 'checked' : ''}
                                   onchange="bankIntegrationManager.toggleBankIntegration('${bank.bank_code}')">
                            <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                        </label>
                    </div>
                </div>
                
                <!-- Custom Bank Details -->
                <div id="${bank.bank_code}-details" class="bank-details mt-4 ${bank.is_enabled ? '' : 'hidden'}">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                        <div>
                            <span class="font-medium text-gray-600">${window.i18n.t('status')}:</span>
                            <span class="ml-1 ${bank.is_enabled ? 'text-green-600' : 'text-gray-500'}">
                                ${bank.is_enabled ? '✅ ' + window.i18n.t('enabled') : '❌ ' + window.i18n.t('disabled')}
                            </span>
                        </div>
                        <div>
                            <span class="font-medium text-gray-600">${window.i18n.t('last_sync')}:</span>
                            <span id="${bank.bank_code}-last-sync" class="ml-1 text-gray-700">
                                ${bank.last_sync ? new Date(bank.last_sync).toLocaleString() : window.i18n.t('never')}
                            </span>
                        </div>
                    </div>
                    
                    <!-- Action Buttons -->
                    <div class="flex space-x-2 mt-3">
                        <button onclick="bankIntegrationManager.manualSync('${bank.bank_code}')" 
                                class="bg-purple-100 text-purple-700 px-3 py-1 rounded text-sm hover:bg-purple-200 transition-colors">
                            🔄 ${window.i18n.t('sync_now')}
                        </button>
                        <button onclick="bankIntegrationManager.showSyncHistory('${bank.bank_code}')" 
                                class="bg-gray-100 text-gray-700 px-3 py-1 rounded text-sm hover:bg-gray-200 transition-colors">
                            📜 ${window.i18n.t('view_history')}
                        </button>
                        <button onclick="bankIntegrationManager.deleteCustomBank('${bank.bank_code}')" 
                                class="bg-red-100 text-red-700 px-3 py-1 rounded text-sm hover:bg-red-200 transition-colors">
                            🗑️ ${window.i18n.t('delete')}
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
        
        container.innerHTML = customBanksHTML;
    }

    /**
     * Delete custom bank
     */
    async deleteCustomBank(bankCode) {
        if (typeof showConfirmationDialog === 'function') {
            const confirmed = await showConfirmationDialog(
                window.i18n.t('delete_custom_bank_confirm'),
                { type: 'warning' }
            );
            
            if (!confirmed) return;
        } else {
            if (!confirm(window.i18n.t('delete_custom_bank_confirm'))) return;
        }
        
        try {
            const response = await fetch('/api/bank-integration/disable/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                },
                body: JSON.stringify({
                    bank_code: bankCode,
                    delete_custom: true
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                if (typeof showAlertDialog === 'function') {
                    showAlertDialog(
                        `✅ ${window.i18n.t('custom_bank_deleted_success')}`,
                        { type: 'success' }
                    );
                }
                
                // Refresh bank list
                await this.loadAllBankConfigs();
                
            } else {
                throw new Error(result.error || 'Failed to delete custom bank');
            }
            
        } catch (error) {
            console.error('Custom bank deletion error:', error);
            if (typeof showAlertDialog === 'function') {
                showAlertDialog(
                    `❌ ${window.i18n.t('custom_bank_deletion_failed')}: ${error.message}`,
                    { type: 'error' }
                );
            }
        }
    }

    /**
     * Show sync progress indicator
     */
    showSyncProgress(bankCode, operation = 'sync') {
        // Remove any existing progress indicators
        this.hideSyncProgress();
        
        const progressId = 'sync-progress-indicator';
        const messages = {
            'sync': window.i18n.t('syncing_emails'),
            'preview': window.i18n.t('loading_preview'),
            'import': window.i18n.t('importing_transactions')
        };
        
        const progressModal = document.createElement('div');
        progressModal.id = progressId;
        progressModal.className = 'fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm z-[60] flex items-center justify-center';
        
        progressModal.innerHTML = `
            <div class="bg-white rounded-xl p-8 mx-4 shadow-2xl text-center max-w-md">
                <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-purple-600 mx-auto mb-4"></div>
                <h3 class="text-lg font-medium text-gray-800 mb-2">
                    ${messages[operation] || messages.sync} ${bankCode.toUpperCase()}
                </h3>
                <p class="text-sm text-gray-600 mb-4">${window.i18n.t('please_wait')}</p>
                <div class="w-full bg-gray-200 rounded-full h-2">
                    <div class="bg-gradient-to-r from-purple-600 to-pink-600 h-2 rounded-full animate-pulse" style="width: 60%"></div>
                </div>
            </div>
        `;
        
        document.body.appendChild(progressModal);
    }

    /**
     * Hide sync progress indicator
     */
    hideSyncProgress() {
        const progressModal = document.getElementById('sync-progress-indicator');
        if (progressModal) {
            progressModal.remove();
        }
    }

    /**
     * Show transaction preview modal with currency conversion info
     */
    showTransactionPreviewModal(bankCode, previewData) {
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm z-50 flex items-center justify-center';
        
        const transactions = previewData.transactions || [];
        const exchangeRate = previewData.exchange_rate_info?.usd_to_vnd_rate;
        
        modal.innerHTML = `
            <div class="bg-white rounded-xl w-full max-w-4xl mx-4 shadow-2xl max-h-[90vh] overflow-hidden">
                <div class="bg-gradient-to-r from-blue-600 to-cyan-600 text-white p-6">
                    <div class="flex items-center justify-between">
                        <div>
                            <h3 class="text-xl font-bold">👀 ${window.i18n.t('transaction_preview')} - ${bankCode.toUpperCase()}</h3>
                            <p class="text-blue-100">${transactions.length} ${window.i18n.t('transactions_found')}</p>
                        </div>
                        <button onclick="this.closest('.fixed').remove()" class="text-blue-100 hover:text-white">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                            </svg>
                        </button>
                    </div>
                    
                    ${exchangeRate ? `
                        <div class="mt-4 bg-blue-500 bg-opacity-30 rounded-lg p-3">
                            <p class="text-sm">💱 ${window.i18n.t('current_exchange_rate')}: 1 USD = ${exchangeRate.toLocaleString()} VND</p>
                        </div>
                    ` : ''}
                </div>
                
                <div class="p-6 overflow-y-auto max-h-[60vh]">
                    ${transactions.length === 0 ? `
                        <div class="text-center py-8">
                            <p class="text-gray-500">${window.i18n.t('no_new_transactions_found')}</p>
                        </div>
                    ` : `
                        <div class="mb-4 flex items-center justify-between">
                            <label class="flex items-center">
                                <input type="checkbox" id="select-all-transactions" class="mr-2" checked>
                                <span class="text-sm font-medium">${window.i18n.t('select_all')}</span>
                            </label>
                            <span class="text-sm text-gray-600">
                                <span id="selected-count">${transactions.length}</span> / ${transactions.length} ${window.i18n.t('selected')}
                            </span>
                        </div>
                        
                        <div class="space-y-3">
                            ${transactions.map((transaction, index) => `
                                <div class="border rounded-lg p-4 ${transaction.currency_info?.conversion_applied ? 'border-orange-200 bg-orange-50' : 'border-gray-200 bg-gray-50'}">
                                    <div class="flex items-start justify-between">
                                        <label class="flex items-start space-x-3 flex-1 cursor-pointer">
                                            <input type="checkbox" class="transaction-checkbox mt-1" data-index="${index}" checked>
                                            <div class="flex-1">
                                                <div class="flex items-center space-x-2 mb-2">
                                                    <span class="text-sm font-medium text-gray-800">${transaction.email_subject || 'No subject'}</span>
                                                    <span class="text-xs bg-gray-200 text-gray-600 px-2 py-1 rounded">${new Date(transaction.email_date).toLocaleDateString()}</span>
                                                    <span class="text-xs bg-${transaction.transaction_type === 'expense' ? 'red' : transaction.transaction_type === 'saving' ? 'green' : 'blue'}-100 text-${transaction.transaction_type === 'expense' ? 'red' : transaction.transaction_type === 'saving' ? 'green' : 'blue'}-700 px-2 py-1 rounded">
                                                        ${window.i18n.t('transaction_type_' + transaction.transaction_type)}
                                                    </span>
                                                </div>
                                                
                                                <div class="grid grid-cols-2 gap-4 text-sm">
                                                    <div>
                                                        <span class="font-medium text-gray-600">${window.i18n.t('amount')}:</span>
                                                        ${transaction.currency_info?.conversion_applied ? `
                                                            <div class="mt-1">
                                                                <div class="text-orange-600 font-bold">
                                                                    💱 $${transaction.amount} USD → ${transaction.final_amount?.toLocaleString()} VND
                                                                </div>
                                                                <div class="text-xs text-orange-500">
                                                                    Rate: ${transaction.currency_info.exchange_rate?.toLocaleString()} VND/USD
                                                                </div>
                                                            </div>
                                                        ` : `
                                                            <span class="ml-1 font-bold text-${transaction.transaction_type === 'expense' ? 'red' : 'green'}-600">
                                                                ${transaction.final_amount?.toLocaleString()} VND
                                                            </span>
                                                        `}
                                                    </div>
                                                    <div>
                                                        <span class="font-medium text-gray-600">${window.i18n.t('confidence')}:</span>
                                                        <span class="ml-1 text-sm ${transaction.ai_confidence > 0.7 ? 'text-green-600' : transaction.ai_confidence > 0.4 ? 'text-yellow-600' : 'text-red-600'}">
                                                            ${(transaction.ai_confidence * 100).toFixed(1)}%
                                                        </span>
                                                    </div>
                                                </div>
                                                
                                                <div class="mt-2">
                                                    <span class="font-medium text-gray-600">${window.i18n.t('description')}:</span>
                                                    <span class="ml-1">${transaction.description || 'N/A'}</span>
                                                </div>
                                            </div>
                                        </label>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    `}
                </div>
                
                ${transactions.length > 0 ? `
                    <div class="border-t bg-gray-50 p-6">
                        <div class="flex space-x-3">
                            <button id="import-selected-btn" 
                                    class="flex-1 bg-gradient-to-r from-green-600 to-emerald-600 text-white px-6 py-3 rounded-lg font-medium hover:from-green-700 hover:to-emerald-700 transition-all">
                                ✅ ${window.i18n.t('import_selected_transactions')}
                            </button>
                            <button onclick="this.closest('.fixed').remove()" 
                                    class="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors">
                                ${window.i18n.t('cancel')}
                            </button>
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Setup select all functionality
        const selectAllCheckbox = modal.querySelector('#select-all-transactions');
        const transactionCheckboxes = modal.querySelectorAll('.transaction-checkbox');
        const selectedCountSpan = modal.querySelector('#selected-count');
        const importBtn = modal.querySelector('#import-selected-btn');
        
        if (selectAllCheckbox && transactionCheckboxes.length > 0) {
            selectAllCheckbox.addEventListener('change', () => {
                transactionCheckboxes.forEach(checkbox => {
                    checkbox.checked = selectAllCheckbox.checked;
                });
                this.updateSelectedCount(selectedCountSpan, transactionCheckboxes);
            });
            
            transactionCheckboxes.forEach(checkbox => {
                checkbox.addEventListener('change', () => {
                    this.updateSelectedCount(selectedCountSpan, transactionCheckboxes);
                    
                    // Update select all checkbox
                    const checkedCount = Array.from(transactionCheckboxes).filter(cb => cb.checked).length;
                    selectAllCheckbox.checked = checkedCount === transactionCheckboxes.length;
                    selectAllCheckbox.indeterminate = checkedCount > 0 && checkedCount < transactionCheckboxes.length;
                });
            });
        }
        
        // Add import functionality
        if (importBtn) {
            importBtn.addEventListener('click', () => {
                this.importSelectedTransactions(bankCode, transactions, transactionCheckboxes);
            });
        }
    }

    /**
     * Update selected transaction count
     */
    updateSelectedCount(countSpan, checkboxes) {
        if (countSpan) {
            const selectedCount = Array.from(checkboxes).filter(cb => cb.checked).length;
            countSpan.textContent = selectedCount;
        }
    }

    /**
     * Import selected transactions
     */
    async importSelectedTransactions(bankCode, allTransactions, checkboxes) {
        const selectedTransactions = [];
        
        Array.from(checkboxes).forEach((checkbox, index) => {
            if (checkbox.checked && allTransactions[index]) {
                selectedTransactions.push(allTransactions[index]);
            }
        });
        
        if (selectedTransactions.length === 0) {
            if (typeof showAlertDialog === 'function') {
                showAlertDialog(
                    window.i18n.t('no_transactions_selected'),
                    { type: 'warning' }
                );
            }
            return;
        }
        
        // Show progress
        this.showSyncProgress(bankCode, 'import');
        
        try {
            const response = await fetch('/api/bank-integration/import-selected/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                },
                body: JSON.stringify({
                    selected_transactions: selectedTransactions
                })
            });
            
            const result = await response.json();
            
            // Hide progress
            this.hideSyncProgress();
            
            if (result.success) {
                // Close preview modal
                document.querySelector('.fixed')?.remove();
                
                // Show success message
                if (typeof showAlertDialog === 'function') {
                    showAlertDialog(
                        `✅ ${window.i18n.t('import_completed')}: ${result.imported_count} ${window.i18n.t('transactions_imported')}`,
                        { type: 'success' }
                    );
                }
                
                // Refresh page to show new transactions
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            } else {
                throw new Error(result.error || 'Import failed');
            }
            
        } catch (error) {
            console.error('💥 Import error:', error);
            this.hideSyncProgress();
            
            if (typeof showAlertDialog === 'function') {
                showAlertDialog(
                    `❌ ${window.i18n.t('import_failed')}: ${error.message}`,
                    { type: 'error' }
                );
            }
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