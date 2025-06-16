/**
 * AI Meme Generator - JavaScript Frontend
 * Handles meme generation, display, and sharing functionality
 */

class MemeGenerator {
    constructor() {
        this.currentMeme = null;
        this.currentLanguage = window.i18n ? window.i18n.currentLang : 'vi';
        
        // Initialize event listeners
        this.initEventListeners();
    }
    
    initEventListeners() {
        // Modal close handlers
        document.addEventListener('click', (e) => {
            if (e.target.id === 'meme-modal' || e.target.closest('.meme-close-btn')) {
                this.closeMeme();
            }
        });
        
        // Escape key to close modal
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !document.getElementById('meme-modal').classList.contains('hidden')) {
                this.closeMeme();
            }
        });
    }
    
    async generateMeme() {
        try {
            // Show loading state
            this.showLoadingState();
            
            // Open modal immediately
            this.openMemeModal();
            
            // Fetch meme data from API
            const response = await fetch('/api/meme/weekly/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            if (!response.ok) {
                throw new Error('Failed to generate meme');
            }
            
            const memeData = await response.json();
            this.currentMeme = memeData;
            
            // Display meme
            this.displayMeme(memeData);
            
        } catch (error) {
            console.error('Error generating meme:', error);
            this.showErrorState(error.message);
        }
    }
    
    async getMemeAnalysis() {
        try {
            const response = await fetch('/api/meme/analysis/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            if (!response.ok) {
                throw new Error('Failed to get analysis');
            }
            
            return await response.json();
            
        } catch (error) {
            console.error('Error getting analysis:', error);
            return null;
        }
    }
    
    openMemeModal() {
        const modal = document.getElementById('meme-modal');
        if (!modal) {
            this.createMemeModal();
        }
        document.getElementById('meme-modal').classList.remove('hidden');
        document.body.style.overflow = 'hidden'; // Prevent background scroll
    }
    
    closeMeme() {
        document.getElementById('meme-modal').classList.add('hidden');
        document.body.style.overflow = ''; // Restore scrolling
    }
    
    createMemeModal() {
        const modalHTML = `
            <div id="meme-modal" class="hidden fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-2 sm:p-4">
                <div class="bg-white rounded-2xl max-w-lg w-full max-h-screen overflow-y-auto shadow-2xl">
                    <div class="bg-gradient-to-r from-yellow-500 to-orange-500 p-6 text-white">
                        <div class="flex justify-between items-center">
                            <h3 class="text-xl font-bold" data-i18n="weekly_meme">🎭 Weekly Meme</h3>
                            <button class="meme-close-btn text-white hover:text-gray-200 transition-colors">
                                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                                </svg>
                            </button>
                        </div>
                    </div>
                    <div class="p-6">
                        <!-- Meme Content -->
                        <div id="meme-content" class="text-center">
                            <!-- Content will be dynamically inserted here -->
                        </div>
                        
                        <!-- Controls -->
                        <div class="mt-6 flex flex-col sm:flex-row justify-center gap-3">
                            <button onclick="window.memeGenerator.generateMeme()" 
                                class="px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl hover:from-purple-700 hover:to-pink-700 transition-all duration-300 font-semibold text-center">
                                🔄 <span data-i18n="generate_new">Tạo mới</span>
                            </button>
                            <button onclick="window.memeGenerator.shareMeme()" 
                                class="px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 font-semibold text-center">
                                📱 <span data-i18n="share">Chia sẻ</span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }
    
    showLoadingState() {
        const content = document.getElementById('meme-content');
        if (content) {
            content.innerHTML = `
                <div class="text-center py-8">
                    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mx-auto"></div>
                    <p class="mt-4 text-gray-600" data-i18n="analyzing_spending">Đang phân tích chi tiêu của bạn...</p>
                </div>
            `;
        }
    }
    
    showErrorState(message) {
        const content = document.getElementById('meme-content');
        if (content) {
            content.innerHTML = `
                <div class="text-center py-8">
                    <div class="text-4xl mb-4">😅</div>
                    <p class="text-red-600 font-semibold">Oops! ${message}</p>
                    <p class="text-gray-600 mt-2" data-i18n="try_again">Hãy thử lại sau nhé!</p>
                    <button onclick="window.memeGenerator.generateMeme()" 
                        class="mt-4 px-4 py-2 bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-lg hover:from-orange-600 hover:to-red-600 transition-all duration-300">
                        🔄 Thử lại
                    </button>
                </div>
            `;
        }
    }
    
    displayMeme(memeData) {
        const content = document.getElementById('meme-content');
        if (!content) return;
        
        const { template, personality, text, analysis, shareable_text } = memeData;
        
        // Create meme using CSS template
        let memeHTML;
        switch(template) {
            case 'drake_pointing':
                memeHTML = this.createDrakeTemplate(text, personality);
                break;
            case 'success_kid':
                memeHTML = this.createSuccessKidTemplate(text, personality);
                break;
            case 'this_is_fine':
                memeHTML = this.createThisIsFineTemplate(text, personality);
                break;
            case 'expanding_brain':
                memeHTML = this.createExpandingBrainTemplate(text, personality);
                break;
            case 'distracted_boyfriend':
                memeHTML = this.createDistractedBoyfriendTemplate(text, personality);
                break;
            case 'two_buttons':
                memeHTML = this.createTwoButtonsTemplate(text, personality);
                break;
            case 'change_my_mind':
                memeHTML = this.createChangeMyMindTemplate(text, personality);
                break;
            case 'woman_yelling_cat':
                memeHTML = this.createWomanYellingCatTemplate(text, personality);
                break;
            case 'stonks':
                memeHTML = this.createStonksTemplate(text, personality);
                break;
            case 'panik_kalm':
                memeHTML = this.createPanikKalmTemplate(text, personality);
                break;
            case 'galaxy_brain':
                memeHTML = this.createGalaxyBrainTemplate(text, personality);
                break;
            default:
                memeHTML = this.createFallbackTemplate(text, personality);
        }
        
        content.innerHTML = `
            <!-- Meme Display -->
            <div class="bg-gradient-to-br from-gray-100 to-gray-200 rounded-xl p-6 mb-6">
                ${memeHTML}
            </div>
            
            <!-- Analysis -->
            <div class="text-left bg-orange-50 rounded-lg p-4 mb-4">
                <h4 class="font-semibold text-gray-800 mb-2 flex items-center">
                    🔍 <span data-i18n="ai_analysis">AI phân tích:</span>
                </h4>
                <p class="text-sm text-gray-700">${shareable_text}</p>
                ${this.createInsightsSection(analysis)}
            </div>
        `;
        
        // Update i18n if available
        if (window.i18n) {
            window.i18n.updatePageTexts();
        }
    }
    
    createInsightsSection(analysis) {
        if (!analysis.category_totals || Object.keys(analysis.category_totals).length === 0) {
            return '';
        }
        
        let insights = '<div class="mt-3 text-xs text-gray-600"><strong>Chi tiết:</strong><ul class="list-disc list-inside mt-1">';
        
        for (const [category, amount] of Object.entries(analysis.category_totals)) {
            if (amount > 0) {
                const categoryName = this.getCategoryName(category);
                insights += `<li>${categoryName}: ${this.formatMoney(amount)}</li>`;
            }
        }
        
        insights += '</ul></div>';
        return insights;
    }
    
    createDrakeTemplate(text, personality) {
        const { top, bottom } = text;
        return `
            <div class="relative bg-gradient-to-br from-blue-100 to-purple-100 rounded-lg p-6">
                <div class="grid grid-cols-2 gap-4 items-center">
                    <!-- Drake No -->
                    <div class="text-right">
                        <div class="text-4xl mb-2">🙅‍♂️</div>
                        <p class="text-sm font-semibold text-gray-700">${top}</p>
                    </div>
                    <!-- Drake Yes -->
                    <div class="text-left">
                        <div class="text-4xl mb-2">👉</div>
                        <p class="text-sm font-semibold text-gray-700">${bottom}</p>
                    </div>
                </div>
                <div class="absolute top-2 right-2">
                    <span class="px-2 py-1 bg-yellow-400 text-black text-xs rounded-full font-bold">
                        ${this.getPersonalityIcon(personality)}
                    </span>
                </div>
            </div>
        `;
    }
    
    createSuccessKidTemplate(text, personality) {
        return `
            <div class="relative bg-gradient-to-br from-green-100 to-blue-100 rounded-lg p-6">
                <div class="text-center">
                    <div class="text-6xl mb-4">👶💪</div>
                    <p class="text-lg font-bold text-gray-800">${text.text}</p>
                </div>
                <div class="absolute top-2 right-2">
                    <span class="px-2 py-1 bg-green-400 text-black text-xs rounded-full font-bold">
                        ${this.getPersonalityIcon(personality)}
                    </span>
                </div>
            </div>
        `;
    }
    
    createThisIsFineTemplate(text, personality) {
        return `
            <div class="relative bg-gradient-to-br from-orange-100 to-red-100 rounded-lg p-6">
                <div class="text-center">
                    <div class="text-6xl mb-4">🔥☕🐕</div>
                    <p class="text-lg font-bold text-gray-800">${text.text}</p>
                    <p class="text-sm text-gray-600 mt-2 italic">This is fine.</p>
                </div>
                <div class="absolute top-2 right-2">
                    <span class="px-2 py-1 bg-orange-400 text-black text-xs rounded-full font-bold">
                        ${this.getPersonalityIcon(personality)}
                    </span>
                </div>
            </div>
        `;
    }
    
    createExpandingBrainTemplate(text, personality) {
        const levels = text.levels || ['Level 1', 'Level 2', 'Level 3', 'Level 4'];
        const brainEmojis = ['🧠', '💡', '🌟', '💎'];
        
        return `
            <div class="relative bg-gradient-to-br from-purple-100 to-pink-100 rounded-lg p-6">
                <div class="space-y-3">
                    ${levels.map((level, index) => `
                        <div class="flex items-center space-x-3 ${index === levels.length - 1 ? 'font-bold text-purple-800' : 'text-gray-700'}">
                            <div class="text-2xl">${brainEmojis[index] || '🧠'}</div>
                            <p class="text-sm flex-1">${level}</p>
                        </div>
                    `).join('')}
                </div>
                <div class="absolute top-2 right-2">
                    <span class="px-2 py-1 bg-purple-400 text-black text-xs rounded-full font-bold">
                        ${this.getPersonalityIcon(personality)}
                    </span>
                </div>
            </div>
        `;
    }
    
    createFallbackTemplate(text, personality) {
        return `
            <div class="relative bg-gradient-to-br from-gray-100 to-gray-200 rounded-lg p-6">
                <div class="text-center">
                    <div class="text-6xl mb-4">🤔</div>
                    <p class="text-lg font-bold text-gray-800">${text.text || 'Chi tiêu của bạn tuần này thật thú vị!'}</p>
                </div>
                <div class="absolute top-2 right-2">
                    <span class="px-2 py-1 bg-gray-400 text-black text-xs rounded-full font-bold">
                        ${this.getPersonalityIcon(personality)}
                    </span>
                </div>
            </div>
        `;
    }
    
    createDistractedBoyfriendTemplate(text, personality) {
        const { boyfriend, girlfriend, other_woman } = text;
        return `
            <div class="relative bg-gradient-to-br from-pink-100 to-purple-100 rounded-lg p-6">
                <div class="grid grid-cols-3 gap-4 text-center items-center">
                    <div>
                        <div class="text-4xl mb-2">👨</div>
                        <p class="text-xs font-semibold text-gray-700">${boyfriend}</p>
                    </div>
                    <div>
                        <div class="text-4xl mb-2">😠👩</div>
                        <p class="text-xs font-semibold text-gray-700">${girlfriend}</p>
                    </div>
                    <div>
                        <div class="text-4xl mb-2">😍👩</div>
                        <p class="text-xs font-semibold text-gray-700">${other_woman}</p>
                    </div>
                </div>
                <div class="absolute top-2 right-2">
                    <span class="px-2 py-1 bg-pink-400 text-black text-xs rounded-full font-bold">
                        ${this.getPersonalityIcon(personality)}
                    </span>
                </div>
            </div>
        `;
    }
    
    createTwoButtonsTemplate(text, personality) {
        const { button1, button2 } = text;
        return `
            <div class="relative bg-gradient-to-br from-red-100 to-blue-100 rounded-lg p-6">
                <div class="text-center">
                    <div class="text-6xl mb-4">😰</div>
                    <div class="space-y-3">
                        <button class="w-full p-3 bg-red-400 text-white rounded-lg font-semibold text-sm">
                            ${button1}
                        </button>
                        <button class="w-full p-3 bg-blue-400 text-white rounded-lg font-semibold text-sm">
                            ${button2}
                        </button>
                    </div>
                </div>
                <div class="absolute top-2 right-2">
                    <span class="px-2 py-1 bg-yellow-400 text-black text-xs rounded-full font-bold">
                        ${this.getPersonalityIcon(personality)}
                    </span>
                </div>
            </div>
        `;
    }
    
    createChangeMyMindTemplate(text, personality) {
        return `
            <div class="relative bg-gradient-to-br from-cyan-100 to-blue-100 rounded-lg p-6">
                <div class="text-center">
                    <div class="text-4xl mb-3">🪑☕</div>
                    <div class="bg-white p-4 rounded-lg border-2 border-gray-300 transform -rotate-1">
                        <p class="text-sm font-bold text-gray-800">${text}</p>
                        <p class="text-xs text-gray-600 mt-2 italic">Change My Mind</p>
                    </div>
                </div>
                <div class="absolute top-2 right-2">
                    <span class="px-2 py-1 bg-cyan-400 text-black text-xs rounded-full font-bold">
                        ${this.getPersonalityIcon(personality)}
                    </span>
                </div>
            </div>
        `;
    }
    
    createWomanYellingCatTemplate(text, personality) {
        const { woman, cat } = text;
        return `
            <div class="relative bg-gradient-to-br from-yellow-100 to-orange-100 rounded-lg p-6">
                <div class="grid grid-cols-2 gap-4 items-center">
                    <div class="text-center">
                        <div class="text-4xl mb-2">😡👩</div>
                        <p class="text-xs font-semibold text-gray-700">${woman}</p>
                    </div>
                    <div class="text-center">
                        <div class="text-4xl mb-2">😐🐱</div>
                        <p class="text-xs font-semibold text-gray-700">${cat}</p>
                    </div>
                </div>
                <div class="absolute top-2 right-2">
                    <span class="px-2 py-1 bg-yellow-400 text-black text-xs rounded-full font-bold">
                        ${this.getPersonalityIcon(personality)}
                    </span>
                </div>
            </div>
        `;
    }
    
    createStonksTemplate(text, personality) {
        return `
            <div class="relative bg-gradient-to-br from-green-100 to-emerald-100 rounded-lg p-6">
                <div class="text-center">
                    <div class="text-6xl mb-4">📈🤓</div>
                    <p class="text-xl font-bold text-green-800">${text}</p>
                    <p class="text-sm text-green-600 mt-2 italic">STONKS ↗️</p>
                </div>
                <div class="absolute top-2 right-2">
                    <span class="px-2 py-1 bg-green-400 text-black text-xs rounded-full font-bold">
                        ${this.getPersonalityIcon(personality)}
                    </span>
                </div>
            </div>
        `;
    }
    
    createPanikKalmTemplate(text, personality) {
        const { panik1, kalm, panik2 } = text;
        return `
            <div class="relative bg-gradient-to-br from-red-100 via-green-100 to-red-100 rounded-lg p-6">
                <div class="space-y-4 text-center">
                    <div class="bg-red-200 p-3 rounded-lg">
                        <div class="text-2xl mb-1">😱</div>
                        <p class="text-xs font-bold text-red-800">PANIK</p>
                        <p class="text-xs text-red-700">${panik1}</p>
                    </div>
                    <div class="bg-green-200 p-3 rounded-lg">
                        <div class="text-2xl mb-1">😌</div>
                        <p class="text-xs font-bold text-green-800">KALM</p>
                        <p class="text-xs text-green-700">${kalm}</p>
                    </div>
                    <div class="bg-red-200 p-3 rounded-lg">
                        <div class="text-2xl mb-1">😱</div>
                        <p class="text-xs font-bold text-red-800">PANIK</p>
                        <p class="text-xs text-red-700">${panik2}</p>
                    </div>
                </div>
                <div class="absolute top-2 right-2">
                    <span class="px-2 py-1 bg-purple-400 text-black text-xs rounded-full font-bold">
                        ${this.getPersonalityIcon(personality)}
                    </span>
                </div>
            </div>
        `;
    }
    
    createGalaxyBrainTemplate(text, personality) {
        const levels = text.levels || text || ['Level 1', 'Level 2', 'Level 3', 'Level 4'];
        const brainEmojis = ['🧠', '💫', '🌟', '🌌'];
        const glowLevels = ['text-gray-700', 'text-blue-700', 'text-purple-700', 'text-pink-700'];
        
        return `
            <div class="relative bg-gradient-to-br from-indigo-100 to-purple-100 rounded-lg p-6">
                <div class="space-y-3">
                    ${levels.map((level, index) => `
                        <div class="flex items-center space-x-3 ${index === levels.length - 1 ? 'font-bold ' + glowLevels[index] : 'text-gray-700'}">
                            <div class="text-2xl">${brainEmojis[index] || '🧠'}</div>
                            <p class="text-sm flex-1">${level}</p>
                        </div>
                    `).join('')}
                </div>
                <div class="absolute top-2 right-2">
                    <span class="px-2 py-1 bg-indigo-400 text-black text-xs rounded-full font-bold">
                        ${this.getPersonalityIcon(personality)}
                    </span>
                </div>
            </div>
        `;
    }
    
    getPersonalityIcon(personality) {
        const icons = {
            'coffee_addict': '☕',
            'foodie_explorer': '🍜',
            'saving_master': '💰',
            'balanced_spender': '⚖️'
        };
        return icons[personality] || '🤔';
    }
    
    getCategoryName(category) {
        const names = {
            'vi': {
                'coffee': 'Coffee',
                'food': 'Ăn uống',
                'transport': 'Di chuyển',
                'shopping': 'Mua sắm',
                'entertainment': 'Giải trí',
                'health': 'Sức khỏe',
                'education': 'Giáo dục',
                'utilities': 'Tiện ích',
                'other': 'Khác'
            },
            'en': {
                'coffee': 'Coffee',
                'food': 'Food & Dining',
                'transport': 'Transportation',
                'shopping': 'Shopping',
                'entertainment': 'Entertainment',
                'health': 'Healthcare',
                'education': 'Education',
                'utilities': 'Utilities',
                'other': 'Other'
            }
        };
        
        return names[this.currentLanguage]?.[category] || category;
    }
    
    formatMoney(amount) {
        return `${Math.abs(amount).toLocaleString('vi-VN')}₫`;
    }
    
    async shareMeme() {
        if (!this.currentMeme) {
            if (window.showAlertDialog) {
                window.showAlertDialog('Không có meme để chia sẻ!', { type: 'error' });
            } else {
                showAlertDialog(window.i18n.t('no_meme_to_share'), { type: 'error' });
            }
            return;
        }
        
        try {
            const shareData = {
                meme_data: this.currentMeme,
                timestamp: new Date().toISOString()
            };
            
            const response = await fetch('/api/meme/share/', {
                method: 'POST',
                headers: getCommonHeaders(),
                body: JSON.stringify(shareData)
            });
            
            if (response.ok) {
                // Use Web Share API if available
                if (navigator.share) {
                    await navigator.share({
                        title: 'My Expense Tracker Meme',
                        text: this.currentMeme.shareable_text,
                        url: window.location.href
                    });
                } else {
                    // Fallback: copy to clipboard
                    await navigator.clipboard.writeText(this.currentMeme.shareable_text);
                    this.showNotification('📋 Đã copy vào clipboard!');
                }
            } else {
                throw new Error('Failed to share meme');
            }
            
        } catch (error) {
            console.error('Error sharing meme:', error);
            // Simple fallback
            const text = this.currentMeme.shareable_text + ' - From Expense Tracker App';
            prompt('Copy this text to share:', text);
        }
    }
    
    showNotification(message) {
        // Simple notification - could be enhanced with a proper notification system
        const notification = document.createElement('div');
        notification.className = 'fixed top-4 right-4 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg z-50';
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// Global function for the button onclick
function generateMeme() {
    if (!window.memeGenerator) {
        window.memeGenerator = new MemeGenerator();
    }
    window.memeGenerator.generateMeme();
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.memeGenerator = new MemeGenerator();
});
