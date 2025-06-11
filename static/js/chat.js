/**
 * AI Chat Interface for Expense Tracker
 * Handles real-time chat with AI, transaction confirmations, and UI updates
 */

class AIChat {
    constructor() {
        this.chatContainer = document.getElementById('chat-messages');
        this.chatInput = document.getElementById('chat-input');
        this.currentLanguage = window.i18n ? window.i18n.currentLang : 'vi';
        this.isProcessing = false;
        
        this.initializeChat();
    }
    
    /**
     * Check if auto-confirm is enabled
     */
    isAutoConfirmEnabled() {
        return localStorage.getItem('chat-auto-confirm') === 'true';
    }
    
    /**
     * Start auto-confirm countdown
     */
    startAutoConfirmCountdown(data, totalMs) {
        let remainingMs = totalMs;
        const intervalMs = 100; // Update every 100ms for smooth countdown
        const countdownElement = document.getElementById(`auto-confirm-countdown-${data.chat_id}`);
        
        const countdownInterval = setInterval(() => {
            remainingMs -= intervalMs;
            const remainingSeconds = Math.ceil(remainingMs / 1000);
            
            if (countdownElement) {
                const text = remainingSeconds > 0 ? 
                    `${window.i18n.t('auto_confirm')} (${remainingSeconds}s)` : 
                    `${window.i18n.t('auto_confirm')} ✓`;
                countdownElement.querySelector('span:last-child').textContent = text;
            }
            
            if (remainingMs <= 0) {
                clearInterval(countdownInterval);
                this.confirmTransaction(data);
            }
        }, intervalMs);
        
        // Store interval ID in case we need to cancel it
        data.countdownInterval = countdownInterval;
    }
    
    /**
     * Cancel auto-confirm countdown
     */
    cancelAutoConfirm(data) {
        // Clear countdown interval
        if (data.countdownInterval) {
            clearInterval(data.countdownInterval);
            data.countdownInterval = null;
        }
        
        // Convert to manual confirmation mode
        this.convertToManualConfirm(data);
    }
    
    /**
     * Convert auto-confirm UI to manual confirm UI
     */
    convertToManualConfirm(data) {
        const confirmText = window.i18n.t('confirm');
        const editText = window.i18n.t('edit');
        
        // Find the action buttons container for this message
        const countdownElement = document.getElementById(`auto-confirm-countdown-${data.chat_id}`);
        if (countdownElement) {
            const container = countdownElement.parentElement;
            if (container) {
                // Replace with manual confirmation buttons
                container.innerHTML = `
                    <button 
                        onclick="window.aiChat.confirmTransaction(${this.escapeJson(data)})" 
                        class="px-3 py-2 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-xl text-xs hover:from-green-600 hover:to-emerald-600 transition-all duration-300 font-medium shadow-md hover:shadow-lg hover:scale-105"
                    >
                        ${confirmText}
                    </button>
                    <button 
                        onclick="window.aiChat.editTransaction(${this.escapeJson(data)})" 
                        class="px-3 py-2 bg-gradient-to-r from-yellow-500 to-orange-500 text-white rounded-xl text-xs hover:from-yellow-600 hover:to-orange-600 transition-all duration-300 font-medium shadow-md hover:shadow-lg hover:scale-105"
                    >
                        ${editText}
                    </button>
                `;
            }
        }
    }
    
    initializeChat() {
        // Set up event listeners
        if (this.chatInput) {
            this.chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }
        
        // Add welcome message if no messages exist
        if (this.chatContainer && this.chatContainer.children.length === 0) {
            this.addWelcomeMessage();
        }
    }
    
    addWelcomeMessage() {
        const welcomeText = window.i18n ? 
            `👋 ${window.i18n.t('welcome_message')}` :
            '👋 Xin chào! Hãy nói cho tôi biết giao dịch của bạn. VD: "ăn trưa 50k"';
            
        this.addMessage(welcomeText, 'bot');
    }
    
