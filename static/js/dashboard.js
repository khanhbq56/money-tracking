/**
 * Dashboard Module
 * Manages the 4-card dashboard display and real-time updates
 */
class Dashboard {
    constructor() {
        this.elements = {};
        this.animationDuration = 300;
        this.updateInterval = null;
        this.currentTotals = {};
        this.init();
    }
    
    /**
     * Initialize dashboard
     */
    async init() {
        try {
            console.log('📊 Initializing Dashboard...');
            
            // Wait for app to be ready
            await this.waitForApp();
            
            // Get DOM elements
            this.getDOMElements();
            
            // Load initial data
            await this.loadDashboardData();
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Setup auto-refresh
            this.setupAutoRefresh();
            
            console.log('✅ Dashboard initialized successfully');
            
        } catch (error) {
            console.error('❌ Error initializing dashboard:', error);
        }
    }
    
    /**
     * Wait for main app to be available
     */
    async waitForApp() {
        return new Promise((resolve) => {
            const checkApp = () => {
                if (window.app && window.app.initialized) {
                    resolve();
                } else {
                    setTimeout(checkApp, 100);
                }
            };
            checkApp();
        });
    }
    
    /**
     * Get DOM elements
     */
    getDOMElements() {
        this.elements = {
            expenseTotal: document.getElementById('expense-total'),
            savingTotal: document.getElementById('saving-total'), 
            investmentTotal: document.getElementById('investment-total'),
            monthlyNetTotal: document.getElementById('monthly-net-total'),
            todaySummary: document.getElementById('today-summary')
        };
        
        // Check if all elements exist
        Object.keys(this.elements).forEach(key => {
            if (!this.elements[key]) {
                console.warn(`Dashboard element not found: ${key}`);
            }
        });
    }
    
    /**
     * Load dashboard data
     */
    async loadDashboardData() {
        try {
            // For Phase 3, get data from app mock data
            // In later phases, this will fetch from API
            const data = window.app.getCurrentData();
            
            if (data && data.totals) {
                this.updateDashboardCards(data.totals);
            }
            
            if (data && data.todayTransactions) {
                this.updateTodaySummary(data.todayTransactions);
            }
            
            console.log('📄 Dashboard data loaded');
            
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            this.showErrorState();
        }
    }
    
    /**
     * Update dashboard cards with new totals
     */
    updateDashboardCards(totals) {
        const updates = {
            expense: {
                element: this.elements.expenseTotal,
                amount: totals.expense || 0,
                isNegative: true
            },
            saving: {
                element: this.elements.savingTotal,
                amount: totals.saving || 0,
                isNegative: false
            },
            investment: {
                element: this.elements.investmentTotal,
                amount: totals.investment || 0,
                isNegative: false
            },
            monthlyNet: {
                element: this.elements.monthlyNetTotal,
                amount: totals.monthly_net || 0,
                isNegative: totals.monthly_net < 0
            }
        };
        
        // Animate updates
        Object.keys(updates).forEach(key => {
            const update = updates[key];
            if (update.element) {
                this.animateValueChange(update.element, update.amount, update.isNegative);
            }
        });
        
        // Update monthly total card color
        this.updateMonthlyTotalCardColor(totals.monthly_net || 0);
        
        // Store current totals
        this.currentTotals = totals;
    }
    
    /**
     * Animate value changes
     */
    animateValueChange(element, newAmount, isNegative = false) {
        const currentText = element.textContent;
        const currentAmount = this.parseAmountFromText(currentText);
        
        // Skip animation if same value
        if (currentAmount === newAmount) return;
        
        // Add loading class
        element.classList.add('loading');
        
        // Animate the number change
        this.animateNumber(element, currentAmount, newAmount, isNegative);
        
        // Remove loading class after animation
        setTimeout(() => {
            element.classList.remove('loading');
        }, this.animationDuration);
    }
    
    /**
     * Animate number from old to new value
     */
    animateNumber(element, from, to, isNegative) {
        const startTime = performance.now();
        const duration = this.animationDuration;
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function
            const easeProgress = this.easeOutCubic(progress);
            
            const currentValue = from + (to - from) * easeProgress;
            const sign = isNegative ? '-' : '+';
            const formattedValue = this.formatAmount(Math.abs(currentValue));
            
            element.textContent = `${sign}${formattedValue}`;
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }
    
    /**
     * Easing function
     */
    easeOutCubic(t) {
        return 1 - Math.pow(1 - t, 3);
    }
    
    /**
     * Parse amount from text
     */
    parseAmountFromText(text) {
        const match = text.replace(/[^\d]/g, '');
        return parseInt(match) || 0;
    }
    
    /**
     * Format amount for display
     */
    formatAmount(amount) {
        if (window.i18n) {
            return window.i18n.formatNumber(amount) + '₫';
        }
        return new Intl.NumberFormat('vi-VN').format(amount) + '₫';
    }
    
