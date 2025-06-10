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
     * Get local translations (using separate translation files)
     */
    getLocalTranslations(lang) {
        // Use translations from separate files if available
        if (lang === 'vi' && window.viTranslations) {
            return window.viTranslations;
        }
        if (lang === 'en' && window.enTranslations) {
            return window.enTranslations;
        }
        
        // Fallback to basic translations if files not loaded
        const fallbackTranslations = {
            'vi': {
                'expense': 'Chi Tiêu',
                'saving': 'Tiết Kiệm', 
                'investment': 'Đầu Tư',
                'send': 'Gửi',
                'today': 'Hôm Nay',
                'ai_assistant': 'AI Assistant'
            },
            'en': {
                'expense': 'Expense',
                'saving': 'Saving',
                'investment': 'Investment',
                'send': 'Send',
                'today': 'Today',
                'ai_assistant': 'AI Assistant'
            }
        };
        
        return fallbackTranslations[lang] || fallbackTranslations['vi'];
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
        
        // Update language switcher flag
        const currentFlag = document.getElementById('current-flag');
        if (currentFlag) {
            currentFlag.textContent = lang === 'vi' ? '🇻🇳' : '🇺🇸';
        }
        
        // Reload translations
        await this.loadTranslations();
        
        // Update page content
        this.updatePageTexts();
        
        // Update HTML lang attribute
        document.documentElement.lang = lang;
        
        // Dispatch languageChanged event for calendar and other components
        const languageChangeEvent = new CustomEvent('languageChanged', {
            detail: { 
                language: lang,
                previousLanguage: this.currentLang 
            }
        });
        document.dispatchEvent(languageChangeEvent);
        
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
        const dropdown = document.getElementById('language-dropdown');
        const currentFlag = document.getElementById('current-flag');
        
        if (switcher && dropdown && currentFlag) {
            // Set initial flag
            currentFlag.textContent = this.currentLang === 'vi' ? '🇻🇳' : '🇺🇸';
            
            // Toggle dropdown on click
            switcher.addEventListener('click', (e) => {
                e.stopPropagation();
                dropdown.classList.toggle('hidden');
            });
            
            // Handle language option clicks
            dropdown.querySelectorAll('.language-option').forEach(option => {
                option.addEventListener('click', (e) => {
                    const selectedLang = option.getAttribute('data-lang');
                    this.setLanguage(selectedLang);
                    dropdown.classList.add('hidden');
                });
            });
            
            // Close dropdown when clicking outside
            document.addEventListener('click', () => {
                dropdown.classList.add('hidden');
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