/**
 * Authentication Module - Login Dialog System
 * Handles Google OAuth and Demo account login
 */

class AuthManager {
    constructor() {
        this.loginModal = null;
        this.init();
    }

    init() {
        
        // Skip authentication for legal pages
        const currentPath = window.location.pathname;
        const legalPages = ['/auth/privacy/', '/auth/terms/'];
        
        if (legalPages.includes(currentPath)) {
            return;
        }
        
        // Check if user is already authenticated
        this.checkAuthenticationStatus();
        
        const isAuthenticated = this.isUserAuthenticated();
        
        // Show login modal if not authenticated
        if (!isAuthenticated) {
            this.showLoginModal();
        } else {
        }
        
        // Set up logout handlers
        this.setupLogoutHandlers();
    }

    isUserAuthenticated() {
        // Check if user is authenticated (you can check session, cookies, etc.)
        return document.body.classList.contains('authenticated');
    }

    checkAuthenticationStatus() {
        // Check URL for authentication errors
        const urlParams = new URLSearchParams(window.location.search);
        
        if (urlParams.has('error')) {
            const error = urlParams.get('error');
            let errorMessage = window.i18n.t('login_error');
            
            switch (error) {
                case 'oauth_state_mismatch':
                    errorMessage = window.i18n.t('oauth_state_mismatch_error');
                    break;
                case 'oauth_callback_failed':
                    errorMessage = window.i18n.t('oauth_callback_error');
                    break;
                case 'oauth_not_configured':
                    errorMessage = window.i18n.t('oauth_not_configured_notice');
                    break;
                case 'demo_expired':
                    errorMessage = window.i18n.t('demo_session_expired');
                    break;
            }
            
            showAlertDialog(errorMessage, { type: 'error' });
            
            // Clean URL
            window.history.replaceState({}, document.title, window.location.pathname);
        }
        
        // Check for demo expiration
        if (urlParams.has('demo_expired')) {
            showAlertDialog(window.i18n.t('demo_session_expired'), { type: 'warning' });
            window.history.replaceState({}, document.title, window.location.pathname);
        }
    }

    showLoginModal() {
        
        if (this.loginModal) {
            this.loginModal.show();
            return;
        }

        // Create login modal content
        const modalContent = this.createLoginModalContent();
        
        // Create modal using UIComponents
        this.loginModal = UIComponents.createModal('login-modal', '', modalContent, {
            size: 'medium',
            persistent: true, // Cannot close without logging in
            showCloseButton: false
        });

        // Add custom styling
        this.loginModal.element.style.zIndex = '60';
        this.loginModal.element.classList.add('login-modal');
        
        // Override ESC key behavior to prevent closing
        this.setupModalKeyHandlers();
        
        this.loginModal.show();
    }

    setupModalKeyHandlers() {
        // Override ESC key to prevent closing the login modal
        const handleKeydown = (e) => {
            if (e.key === 'Escape' && this.loginModal && this.loginModal.element.style.display !== 'none') {
                e.preventDefault();
                e.stopPropagation();
                // Show a gentle reminder instead
                showAlertDialog(window.i18n.t('login_required_notice'), { type: 'info' });
            }
        };
        
        document.addEventListener('keydown', handleKeydown, true); // Capture phase
        
        // Store handler to remove later if needed
        this.keydownHandler = handleKeydown;
    }

    cleanup() {
        // Remove event handlers to prevent memory leaks
        if (this.keydownHandler) {
            document.removeEventListener('keydown', this.keydownHandler, true);
            this.keydownHandler = null;
        }
        
        // Clean up modal reference
        if (this.loginModal) {
            this.loginModal.hide();
            this.loginModal = null;
        }
    }

    // Call cleanup when user successfully logs in
    onLoginSuccess() {
        this.cleanup();
        // Reload page to show authenticated content
        window.location.reload();
    }