    /**
     * Update monthly total card color based on positive/negative
     */
    updateMonthlyTotalCardColor(netTotal) {
        const card = this.elements.monthlyNetTotal?.closest('.bg-gradient-to-br');
        const textElement = this.elements.monthlyNetTotal;
        
        if (!card || !textElement) return;
        
        // Remove existing color classes
        card.classList.remove(
            'from-purple-50', 'to-indigo-50', 'border-purple-200',
            'from-green-50', 'to-emerald-50', 'border-green-200',
            'from-red-50', 'to-pink-50', 'border-red-200'
        );
        textElement.classList.remove('text-purple-700', 'text-green-700', 'text-red-700');
        
        // Add appropriate color classes
        if (netTotal > 0) {
            card.classList.add('from-green-50', 'to-emerald-50', 'border-green-200');
            textElement.classList.add('text-green-700');
        } else if (netTotal < 0) {
            card.classList.add('from-red-50', 'to-pink-50', 'border-red-200');
            textElement.classList.add('text-red-700');
        } else {
            card.classList.add('from-purple-50', 'to-indigo-50', 'border-purple-200');
            textElement.classList.add('text-purple-700');
        }
    }
    
    /**
     * Update today's summary section
     */
    updateTodaySummary(transactions) {
        if (!this.elements.todaySummary) return;
        
        const summaryHTML = this.generateTodaySummaryHTML(transactions);
        this.elements.todaySummary.innerHTML = summaryHTML;
    }
    
    /**
     * Generate HTML for today's summary
     */
    generateTodaySummaryHTML(transactions) {
        if (!transactions || transactions.length === 0) {
            return `
                <div class="text-center text-gray-500 py-4">
                    <div class="text-4xl mb-2">📋</div>
                    <p class="text-sm">${window.i18n?.t('no_transactions_today') || 'Chưa có giao dịch hôm nay'}</p>
                </div>
            `;
        }
        
        let totalToday = 0;
        const transactionHTML = transactions.map(transaction => {
            const amount = transaction.type === 'expense' ? -transaction.amount : transaction.amount;
            totalToday += amount;
            
            const colorClass = transaction.type === 'expense' ? 'text-red-600' : 'text-green-600';
            const sign = transaction.type === 'expense' ? '-' : '+';
            
            return `
                <div class="flex justify-between items-center">
                    <span class="${colorClass} flex items-center">
                        ${transaction.icon} ${transaction.description}
                    </span>
                    <span class="${colorClass} font-semibold">
                        ${sign}${this.formatAmount(transaction.amount).replace('₫', '')}₫
                    </span>
                </div>
            `;
        }).join('');
        
        const totalClass = totalToday >= 0 ? 'text-green-600' : 'text-red-600';
        const totalSign = totalToday >= 0 ? '+' : '';
        
        return `
            ${transactionHTML}
            <hr class="my-3 border-gray-200">
            <div class="flex justify-between items-center font-bold">
                <span class="text-gray-900">${window.i18n?.t('today_total') || 'Tổng hôm nay:'}</span>
                <span class="${totalClass} text-lg">${totalSign}${this.formatAmount(Math.abs(totalToday))}</span>
            </div>
        `;
    }
    
    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Listen for data updates
        document.addEventListener('dataUpdated', (e) => {
            this.handleDataUpdate(e.detail);
        });
        
        // Listen for language changes
        document.addEventListener('languageChanged', (e) => {
            this.updateLanguage(e.detail.language);
        });
        
        // Listen for window resize
        window.addEventListener('resize', this.debounce(() => {
            this.handleResize();
        }, 250));
    }
    
    /**
     * Handle data updates
     */
    handleDataUpdate(newData) {
        if (newData.totals) {
            this.updateDashboardCards(newData.totals);
        }
        
        if (newData.todayTransactions) {
            this.updateTodaySummary(newData.todayTransactions);
        }
    }
    
    /**
     * Update language-dependent content
     */
    updateLanguage(language) {
        // Re-render today's summary with new language
        const data = window.app.getCurrentData();
        if (data && data.todayTransactions) {
            this.updateTodaySummary(data.todayTransactions);
        }
    }
    
    /**
     * Handle window resize
     */
    handleResize() {
        // Re-calculate responsive layouts if needed
        const isMobile = window.innerWidth < 768;
        
        // Adjust card layouts for mobile
        document.querySelectorAll('.dashboard-card').forEach(card => {
            if (isMobile) {
                card.classList.add('mobile-layout');
            } else {
                card.classList.remove('mobile-layout');
            }
        });
    }
    
    /**
     * Setup auto-refresh for dashboard
     */
    setupAutoRefresh() {
        // Refresh dashboard every 30 seconds
        this.updateInterval = setInterval(() => {
            this.loadDashboardData();
        }, 30000);
        
        console.log('🔄 Auto-refresh setup for dashboard (30s interval)');
    }
    
    /**
     * Manually refresh dashboard
     */
    async refreshDashboard() {
        console.log('🔄 Manually refreshing dashboard...');
        await this.loadDashboardData();
    }
    
    /**
     * Show error state
     */
    showErrorState() {
        Object.values(this.elements).forEach(element => {
            if (element) {
                element.textContent = '---';
                element.classList.add('text-gray-400');
            }
        });
        
        if (this.elements.todaySummary) {
            this.elements.todaySummary.innerHTML = `
                <div class="text-center text-red-500 py-4">
                    <div class="text-4xl mb-2">⚠️</div>
                    <p class="text-sm">Lỗi tải dữ liệu</p>
                </div>
            `;
        }
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
     * Cleanup
     */
    destroy() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Wait a bit for other modules to initialize
    setTimeout(() => {
        window.dashboard = new Dashboard();
    }, 500);
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Dashboard;
} 