/**
 * Future Me Simulator - Financial Projection Calculator
 * Phase 8 Implementation
 */
class FutureMe {
    constructor() {
        this.modal = null;
        this.timelineSlider = null;
        this.currentProjection = null;
        this.isLoading = false;
        
        this.initializeElements();
        this.bindEvents();
    }
    
    initializeElements() {
        // Modal will be created dynamically when opened
        this.modal = null;
        this.timelineSlider = null;
    }
    
    bindEvents() {
        // Escape key to close modal
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modal && !this.modal.classList.contains('hidden')) {
                this.close();
            }
        });
        
        // Timeline slider change
        if (this.timelineSlider) {
            this.timelineSlider.addEventListener('input', () => {
                this.updateProjection();
            });
        }
    }
    
    createModal() {
        // Get current language translations
        const t = (key) => window.i18n.t(key);
        
        const modalHTML = `
            <!-- Future Me Modal -->
            <div id="future-me-modal" class="hidden fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
                <div class="bg-white rounded-2xl max-w-7xl w-full max-h-[90vh] shadow-2xl flex flex-col">
                    <!-- Modal Header - Fixed at top -->
                    <div class="bg-gradient-to-r from-purple-600 to-pink-600 p-6 text-white rounded-t-2xl flex-shrink-0">
                        <div class="flex justify-between items-center">
                            <div>
                                <h3 class="text-xl font-bold">🔮 <span data-i18n="future_me">${t('future_me', 'Future Me Simulator')}</span></h3>
                                <p class="text-white/80 text-sm mt-1" data-i18n="future_me_subtitle">${t('future_me_subtitle', 'Dự báo tài chính thông minh dựa trên dữ liệu thực')}</p>
                            </div>
                            <button onclick="window.futureMe.close()" class="text-white hover:text-gray-200 transition-colors z-10 relative">
                                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                                </svg>
                            </button>
                        </div>
                    </div>
                    
                    <!-- Modal Content - Scrollable body -->
                    <div class="p-6 overflow-y-auto custom-scrollbar flex-1">
                        <!-- Loading State -->
                        <div id="future-loading" class="hidden text-center py-16">
                            <div class="relative">
                                <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-gray-200 border-t-purple-600"></div>
                                <div class="absolute inset-0 flex items-center justify-center">
                                    <div class="text-2xl">🔮</div>
                                </div>
                            </div>
                            <p class="mt-6 text-gray-600 text-lg font-medium" data-i18n="analyzing_financial_data">${t('analyzing_financial_data', 'Đang phân tích dữ liệu tài chính...')}</p>
                            <p class="mt-2 text-gray-500 text-sm" data-i18n="please_wait">${t('please_wait', 'Vui lòng chờ trong giây lát')}</p>
                        </div>
                        
                        <!-- Main Content -->
                        <div id="future-content" class="space-y-6">
                            <!-- Timeline Section -->
                            <div class="bg-gradient-to-br from-gray-50 to-blue-50 rounded-xl p-6 border border-gray-200">
                                <div class="text-center">
                                    <label class="block text-sm font-semibold text-gray-700 mb-3">
                                        📅 <span data-i18n="select_forecast_period">${t('select_forecast_period', 'Chọn khoảng thời gian dự báo')}</span>
                                    </label>
                                    <input 
                                        type="range" 
                                        id="timeline-slider" 
                                        min="1" 
                                        max="60" 
                                        value="12" 
                                        class="w-full h-3 bg-gradient-to-r from-purple-200 to-pink-200 rounded-lg appearance-none cursor-pointer slider"
                                    >
                                    <div class="flex justify-between text-xs text-gray-500 mt-2">
                                        <span data-i18n="one_month">${t('one_month', '1 tháng')}</span>
                                        <span data-i18n="five_years">${t('five_years', '5 năm')}</span>
                                    </div>
                                    <p class="text-center mt-4 font-bold text-2xl text-purple-700 transition-all duration-300" id="timeline-display">12 <span data-i18n="months">${t('months', 'tháng')}</span></p>
                                </div>
                            </div>

                            <!-- Projections Grid -->
                            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                                <!-- Expense Projection -->
                                <div class="text-center p-6 bg-gradient-to-br from-red-50 to-pink-50 rounded-xl border border-red-200 transition-all duration-300 hover:shadow-lg">
                                    <div class="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-3">
                                        <span class="text-2xl">🔴</span>
                                    </div>
                                    <h4 class="font-semibold text-red-700 mb-2" data-i18n="expected_expense">${t('expected_expense', 'Chi Tiêu Dự Kiến')}</h4>
                                    <p class="text-2xl font-black text-red-600" id="future-expense">-0₫</p>
                                    <p class="text-xs text-red-500 mt-1" id="expense-monthly">0₫/tháng</p>
                                </div>
                                
                                <!-- Saving Projection -->
                                <div class="text-center p-6 bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl border border-green-200 transition-all duration-300 hover:shadow-lg">
                                    <div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                                        <span class="text-2xl">🟢</span>
                                    </div>
                                    <h4 class="font-semibold text-green-700 mb-2" data-i18n="expected_saving">${t('expected_saving', 'Tiết Kiệm Dự Kiến')}</h4>
                                    <p class="text-2xl font-black text-green-600" id="future-saving">+0₫</p>
                                    <p class="text-xs text-green-500 mt-1" id="saving-monthly">0₫/tháng</p>
                                </div>
                                
                                <!-- Investment Projection -->
                                <div class="text-center p-6 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-200 transition-all duration-300 hover:shadow-lg">
                                    <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                                        <span class="text-2xl">🔵</span>
                                    </div>
                                    <h4 class="font-semibold text-blue-700 mb-2" data-i18n="expected_investment">${t('expected_investment', 'Đầu Tư Dự Kiến')}</h4>
                                    <p class="text-2xl font-black text-blue-600" id="future-investment">+0₫</p>
                                    <p class="text-xs text-blue-500 mt-1" id="investment-monthly">0₫/tháng</p>
                                </div>
                                
                                <!-- Net Total - Always Purple as requested -->
                                <div class="text-center p-6 bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl border border-purple-200 transition-all duration-300 hover:shadow-lg">
                                    <div class="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
                                        <span class="text-2xl">📊</span>
                                    </div>
                                    <h4 class="font-semibold text-purple-700 mb-2" data-i18n="expected_total">${t('expected_total', 'Tổng Dự Kiến')}</h4>
                                    <p class="text-2xl font-black text-purple-600" id="future-net">+0₫</p>
                                    <p class="text-xs text-purple-500 mt-1" data-i18n="net_amount">${t('net_amount', 'Số dư ròng')}</p>
                                </div>
                            </div>

                            <!-- Scenarios Section -->
                            <div class="bg-gradient-to-r from-purple-50 to-pink-50 p-8 rounded-xl border border-purple-200">
                                <h4 class="font-semibold text-gray-800 mb-4 flex items-center">
                                    💡 <span data-i18n="scenarios_what_if">${t('scenarios_what_if', 'Scenarios "What if" - Các kịch bản tối ưu')}</span>
                                </h4>
                                <div id="scenarios-list">
                                    <!-- Scenarios will be populated here -->
                                </div>
                            </div>

                            <!-- Goals Section -->
                            <div class="bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200 rounded-xl">
                                <div class="p-8">
                                    <div class="text-center mb-6">
                                        <div class="text-4xl mb-3">🎯</div>
                                        <h4 class="font-semibold text-gray-800 mb-2" data-i18n="goal_calculator">${t('goal_calculator', 'Goal Calculator - Máy tính mục tiêu')}</h4>
                                        <p class="text-sm text-gray-600" data-i18n="goal_calculator_desc">${t('goal_calculator_desc', 'Với tốc độ tiết kiệm hiện tại, bạn có thể đạt được:')}</p>
                                    </div>
                                    
                                    <div id="goals-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                        <!-- Goals will be populated here -->
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }
    
    async open() {
        // Remove existing modal if present
        const existingModal = document.getElementById('future-me-modal');
        if (existingModal) {
            existingModal.remove();
        }
        
        // Create fresh modal with current language
        this.createModal();
        this.modal = document.getElementById('future-me-modal');
        this.timelineSlider = document.getElementById('timeline-slider');
        
        // Re-bind timeline slider event
        if (this.timelineSlider) {
            this.timelineSlider.addEventListener('input', () => {
                this.updateProjection();
            });
        }
        
        this.modal.classList.remove('hidden');
        this.showLoading(true);
        
        // Load initial projection
        await this.updateProjection();
        
        // Force net total to be purple after data loads - additional protection
        this.enforceNetTotalStyling();
        
        this.showLoading(false);
    }
    
    close() {
        this.modal.classList.add('hidden');
    }
    
    showLoading(show) {
        const loading = document.getElementById('future-loading');
        const content = document.getElementById('future-content');
        
        if (show) {
            loading.classList.remove('hidden');
            content.classList.add('hidden');
        } else {
            loading.classList.add('hidden');
            content.classList.remove('hidden');
        }
    }
    
    async updateProjection() {
        if (this.isLoading) return;
        
        this.isLoading = true;
        const months = parseInt(this.timelineSlider.value);
        
        // Update timeline display
        this.updateTimelineDisplay(months);
        
        try {
            const response = await fetch(`/api/future-projection/?months=${months}`);
            const result = await response.json();
            
            if (result.success) {
                this.currentProjection = result.data;
                this.renderProjection(result.data);
            } else {
                throw new Error(result.error || 'Unknown error');
            }
        } catch (error) {
            console.error('Error fetching projection:', error);
            this.showError('Không thể tải dữ liệu dự báo. Vui lòng thử lại.');
        } finally {
            this.isLoading = false;
        }
    }
    
    updateTimelineDisplay(months) {
        const display = document.getElementById('timeline-display');
        
        if (months < 12) {
            const monthsText = window.i18n.t('months');
            display.textContent = `${months} ${monthsText}`;
        } else {
            const years = Math.floor(months / 12);
            const remainingMonths = months % 12;
            const yearsText = window.i18n.t('years');
            const monthsText = window.i18n.t('months');
            
            if (remainingMonths === 0) {
                display.textContent = `${years} ${yearsText}`;
            } else {
                display.textContent = `${years} ${yearsText} ${remainingMonths} ${monthsText}`;
            }
        }
    }
    
    renderProjection(data) {
        // Update base projections
        this.updateProjectionCards(data.base_projections);
        
        // Update scenarios
        this.updateScenarios(data.scenarios);
        
        // Update goals
        this.updateGoals(data.goals);
    }
    
    updateProjectionCards(projections) {
        // Get translation for "month"
        const monthText = window.i18n.t('per_month');
        
        // Expense
        document.getElementById('future-expense').textContent = projections.expense.formatted;
        document.getElementById('expense-monthly').textContent = `${projections.expense.monthly_avg.toLocaleString()}₫${monthText}`;
        
        // Saving
        document.getElementById('future-saving').textContent = projections.saving.formatted;
        document.getElementById('saving-monthly').textContent = `${projections.saving.monthly_avg.toLocaleString()}₫${monthText}`;
        
        // Investment
        document.getElementById('future-investment').textContent = projections.investment.formatted;
        document.getElementById('investment-monthly').textContent = `${projections.investment.monthly_avg.toLocaleString()}₫${monthText}`;
        
        // Net total
        const netElement = document.getElementById('future-net');
        netElement.textContent = projections.net.formatted;
        
        // Keep net total always purple as requested by user
        // Force purple color and remove any other color classes that might interfere
        netElement.className = 'text-2xl font-black text-purple-600';
        
        // Also ensure the parent card maintains purple styling
        const netCard = netElement.closest('.text-center');
        if (netCard) {
            netCard.className = 'text-center p-6 bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl border border-purple-200 transition-all duration-300 hover:shadow-lg';
        }
    }
    
    updateScenarios(scenarios) {
        const container = document.getElementById('scenarios-list');
        container.innerHTML = '';
        
        // Use grid layout for scenarios
        container.className = 'grid grid-cols-1 md:grid-cols-2 gap-4';
        
        scenarios.forEach(scenario => {
            const scenarioElement = document.createElement('div');
            scenarioElement.className = 'p-4 bg-white/70 rounded-lg border border-white/50 hover:bg-white/90 transition-all duration-300 hover:shadow-md';
            
            const impactColor = scenario.impact === 'investment' ? 'text-blue-600' : 'text-green-600';
            
            // Get translated text
            const title = window.i18n.t(scenario.title_key);
            const description = window.i18n.t(scenario.description_key);
            
            scenarioElement.innerHTML = `
                <div class="flex justify-between items-start">
                    <div class="flex-1">
                        <span class="font-semibold text-gray-800 text-sm">${title}</span>
                        <p class="text-xs text-gray-600 mt-1 leading-relaxed">${description}</p>
                    </div>
                    <span class="font-bold ${impactColor} text-sm ml-2 whitespace-nowrap">${scenario.formatted}</span>
                </div>
            `;
            
            container.appendChild(scenarioElement);
        });
    }
    
    updateGoals(goals) {
        const container = document.getElementById('goals-grid');
        container.innerHTML = '';
        
        // Show top 6 most achievable goals
        const topGoals = goals.slice(0, 6);
        
        topGoals.forEach(goal => {
            const goalElement = document.createElement('div');
            goalElement.className = `p-4 bg-white rounded-lg border ${goal.achievable ? 'border-green-200' : 'border-red-200'} text-center`;
            
            const timeColor = goal.achievable ? 'text-green-600' : 'text-red-600';
            const bgColor = goal.achievable ? 'bg-green-50' : 'bg-red-50';
            
            // Get translated text with substitutions
            const title = window.i18n.t(goal.title_key);
            let timeText = '';
            if (goal.time_text_key) {
                if (goal.time_text_data && Object.keys(goal.time_text_data).length > 0) {
                    // Use interpolation for time text with data
                    timeText = window.i18n.t(goal.time_text_key, goal.time_text_data);
                } else {
                    timeText = window.i18n.t(goal.time_text_key);
                }
            } else {
                timeText = '';
            }
            
            goalElement.innerHTML = `
                <div class="text-2xl mb-2">${goal.icon}</div>
                <h5 class="font-semibold text-sm text-gray-800 mb-1">${title}</h5>
                <p class="text-xs text-gray-600 mb-2">${goal.formatted_price}</p>
                <div class="px-2 py-1 ${bgColor} rounded-lg">
                    <p class="text-xs font-semibold ${timeColor}">${timeText}</p>
                </div>
            `;
            
            container.appendChild(goalElement);
        });
    }
    
    enforceNetTotalStyling() {
        // This function ensures the net total always stays purple
        const netElement = document.getElementById('future-net');
        const netCard = netElement?.closest('.text-center');
        
        if (netElement) {
            // Force purple styling
            netElement.className = 'text-2xl font-black text-purple-600';
            
            // Remove any conflicting styles that might have been added by other scripts
            netElement.style.color = '';
            
            if (netCard) {
                netCard.className = 'text-center p-6 bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl border border-purple-200 transition-all duration-300 hover:shadow-lg';
            }
            
            // Set up a protection observer to prevent other scripts from changing this
            if (!this.netElementObserver && window.MutationObserver) {
                this.netElementObserver = new MutationObserver((mutations) => {
                    mutations.forEach((mutation) => {
                        if (mutation.type === 'attributes' && 
                            (mutation.attributeName === 'class' || mutation.attributeName === 'style')) {
                            // Reset to purple if changed by another script
                            const target = mutation.target;
                            if (target.id === 'future-net' && 
                                !target.className.includes('text-purple-600')) {
                                target.className = 'text-2xl font-black text-purple-600';
                                target.style.color = '';
                            }
                        }
                    });
                });
                
                this.netElementObserver.observe(netElement, {
                    attributes: true,
                    attributeFilter: ['class', 'style']
                });
            }
        }
    }

    showError(message) {
        // Use toast notification instead of showing error in modal content
        if (window.app && typeof window.app.showNotification === 'function') {
            window.app.showNotification(message, 'error');
        } else if (window.showAlertDialog) {
            window.showAlertDialog(message, { type: 'error' });
        } else {
            // Fallback to showing error in modal content
            const content = document.getElementById('future-content');
            content.innerHTML = `
                <div class="text-center py-16">
                    <div class="bg-red-50 border border-red-200 rounded-2xl p-8 max-w-md mx-auto">
                        <div class="text-6xl mb-6">😔</div>
                        <h3 class="text-xl font-bold text-gray-800 mb-3" data-i18n="error_occurred_title">Oops! Có lỗi xảy ra</h3>
                        <p class="text-gray-600 mb-6 leading-relaxed">${message}</p>
                        <button onclick="window.futureMe.updateProjection()" 
                                class="px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all duration-300 transform hover:scale-105 font-medium shadow-lg">
                            🔄 <span data-i18n="try_again">Thử lại</span>
                        </button>
                        <p class="text-xs text-gray-500 mt-4" data-i18n="check_connection">Nếu lỗi vẫn tiếp tục, hãy kiểm tra kết nối mạng</p>
                    </div>
                </div>
            `;
        }
    }
}

// Initialize Future Me when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    if (!window.futureMe) {
        window.futureMe = new FutureMe();
    }
});

// Global function for opening Future Me (called from template buttons)
function openFutureMe() {
    if (window.futureMe) {
        window.futureMe.open();
    }
}

// CSS for custom slider styling and scroll bar (add to head)
const sliderCSS = `
<style>
/* Slider Styling */
.slider::-webkit-slider-thumb {
    appearance: none;
    height: 20px;
    width: 20px;
    border-radius: 50%;
    background: linear-gradient(135deg, #9333ea, #e11d48);
    cursor: pointer;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    transition: all 0.2s ease;
}

.slider::-webkit-slider-thumb:hover {
    transform: scale(1.1);
    box-shadow: 0 6px 12px rgba(0,0,0,0.3);
}

.slider::-moz-range-thumb {
    height: 20px;
    width: 20px;
    border-radius: 50%;
    background: linear-gradient(135deg, #9333ea, #e11d48);
    cursor: pointer;
    border: none;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

/* Custom Scrollbar Styling */
.custom-scrollbar {
    scrollbar-width: thin;
    scrollbar-color: #9333ea #f1f5f9;
}

.custom-scrollbar::-webkit-scrollbar {
    width: 8px;
}

.custom-scrollbar::-webkit-scrollbar-track {
    background: linear-gradient(to bottom, #f1f5f9, #e2e8f0);
    border-radius: 4px;
    box-shadow: inset 0 0 3px rgba(0,0,0,0.1);
}

.custom-scrollbar::-webkit-scrollbar-thumb {
    background: linear-gradient(to bottom, #9333ea, #e11d48);
    border-radius: 4px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    transition: all 0.2s ease;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(to bottom, #7c3aed, #dc2626);
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}

.custom-scrollbar::-webkit-scrollbar-thumb:active {
    background: linear-gradient(to bottom, #6d28d9, #b91c1c);
}

/* Enhanced Modal Animations */
#future-me-modal:not(.hidden) {
    animation: modalFadeIn 0.3s ease-out;
}

@keyframes modalFadeIn {
    from {
        opacity: 0;
        transform: scale(0.95);
    }
    to {
        opacity: 1;
        transform: scale(1);
    }
}

/* Responsive Grid Improvements */
@media (max-width: 768px) {
    .custom-scrollbar {
        max-h-[95vh];
    }
    
    #future-me-modal .bg-white {
        margin: 0.5rem;
        max-width: calc(100vw - 1rem);
    }
}

/* Enhanced Hover Effects */
.hover\\:shadow-lg:hover {
    transform: translateY(-2px);
    transition: all 0.3s ease;
}
</style>
`;

// Add slider CSS to document head
document.head.insertAdjacentHTML('beforeend', sliderCSS);
