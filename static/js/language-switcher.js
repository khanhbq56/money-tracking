/**
 * Enhanced Language Switcher
 * Beautiful dropdown UI for language selection
 */

class LanguageSwitcher {
    constructor() {
        this.currentLang = 'vi';
        this.isOpen = false;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.updateCurrentLanguage();
    }

    setupEventListeners() {
        const switcherBtn = document.getElementById('language-switcher-btn');
        const dropdown = document.getElementById('language-dropdown');
        const languageOptions = document.querySelectorAll('.language-option');

        if (!switcherBtn || !dropdown) {
            console.warn('Language switcher elements not found');
            return;
        }

        // Toggle dropdown
        switcherBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleDropdown();
        });

        // Language option clicks
        languageOptions.forEach(option => {
            option.addEventListener('click', (e) => {
                e.stopPropagation();
                const lang = option.getAttribute('data-lang');
                this.selectLanguage(lang);
            });
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!switcherBtn.contains(e.target) && !dropdown.contains(e.target)) {
                this.closeDropdown();
            }
        });

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.closeDropdown();
            }
        });
    }

    toggleDropdown() {
        if (this.isOpen) {
            this.closeDropdown();
        } else {
            this.openDropdown();
        }
    }

    openDropdown() {
        const dropdown = document.getElementById('language-dropdown');
        const arrow = document.getElementById('dropdown-arrow');
        
        dropdown.classList.add('show');
        arrow.style.transform = 'rotate(180deg)';
        this.isOpen = true;

        // Create overlay for click outside
        const overlay = document.createElement('div');
        overlay.className = 'language-overlay';
        overlay.onclick = () => this.closeDropdown();
        document.body.appendChild(overlay);
    }

    closeDropdown() {
        const dropdown = document.getElementById('language-dropdown');
        const arrow = document.getElementById('dropdown-arrow');
        const overlay = document.querySelector('.language-overlay');
        
        dropdown.classList.remove('show');
        arrow.style.transform = 'rotate(0deg)';
        this.isOpen = false;

        if (overlay) {
            overlay.remove();
        }
    }

    selectLanguage(lang) {
        if (lang === this.currentLang) {
            this.closeDropdown();
            return;
        }

        this.currentLang = lang;
        this.updateCurrentLanguage();
        this.closeDropdown();

        // Trigger language change
        if (window.i18n && window.i18n.setLanguage) {
            window.i18n.setLanguage(lang);
        }

        // Update active state
        this.updateActiveOption();

        // Dispatch custom event
        document.dispatchEvent(new CustomEvent('languageChanged', {
            detail: { language: lang }
        }));

        console.log(`🌐 Language changed to: ${lang}`);
    }

    updateCurrentLanguage() {
        const flagElement = document.getElementById('current-flag');
        const langElement = document.getElementById('current-lang');

        if (!flagElement || !langElement) return;

        const languageData = {
            'vi': {
                flag: '🇻🇳',
                name: 'Tiếng Việt'
            },
            'en': {
                flag: '🇺🇸',
                name: 'English'
            }
        };

        const data = languageData[this.currentLang];
        if (data) {
            flagElement.textContent = data.flag;
            langElement.textContent = data.name;
        }
    }

    updateActiveOption() {
        const options = document.querySelectorAll('.language-option');
        options.forEach(option => {
            const lang = option.getAttribute('data-lang');
            if (lang === this.currentLang) {
                option.classList.add('active');
            } else {
                option.classList.remove('active');
            }
        });
    }

    // Public method to get current language
    getCurrentLanguage() {
        return this.currentLang;
    }

    // Public method to set language programmatically
    setLanguage(lang) {
        if (['vi', 'en'].includes(lang)) {
            this.selectLanguage(lang);
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('language-switcher-btn')) {
        window.languageSwitcher = new LanguageSwitcher();
        console.log('✅ Enhanced Language Switcher initialized');
    }
});

// Backward compatibility with old language switcher
function setLanguage(lang) {
    if (window.languageSwitcher) {
        window.languageSwitcher.setLanguage(lang);
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LanguageSwitcher;
} 