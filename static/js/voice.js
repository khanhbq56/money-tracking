/**
 * Voice Input functionality for Expense Tracker
 * Handles Web Speech API, visual feedback, and language support
 */

class VoiceInput {
    constructor() {
        this.recognition = null;
        this.isListening = false;
        this.isSupported = false;
        this.currentLanguage = 'vi-VN';
        
        this.initSpeechRecognition();
        this.setupEventListeners();
    }
    
    initSpeechRecognition() {
        // Check for browser support
        if ('webkitSpeechRecognition' in window) {
            this.recognition = new webkitSpeechRecognition();
            this.isSupported = true;
        } else if ('SpeechRecognition' in window) {
            this.recognition = new SpeechRecognition();
            this.isSupported = true;
        } else {
            console.warn('Speech Recognition not supported in this browser');
            this.showBrowserNotSupported();
            return;
        }
        
        // Configure recognition settings
        this.recognition.continuous = false;
        this.recognition.interimResults = true;
        this.recognition.maxAlternatives = 3;
        
        // Set initial language
        this.updateLanguage();
        
        // Set up event handlers
        this.recognition.onstart = () => {
            this.isListening = true;
            this.updateVoiceButton(true);
            this.showListeningFeedback();
            console.log('Voice recognition started');
        };
        
        this.recognition.onresult = (event) => {
            this.handleVoiceResult(event);
        };
        
        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            this.handleVoiceError(event.error);
            this.stopListening();
        };
        
