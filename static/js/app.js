/**
 * Main Application Module
 * Handles overall app state, utilities, and common functionality
 */
class ExpenseTrackerApp {
    constructor() {
        this.initialized = false;
        this.currentData = {
            transactions: [],
            totals: {},
            todayTransactions: []
        };
        this.init();
    }
    
    /**
     * Initialize the application
     */
    async init() {
        try {
            console.log('🚀 Initializing Expense Tracker App...');
            
            // Wait for i18n to be ready
            await this.waitForI18n();
            
            // Initialize modules
            this.initializeModules();
            
            // Load initial data
            await this.loadInitialData();
            
            // Setup event listeners
            this.setupEventListeners();
            
            this.initialized = true;
            console.log('✅ App initialized successfully');
            
        } catch (error) {
            console.error('❌ Error initializing app:', error);
        }
    }
    
    /**
     * Wait for i18n to be available
     */
    async waitForI18n() {
        return new Promise((resolve) => {
            const checkI18n = () => {
                if (window.i18n) {
                    resolve();
                } else {
                    setTimeout(checkI18n, 100);
                }
            };
            checkI18n();
        });
    }
    
    /**
     * Initialize other modules
     */
    initializeModules() {
        // Dashboard will be initialized in dashboard.js
        console.log('📊 Initializing dashboard...');
        
        // Other modules will be initialized in their respective phases
        console.log('🗓️ Calendar module will be initialized in Phase 4');
        console.log('🤖 AI Chat module will be initialized in Phase 5');
    }
    
    /**
     * Load initial data
     */
    async loadInitialData() {
        try {
            // For Phase 3, we'll use mock data
            // In later phases, this will fetch from APIs
            this.currentData = this.getMockData();
            
            console.log('📄 Loaded initial data:', this.currentData);
            
        } catch (error) {
            console.error('Error loading initial data:', error);
            // Use fallback data
            this.currentData = this.getFallbackData();
        }
    }
    
    /**
     * Get mock data for Phase 3
     */
    getMockData() {
        return {
            totals: {
                expense: 2450000,
                saving: 1200000,
                investment: 3000000,
                monthly_net: 1750000
            },
            todayTransactions: [
                {
                    id: 1,
                    type: 'expense',
                    category: 'food',
                    amount: 50000,
                    description: 'Ăn trưa',
                    icon: '🍜',
                    time: '12:30'
                },
                {
                    id: 2,
                    type: 'expense',
                    category: 'coffee',
                    amount: 25000,
                    description: 'Coffee',
                    icon: '☕',
                    time: '09:15'
                },
                {
                    id: 3,
                    type: 'saving',
                    amount: 200000,
                    description: 'Tiết kiệm',
                    icon: '💰',
                    time: '08:00'
                }
            ],
            transactions: []
        };
    }
    
    /**
     * Get fallback data
     */
    getFallbackData() {
        return {
            totals: {
                expense: 0,
                saving: 0,
                investment: 0,
                monthly_net: 0
            },
            todayTransactions: [],
            transactions: []
        };
    }
    
