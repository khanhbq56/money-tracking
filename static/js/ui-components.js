/**
 * Professional UI Components Library
 * Using CSS custom properties and BEM methodology
 */

class UIComponents {
    
    /**
     * Create standardized buttons using CSS classes
     */
    static createButton(text, type = 'primary', onclick = null, options = {}) {
        const button = document.createElement('button');
        button.textContent = text;
        button.className = `btn btn--${type}`;
        
        if (options.fullWidth) {
            button.classList.add('btn--full');
        }
        
        if (options.small) {
            button.classList.add('btn--small');
        }
        
        if (options.large) {
            button.classList.add('btn--large');
        }
        
        if (options.icon) {
            button.innerHTML = `${options.icon} ${text}`;
        }
        
        if (onclick) {
            button.onclick = onclick;
        }
        
        return button;
    }

    /**
     * Create standardized modal using CSS classes
     */
    static createModal(id, title, content, options = {}) {
        const modal = document.createElement('div');
        modal.id = id;
        modal.className = 'modal';
        
        // Handle close button visibility
        const closeButtonHtml = options.showCloseButton !== false ? `
            <button onclick="UIComponents.closeModal('${id}')" class="modal__close">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
            </button>
        ` : '';

        // Handle modal size
        const sizeClass = options.size === 'medium' ? 'max-w-lg' : 
                         options.size === 'large' ? 'max-w-2xl' : 
                         options.maxWidth || 'max-w-md';
        
        modal.innerHTML = `
            <div class="modal__content ${sizeClass}" onclick="event.stopPropagation()">
                <div class="modal__header">
                    <h3 class="modal__title">${title}</h3>
                    ${closeButtonHtml}
                </div>
                <div class="modal__body">
                    <!-- Content will be appended here -->
                </div>
            </div>
        `;
        
        // Append content (could be HTML string or DOM element)
        const modalBody = modal.querySelector('.modal__body');
        if (typeof content === 'string') {
            modalBody.innerHTML = content;
        } else {
            modalBody.appendChild(content);
        }
        
        // Add event listeners (only if not persistent)
        if (!options.persistent) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                UIComponents.closeModal(id);
            }
        });
        
        // ESC key handler
        const escHandler = (e) => {
            if (e.key === 'Escape' && modal.classList.contains('modal--visible')) {
                UIComponents.closeModal(id);
                document.removeEventListener('keydown', escHandler);
            }
        };
        document.addEventListener('keydown', escHandler);
        }
        
        document.body.appendChild(modal);
        
        // Add show/hide methods to the modal element
        modal.show = () => UIComponents.showModal(id);
        modal.hide = () => UIComponents.closeModal(id);
        modal.element = modal;
        
        return modal;
    }

    /**
     * Show modal
     */
    static showModal(id) {
        const modal = document.getElementById(id);
        if (modal) {
            modal.classList.add('modal--visible');
        }
    }

    /**
     * Close modal
     */
    static closeModal(id) {
        const modal = document.getElementById(id);
        if (modal) {
            modal.classList.remove('modal--visible');
        }
    }

    /**
     * Create standardized dashboard card using CSS classes
     */
    static createDashboardCard(title, value, type, icon) {
        const emojis = {
            expense: '🔴',
            saving: '🟢',
            investment: '🔵',
            total: '📊'
        };

        const card = document.createElement('div');
        card.className = `card card--${type}`;
        
        card.innerHTML = `
            <div class="card__body">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-sm font-semibold mb-1">${emojis[type]} ${title}</p>
                        <p class="text-3xl font-black">${value}</p>
                        <p class="text-xs mt-1">${window.i18n.t('this_month')}</p>
                    </div>
                    <div class="w-12 h-12 bg-${type === 'expense' ? 'red' : type === 'saving' ? 'green' : type === 'investment' ? 'blue' : 'purple'}-100 rounded-full flex items-center justify-center">
                        ${icon}
                    </div>
                </div>
            </div>
        `;
        
        return card;
    }

    /**
     * Create standardized slider using CSS classes
     */
    static createSlider(id, min, max, value, label, onInput) {
        const sliderContainer = document.createElement('div');
        sliderContainer.className = 'form-group';
        
        sliderContainer.innerHTML = `
            <label class="form-label">${label}</label>
            <div class="relative">
                <input 
                    type="range" 
                    id="${id}"
                    min="${min}" 
                    max="${max}" 
                    value="${value}"
                    class="slider"
                >
                <div class="text-center mt-2">
                    <span id="${id}-value" class="text-lg font-semibold text-purple-600">${value}</span>
                </div>
            </div>
        `;
        
        const slider = sliderContainer.querySelector('input');
        const valueDisplay = sliderContainer.querySelector(`#${id}-value`);
        
        slider.addEventListener('input', () => {
            valueDisplay.textContent = slider.value;
            if (onInput) onInput(slider.value);
        });
        
        return sliderContainer;
    }

    /**
     * Show toast notification using existing dialog system
     */
    static showToast(message, type = 'info', duration = 3000) {
        showAlertDialog(message, { type: type });
        
        if (duration > 0) {
            setTimeout(() => {
                closeConfirmationModal();
            }, duration);
        }
    }

    /**
     * Create standardized quick action button
     */
    static createQuickActionButton(text, icon, onclick, type = 'primary') {
        const button = document.createElement('button');
        button.className = `btn btn--${type} btn--full`;
        button.innerHTML = `${icon} ${text}`;
        
        if (onclick) {
            button.onclick = onclick;
        }
        
        return button;
    }

    /**
     * Create standardized filter button
     */
    static createFilterButton(text, type, onclick, isActive = false) {
        const typeClasses = {
            all: 'bg-white/20 text-white',
            expense: 'bg-red-100 text-red-700 hover:bg-red-200',
            saving: 'bg-green-100 text-green-700 hover:bg-green-200',
            investment: 'bg-blue-100 text-blue-700 hover:bg-blue-200'
        };

        const button = document.createElement('button');
        button.className = `filter-btn ${typeClasses[type]} px-4 py-2 rounded-xl font-medium transition-all duration-200 ${isActive ? 'active' : ''}`;
        button.textContent = text;
        
        if (onclick) {
            button.onclick = onclick;
        }
        
        return button;
    }
}

// Make UIComponents globally available
window.UIComponents = UIComponents; 