        this.recognition.onend = () => {
            this.isListening = false;
            this.updateVoiceButton(false);
            this.hideListeningFeedback();
            console.log('Voice recognition ended');
        };
    }
    
    setupEventListeners() {
        // Language change listener
        if (window.i18n) {
            document.addEventListener('languageChanged', () => {
                this.updateLanguage();
            });
        }
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (event) => {
            // Ctrl/Cmd + Shift + V to toggle voice
            if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'V') {
                event.preventDefault();
                this.toggleListening();
            }
        });
    }
    
    updateLanguage() {
        if (!this.recognition) return;
        
        const currentLang = window.i18n ? window.i18n.currentLang : 'vi';
        
        // Map language codes to speech recognition locales
        const languageMap = {
            'vi': 'vi-VN',
            'en': 'en-US'
        };
        
        this.currentLanguage = languageMap[currentLang] || 'vi-VN';
        this.recognition.lang = this.currentLanguage;
        
        console.log(`Voice recognition language set to: ${this.currentLanguage}`);
    }
    
    toggleListening() {
        if (!this.isSupported) {
            this.showBrowserNotSupported();
            return;
        }
        
        if (this.isListening) {
            this.stopListening();
        } else {
            this.startListening();
        }
    }
    
    startListening() {
        if (!this.isSupported || this.isListening) return;
        
        try {
            // Update language before starting
            this.updateLanguage();
            
            // Start recognition
            this.recognition.start();
            
            // Set timeout to auto-stop after 30 seconds
            this.autoStopTimeout = setTimeout(() => {
                if (this.isListening) {
                    this.stopListening();
                }
            }, 30000);
            
        } catch (error) {
            console.error('Error starting voice recognition:', error);
            this.handleVoiceError('start_error');
        }
    }
    
    stopListening() {
        if (!this.recognition || !this.isListening) return;
        
        try {
            this.recognition.stop();
            
            // Clear auto-stop timeout
            if (this.autoStopTimeout) {
                clearTimeout(this.autoStopTimeout);
                this.autoStopTimeout = null;
            }
        } catch (error) {
            console.error('Error stopping voice recognition:', error);
        }
    }
    
    handleVoiceResult(event) {
        let interimTranscript = '';
        let finalTranscript = '';
        
        // Process results
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            
            if (event.results[i].isFinal) {
                finalTranscript += transcript;
            } else {
                interimTranscript += transcript;
            }
        }
        
        // Show interim results
        if (interimTranscript) {
            this.showInterimResult(interimTranscript);
        }
        
        // Process final result
        if (finalTranscript) {
            this.processFinalResult(finalTranscript.trim());
        }
    }
    
    processFinalResult(transcript) {
        console.log('Final voice transcript:', transcript);
        
        if (!transcript) {
            this.showVoiceError('empty_transcript');
            return;
        }
        
        // Update chat input with transcript
        const chatInput = document.getElementById('chat-input');
        if (chatInput) {
            chatInput.value = transcript;
            
            // Focus the input
            chatInput.focus();
        }
        
        // Auto-send if enabled and transcript seems complete
        if (this.shouldAutoSend(transcript)) {
            this.autoSendMessage(transcript);
        } else {
            // Show confirmation to send
            this.showSendConfirmation(transcript);
        }
        
        // Hide listening feedback
        this.hideListeningFeedback();
    }
    
    shouldAutoSend(transcript) {
        // Auto-send if transcript contains amount and transaction type
        const hasAmount = /\d+/.test(transcript);
        const currentLang = window.i18n ? window.i18n.currentLang : 'vi';
        
        let hasTransactionType = false;
        
        if (currentLang === 'vi') {
            const keywords = ['coffee', 'ăn', 'trưa', 'sáng', 'tối', 'tiết kiệm', 'taxi', 'grab', 'xăng'];
            hasTransactionType = keywords.some(keyword => transcript.toLowerCase().includes(keyword));
        } else {
            const keywords = ['coffee', 'lunch', 'dinner', 'breakfast', 'saving', 'taxi', 'gas'];
            hasTransactionType = keywords.some(keyword => transcript.toLowerCase().includes(keyword));
        }
        
        return hasAmount && hasTransactionType && transcript.length >= 5;
    }
    
    autoSendMessage(transcript) {
        // Send message through chat interface
        if (window.aiChat) {
            window.aiChat.sendMessage(true); // Pass voice flag
        } else if (typeof sendMessage === 'function') {
            sendMessage(true);
        }
    }
    
    showSendConfirmation(transcript) {
        const currentLang = window.i18n ? window.i18n.currentLang : 'vi';
        const message = currentLang === 'vi' 
            ? `Đã ghi nhận: "${transcript}". Nhấn Gửi để xử lý.`
            : `Recorded: "${transcript}". Press Send to process.`;
        
        this.showVoiceMessage(message, 'info');
    }
    
    handleVoiceError(error) {
        const currentLang = window.i18n ? window.i18n.currentLang : 'vi';
        let errorMessage = '';
        
        switch (error) {
            case 'no-speech':
                errorMessage = currentLang === 'vi' 
                    ? 'Không nghe thấy giọng nói. Hãy thử lại.'
                    : 'No speech detected. Please try again.';
                break;
            case 'audio-capture':
                errorMessage = currentLang === 'vi'
                    ? 'Không thể truy cập microphone. Kiểm tra quyền truy cập.'
                    : 'Cannot access microphone. Check permissions.';
                break;
            case 'not-allowed':
                errorMessage = currentLang === 'vi'
                    ? 'Quyền truy cập microphone bị từ chối.'
                    : 'Microphone access denied.';
                break;
            case 'network':
                errorMessage = currentLang === 'vi'
                    ? 'Lỗi mạng. Kiểm tra kết nối internet.'
                    : 'Network error. Check internet connection.';
                break;
            case 'start_error':
                errorMessage = currentLang === 'vi'
                    ? 'Không thể khởi động voice recognition.'
                    : 'Cannot start voice recognition.';
                break;
            case 'empty_transcript':
                errorMessage = currentLang === 'vi'
                    ? 'Không nhận diện được giọng nói. Hãy nói rõ hơn.'
                    : 'No speech recognized. Please speak more clearly.';
                break;
            default:
                errorMessage = currentLang === 'vi'
                    ? 'Lỗi voice recognition. Hãy thử lại.'
                    : 'Voice recognition error. Please try again.';
        }
        
        this.showVoiceError(errorMessage);
    }
    
    showBrowserNotSupported() {
        const currentLang = window.i18n ? window.i18n.currentLang : 'vi';
        const message = currentLang === 'vi'
            ? 'Trình duyệt không hỗ trợ voice input. Hãy sử dụng Chrome hoặc Edge.'
            : 'Browser does not support voice input. Please use Chrome or Edge.';
        
        this.showVoiceError(message);
        
        // Hide voice button if not supported
        const voiceBtn = document.getElementById('voice-btn');
        if (voiceBtn) {
            voiceBtn.style.display = 'none';
        }
    }
    
    updateVoiceButton(isListening) {
        const voiceBtn = document.getElementById('voice-btn');
        if (!voiceBtn) return;
        
        const currentLang = window.i18n ? window.i18n.currentLang : 'vi';
        
        if (isListening) {
            voiceBtn.classList.add('listening', 'bg-red-500', 'hover:bg-red-600');
            voiceBtn.classList.remove('bg-orange-500', 'hover:bg-orange-600');
            voiceBtn.innerHTML = currentLang === 'vi' ? '🎤 Đang nghe...' : '🎤 Listening...';
            voiceBtn.disabled = false;
        } else {
            voiceBtn.classList.remove('listening', 'bg-red-500', 'hover:bg-red-600');
            voiceBtn.classList.add('bg-orange-500', 'hover:bg-orange-600');
            voiceBtn.innerHTML = '🎤';
            voiceBtn.disabled = false;
        }
    }
    
    showListeningFeedback() {
        // Create listening indicator if it doesn't exist
        let indicator = document.getElementById('voice-listening-indicator');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'voice-listening-indicator';
            indicator.className = 'fixed top-4 right-4 bg-red-500 text-white px-4 py-2 rounded-lg shadow-lg z-50 flex items-center space-x-2';
            
            const currentLang = window.i18n ? window.i18n.currentLang : 'vi';
            indicator.innerHTML = `
                <div class="w-3 h-3 bg-white rounded-full animate-pulse"></div>
                <span>${currentLang === 'vi' ? 'Đang nghe...' : 'Listening...'}</span>
            `;
            
            document.body.appendChild(indicator);
        }
        
        indicator.style.display = 'flex';
        
        // Add listening animation to chat input
        const chatInput = document.getElementById('chat-input');
        if (chatInput) {
            chatInput.classList.add('border-red-500', 'ring-2', 'ring-red-200');
            chatInput.placeholder = window.i18n ? window.i18n.currentLang === 'vi' 
                ? 'Đang nghe...' 
                : 'Listening...' 
                : 'Đang nghe...';
        }
    }
    
    hideListeningFeedback() {
        // Hide listening indicator
        const indicator = document.getElementById('voice-listening-indicator');
        if (indicator) {
            indicator.style.display = 'none';
        }
        
        // Remove listening animation from chat input
        const chatInput = document.getElementById('chat-input');
        if (chatInput) {
            chatInput.classList.remove('border-red-500', 'ring-2', 'ring-red-200');
            const currentLang = window.i18n ? window.i18n.currentLang : 'vi';
            chatInput.placeholder = currentLang === 'vi' 
                ? 'VD: coffee 25k, tiết kiệm 200k...' 
                : 'E.g.: coffee 25k, saving 200k...';
        }
    }
    
    showInterimResult(transcript) {
        const chatInput = document.getElementById('chat-input');
        if (chatInput) {
            chatInput.value = transcript;
            chatInput.style.fontStyle = 'italic';
            chatInput.style.color = '#666';
        }
    }
    
    showVoiceMessage(message, type = 'info') {
        // Create or update voice message
        let messageElement = document.getElementById('voice-message');
        if (!messageElement) {
            messageElement = document.createElement('div');
            messageElement.id = 'voice-message';
            messageElement.className = 'fixed bottom-4 left-1/2 transform -translate-x-1/2 px-4 py-2 rounded-lg shadow-lg z-50 max-w-md text-center';
            document.body.appendChild(messageElement);
        }
        
        // Set styling based on type
        messageElement.className = messageElement.className.replace(/bg-\w+-\d+/, '');
        if (type === 'error') {
            messageElement.classList.add('bg-red-500', 'text-white');
        } else if (type === 'success') {
            messageElement.classList.add('bg-green-500', 'text-white');
        } else {
            messageElement.classList.add('bg-blue-500', 'text-white');
        }
        
        messageElement.textContent = message;
        messageElement.style.display = 'block';
        
        // Auto-hide after 3 seconds
        setTimeout(() => {
            if (messageElement) {
                messageElement.style.display = 'none';
            }
        }, 3000);
    }
    
    showVoiceError(message) {
        this.showVoiceMessage(message, 'error');
    }
    
    // Public methods for external use
    getIsSupported() {
        return this.isSupported;
    }
    
    getIsListening() {
        return this.isListening;
    }
    
    getCurrentLanguage() {
        return this.currentLanguage;
    }
}

// Global functions for button clicks
function toggleVoiceInput() {
    if (window.voiceInput) {
        window.voiceInput.toggleListening();
    }
}

// Initialize voice input when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize voice input
    window.voiceInput = new VoiceInput();
    
    console.log('Voice input initialized:', window.voiceInput.getIsSupported() ? 'Supported' : 'Not supported');
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VoiceInput;
} 