    async sendMessage(hasVoice = false) {
        if (this.isProcessing) return;
        
        const message = this.chatInput.value.trim();
        if (!message) return;
        
        // Clear input and add user message
        this.chatInput.value = '';
        
        // Reset input styling if it was from voice
        if (hasVoice && this.chatInput) {
            this.chatInput.style.fontStyle = 'normal';
            this.chatInput.style.color = '';
        }
        
        this.addMessage(message, 'user', null, hasVoice);
        
        // Show typing indicator
        this.showTypingIndicator();
        this.isProcessing = true;
        
        try {
            // Process message with AI
            const response = await this.processMessage(message, hasVoice);
            
            // Remove typing indicator
            this.removeTypingIndicator();
            
            // Add AI response with date info if available
            let responseText = response.suggested_text;
            if (response.parsed_date_description && response.parsed_date_description !== 'hôm nay' && response.parsed_date_description !== 'today') {
                responseText += ` (${response.parsed_date_description})`;
            }
            
            this.addMessage(responseText, 'bot', response);
            
        } catch (error) {
            console.error('Chat error:', error);
            this.removeTypingIndicator();
            
            const errorText = window.i18n ? 
                `❌ ${window.i18n.t('error_occurred')}` :
                '❌ Xin lỗi, có lỗi xảy ra. Vui lòng thử lại!';
                
            this.addMessage(errorText, 'bot');
        } finally {
            this.isProcessing = false;
        }
    }
    
    async processMessage(message, hasVoice = false) {
        const payload = {
            message: message,
            has_voice: hasVoice,
            language: this.currentLanguage
        };
        
        const response = await fetch('/api/chat/process/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Network error');
        }
        