    createLoginModalContent() {
        const content = document.createElement('div');
        content.className = 'login-modal-content';

        content.innerHTML = `
            <!-- Animated Background -->
            <div class="absolute inset-0 bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 rounded-lg opacity-70"></div>
            <div class="absolute inset-0 bg-white/80 backdrop-blur-sm rounded-lg"></div>
            
            <!-- Content Container -->
            <div class="relative z-10 p-6 text-center">
                <!-- Animated Header -->
                <div class="mb-6">
                    <!-- Logo Animation -->
                    <div class="relative w-16 h-16 mx-auto mb-4">
                        <div class="absolute inset-0 bg-gradient-to-r from-purple-500 via-pink-500 to-blue-500 rounded-full animate-pulse"></div>
                        <div class="absolute inset-1 bg-white rounded-full flex items-center justify-center">
                            <div class="text-2xl animate-bounce">💰</div>
                        </div>
                        <!-- Floating elements -->
                        <div class="absolute -top-1 -right-1 w-3 h-3 bg-yellow-400 rounded-full animate-ping"></div>
                        <div class="absolute -bottom-1 -left-1 w-2 h-2 bg-green-400 rounded-full animate-pulse delay-500"></div>
                    </div>
                    
                    <h2 class="text-2xl font-bold bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 bg-clip-text text-transparent mb-2">
                        ${window.i18n.t('welcome_login')}
                    </h2>
                    <p class="text-base text-gray-600 font-medium">${window.i18n.t('login_subtitle')}</p>
                </div>

                <!-- Login Options -->
                <div class="space-y-4 mb-6">
                    <!-- Google Login Button -->
                    <div id="google-login-container"></div>
                    
                    <!-- Divider -->
                    <div class="flex items-center my-4">
                        <div class="flex-1 border-t border-gray-200"></div>
                        <div class="px-3 text-sm text-gray-500 font-medium">${window.i18n.t('or')}</div>
                        <div class="flex-1 border-t border-gray-200"></div>
                    </div>
                    
                    <!-- Demo Account Button -->
                    <div id="demo-login-container"></div>
                </div>

                <!-- Benefits Section -->
                <div class="bg-gradient-to-br from-emerald-50 via-blue-50 to-purple-50 border border-transparent shadow-md p-5 rounded-xl mb-6 relative overflow-hidden">
                    <!-- Background decoration -->
                    <div class="absolute inset-0 bg-gradient-to-br from-emerald-100/20 via-blue-100/20 to-purple-100/20"></div>
                    <div class="absolute top-0 right-0 w-20 h-20 bg-gradient-to-br from-purple-200 to-pink-200 rounded-full opacity-30 transform translate-x-10 -translate-y-10"></div>
                    
                    <div class="relative z-10">
                        <h3 class="text-sm font-bold bg-gradient-to-r from-emerald-600 to-blue-600 bg-clip-text text-transparent mb-3 flex items-center">
                            <span class="w-5 h-5 bg-gradient-to-r from-emerald-500 to-blue-500 rounded-full flex items-center justify-center mr-2">
                                <i class="fas fa-star text-white text-xs"></i>
                            </span>
                            ${window.i18n.t('login_benefits_title')}
                        </h3>
                        <div class="space-y-2">
                            <div class="flex items-center group">
                                <div class="w-6 h-6 bg-gradient-to-r from-emerald-400 to-emerald-500 rounded-full flex items-center justify-center mr-3 group-hover:scale-110 transition-transform">
                                    <i class="fas fa-sync-alt text-white text-xs"></i>
                                </div>
                                <span class="text-xs font-medium text-gray-700">${window.i18n.t('sync_across_devices')}</span>
                            </div>
                            <div class="flex items-center group">
                                <div class="w-6 h-6 bg-gradient-to-r from-blue-400 to-blue-500 rounded-full flex items-center justify-center mr-3 group-hover:scale-110 transition-transform">
                                    <i class="fas fa-shield-alt text-white text-xs"></i>
                                </div>
                                <span class="text-xs font-medium text-gray-700">${window.i18n.t('secure_data_backup')}</span>
                            </div>
                            <div class="flex items-center group">
                                <div class="w-6 h-6 bg-gradient-to-r from-purple-400 to-purple-500 rounded-full flex items-center justify-center mr-3 group-hover:scale-110 transition-transform">
                                    <i class="fas fa-chart-line text-white text-xs"></i>
                                </div>
                                <span class="text-xs font-medium text-gray-700">${window.i18n.t('advanced_analytics')}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Legal Acceptance -->
                <div class="space-y-4">
                    <label class="flex items-start space-x-2 text-sm text-gray-600 cursor-pointer hover:text-gray-800 transition-colors">
                        <input type="checkbox" id="legal-acceptance" class="mt-1 rounded border-gray-300 text-purple-600 focus:ring-purple-500 focus:ring-2" checked>
                        <span class="leading-relaxed text-left">
                            ${window.i18n.t('legal_acceptance')
                                .replace('{terms}', `<a href="/auth/terms/" target="_blank" class="text-purple-600 hover:text-purple-800 font-semibold underline decoration-2 decoration-purple-200 hover:decoration-purple-400 transition-all">${window.i18n.t('terms_of_service')}</a>`)
                                .replace('{privacy}', `<a href="/auth/privacy/" target="_blank" class="text-purple-600 hover:text-purple-800 font-semibold underline decoration-2 decoration-purple-200 hover:decoration-purple-400 transition-all">${window.i18n.t('privacy_policy')}</a>`)
                            }
                        </span>
                    </label>
                </div>

                <!-- Loading State -->
                <div id="login-loading" class="hidden">
                    <div class="flex items-center justify-center space-x-3 py-4">
                        <div class="animate-spin rounded-full h-6 w-6 border-4 border-purple-200 border-t-purple-600"></div>
                        <div class="flex flex-col">
                            <p class="text-gray-700 font-medium text-sm" id="login-status">${window.i18n.t('logging_in')}</p>
                            <p class="text-xs text-gray-500">${window.i18n.t('please_wait')}</p>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Add buttons after content is created
        setTimeout(() => {
            this.addLoginButtons(content);
        }, 0);

        return content;
    }

    addLoginButtons(container) {
        // Google Login Button
        const googleContainer = container.querySelector('#google-login-container');
        const googleBtn = UIComponents.createButton(
            window.i18n.t('login_with_google'),
            'primary',
            () => this.handleGoogleLogin(),
            { 
                fullWidth: true,
                disabled: false // Enabled by default since legal checkbox is checked
            }
        );
        
        // Add Google icon manually
        const googleIcon = document.createElement('i');
        googleIcon.className = 'fab fa-google mr-3 text-lg';
        googleBtn.insertBefore(googleIcon, googleBtn.firstChild);
        
        googleBtn.classList.add('google-login-btn', 'h-12', 'text-base', 'shadow-lg', 'hover:shadow-xl', 'transition-all', 'duration-300', 'font-semibold');
        googleBtn.style.background = 'linear-gradient(135deg, #4285f4 0%, #34a853 50%, #fbbc05 75%, #ea4335 100%)';
        googleContainer.appendChild(googleBtn);

        // Demo Login Button  
        const demoContainer = container.querySelector('#demo-login-container');
        const demoBtn = UIComponents.createButton(
            window.i18n.t('try_demo_account'),
            'neutral',
            () => this.handleDemoLogin(),
            { 
                fullWidth: true,
                disabled: false // Enabled by default since legal checkbox is checked
            }
        );
        
        // Add rocket icon manually
        const rocketIcon = document.createElement('i');
        rocketIcon.className = 'fas fa-rocket mr-3 text-lg';
        demoBtn.insertBefore(rocketIcon, demoBtn.firstChild);
        
        demoBtn.classList.add('demo-login-btn', 'h-12', 'text-base', 'bg-gradient-to-r', 'from-gray-600', 'to-gray-700', 'hover:from-gray-700', 'hover:to-gray-800', 'shadow-lg', 'hover:shadow-xl', 'transition-all', 'duration-300', 'font-semibold');
        demoContainer.appendChild(demoBtn);

        // Set up legal acceptance handler
        const legalCheckbox = container.querySelector('#legal-acceptance');
        if (legalCheckbox) {
            legalCheckbox.addEventListener('change', (e) => {
                const isChecked = e.target.checked;
                googleBtn.disabled = !isChecked;
                demoBtn.disabled = !isChecked;
                
                // Visual feedback
                if (isChecked) {
                    googleBtn.classList.remove('opacity-50', 'cursor-not-allowed');
                    demoBtn.classList.remove('opacity-50', 'cursor-not-allowed');
                    googleBtn.classList.add('hover:scale-105');
                    demoBtn.classList.add('hover:scale-105');
                } else {
                    googleBtn.classList.add('opacity-50', 'cursor-not-allowed');
                    demoBtn.classList.add('opacity-50', 'cursor-not-allowed');
                    googleBtn.classList.remove('hover:scale-105');
                    demoBtn.classList.remove('hover:scale-105');
                }
            });
            
            // Since checkbox is now checked by default, enable buttons initially
            googleBtn.disabled = false;
            demoBtn.disabled = false;
            googleBtn.classList.add('hover:scale-105');
            demoBtn.classList.add('hover:scale-105');
        }
    }

    handleGoogleLogin() {
        if (!this.validateLegalAcceptance()) return;
        
        this.showLoadingState(window.i18n.t('logging_in'));
        
        // Redirect to Google OAuth
        window.location.href = '/auth/oauth/google/';
    }

    async handleDemoLogin() {
        if (!this.validateLegalAcceptance()) return;
        
        this.showLoadingState(window.i18n.t('creating_demo'));
        
        try {
            const response = await fetch('/auth/demo/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    legal_accepted: true
                })
            });

            const data = await response.json();

            if (data.success) {
                showAlertDialog(data.message, { type: 'success' });
                
                // Clean up and refresh page to load authenticated state
                setTimeout(() => {
                    this.onLoginSuccess();
                }, 1500);
            } else {
                throw new Error(data.error || 'Demo login failed');
            }
            
        } catch (error) {
            console.error('Demo login error:', error);
            showAlertDialog(window.i18n.t('demo_login_error'), { type: 'error' });
        }
    }

    validateLegalAcceptance() {
        const legalCheckbox = document.querySelector('#legal-acceptance');
        if (!legalCheckbox || !legalCheckbox.checked) {
            showAlertDialog(window.i18n.t('must_accept_legal'), { type: 'warning' });
            return false;
        }
        return true;
    }

    showLoadingState(message) {
        const container = document.querySelector('.login-modal-content');
        const loginOptions = container.querySelector('#google-login-container').parentElement;
        const loadingDiv = container.querySelector('#login-loading');
        const statusText = container.querySelector('#login-status');

        loginOptions.style.display = 'none';
        loadingDiv.classList.remove('hidden');
        statusText.textContent = message;
        
        this.isAuthenticating = true;
    }

    hideLoadingState() {
        const container = document.querySelector('.login-modal-content');
        const loginOptions = container.querySelector('#google-login-container').parentElement;
        const loadingDiv = container.querySelector('#login-loading');

        loginOptions.style.display = 'block';
        loadingDiv.classList.add('hidden');
        
        this.isAuthenticating = false;
    }

    setupLogoutHandlers() {
        // Add logout button to header if user is authenticated
        if (this.isUserAuthenticated()) {
            this.addLogoutButton();
            this.setupDemoCountdown();
            this.setupUserProfileFeatures();
            this.setupUserDropdown();
        }
    }

    addLogoutButton() {
        // Check if logout button already exists
        if (document.getElementById('logout-btn')) {
            return;
        }

        // Create logout button with enhanced styling for dropdown menu
        const logoutBtn = document.createElement('button');
        logoutBtn.id = 'logout-btn';
        logoutBtn.className = 'w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center space-x-2 rounded-lg transition-colors';
        logoutBtn.innerHTML = `
            <i class="fas fa-sign-out-alt w-4"></i>
            <span>${window.i18n.t('logout')}</span>
        `;
        logoutBtn.onclick = () => this.handleLogout();

        // Try multiple selectors for logout button placement
        const navArea = document.querySelector('.header-actions') || 
                       document.querySelector('.nav-area') ||
                       document.querySelector('.user-actions') ||
                       document.querySelector('[data-user-actions]');
        
        if (navArea) {
            navArea.appendChild(logoutBtn);
        } else {
            // Fallback: add to top right corner
            console.warn('⚠️ Header actions area not found, adding logout button to body');
            const fallbackContainer = document.createElement('div');
            fallbackContainer.className = 'fixed top-4 right-4 z-50';
            const fallbackBtn = UIComponents.createButton(
                `<i class="fas fa-sign-out-alt mr-2"></i>${window.i18n.t('logout')}`, 
                'danger', 
                () => this.handleLogout(),
                { small: true }
            );
            fallbackBtn.id = 'logout-btn-fallback';
            fallbackContainer.appendChild(fallbackBtn);
            document.body.appendChild(fallbackContainer);
        }
    }

    setupUserDropdown() {
        const userMenuButton = document.getElementById('user-menu-button');
        const userDropdown = document.getElementById('user-dropdown');
        const headerActions = document.querySelector('.header-actions');

        if (!userMenuButton || !userDropdown || !headerActions) {
            console.error('❌ Missing user dropdown elements');
            return;
        }

        // Check if logout button already exists
        let logoutBtn = document.getElementById('logout-btn');
        if (!logoutBtn) {
            // Create logout button manually
            logoutBtn = document.createElement('button');
            logoutBtn.className = 'w-full text-left px-4 py-2 text-sm text-red-700 hover:bg-red-50 flex items-center space-x-2 rounded-lg transition-colors';
            logoutBtn.innerHTML = `
                <i class="fas fa-sign-out-alt w-4"></i>
                <span>${window.i18n.t('logout')}</span>
            `;
            logoutBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.handleLogout();
            });
            logoutBtn.id = 'logout-btn';
            headerActions.appendChild(logoutBtn);
        }

        // Toggle dropdown
        userMenuButton.addEventListener('click', (e) => {
            e.stopPropagation();
            userDropdown.classList.toggle('hidden');
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!userMenuButton.contains(e.target) && !userDropdown.contains(e.target)) {
                userDropdown.classList.add('hidden');
            }
        });

        // Close dropdown on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                userDropdown.classList.add('hidden');
            }
        });
    }

    async handleLogout() {
        try {
            // Show confirmation dialog
            const confirmed = await this.showLogoutConfirmation();
            
            if (!confirmed) {
                return;
            }

            // Send logout request
            const response = await fetch('/auth/logout/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                credentials: 'same-origin'
            });

            if (response.ok) {
                const data = await response.json();
                
                if (data.success) {
                    showAlertDialog(window.i18n.t('logout_success'), { type: 'success' });
                    
                    // Redirect after short delay
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                } else {
                    showAlertDialog(data.message || window.i18n.t('logout_error'), { type: 'error' });
                }
            } else {
                showAlertDialog(window.i18n.t('logout_error'), { type: 'error' });
            }
        } catch (error) {
            console.error('❌ Logout error:', error);
            showAlertDialog(window.i18n.t('logout_error'), { type: 'error' });
        }
    }

    showLogoutConfirmation() {
        return new Promise((resolve) => {
            // Check if showConfirmationDialog exists
            if (typeof window.showConfirmationDialog !== 'function') {
                console.error('❌ showConfirmationDialog function not found, using fallback');
                const confirmed = confirm(window.i18n.t('logout_confirm_message'));
                resolve(confirmed);
                return;
            }

            // IMPORTANT: showConfirmationDialog uses callback-style API, not Promise-style
            // Signature: showConfirmationDialog(message, onConfirm, options)
            // - message: string - the confirmation message
            // - onConfirm: function - callback when user confirms
            // - options: object - { title, confirmText, cancelText, onCancel }
            window.showConfirmationDialog(
                window.i18n.t('logout_confirm_message'),
                () => {
                    // User confirmed logout
                    resolve(true);
                },
                {
                    title: window.i18n.t('logout_confirm'),
                    confirmText: window.i18n.t('logout'),
                    cancelText: window.i18n.t('cancel'),
                    onCancel: () => {
                        // User cancelled logout
                        resolve(false);
                    }
                }
            );
        });
    }

    showTerms() {
        // Show terms of service modal
        const termsContent = document.createElement('div');
        termsContent.innerHTML = `
            <div class="prose max-w-none">
                <h3>Terms of Service</h3>
                <p>By using Money Tracker, you agree to the following terms:</p>
                <ul>
                    <li>This is a personal finance tracking application</li>
                    <li>Demo accounts are temporary and expire after 24 hours</li>
                    <li>You are responsible for the accuracy of your financial data</li>
                    <li>We reserve the right to terminate accounts for misuse</li>
                    <li>The service is provided "as is" without warranties</li>
                </ul>
                <p>For questions, please contact our support team.</p>
            </div>
        `;

        const termsModal = UIComponents.createModal(
            'terms-modal',
            window.i18n.t('terms_of_service'),
            termsContent
        );
        termsModal.show();
    }

    showPrivacyPolicy() {
        // Show privacy policy modal
        const privacyContent = document.createElement('div');
        privacyContent.innerHTML = `
            <div class="prose max-w-none">
                <h3>Privacy Policy</h3>
                <h4>Data Collection</h4>
                <p>We collect minimal information:</p>
                <ul>
                    <li>Email address (for authentication)</li>
                    <li>Name and profile picture (from Google OAuth)</li>
                    <li>Financial transaction data you input</li>
                </ul>
                
                <h4>Data Usage</h4>
                <ul>
                    <li>To provide financial tracking services</li>
                    <li>To identify your account and transactions</li>
                    <li>To provide AI-powered insights (optional)</li>
                </ul>
                
                <h4>Data Protection</h4>
                <ul>
                    <li>Data is encrypted in transit and at rest</li>
                    <li>No data is shared with third parties</li>
                    <li>Demo accounts are automatically deleted after 24 hours</li>
                    <li>You can delete your account and data at any time</li>
                </ul>
            </div>
        `;

        const privacyModal = UIComponents.createModal(
            'privacy-modal',
            window.i18n.t('privacy_policy'),
            privacyContent
        );
        privacyModal.show();
    }

    getCSRFToken() {
        // Try multiple methods to get CSRF token
        let token = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                   document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || 
                   document.querySelector('input[name="csrfmiddlewaretoken"]')?.value ||
                   '';
        
        // If no token found, try to get from cookie
        if (!token) {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                const [name, value] = cookie.trim().split('=');
                if (name === 'csrftoken') {
                    token = value;
                    break;
                }
            }
        }
        
        return token;
    }

    setupDemoCountdown() {
        const demoCountdown = document.getElementById('demo-countdown');
        if (!demoCountdown) return;

        const expiresAt = demoCountdown.getAttribute('data-expires');
        if (!expiresAt) return;

        const updateCountdown = () => {
            const now = new Date().getTime();
            const expiry = new Date(expiresAt).getTime();
            const distance = expiry - now;

            if (distance < 0) {
                demoCountdown.textContent = window.i18n.t('expired');
                demoCountdown.className += ' text-red-600 font-semibold';
                return;
            }

            const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((distance % (1000 * 60)) / 1000);

            demoCountdown.textContent = `${hours}h ${minutes}m ${seconds}s`;
            
            // Color coding based on time remaining
            if (distance < 30 * 60 * 1000) { // Less than 30 minutes
                demoCountdown.className = demoCountdown.className.replace(/text-\w+-\d+/, 'text-red-600 font-semibold animate-pulse');
            } else if (distance < 60 * 60 * 1000) { // Less than 1 hour
                demoCountdown.className = demoCountdown.className.replace(/text-\w+-\d+/, 'text-yellow-600 font-semibold');
            } else {
                demoCountdown.className = demoCountdown.className.replace(/text-\w+-\d+/, 'text-gray-600');
            }
        };

        updateCountdown();
        setInterval(updateCountdown, 1000);
    }

    setupUserProfileFeatures() {
        // Add user profile dropdown functionality if needed
        const userAvatar = document.querySelector('[data-user-avatar]');
        if (userAvatar) {
            userAvatar.addEventListener('click', () => {
                this.showUserMenu();
            });
        }

        // Add keyboard shortcut for quick logout
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.shiftKey && e.key === 'L') {
                e.preventDefault();
                this.handleLogout();
            }
        });
    }

    showUserMenu() {
        // Future: Add user profile dropdown menu
        console.log('User menu clicked - can add profile options here');
    }
}

// Initialize AuthManager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Wait for i18n to be ready
    const initAuth = () => {
        if (window.i18n && typeof window.i18n.t === 'function') {
            window.authManager = new AuthManager();
        } else {
            setTimeout(initAuth, 100);
        }
    };
    
    initAuth();
});

// Export for global access (will be set after initialization)
window.authManager = null;

// Global functions for user menu actions
function showUserProfile() {
    if (typeof showAlertDialog === 'function') {
        showAlertDialog(window.i18n.t('feature_coming_soon'), { 
            type: 'info',
            title: window.i18n.t('user_profile')
        });
    } else {
        alert('User Profile feature coming soon!');
    }
}

function showSettings() {
    if (typeof showAlertDialog === 'function') {
        showAlertDialog(window.i18n.t('feature_coming_soon'), { 
            type: 'info',
            title: window.i18n.t('settings')
        });
    } else {
        alert('Settings feature coming soon!');
    }
} 