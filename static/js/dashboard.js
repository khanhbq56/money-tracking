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
            console.log('📊 Loading dashboard data from API...');
            
            // Load monthly totals and today summary in parallel
            const [monthlyData, todayData] = await Promise.all([
                this.fetchMonthlyTotals(),
                this.fetchTodaySummary()
            ]);
            
            if (monthlyData) {
                this.updateDashboardCards(monthlyData);
            }
            
            if (todayData) {
                this.updateTodaySummary(todayData.transactions);
            }
            
            console.log('✅ Dashboard data loaded successfully');
            
        } catch (error) {
            console.error('❌ Error loading dashboard data:', error);
            this.showErrorState();
        }
    }

    /**
     * Fetch monthly totals from API
     */
    async fetchMonthlyTotals() {
        try {
            const response = await fetch('/api/monthly-totals/');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('📈 Monthly totals fetched:', data);
            
            // Transform API response to expected format
            if (data.monthly_totals) {
                return {
                    expense: Math.abs(data.monthly_totals.expense || 0),
                    saving: Math.abs(data.monthly_totals.saving || 0),
                    investment: Math.abs(data.monthly_totals.investment || 0),
                    monthly_net: data.monthly_totals.net_total || 0
                };
            }
            
            return null;
        } catch (error) {
            console.error('❌ Error fetching monthly totals:', error);
            return null;
        }
    }

    /**
     * Fetch today's summary from API
     */
    async fetchTodaySummary() {
        try {
            const response = await fetch('/api/today-summary/');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('📅 Today summary fetched:', data);
            
            return data;
        } catch (error) {
            console.error('❌ Error fetching today summary:', error);
            return null;
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
        
        // Use timeout to ensure DOM has been updated first
        setTimeout(() => {
            // Remove ALL existing gradient and border classes more thoroughly
            card.className = card.className
                .replace(/from-\w+-\d+/g, '')
                .replace(/to-\w+-\d+/g, '')
                .replace(/border-\w+-\d+/g, '')
                .replace(/\s+/g, ' ')
                .trim();
            
            textElement.className = textElement.className
                .replace(/text-\w+-\d+/g, '')
                .replace(/\s+/g, ' ')
                .trim();
            
            // Add appropriate color classes based on net total
            if (netTotal > 0) {
                // Positive - Green colors
                card.classList.add('from-green-50', 'to-emerald-50', 'border-green-200');
                textElement.classList.add('text-green-700');
            } else if (netTotal < 0) {
                // Negative - Red colors  
                card.classList.add('from-red-50', 'to-pink-50', 'border-red-200');
                textElement.classList.add('text-red-700');
            } else {
                // Zero - Purple colors (default)
                card.classList.add('from-purple-50', 'to-indigo-50', 'border-purple-200');
                textElement.classList.add('text-purple-700');
            }
        }, 50);
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
            // Handle API format: transaction_type, amount
            const transactionType = transaction.transaction_type;
            const amount = Math.abs(parseFloat(transaction.amount)); // Ensure positive amount
            // For total calculation: use absolute values (total money moved in a day)
            totalToday += amount;
            
            const colorClass = transactionType === 'expense' ? 'text-red-600' : 'text-green-600';
            const sign = transactionType === 'expense' ? '-' : '+';
            
            // Get icon based on transaction type and category
            const icon = this.getTransactionIcon(transactionType, transaction.expense_category);
            
            return `
                <div class="flex justify-between items-center py-1">
                    <span class="${colorClass} flex items-center text-sm">
                        <span class="mr-2">${icon}</span>
                        <span class="truncate max-w-32">${transaction.description}</span>
                    </span>
                    <span class="${colorClass} font-semibold text-sm">
                        ${sign}${this.formatAmount(amount)}
                    </span>
                </div>
            `;
        }).join('');
        
        // Total is always positive (sum of absolute values)
        const totalClass = 'text-blue-600'; // Blue for total amount moved
        const totalSign = '+'; // Always positive for total money moved
        const totalAbsAmount = totalToday;
        
        return `
            <div class="space-y-1">
                ${transactionHTML}
            </div>
            <hr class="my-3 border-gray-200">
            <div class="flex justify-between items-center font-bold">
                <span class="text-gray-900">${window.i18n?.t('today_total') || 'Tổng hôm nay:'}</span>
                <span class="${totalClass} text-lg">${totalSign}${this.formatAmount(totalAbsAmount)}</span>
            </div>
        `;
    }

    /**
     * Get icon for transaction type and category
     */
    getTransactionIcon(transactionType, category) {
        const iconMap = {
            'expense': {
                'food': '🍽️',
                'transport': '🚗',
                'shopping': '🛒',
                'entertainment': '🎬',
                'health': '🏥',
                'education': '📚',
                'bills': '💡',
                'rent': '🏠',
                'other': '💸'
            },
            'saving': '💰',
            'investment': '📈'
        };
        
        if (transactionType === 'expense' && category) {
            return iconMap.expense[category] || iconMap.expense.other;
        }
        
        return iconMap[transactionType] || '💰';
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
    async handleDataUpdate(newData) {
        // When data updates (new transaction added), refresh from API
        console.log('🔄 Data updated, refreshing dashboard...');
        await this.loadDashboardData();
    }
    
    /**
     * Update language-dependent content
     */
    async updateLanguage(language) {
        // Re-load data with new language
        console.log('🌐 Language changed, refreshing dashboard...');
        await this.loadDashboardData();
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