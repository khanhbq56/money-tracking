/**
 * Internationalization (i18n) Module
 * Handles language switching and translation management
 */
class I18n {
    constructor() {
        this.currentLang = localStorage.getItem('language') || 'vi';
        this.translations = {};
        this.loadTranslations();
        this.initLanguageSwitcher();
    }
    
    /**
     * Load translations for current language
     */
    async loadTranslations() {
        try {
            // For Phase 3, we'll use local translations
            // In Phase 5, this will fetch from /api/translations/${this.currentLang}/
            this.translations = this.getLocalTranslations(this.currentLang);
            this.updatePageTexts();
        } catch (error) {
            console.error('Error loading translations:', error);
            // Fallback to Vietnamese
            this.translations = this.getLocalTranslations('vi');
        }
    }
    
    /**
     * Get local translations (fallback for Phase 3)
     */
    getLocalTranslations(lang) {
        const translations = {
            'vi': {
                'expense': 'Chi Tiêu',
                'saving': 'Tiết Kiệm', 
                'investment': 'Đầu Tư',
                'monthly_total': 'Tổng Tháng',
                'this_month': 'Tháng này',
                'net_amount': 'Số dư ròng',
                'send': 'Gửi',
                'today': 'Hôm Nay',
                'ai_assistant': 'AI Assistant',
                'enter_transaction': 'VD: coffee 25k, tiết kiệm 200k...',
                'welcome_message': 'Xin chào! Hãy nói cho tôi biết giao dịch của bạn. VD: "ăn trưa 50k"',
                'lunch': 'Ăn trưa',
                'quick_actions': 'Thao Tác Nhanh',
                'future_me': 'Future Me Simulator',
                'generate_meme': 'Tạo Meme',
                'statistics': 'Thống Kê',
                'today_total': 'Tổng hôm nay:',
                'all': 'Tất cả',
                'smart_financial_management': 'Quản lý tài chính thông minh',
                'calendar_coming_soon': 'Lịch sẽ được triển khai ở Phase 4',
                'calendar_description': 'Calendar tương tác với hiển thị giao dịch theo ngày',
                'online': 'Online',
                'tieng_viet': 'Tiếng Việt',
                'english': 'English',
                'expense_tracker': 'Theo Dõi Chi Tiêu',
                'financial_calendar': 'Lịch Tài Chính'
            },
            'en': {
                'expense': 'Expense',
                'saving': 'Saving',
                'investment': 'Investment', 
                'monthly_total': 'Monthly Total',
                'this_month': 'This month',
                'net_amount': 'Net amount',
                'send': 'Send',
                'today': 'Today',
                'ai_assistant': 'AI Assistant',
                'enter_transaction': 'e.g: coffee 25k, saving 200k...',
                'welcome_message': 'Hello! Tell me about your transaction. e.g: "lunch 50k"',
                'lunch': 'Lunch',
                'quick_actions': 'Quick Actions',
                'future_me': 'Future Me Simulator',
                'generate_meme': 'Generate Meme',
                'statistics': 'Statistics',
                'today_total': 'Today total:',
                'all': 'All',
                'smart_financial_management': 'Smart financial management',
                'calendar_coming_soon': 'Calendar will be implemented in Phase 4',
                'calendar_description': 'Interactive calendar with daily transaction display',
                'online': 'Online',
                'tieng_viet': 'Tiếng Việt',
                'english': 'English',
                'expense_tracker': 'Expense Tracker',
                'financial_calendar': 'Financial Calendar'
            }
        };
        
        return translations[lang] || translations['vi'];
    }
    
    /**
     * Translate text by key with parameters
     */
    t(key, params = {}) {
        let text = this.translations[key] || key;
        
        // Replace parameters
        Object.keys(params).forEach(param => {
            text = text.replace(`{${param}}`, params[param]);
        });
        
        return text;
    }
    
    /**
     * Set new language
     */
    async setLanguage(lang) {
        if (this.currentLang === lang) return;
        
        this.currentLang = lang;
        localStorage.setItem('language', lang);
        
        // Update language switcher
        document.getElementById('language-switcher').value = lang;
        
        // Reload translations
        await this.loadTranslations();
        
        // Update page content
        this.updatePageTexts();
        
        // Update HTML lang attribute
        document.documentElement.lang = lang;
        
        console.log(`Language changed to: ${lang}`);
    }
    
    /**
     * Update all text elements with data-i18n attributes
     */
    updatePageTexts() {
        // Update elements with data-i18n attribute
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            const translatedText = this.t(key);
            
            // Preserve emojis and icons - enhanced handling for colored emojis
            const emojiRegex = /[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]|🟢|🔴|🔵|📊|📅|🤖|⚡|📝/gu;
            const currentText = element.textContent.trim();
            const emojiMatch = currentText.match(emojiRegex);
            
            if (emojiMatch && emojiMatch.length > 0) {
                const emoji = emojiMatch[0];
                element.textContent = `${emoji} ${translatedText}`;
            } else {
                element.textContent = translatedText;
            }
        });
        
        // Update placeholder attributes
        document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
            const key = element.getAttribute('data-i18n-placeholder');
            element.placeholder = this.t(key);
        });
        
        // Update title if needed
        if (document.title.includes('Expense Tracker') || document.title.includes('Theo Dõi Chi Tiêu')) {
            document.title = this.t('expense_tracker') + ' - ' + this.t('ai_assistant');
        }
    }
    
    /**
     * Initialize language switcher dropdown
     */
    initLanguageSwitcher() {
        const switcher = document.getElementById('language-switcher');
        if (switcher) {
            switcher.value = this.currentLang;
            switcher.addEventListener('change', (e) => {
                this.setLanguage(e.target.value);
            });
        }
    }
    
    /**
     * Get current language
     */
    getCurrentLanguage() {
        return this.currentLang;
    }
    
    /**
     * Check if RTL language (not applicable for vi/en but good for future)
     */
    isRTL() {
        const rtlLanguages = ['ar', 'he', 'fa'];
        return rtlLanguages.includes(this.currentLang);
    }
    
    /**
     * Format currency based on language
     */
    formatCurrency(amount) {
        const formatters = {
            'vi': new Intl.NumberFormat('vi-VN', { 
                style: 'currency', 
                currency: 'VND',
                minimumFractionDigits: 0
            }),
            'en': new Intl.NumberFormat('en-US', { 
                style: 'currency', 
                currency: 'VND',
                minimumFractionDigits: 0
            })
        };
        
        const formatter = formatters[this.currentLang] || formatters['vi'];
        return formatter.format(amount).replace('₫', '₫');
    }
    
    /**
     * Format number with thousands separator
     */
    formatNumber(number) {
        const formatters = {
            'vi': new Intl.NumberFormat('vi-VN'),
            'en': new Intl.NumberFormat('en-US')
        };
        
        const formatter = formatters[this.currentLang] || formatters['vi'];
        return formatter.format(number);
    }
    
    /**
     * Get date format for current language
     */
    getDateFormat() {
        return this.currentLang === 'vi' ? 'dd/MM/yyyy' : 'MM/dd/yyyy';
    }
    
    /**
     * Format date based on language
     */
    formatDate(date) {
        const formatters = {
            'vi': new Intl.DateTimeFormat('vi-VN', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            }),
            'en': new Intl.DateTimeFormat('en-US', {
                year: 'numeric',
                month: 'long', 
                day: 'numeric'
            })
        };
        
        const formatter = formatters[this.currentLang] || formatters['vi'];
        return formatter.format(date);
    }
}

// Initialize i18n when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.i18n = new I18n();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = I18n;
} 