/**
 * Custom Calendar Implementation for Expense Tracker - Phase 4
 * Features: Custom 7x6 grid, month navigation, transaction events, filters, API integration
 */
class ExpenseCalendar {
    constructor() {
        this.currentMonth = new Date().getMonth();
        this.currentYear = new Date().getFullYear();
        this.currentFilter = 'all';
        this.transactions = {};
        this.isLoading = false;
        
        // Month names in Vietnamese and English
        this.monthNames = {
            vi: [
                'Tháng 1', 'Tháng 2', 'Tháng 3', 'Tháng 4', 'Tháng 5', 'Tháng 6',
                'Tháng 7', 'Tháng 8', 'Tháng 9', 'Tháng 10', 'Tháng 11', 'Tháng 12'
            ],
            en: [
                'January', 'February', 'March', 'April', 'May', 'June',
                'July', 'August', 'September', 'October', 'November', 'December'
            ]
        };
        
        // Day headers using i18n keys
        this.dayHeaderKeys = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
        
        // Vietnamese day names as default
        this.dayNamesVi = ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'CN'];
        this.dayNamesEn = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
        
        // Transaction type configurations
        this.transactionConfig = {
            expense: {
                color: 'red',
                gradient: 'from-red-50 to-pink-50',
                border: 'border-red-200',
                text: 'text-red-600',
                bgClass: 'bg-red-100',
                icon: '🔴'
            },
            saving: {
                color: 'green',
                gradient: 'from-green-50 to-emerald-50',
                border: 'border-green-200',
                text: 'text-green-600',
                bgClass: 'bg-green-100',
                icon: '🟢'
            },
            investment: {
                color: 'blue',
                gradient: 'from-blue-50 to-indigo-50',
                border: 'border-blue-200',
                text: 'text-blue-600',
                bgClass: 'bg-blue-100',
                icon: '🔵'
            }
        };
        