    /**
     * Setup global event listeners
     */
    setupEventListeners() {
        // Language change events
        document.addEventListener('languageChanged', (e) => {
            console.log('Language changed:', e.detail.language);
            this.handleLanguageChange(e.detail.language);
        });
        
        // Window resize events
        window.addEventListener('resize', this.debounce(() => {
            this.handleWindowResize();
        }, 250));
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardShortcuts(e);
        });
        
        // Error handling
        window.addEventListener('error', (e) => {
            this.handleGlobalError(e);
        });
    }
    
    /**
     * Handle language change
     */
    handleLanguageChange(language) {
        // Update any language-dependent content
        if (window.dashboard) {
            window.dashboard.updateLanguage(language);
        }
    }
    
    /**
     * Handle window resize
     */
    handleWindowResize() {
        // Update responsive layouts
        const isMobile = window.innerWidth < 768;
        document.body.classList.toggle('mobile', isMobile);
        
        // Notify other modules
        if (window.dashboard) {
            window.dashboard.handleResize();
        }
    }
    
    /**
     * Handle keyboard shortcuts
     */
    handleKeyboardShortcuts(e) {
        // Ctrl/Cmd + K for quick search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            document.getElementById('chat-input')?.focus();
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            this.closeAllModals();
        }
    }
    
    /**
     * Handle global errors
     */
    handleGlobalError(error) {
        console.error('Global error:', error);
        
        // Show user-friendly error message
        this.showNotification('Đã xảy ra lỗi. Vui lòng thử lại.', 'error');
    }
    
    /**
     * Close all open modals
     */
    closeAllModals() {
        document.querySelectorAll('.modal, [id$="-modal"]').forEach(modal => {
            if (modal.classList.contains('hidden') === false) {
                modal.classList.add('hidden');
            }
        });
    }
    
    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type} fixed top-4 right-4 z-50 px-6 py-4 rounded-xl text-white font-medium shadow-lg transform transition-all duration-300 translate-x-full`;
        
        // Set background color based on type
        const colors = {
            success: 'bg-green-500',
            error: 'bg-red-500',
            warning: 'bg-yellow-500',
            info: 'bg-blue-500'
        };
        notification.classList.add(colors[type] || colors.info);
        
        notification.textContent = message;
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.classList.remove('translate-x-full');
        }, 100);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            notification.classList.add('translate-x-full');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    }
    
    /**
     * Utility: Debounce function
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    /**
     * Utility: Format money
     */
    formatMoney(amount, showSign = true) {
        if (!window.i18n) {
            return new Intl.NumberFormat('vi-VN').format(Math.abs(amount)) + '₫';
        }
        
        const formatted = window.i18n.formatNumber(Math.abs(amount)) + '₫';
        
        if (showSign && amount !== 0) {
            return (amount > 0 ? '+' : '-') + formatted;
        }
        
        return formatted;
    }
    
    /**
     * Utility: Parse amount from string (e.g., "25k" -> 25000)
     */
    parseAmount(text) {
        const match = text.match(/(\d+(?:\.\d+)?)\s*([km]?)/i);
        if (!match) return 0;
        
        let amount = parseFloat(match[1]);
        const unit = match[2].toLowerCase();
        
        if (unit === 'k') {
            amount *= 1000;
        } else if (unit === 'm') {
            amount *= 1000000;
        }
        
        return Math.round(amount);
    }
    
    /**
     * Get current data
     */
    getCurrentData() {
        return this.currentData;
    }
    
    /**
     * Update data
     */
    updateData(newData) {
        this.currentData = { ...this.currentData, ...newData };
        
        // Notify other modules
        document.dispatchEvent(new CustomEvent('dataUpdated', {
            detail: this.currentData
        }));
    }
    
    /**
     * Get app status
     */
    getStatus() {
        return {
            initialized: this.initialized,
            language: window.i18n?.getCurrentLanguage() || 'vi',
            theme: 'light', // Future feature
            version: '1.0.0'
        };
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.app = new ExpenseTrackerApp();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ExpenseTrackerApp;
}

// Global event system for component communication
class EventBus {
    constructor() {
        this.events = {};
    }

    on(event, callback) {
        if (!this.events[event]) {
            this.events[event] = [];
        }
        this.events[event].push(callback);
    }

    off(event, callback) {
        if (!this.events[event]) return;
        this.events[event] = this.events[event].filter(cb => cb !== callback);
    }

    emit(event, data) {
        if (!this.events[event]) return;
        this.events[event].forEach(callback => {
            try {
                callback(data);
            } catch (error) {
                console.error(`Error in event handler for ${event}:`, error);
            }
        });
    }
}

// Global event bus instance
window.eventBus = new EventBus();

// Transaction update event handlers
window.eventBus.on('transactionAdded', (data) => {
    console.log('Transaction added, refreshing components:', data);
    
    // Refresh dashboard
    if (window.dashboard && typeof window.dashboard.refreshDashboard === 'function') {
        window.dashboard.refreshDashboard();
    }
    
    // Refresh calendar
    if (window.calendar && typeof window.calendar.refreshCalendar === 'function') {
        window.calendar.refreshCalendar();
    }
    
    // Show success notification (unless explicitly skipped)
    if (!data.skipNotification && window.app && typeof window.app.showNotification === 'function') {
        const message = window.i18n ? window.i18n.t('transaction_added_success') : '✅ Transaction added successfully!';
        window.app.showNotification(message, 'success');
    }
});

window.eventBus.on('transactionUpdated', (data) => {
    console.log('Transaction updated, refreshing components:', data);
    
    // Refresh dashboard
    if (window.dashboard && typeof window.dashboard.refreshDashboard === 'function') {
        window.dashboard.refreshDashboard();
    }
    
    // Refresh calendar
    if (window.calendar && typeof window.calendar.refreshCalendar === 'function') {
        window.calendar.refreshCalendar();
    }
});

window.eventBus.on('transactionDeleted', (data) => {
    console.log('Transaction deleted, refreshing components:', data);
    
    // Refresh dashboard
    if (window.dashboard && typeof window.dashboard.refreshDashboard === 'function') {
        window.dashboard.refreshDashboard();
    }
    
    // Refresh calendar
    if (window.calendar && typeof window.calendar.refreshCalendar === 'function') {
        window.calendar.refreshCalendar();
    }
}); 