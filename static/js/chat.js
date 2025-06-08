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
        if (this.chatContainer && this.chatContainer.children.length <= 1) {
            this.addWelcomeMessage();
        }
    }
    
    addWelcomeMessage() {
        const welcomeText = this.currentLanguage === 'vi' 
            ? '👋 Xin chào! Hãy nói cho tôi biết giao dịch của bạn. VD: "ăn trưa 50k"'
            : '👋 Hello! Tell me about your transaction. E.g.: "coffee 25k"';
            
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
            
            const errorText = this.currentLanguage === 'vi'
                ? '❌ Xin lỗi, có lỗi xảy ra. Vui lòng thử lại!'
                : '❌ Sorry, an error occurred. Please try again!';
                
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
            messageDiv.innerHTML = `
                <div class="bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg p-3 text-sm ml-8 max-w-xs">
                    <p>${voiceIndicator}${this.escapeHtml(text)}</p>
                </div>
            `;
        } else {
            let actionButtons = '';
            if (data && data.ai_result) {
                const confirmText = this.currentLanguage === 'vi' ? '✅ Xác nhận' : '✅ Confirm';
                const editText = this.currentLanguage === 'vi' ? '✏️ Sửa' : '✏️ Edit';
                
                actionButtons = `
                    <div class="mt-3 flex flex-wrap gap-2">
                        <button 
                            onclick="window.aiChat.confirmTransaction(${this.escapeJson(data)})" 
                            class="px-3 py-1 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-lg text-xs hover:from-green-600 hover:to-emerald-600 transition-all duration-300 font-medium shadow-md hover:shadow-lg"
                        >
                            ${confirmText}
                        </button>
                        <button 
                            onclick="window.aiChat.editTransaction(${this.escapeJson(data)})" 
                            class="px-3 py-1 bg-gradient-to-r from-gray-500 to-gray-600 text-white rounded-lg text-xs hover:from-gray-600 hover:to-gray-700 transition-all duration-300 font-medium shadow-md hover:shadow-lg"
                        >
                            ${editText}
                        </button>
                    </div>
                `;
            }
            
            messageDiv.innerHTML = `
                <div class="bg-gray-100 rounded-lg p-3 text-sm mr-8 max-w-xs">
                    <p>${this.escapeHtml(text)}</p>
                    ${actionButtons}
                </div>
            `;
        }
        
        this.chatContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    showTypingIndicator() {
        if (!this.chatContainer) return;
        
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typing-indicator';
        typingDiv.className = 'chat-bubble';
        typingDiv.innerHTML = `
            <div class="bg-gray-100 rounded-lg p-3 text-sm mr-8 max-w-xs">
                <div class="flex items-center space-x-1">
                    <span>🤖</span>
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
            const successText = this.currentLanguage === 'vi'
                ? '✅ Đã thêm giao dịch thành công!'
                : '✅ Transaction added successfully!';
                
            this.addMessage(successText, 'bot');
            
            // Broadcast transaction added event
            if (window.eventBus) {
                window.eventBus.emit('transactionAdded', {
                    transaction: result.transaction,
                    source: 'chat'
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
            
            const errorText = this.currentLanguage === 'vi'
                ? '❌ Lỗi khi xác nhận giao dịch. Vui lòng thử lại!'
                : '❌ Error confirming transaction. Please try again!';
                
            this.addMessage(errorText, 'bot');
        }
    }
    
    editTransaction(data) {
        // For now, just populate the input with the transaction details for re-editing
        const aiResult = data.ai_result;
        const editText = `${aiResult.description} ${aiResult.amount/1000}k`;
        
        this.chatInput.value = editText;
        this.chatInput.focus();
        
        const helpText = this.currentLanguage === 'vi'
            ? '✏️ Hãy chỉnh sửa và gửi lại!'
            : '✏️ Please edit and send again!';
            
        this.addMessage(helpText, 'bot');
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