        this.init();
    }
    
    /**
     * Initialize calendar
     */
    async init() {
        try {
            console.log('📅 Initializing Calendar...');
            
            // Wait for i18n to be ready
            await this.waitForI18n();
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Load initial data and render
            await this.loadTransactions();
            this.render();
            
            console.log('✅ Calendar initialized successfully');
            
        } catch (error) {
            console.error('❌ Error initializing calendar:', error);
            this.showError('Failed to initialize calendar');
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
     * Setup event listeners
     */
    setupEventListeners() {
        // Language change events
        document.addEventListener('languageChanged', (e) => {
            this.updateCalendarHeader();
            this.updateDayHeaders();
        });
        
        // Window resize events
        window.addEventListener('resize', this.debounce(() => {
            this.handleResize();
        }, 250));
    }
    
    /**
     * Load transactions for current month
     */
    async loadTransactions() {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.showLoadingState();
        
        try {
            const response = await fetch(
                `/api/ai_chat/calendar/${this.currentYear}/${this.currentMonth + 1}/`
            );
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.transactions = this.processNewTransactionData(data.daily_data || {});
            
            console.log('📊 Loaded calendar data:', this.transactions);
            
        } catch (error) {
            console.error('Error loading transactions:', error);
            this.showError('Failed to load calendar data');
            // Use fallback data
            this.transactions = this.getFallbackData();
        } finally {
            this.isLoading = false;
            this.hideLoadingState();
        }
    }
    
    /**
     * Process transaction data from API
     */
    processTransactionData(calendarData) {
        const processed = {};
        
        calendarData.forEach(dayData => {
            const dateKey = dayData.date;
            processed[dateKey] = {
                transactions: dayData.transactions || [],
                total: dayData.daily_total || 0,
                counts: {
                    expense: dayData.expense_count || 0,
                    saving: dayData.saving_count || 0,
                    investment: dayData.investment_count || 0
                }
            };
        });
        
        return processed;
    }

    /**
     * Process new transaction data format from Phase 7 API
     */
    processNewTransactionData(dailyData) {
        const processed = {};
        
        Object.keys(dailyData).forEach(dateKey => {
            const dayData = dailyData[dateKey];
            processed[dateKey] = {
                transactions: dayData.transactions || [],
                total: dayData.totals.net || 0,
                counts: {
                    expense: dayData.transactions.filter(t => t.type === 'expense').length,
                    saving: dayData.transactions.filter(t => t.type === 'saving').length,
                    investment: dayData.transactions.filter(t => t.type === 'investment').length
                }
            };
        });
        
        return processed;
    }
    
    /**
     * Get fallback data when API fails
     */
    getFallbackData() {
        const today = new Date();
        const todayKey = this.formatDateForDatabase(today);
        
        return {
            [todayKey]: {
                transactions: [
                    {
                        id: 1,
                        transaction_type: 'expense',
                        expense_category: 'coffee',
                        amount: -25000,
                        description: 'Coffee',
                        icon: '☕'
                    }
                ],
                total: -25000,
                counts: { expense: 1, saving: 0, investment: 0 }
            }
        };
    }
    
    /**
     * Render complete calendar
     */
    render() {
        this.updateCalendarHeader();
        this.updateDayHeaders();
        this.renderCalendarGrid();
    }
    
    /**
     * Update calendar header with current month/year
     */
    updateCalendarHeader() {
        const language = window.i18n?.currentLang || 'vi';
        const monthName = this.monthNames[language][this.currentMonth];
        const headerElement = document.querySelector('.calendar-header h2');
        
        if (headerElement) {
            headerElement.textContent = `📅 ${monthName}, ${this.currentYear}`;
        }
    }
    
    /**
     * Update day headers based on current language using i18n
     */
    updateDayHeaders() {
        const headerElements = document.querySelectorAll('.calendar-day-header');
        
        // Use i18n keys for proper translation
        const dayKeys = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
        
        headerElements.forEach((element, index) => {
            if (index < dayKeys.length && window.i18n) {
                // Try to get translation from i18n
                const translatedText = window.i18n.t(dayKeys[index]);
                if (translatedText && translatedText !== dayKeys[index]) {
                    element.textContent = translatedText;
                } else {
                    // Fallback to hardcoded names if i18n not available
                    const currentLang = window.i18n?.currentLang || 'vi';
                    const dayNames = currentLang === 'vi' ? this.dayNamesVi : this.dayNamesEn;
                    if (index < dayNames.length) {
                        element.textContent = dayNames[index];
                    }
                }
            }
        });
        
        console.log('📅 Calendar day headers updated for language:', window.i18n?.currentLang || 'vi');
    }
    
    /**
     * Render the calendar grid (7x6 = 42 days)
     */
    renderCalendarGrid() {
        const calendarGrid = document.getElementById('calendar-grid');
        if (!calendarGrid) {
            console.error('Calendar grid element not found');
            return;
        }
        
        // Clear existing content except day headers
        const dayHeaders = calendarGrid.querySelectorAll('.calendar-day-header');
        calendarGrid.innerHTML = '';
        
        // Re-add day headers
        dayHeaders.forEach(header => calendarGrid.appendChild(header));
        
        // Generate calendar days
        const calendarDays = this.generateCalendarDays();
        calendarDays.forEach(dayElement => {
            calendarGrid.appendChild(dayElement);
        });
    }
    
    /**
     * Generate all calendar day elements (42 days for 6 weeks)
     */
    generateCalendarDays() {
        const days = [];
        const firstDay = new Date(this.currentYear, this.currentMonth, 1);
        const lastDay = new Date(this.currentYear, this.currentMonth + 1, 0);
        const today = new Date();
        
        // Calculate start date (Monday of the first week)
        const startDate = new Date(firstDay);
        const dayOfWeek = firstDay.getDay();
        const daysToSubtract = dayOfWeek === 0 ? 6 : dayOfWeek - 1; // Monday = 0
        startDate.setDate(firstDay.getDate() - daysToSubtract);
        
        // Generate 42 days (6 weeks × 7 days)
        for (let i = 0; i < 42; i++) {
            const date = new Date(startDate);
            date.setDate(startDate.getDate() + i);
            
            const dayElement = this.createDayElement(date, today);
            days.push(dayElement);
        }
        
        return days;
    }
    
    /**
     * Create individual day element
     */
    createDayElement(date, today) {
        const dayDiv = document.createElement('div');
        dayDiv.className = 'calendar-day';
        
        // Add special classes
        if (date.getMonth() !== this.currentMonth) {
            dayDiv.classList.add('other-month');
        }
        if (date.toDateString() === today.toDateString()) {
            dayDiv.classList.add('today');
        }
        
        // Add weekend classes for Saturday (6) and Sunday (0)
        const dayOfWeek = date.getDay();
        if (dayOfWeek === 6) {
            dayDiv.classList.add('saturday');
        } else if (dayOfWeek === 0) {
            dayDiv.classList.add('sunday');
        }
        
        // Get day data - use local date format to match database
        const dateKey = this.formatDateForDatabase(date);
        const dayData = this.transactions[dateKey] || { transactions: [], total: 0, counts: {} };
        
        // Create day number
        const dayNumber = document.createElement('div');
        dayNumber.className = 'day-number';
        dayNumber.textContent = date.getDate();
        
        // Create events container
        const eventsContainer = document.createElement('div');
        eventsContainer.className = 'day-events';
        
        // Add transaction events
        const filteredTransactions = this.filterTransactions(dayData.transactions);
        filteredTransactions.slice(0, 3).forEach(transaction => { // Show max 3 events
            const eventElement = this.createEventElement(transaction, date);
            eventsContainer.appendChild(eventElement);
        });
        
        // Add "more" indicator if there are more than 3 transactions
        if (filteredTransactions.length > 3) {
            const moreElement = document.createElement('div');
            moreElement.className = 'day-event more';
            moreElement.textContent = `+${filteredTransactions.length - 3} more`;
            moreElement.onclick = (e) => {
                e.stopPropagation();
                this.showDayDetails(date, dayData);
            };
            eventsContainer.appendChild(moreElement);
        }
        
        // Create day total badge (only for filtered transactions)
        if (filteredTransactions.length > 0) {
            // Calculate total as sum of absolute values (total money moved in a day)
            // Similar to "today total" and "net total" logic
            const filteredTotal = filteredTransactions.reduce((sum, t) => {
                const amount = Math.abs(t.amount); // Always use absolute value
                return sum + amount;
            }, 0);
            
            if (filteredTotal > 0) {
                const totalBadge = this.createTotalBadge(filteredTotal);
                dayDiv.appendChild(totalBadge);
            }
        }
        
        // Assemble day element
        dayDiv.appendChild(dayNumber);
        dayDiv.appendChild(eventsContainer);
        
        // Add click handler
        dayDiv.onclick = () => this.onDayClick(date, dayData);
        
        return dayDiv;
    }
    
    /**
     * Filter transactions based on current filter
     */
    filterTransactions(transactions) {
        if (this.currentFilter === 'all') {
            return transactions;
        }
        
        const filtered = transactions.filter(t => t.transaction_type === this.currentFilter);
        
        // Debug logging
        if (transactions.length > 0) {
            console.log(`🔍 Filter: ${this.currentFilter}, Original: ${transactions.length}, Filtered: ${filtered.length}`);
            console.log('Sample transaction types:', transactions.map(t => t.transaction_type));
        }
        
        return filtered;
    }
    
    /**
     * Create transaction event element
     */
    createEventElement(transaction, date) {
        const eventDiv = document.createElement('div');
        eventDiv.className = `day-event ${transaction.transaction_type}`;
        
        // Get transaction icon
        const icon = this.getTransactionIcon(transaction);
        const amount = Math.abs(transaction.amount);
        const amountText = amount >= 1000000 ? `${(amount/1000000).toFixed(1)}M` : `${(amount/1000).toFixed(0)}k`;
        
        eventDiv.textContent = `${icon} ${amountText}`;
        eventDiv.title = `${transaction.description} - ${this.formatMoney(transaction.amount)}`;
        
        // Add click handler
        eventDiv.onclick = (e) => {
            e.stopPropagation();
            this.showEventDetails(transaction, date);
        };
        
        return eventDiv;
    }
    
    /**
     * Get transaction icon based on type and category
     */
    getTransactionIcon(transaction) {
        if (transaction.icon) {
            return transaction.icon;
        }
        
        // Default icons based on type
        const typeIcons = {
            expense: '💸',
            saving: '💰',
            investment: '📈'
        };
        
        // Category-specific icons for expenses
        if (transaction.transaction_type === 'expense' && transaction.expense_category) {
            const categoryIcons = {
                food: '🍜',
                coffee: '☕',
                transport: '🚗',
                shopping: '🛒',
                entertainment: '🎬',
                health: '🏥',
                education: '📚',
                utilities: '⚡',
                other: '📦'
            };
            return categoryIcons[transaction.expense_category] || typeIcons.expense;
        }
        
        return typeIcons[transaction.transaction_type] || '💰';
    }
    
    /**
     * Create daily total badge
     */
    createTotalBadge(total) {
        const badge = document.createElement('div');
        // Always use positive styling since we're showing absolute values (total money moved)
        badge.className = `day-total positive`;
        
        const amount = Math.abs(total);
        const amountText = amount >= 1000000 ? `${(amount/1000000).toFixed(1)}M` : `${(amount/1000).toFixed(0)}k`;
        // Always show with + sign since it represents total money movement
        badge.textContent = `+${amountText}`;
        badge.title = this.formatMoney(amount);
        
        return badge;
    }
    
    /**
     * Navigate to previous month
     */
    previousMonth() {
        this.currentMonth--;
        if (this.currentMonth < 0) {
            this.currentMonth = 11;
            this.currentYear--;
        }
        this.refreshCalendar();
    }
    
    /**
     * Navigate to next month
     */
    nextMonth() {
        this.currentMonth++;
        if (this.currentMonth > 11) {
            this.currentMonth = 0;
            this.currentYear++;
        }
        this.refreshCalendar();
    }
    
    /**
     * Set transaction filter
     */
    setFilter(filterType) {
        this.currentFilter = filterType;
        
        // Update filter button states
        this.updateFilterButtons();
        
        // Refresh calendar with new filter
        this.refreshCalendar();
    }
    
    /**
     * Update filter button states
     */
    updateFilterButtons() {
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        const activeButton = document.getElementById(`filter-${this.currentFilter}`);
        if (activeButton) {
            activeButton.classList.add('active');
        }
    }
    
    /**
     * Refresh calendar data and display
     */
    async refreshCalendar() {
        await this.loadTransactions();
        this.render();
    }
    
    /**
     * Handle day click
     */
    async onDayClick(date, dayData) {
        console.log('Day clicked:', date, dayData);
        const dateStr = this.formatDateForDatabase(date);
        
        try {
            // Load detailed day data from API
            const response = await fetch(`/api/ai_chat/daily-summary/${dateStr}/`);
            if (response.ok) {
                const detailedData = await response.json();
                this.showDayDetails(date, detailedData);
            } else {
                // Fallback to existing data or add transaction dialog
                if (dayData && dayData.transactions.length > 0) {
                    this.showDayDetails(date, dayData);
                } else {
                    this.showAddTransactionDialog(date);
                }
            }
        } catch (error) {
            console.error('Error loading day details:', error);
            // Fallback to existing behavior
            if (dayData && dayData.transactions.length > 0) {
                this.showDayDetails(date, dayData);
            } else {
                this.showAddTransactionDialog(date);
            }
        }
    }
    
    /**
     * Show day details modal
     */
    showDayDetails(date, dayData) {
        const language = window.i18n?.currentLang || 'vi';
        const dateStr = date.toLocaleDateString(language === 'vi' ? 'vi-VN' : 'en-US');
        
        // For now, show alert - in future phases this could be a proper modal
        const transactionSummary = dayData.transactions.map(t => 
            `${this.getTransactionIcon(t)} ${t.description}: ${this.formatMoney(t.amount)}`
        ).join('\n');
        
        alert(`📅 ${dateStr}\n\n${transactionSummary}\n\n💰 Total: ${this.formatMoney(dayData.total)}`);
    }
    
    /**
     * Show event details
     */
    showEventDetails(transaction, date) {
        const language = window.i18n?.currentLang || 'vi';
        const dateStr = date.toLocaleDateString(language === 'vi' ? 'vi-VN' : 'en-US');
        
        alert(`💳 ${transaction.description}\n📅 ${dateStr}\n💰 ${this.formatMoney(transaction.amount)}`);
    }
    
    /**
     * Show add transaction dialog
     */
    showAddTransactionDialog(date) {
        const language = window.i18n?.currentLang || 'vi';
        const dateStr = date.toLocaleDateString(language === 'vi' ? 'vi-VN' : 'en-US');
        
        const description = prompt(
            language === 'vi' 
                ? `Thêm giao dịch cho ${dateStr}:\n(VD: coffee 25k, tiết kiệm 200k)`
                : `Add transaction for ${dateStr}:\n(e.g., coffee 25k, save 200k)`
        );
        
        if (description) {
            // In future phases, this will integrate with AI chat
            console.log('Add transaction:', description, 'for date:', date);
            
            // For now, just add to chat input if available
            const chatInput = document.getElementById('chat-input');
            if (chatInput) {
                chatInput.value = description;
                if (window.aiChat) {
                    window.aiChat.sendMessage();
                }
            }
        }
    }
    
    /**
     * Show loading state
     */
    showLoadingState() {
        const calendarGrid = document.getElementById('calendar-grid');
        if (calendarGrid) {
            calendarGrid.style.opacity = '0.6';
            calendarGrid.style.pointerEvents = 'none';
        }
    }
    
    /**
     * Hide loading state
     */
    hideLoadingState() {
        const calendarGrid = document.getElementById('calendar-grid');
        if (calendarGrid) {
            calendarGrid.style.opacity = '1';
            calendarGrid.style.pointerEvents = 'auto';
        }
    }
    
    /**
     * Show error message
     */
    showError(message) {
        console.error('Calendar error:', message);
        
        // Show user-friendly error
        if (window.app) {
            window.app.showNotification(message, 'error');
        }
    }
    
    /**
     * Handle window resize
     */
    handleResize() {
        // Update mobile-specific styling
        const isMobile = window.innerWidth < 768;
        const calendarContainer = document.querySelector('.calendar-container');
        
        if (calendarContainer) {
            calendarContainer.classList.toggle('mobile', isMobile);
        }
    }
    
    /**
     * Format date for database matching (avoid timezone issues)
     */
    formatDateForDatabase(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    /**
     * Format money amount
     */
    formatMoney(amount) {
        const abs = Math.abs(amount);
        const sign = amount >= 0 ? '+' : '-';
        return `${amount < 0 ? '' : sign}${abs.toLocaleString('vi-VN')}₫`;
    }
    
    /**
     * Debounce utility function
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
     * Get current calendar state
     */
    getState() {
        return {
            currentMonth: this.currentMonth,
            currentYear: this.currentYear,
            currentFilter: this.currentFilter,
            transactionCount: Object.keys(this.transactions).length,
            isLoading: this.isLoading
        };
    }
}

// Global functions for template event handlers
function previousMonth() {
    if (window.calendar) {
        window.calendar.previousMonth();
    }
}

function nextMonth() {
    if (window.calendar) {
        window.calendar.nextMonth();
    }
}

function setFilter(filterType) {
    if (window.calendar) {
        window.calendar.setFilter(filterType);
    }
}

// Initialize calendar when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Initialize calendar after a short delay to ensure other modules are ready
    setTimeout(() => {
        window.calendar = new ExpenseCalendar();
    }, 100);
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ExpenseCalendar;
} 