        return await response.json();
    }
    
    addMessage(text, sender, data = null, hasVoice = false) {
        if (!this.chatContainer) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-bubble animate-fadeInUp';
        
        if (sender === 'user') {
            // Add voice indicator for voice messages
            const voiceIndicator = hasVoice ? '<span class="text-xs opacity-75">🎤</span> ' : '';
            messageDiv.className = 'chat-bubble animate-fadeInUp flex justify-end';
            messageDiv.innerHTML = `
                <div class="bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-2xl rounded-br-md p-4 text-sm max-w-xs shadow-lg">
                    <p class="leading-relaxed">${voiceIndicator}${this.escapeHtml(text)}</p>
                </div>
            `;
        } else {
            let actionButtons = '';
            let detailsSection = '';
            
            if (data && data.ai_result) {
                const aiResult = data.ai_result;
                const confirmText = window.i18n ? `✅ ${window.i18n.t('confirm')}` : '✅ Confirm';
                const editText = window.i18n ? `✏️ ${window.i18n.t('edit')}` : '✏️ Edit';
                
                // Create details section with organized info
                let categoryInfo = '';
                if (aiResult.type === 'expense' && aiResult.category) {
                    const categoryNames = {
                        'vi': {
                            'food': '🍜 Ăn uống',
                            'coffee': '☕ Coffee',
                            'transport': '🚗 Di chuyển',
                            'shopping': '🛒 Mua sắm',
                            'entertainment': '🎬 Giải trí',
                            'health': '🏥 Sức khỏe',
                            'education': '📚 Giáo dục',
                            'utilities': '⚡ Tiện ích',
                            'other': '📦 Khác'
                        },
                        'en': {
                            'food': '🍜 Food & Dining',
                            'coffee': '☕ Coffee',
                            'transport': '🚗 Transportation',
                            'shopping': '🛒 Shopping',
                            'entertainment': '🎬 Entertainment',
                            'health': '🏥 Healthcare',
                            'education': '📚 Education',
                            'utilities': '⚡ Utilities',
                            'other': '📦 Other'
                        }
                    };
                    
                    const categoryName = categoryNames[this.currentLanguage]?.[aiResult.category] || aiResult.category;
                    categoryInfo = `<span class="inline-flex items-center gap-1">${categoryName}</span>`;
                }
                
                // Format date info
                let dateText = '';
                if (aiResult.parsed_date) {
                    const date = new Date(aiResult.parsed_date);
                    const localeMap = { 'vi': 'vi-VN', 'en': 'en-US' };
        const locale = localeMap[this.currentLanguage] || 'en-US';
                    dateText = date.toLocaleDateString(locale);
                } else {
                    dateText = window.i18n.t('today');
                }
                
                // Get transaction type display
                const typeDisplayKey = `transaction_type_${aiResult.type}`;
                const typeDisplay = window.i18n.t(typeDisplayKey);
                
                // Format amount
                const formattedAmount = new Intl.NumberFormat('vi-VN').format(Math.abs(aiResult.amount)) + '₫';
                
                detailsSection = `
                    <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-3 mt-3 border border-blue-200">
                        <div class="space-y-2 text-sm">
                            <!-- Transaction Info Row 1 -->
                            <div class="flex items-center justify-between">
                                <span class="text-blue-600 font-medium">${typeDisplay}</span>
                                <span class="text-lg font-bold text-gray-800">${formattedAmount}</span>
                            </div>
                            
                            <!-- Transaction Info Row 2 -->
                            <div class="flex items-center justify-between">
                                <span class="text-blue-600 font-medium">📅 ${dateText}</span>
                                ${categoryInfo ? `<span class="text-green-600 font-medium">${categoryInfo}</span>` : ''}
                            </div>
                            
                            <!-- Description -->
                            <div class="pt-1 border-t border-blue-200">
                                <span class="text-gray-700 italic">"${aiResult.description}"</span>
                            </div>
                        </div>
                    </div>
                `;
                
                // Check if auto-confirm is enabled
                if (this.isAutoConfirmEnabled()) {
                    // Auto-confirm: show countdown and action buttons
                    actionButtons = `
                        <div class="flex flex-wrap gap-2 mt-3">
                            <div id="auto-confirm-countdown-${data.chat_id}" class="px-3 py-2 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-xl text-xs font-medium shadow-md flex items-center gap-1">
                                <span>⚡</span>
                                <span>${window.i18n.t('auto_confirm')} (3s)</span>
                            </div>
                            <button 
                                onclick="window.aiChat.cancelAutoConfirm(${this.escapeJson(data)})" 
                                class="px-3 py-2 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-xl text-xs hover:from-red-600 hover:to-red-700 transition-all duration-300 font-medium shadow-md hover:shadow-lg hover:scale-105"
                                title="${window.i18n.t('cancel')}"
                            >
                                ✋
                            </button>
                            <button 
                                onclick="window.aiChat.editTransaction(${this.escapeJson(data)})" 
                                class="px-3 py-2 bg-gradient-to-r from-yellow-500 to-orange-500 text-white rounded-xl text-xs hover:from-yellow-600 hover:to-orange-600 transition-all duration-300 font-medium shadow-md hover:shadow-lg hover:scale-105"
                            >
                                ${editText}
                            </button>
                        </div>
                    `;
                    
                    // Start countdown and auto-confirm
                    this.startAutoConfirmCountdown(data, 3000); // 3 second countdown
                } else {
                    // Manual confirm: show both buttons
                    actionButtons = `
                        <div class="flex flex-wrap gap-2 mt-3">
                            <button 
                                onclick="window.aiChat.confirmTransaction(${this.escapeJson(data)})" 
                                class="px-3 py-2 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-xl text-xs hover:from-green-600 hover:to-emerald-600 transition-all duration-300 font-medium shadow-md hover:shadow-lg hover:scale-105"
                            >
                                ${confirmText}
                            </button>
                            <button 
                                onclick="window.aiChat.editTransaction(${this.escapeJson(data)})" 
                                class="px-3 py-2 bg-gradient-to-r from-yellow-500 to-orange-500 text-white rounded-xl text-xs hover:from-yellow-600 hover:to-orange-600 transition-all duration-300 font-medium shadow-md hover:shadow-lg hover:scale-105"
                            >
                                ${editText}
                            </button>
                        </div>
                    `;
                }
            }
            
            messageDiv.className = 'chat-bubble animate-fadeInUp flex justify-start';
            
            // For AI results, show simplified message or no message at all if we have details
            let messageContent = '';
            if (data && data.ai_result) {
                // Only show simple confirmation message for AI results since details are shown below
                const confirmationText = window.i18n.t('chat_analysis_message');
                messageContent = `<p class="leading-relaxed text-gray-800 mb-2">${confirmationText}</p>`;
            } else {
                // For regular messages, show the full text
                messageContent = `<p class="leading-relaxed text-gray-800 mb-2">${this.escapeHtml(text)}</p>`;
            }
            
            messageDiv.innerHTML = `
                <div class="bg-white border border-gray-200 rounded-2xl rounded-bl-md p-4 text-sm max-w-sm shadow-lg">
                    <div class="flex items-start gap-2">
                        <span class="text-lg">🤖</span>
                        <div class="flex-1">
                            ${messageContent}
                            ${detailsSection}
                            ${actionButtons}
                        </div>
                    </div>
                </div>
            `;
            
            // Show notification if modal is closed
            this.showNotificationIfModalClosed();
        }
        
        this.chatContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    showNotificationIfModalClosed() {
        const modal = document.getElementById('chat-modal');
        const notification = document.getElementById('chat-notification');
        
        if (modal && modal.classList.contains('hidden') && notification) {
            notification.classList.remove('hidden');
            
            // Auto-hide notification after 5 seconds
            setTimeout(() => {
                if (notification && !notification.classList.contains('hidden')) {
                    notification.classList.add('hidden');
                }
            }, 5000);
        }
    }
    
    hideNotification() {
        const notification = document.getElementById('chat-notification');
        if (notification) {
            notification.classList.add('hidden');
        }
    }
    
    showTypingIndicator() {
        if (!this.chatContainer) return;
        
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typing-indicator';
        typingDiv.className = 'chat-bubble';
        typingDiv.className = 'chat-bubble flex justify-start';
        typingDiv.innerHTML = `
            <div class="bg-white border border-gray-200 rounded-2xl rounded-bl-md p-4 text-sm max-w-xs shadow-lg">
                <div class="flex items-center space-x-2">
                    <span class="text-lg">🤖</span>
                    <span>Đang xử lý</span>
                    <div class="flex space-x-1">
                        <div class="w-1 h-1 bg-gray-400 rounded-full animate-pulse"></div>
                        <div class="w-1 h-1 bg-gray-400 rounded-full animate-pulse delay-75"></div>
                        <div class="w-1 h-1 bg-gray-400 rounded-full animate-pulse delay-150"></div>
                    </div>
                </div>
            </div>
        `;
        
        this.chatContainer.appendChild(typingDiv);
        this.scrollToBottom();
    }
    
    removeTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }
    
    async confirmTransaction(data) {
        try {
            // Check if this transaction is already confirmed to prevent double-confirmation
            if (data.confirmed) {
                return;
            }
            
            // Mark as being confirmed
            data.confirmed = true;
            
            // Clear countdown interval if running
            if (data.countdownInterval) {
                clearInterval(data.countdownInterval);
                data.countdownInterval = null;
            }
            
            const payload = {
                chat_id: data.chat_id,
                transaction_data: data.ai_result,
                custom_date: null // Will use parsed date from AI
            };
            
            const response = await fetch('/api/chat/confirm/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(payload)
            });
            
            if (!response.ok) {
                throw new Error('Failed to confirm transaction');
            }
            
            const result = await response.json();
            
            // Success message
            const successText = window.i18n.t('transaction_confirm_success');
                
            this.addMessage(successText, 'bot');
            
            // Show toast notification for chat confirmation (different from regular add)
            if (window.app && typeof window.app.showNotification === 'function') {
                window.app.showNotification(successText, 'success');
            }
            
            // Broadcast transaction added event (without notification since we already showed it)
            if (window.eventBus) {
                window.eventBus.emit('transactionAdded', {
                    transaction: result.transaction,
                    source: 'chat',
                    skipNotification: true  // Tell eventBus not to show notification
                });
            } else {
                // Fallback to direct calls
            if (window.dashboard) {
                window.dashboard.refreshDashboard();
            }
            if (window.calendar) {
                    window.calendar.refreshCalendar();
                }
            }
            
            // Remove the confirmation buttons
            this.disableConfirmationButtons(data.chat_id);
            
        } catch (error) {
            console.error('Confirmation error:', error);
            
            // Reset confirmation status on error
            data.confirmed = false;
            
            const errorText = window.i18n.t('transaction_confirm_error');
                
            this.addMessage(errorText, 'bot');
        }
    }
    
    editTransaction(data) {
        // Cancel auto-confirm countdown if running
        if (data.countdownInterval) {
            clearInterval(data.countdownInterval);
            data.countdownInterval = null;
        }
        
        // Open transaction form with pre-filled data instead of re-chatting
        const aiResult = data.ai_result;
        
        // Prepare transaction data for editing
        const transactionData = {
            description: aiResult.description,
            amount: Math.abs(aiResult.amount),
            transaction_type: aiResult.type,
            expense_category: aiResult.category || '',
            date: aiResult.parsed_date || new Date().toISOString().split('T')[0]
        };
        
        // Close chat modal first
        const chatModal = document.getElementById('chat-modal');
        if (chatModal) {
            chatModal.classList.add('hidden');
        }
        
        // Use calendar's showTransactionForm if available, otherwise show our own form
        if (window.showTransactionForm) {
            window.showTransactionForm('add', transactionData, new Date(transactionData.date));
        } else {
            // Fallback: populate chat input
            const editText = `${aiResult.description} ${aiResult.amount/1000}k`;
            this.chatInput.value = editText;
            this.chatInput.focus();
            
            const helpText = window.i18n.t('chat_edit_help');
                
            this.addMessage(helpText, 'bot');
        }
    }
    
    disableConfirmationButtons(chatId) {
        // Find and disable buttons for this specific chat message
        const buttons = this.chatContainer.querySelectorAll('button');
        buttons.forEach(button => {
            const onclick = button.getAttribute('onclick');
            if (onclick && onclick.includes(chatId)) {
                button.disabled = true;
                button.classList.add('opacity-50', 'cursor-not-allowed');
                button.classList.remove('hover:from-green-600', 'hover:to-emerald-600', 'hover:from-gray-600', 'hover:to-gray-700');
            }
        });
    }
    
    quickAdd(message) {
        if (this.chatInput) {
            this.chatInput.value = message;
            this.sendMessage();
        }
    }
    
    scrollToBottom() {
        if (this.chatContainer) {
            this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
        }
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    escapeJson(obj) {
        return JSON.stringify(obj).replace(/"/g, '&quot;');
    }
    
    getCSRFToken() {
        // Get CSRF token from Django
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        
        // Fallback: try to get from meta tag
        const csrfMeta = document.querySelector('meta[name="csrf-token"]');
        return csrfMeta ? csrfMeta.getAttribute('content') : '';
    }
    
    updateLanguage(newLanguage) {
        this.currentLanguage = newLanguage;
        // Clear existing messages and add new welcome message
        this.clearChat();
        this.addWelcomeMessage();
        
        // Update auto-confirm tooltip
        if (window.updateAutoConfirmTooltip) {
            const toggle = document.getElementById('auto-confirm-toggle');
            const isEnabled = toggle ? toggle.checked : false;
            window.updateAutoConfirmTooltip(isEnabled);
        }
    }
    
    clearChat() {
        if (this.chatContainer) {
            this.chatContainer.innerHTML = '';
        }
    }
}

// Global functions for backward compatibility with existing HTML
function sendMessage(hasVoice = false) {
    if (window.aiChat) {
        window.aiChat.sendMessage(hasVoice);
    }
}

function handleChatKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

function quickAdd(message) {
    if (window.aiChat) {
        window.aiChat.quickAdd(message);
    }
}

// CSS animation for fade in effect
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .animate-fadeInUp {
        animation: fadeInUp 0.3s ease-out;
    }
    
    .animate-pulse {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: .5;
        }
    }
    
    .delay-75 {
        animation-delay: 75ms;
    }
    
    .delay-150 {
        animation-delay: 150ms;
    }
`;
document.head.appendChild(style);

// Initialize chat when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if chat elements exist
    if (document.getElementById('chat-messages')) {
        window.aiChat = new AIChat();
        console.log('AI Chat initialized');
    }
});

// Update language when i18n changes
if (window.i18n) {
    const originalSetLanguage = window.i18n.setLanguage;
    window.i18n.setLanguage = function(lang) {
        originalSetLanguage.call(this, lang);
        if (window.aiChat) {
            window.aiChat.updateLanguage(lang);
        }
    };
}

// Listen for language change events
document.addEventListener('languageChanged', function(event) {
    if (window.aiChat) {
        window.aiChat.updateLanguage(event.detail.language);
    }
}); 