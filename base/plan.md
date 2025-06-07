# **EXPENSE TRACKER WEB APP - UPDATED DETAILED DEVELOPMENT PLAN**

## **📋 PROJECT OVERVIEW**
Build a single-page financial tracking web application with AI chat interface, custom calendar view, i18n support, and advanced features like Future Me Simulator and AI Meme Generator.

---

## **🎯 PHASE 1: PROJECT SETUP & FOUNDATION (Day 1-2)**

### **1.1 Environment Setup with UV**
```bash
# Install UV package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create Django project
mkdir expense_tracker_app
cd expense_tracker_app

# Initialize UV project
uv init

# Create virtual environment with UV
uv venv

# Activate virtual environment
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies with UV
uv add django djangorestframework python-decouple
uv add psycopg2-binary python-dotenv requests pillow
uv add django-cors-headers whitenoise gunicorn

# Create Django project
uv run django-admin startproject expense_tracker .
uv run python manage.py startapp transactions
uv run python manage.py startapp ai_chat
```

### **1.2 Updated Project Structure**
```
expense_tracker_app/
├── pyproject.toml          # UV configuration
├── uv.lock                 # UV lock file
├── expense_tracker/
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── transactions/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── serializers.py
│   └── admin.py
├── ai_chat/
│   ├── models.py
│   ├── views.py
│   ├── gemini_service.py
│   ├── voice_processor.py
│   └── date_parser.py
├── locale/                 # i18n translations
│   ├── vi/
│   │   └── LC_MESSAGES/
│   │       ├── django.po
│   │       └── django.mo
│   └── en/
│       └── LC_MESSAGES/
│           ├── django.po
│           └── django.mo
├── templates/
│   ├── base.html
│   └── index.html
├── static/
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   ├── calendar.js
│   │   ├── chat.js
│   │   ├── voice.js
│   │   └── app.js
│   └── images/
└── manage.py
```

### **1.3 Settings Configuration with i18n**
```python
# base.py
import os
from django.utils.translation import gettext_lazy as _

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'transactions',
    'ai_chat',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # i18n support
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Internationalization
LANGUAGE_CODE = 'vi'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ('vi', _('Tiếng Việt')),
    ('en', _('English')),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# Environment variables setup
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
```

---

## **🗄 PHASE 2: UPDATED DATABASE MODELS (Day 3)**

### **2.1 Simplified Transaction Model**
```python
# transactions/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('expense', _('🔴 Chi tiêu')),
        ('saving', _('🟢 Tiết kiệm')), 
        ('investment', _('🔵 Đầu tư'))
    ]
    
    # Simplified categories - only for expenses
    EXPENSE_CATEGORIES = [
        ('food', _('🍜 Ăn uống')),
        ('coffee', _('☕ Coffee')),
        ('transport', _('🚗 Di chuyển')),
        ('shopping', _('🛒 Mua sắm')),
        ('entertainment', _('🎬 Giải trí')),
        ('health', _('🏥 Sức khỏe')),
        ('education', _('📚 Giáo dục')),
        ('utilities', _('⚡ Tiện ích')),
        ('other', _('📦 Khác')),
    ]
    
    # Core fields
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=0)
    description = models.CharField(max_length=200)
    date = models.DateField()
    
    # Only expense has categories, saving/investment are simple
    expense_category = models.CharField(
        max_length=20, 
        choices=EXPENSE_CATEGORIES, 
        null=True, 
        blank=True
    )
    
    # AI related
    ai_confidence = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Transaction')
        verbose_name_plural = _('Transactions')
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount:,}₫ - {self.date}"
    
    def get_icon(self):
        """Get icon based on transaction type and category"""
        if self.transaction_type == 'expense':
            category_icons = {
                'food': '🍜', 'coffee': '☕', 'transport': '🚗',
                'shopping': '🛒', 'entertainment': '🎬', 'health': '🏥',
                'education': '📚', 'utilities': '⚡', 'other': '📦'
            }
            return category_icons.get(self.expense_category, '📦')
        elif self.transaction_type == 'saving':
            return '💰'
        elif self.transaction_type == 'investment':
            return '📈'
        return '💰'
```

### **2.2 Enhanced AI Chat Model**
```python
# ai_chat/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _

class ChatMessage(models.Model):
    user_message = models.TextField()
    ai_response = models.TextField()
    suggested_transaction = models.ForeignKey(
        'transactions.Transaction', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL
    )
    is_confirmed = models.BooleanField(default=False)
    
    # Voice support
    has_voice_input = models.BooleanField(default=False)
    voice_transcript = models.TextField(blank=True)
    
    # Date parsing for historical transactions
    parsed_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Chat Message')
        verbose_name_plural = _('Chat Messages')
        ordering = ['-created_at']

class MonthlyTotal(models.Model):
    """Track monthly totals for dashboard"""
    year = models.IntegerField()
    month = models.IntegerField()
    
    total_expense = models.DecimalField(max_digits=15, decimal_places=0, default=0)
    total_saving = models.DecimalField(max_digits=15, decimal_places=0, default=0)
    total_investment = models.DecimalField(max_digits=15, decimal_places=0, default=0)
    net_total = models.DecimalField(max_digits=15, decimal_places=0, default=0)
    
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['year', 'month']
        verbose_name = _('Monthly Total')
        verbose_name_plural = _('Monthly Totals')
```

---

## **🌐 PHASE 3: INTERNATIONALIZATION SETUP (Day 4)**

### **3.1 Django i18n Configuration**
```bash
# Generate translation files
uv run python manage.py makemessages -l vi
uv run python manage.py makemessages -l en

# Compile translations
uv run python manage.py compilemessages
```

### **3.2 Translation Files**
```po
# locale/vi/LC_MESSAGES/django.po
msgid "Expense Tracker"
msgstr "Theo Dõi Chi Tiêu"

msgid "AI Assistant"
msgstr "Trợ Lý AI"

msgid "Enter transaction"
msgstr "Nhập giao dịch"

msgid "Today"
msgstr "Hôm nay"

msgid "This Month Total"
msgstr "Tổng Tháng Này"

msgid "Future Me Simulator"
msgstr "Mô Phỏng Tương Lai"

msgid "Generate Meme"
msgstr "Tạo Meme"

msgid "Statistics"
msgstr "Thống Kê"
```

```po
# locale/en/LC_MESSAGES/django.po
msgid "Expense Tracker"
msgstr "Expense Tracker"

msgid "AI Assistant"
msgstr "AI Assistant"

msgid "Enter transaction"
msgstr "Enter transaction"

msgid "Today"
msgstr "Today"

msgid "This Month Total"
msgstr "This Month Total"

msgid "Future Me Simulator"
msgstr "Future Me Simulator"

msgid "Generate Meme"
msgstr "Generate Meme"

msgid "Statistics"
msgstr "Statistics"
```

### **3.3 Frontend i18n Support**
```javascript
// static/js/i18n.js
class I18n {
    constructor() {
        this.currentLang = localStorage.getItem('language') || 'vi';
        this.translations = {};
        this.loadTranslations();
    }
    
    async loadTranslations() {
        try {
            const response = await fetch(`/api/translations/${this.currentLang}/`);
            this.translations = await response.json();
        } catch (error) {
            console.error('Error loading translations:', error);
        }
    }
    
    t(key, params = {}) {
        let text = this.translations[key] || key;
        
        // Replace parameters
        Object.keys(params).forEach(param => {
            text = text.replace(`{${param}}`, params[param]);
        });
        
        return text;
    }
    
    setLanguage(lang) {
        this.currentLang = lang;
        localStorage.setItem('language', lang);
        this.loadTranslations().then(() => {
            this.updatePageTexts();
        });
    }
    
    updatePageTexts() {
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            element.textContent = this.t(key);
        });
    }
}

// Initialize i18n
window.i18n = new I18n();
```

---

## **🎨 PHASE 4: ENHANCED FRONTEND WITH MONTHLY TOTAL (Day 5-6)**

### **4.1 Updated Header with Monthly Total**
```html
<!-- templates/index.html -->
<div class="bg-white shadow-sm border-b">
    <div class="max-w-7xl mx-auto px-4 py-4">
        <!-- Language Switcher -->
        <div class="flex justify-end mb-4">
            <select id="language-switcher" class="px-3 py-1 border rounded-lg text-sm">
                <option value="vi">🇻🇳 Tiếng Việt</option>
                <option value="en">🇺🇸 English</option>
            </select>
        </div>
        
        <!-- Stats Grid - Now 4 cards -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <!-- Chi tiêu -->
            <div class="bg-gradient-to-br from-red-50 to-pink-50 border border-red-200 rounded-xl p-6 transition-all duration-300 hover:shadow-lg">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-red-600 text-sm font-semibold mb-1" data-i18n="expense">🔴 Chi Tiêu</p>
                        <p class="text-3xl font-black text-red-700" id="expense-total">-2,450,000₫</p>
                        <p class="text-xs text-red-500 mt-1" data-i18n="this_month">Tháng này</p>
                    </div>
                    <div class="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                        <svg class="w-6 h-6 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z"/>
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clip-rule="evenodd"/>
                        </svg>
                    </div>
                </div>
            </div>
            
            <!-- Tiết kiệm -->
            <div class="bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 rounded-xl p-6 transition-all duration-300 hover:shadow-lg">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-green-600 text-sm font-semibold mb-1" data-i18n="saving">🟢 Tiết Kiệm</p>
                        <p class="text-3xl font-black text-green-700" id="saving-total">+1,200,000₫</p>
                        <p class="text-xs text-green-500 mt-1" data-i18n="this_month">Tháng này</p>
                    </div>
                    <div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                        <svg class="w-6 h-6 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M4 4a2 2 0 00-2 2v4a2 2 0 002 2V6h10a2 2 0 00-2-2H4zm2 6a2 2 0 012-2h8a2 2 0 012 2v4a2 2 0 01-2 2H8a2 2 0 01-2-2v-4zm6 4a2 2 0 100-4 2 2 0 000 4z"/>
                        </svg>
                    </div>
                </div>
            </div>
            
            <!-- Đầu tư -->
            <div class="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-6 transition-all duration-300 hover:shadow-lg">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-blue-600 text-sm font-semibold mb-1" data-i18n="investment">🔵 Đầu Tư</p>
                        <p class="text-3xl font-black text-blue-700" id="investment-total">+3,000,000₫</p>
                        <p class="text-xs text-blue-500 mt-1" data-i18n="this_month">Tháng này</p>
                    </div>
                    <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                        <svg class="w-6 h-6 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z"/>
                        </svg>
                    </div>
                </div>
            </div>
            
            <!-- NEW: Tổng Tháng Này -->
            <div class="bg-gradient-to-br from-purple-50 to-indigo-50 border border-purple-200 rounded-xl p-6 transition-all duration-300 hover:shadow-lg">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-purple-600 text-sm font-semibold mb-1" data-i18n="monthly_total">📊 Tổng Tháng</p>
                        <p class="text-3xl font-black text-purple-700" id="monthly-net-total">+1,750,000₫</p>
                        <p class="text-xs text-purple-500 mt-1" data-i18n="net_amount">Số dư ròng</p>
                    </div>
                    <div class="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
                        <svg class="w-6 h-6 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"/>
                        </svg>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
```

---

## **🤖 PHASE 5: ENHANCED AI CHAT WITH VOICE & DATE PARSING (Day 7-9)**

### **5.1 Voice Input Integration**
```javascript
// static/js/voice.js
class VoiceInput {
    constructor() {
        this.recognition = null;
        this.isListening = false;
        this.initSpeechRecognition();
    }
    
    initSpeechRecognition() {
        if ('webkitSpeechRecognition' in window) {
            this.recognition = new webkitSpeechRecognition();
        } else if ('SpeechRecognition' in window) {
            this.recognition = new SpeechRecognition();
        } else {
            console.warn('Speech Recognition not supported');
            return;
        }
        
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
        this.recognition.lang = window.i18n.currentLang === 'vi' ? 'vi-VN' : 'en-US';
        
        this.recognition.onstart = () => {
            this.isListening = true;
            this.updateVoiceButton(true);
        };
        
        this.recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            this.handleVoiceResult(transcript);
        };
        
        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            this.isListening = false;
            this.updateVoiceButton(false);
        };
        
        this.recognition.onend = () => {
            this.isListening = false;
            this.updateVoiceButton(false);
        };
    }
    
    startListening() {
        if (this.recognition && !this.isListening) {
            this.recognition.start();
        }
    }
    
    stopListening() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
        }
    }
    
    handleVoiceResult(transcript) {
        const chatInput = document.getElementById('chat-input');
        chatInput.value = transcript;
        
        // Auto-send voice message
        if (window.aiChat) {
            window.aiChat.sendMessage(true); // Pass voice flag
        }
    }
    
    updateVoiceButton(listening) {
        const voiceBtn = document.getElementById('voice-btn');
        if (listening) {
            voiceBtn.classList.add('listening');
            voiceBtn.innerHTML = '🎤 Đang nghe...';
        } else {
            voiceBtn.classList.remove('listening');
            voiceBtn.innerHTML = '🎤 Voice';
        }
    }
}

// Initialize voice input
window.voiceInput = new VoiceInput();
```

### **5.2 Enhanced Chat with Voice Button**
```html
<!-- Updated chat interface -->
<div class="flex space-x-2">
    <input 
        type="text" 
        id="chat-input" 
        placeholder="VD: coffee 25k, tiết kiệm 200k..." 
        class="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
        onkeypress="handleChatKeyPress(event)"
    >
    <button 
        id="voice-btn"
        onclick="toggleVoiceInput()" 
        class="px-3 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition text-sm font-medium"
    >
        🎤
    </button>
    <button 
        onclick="sendMessage()" 
        class="px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 transition text-sm font-medium"
    >
        <span data-i18n="send">Gửi</span>
    </button>
</div>
```

### **5.3 Date Parser Service**
```python
# ai_chat/date_parser.py
import re
from datetime import datetime, timedelta
from django.utils.translation import gettext as _

class DateParser:
    def __init__(self, language='vi'):
        self.language = language
        self.today = datetime.now().date()
        
    def parse_date_from_message(self, message):
        """Parse date from Vietnamese/English message"""
        message_lower = message.lower()
        
        # Today variations
        today_patterns = {
            'vi': ['hôm nay', 'bữa nay', 'ngày hôm nay'],
            'en': ['today', 'this day']
        }
        
        # Yesterday variations  
        yesterday_patterns = {
            'vi': ['hôm qua', 'qua', 'ngày hôm qua'],
            'en': ['yesterday', 'last day']
        }
        
        # Day before yesterday
        day_before_patterns = {
            'vi': ['hôm kia', 'kia'],
            'en': ['day before yesterday', 'two days ago']
        }
        
        # Week days
        weekdays = {
            'vi': {
                'thứ hai': 0, 'thứ 2': 0, 't2': 0,
                'thứ ba': 1, 'thứ 3': 1, 't3': 1,
                'thứ tư': 2, 'thứ 4': 2, 't4': 2,
                'thứ năm': 3, 'thứ 5': 3, 't5': 3,
                'thứ sáu': 4, 'thứ 6': 4, 't6': 4,
                'thứ bảy': 5, 'thứ 7': 5, 't7': 5,
                'chủ nhật': 6, 'cn': 6
            },
            'en': {
                'monday': 0, 'mon': 0,
                'tuesday': 1, 'tue': 1,
                'wednesday': 2, 'wed': 2,
                'thursday': 3, 'thu': 3,
                'friday': 4, 'fri': 4,
                'saturday': 5, 'sat': 5,
                'sunday': 6, 'sun': 6
            }
        }
        
        # Check for today
        for pattern in today_patterns.get(self.language, []):
            if pattern in message_lower:
                return self.today
        
        # Check for yesterday
        for pattern in yesterday_patterns.get(self.language, []):
            if pattern in message_lower:
                return self.today - timedelta(days=1)
        
        # Check for day before yesterday
        for pattern in day_before_patterns.get(self.language, []):
            if pattern in message_lower:
                return self.today - timedelta(days=2)
        
        # Check for weekdays
        for day_name, day_num in weekdays.get(self.language, {}).items():
            if day_name in message_lower:
                return self._get_last_weekday(day_num)
        
        # Check for specific date patterns (dd/mm, dd-mm, dd.mm)
        date_match = re.search(r'(\d{1,2})[/-.](\d{1,2})', message_lower)
        if date_match:
            day, month = int(date_match.group(1)), int(date_match.group(2))
            try:
                # Assume current year
                target_date = datetime(self.today.year, month, day).date()
                # If date is in future, assume last year
                if target_date > self.today:
                    target_date = datetime(self.today.year - 1, month, day).date()
                return target_date
            except ValueError:
                pass
        
        # Default to today
        return self.today
    
    def _get_last_weekday(self, target_weekday):
        """Get the most recent occurrence of a weekday"""
        current_weekday = self.today.weekday()
        days_back = (current_weekday - target_weekday) % 7
        if days_back == 0:  # Same day
            days_back = 7  # Get last week's occurrence
        return self.today - timedelta(days=days_back)
```

### **5.4 Enhanced Gemini Service with Date Support**
```python
# ai_chat/gemini_service.py
import google.generativeai as genai
from django.conf import settings
import re
import json
from .date_parser import DateParser

class GeminiService:
    def __init__(self, language='vi'):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
        self.language = language
        self.date_parser = DateParser(language)
    
    def categorize_transaction(self, message, has_voice=False):
        """Analyze user message and categorize transaction with date parsing"""
        
        # Parse date first
        parsed_date = self.date_parser.parse_date_from_message(message)
        
        prompt = self._build_prompt(message, self.language)
        
        try:
            response = self.model.generate_content(prompt)
            result = json.loads(response.text)
            
            # Add parsed date and voice flag
            result['parsed_date'] = parsed_date.isoformat()
            result['has_voice'] = has_voice
            
            return result
        except Exception as e:
            # Fallback logic
            return self._fallback_categorization(message, parsed_date, has_voice)
    
    def _build_prompt(self, message, language):
        """Build appropriate prompt based on language"""
        if language == 'vi':
            return f"""
            Phân tích tin nhắn tiếng Việt sau và trả về JSON:
            
            Tin nhắn: "{message}"
            
            Trả về JSON với format:
            {{
                "type": "expense|saving|investment",
                "amount": số_tiền_VND,
                "description": "mô_tả_ngắn_gọn",
                "category": "category_code",
                "confidence": 0.0-1.0,
                "icon": "emoji"
            }}
            
            Quy tắc phân loại:
            - "coffee", "cafe", "cà phê" → expense, coffee category
            - "ăn", "trưa", "sáng", "tối", "phở", "cơm" → expense, food category  
            - "grab", "taxi", "xe ôm", "xăng" → expense, transport category
            - "mua sắm", "shopping", "áo", "quần" → expense, shopping category
            - "tiết kiệm", "gửi ngân hàng", "save" → saving (no category needed)
            - "mua cổ phiếu", "đầu tư", "invest", "bitcoin" → investment (no category needed)
            - Extract số tiền từ "25k" = 25000, "1.5M" = 1500000
            """
        else:  # English
            return f"""
            Analyze the following English message and return JSON:
            
            Message: "{message}"
            
            Return JSON with format:
            {{
                "type": "expense|saving|investment",
                "amount": amount_in_VND,
                "description": "short_description",
                "category": "category_code", 
                "confidence": 0.0-1.0,
                "icon": "emoji"
            }}
            
            Classification rules:
            - "coffee", "cafe" → expense, coffee category
            - "lunch", "dinner", "food", "eat" → expense, food category
            - "transport", "taxi", "gas", "fuel" → expense, transport category
            - "shopping", "buy clothes" → expense, shopping category
            - "saving", "save money", "bank deposit" → saving (no category)
            - "investment", "buy stocks", "invest" → investment (no category)
            - Extract amount from "25k" = 25000, "1.5M" = 1500000
            """
```

### **5.5 Enhanced Chat API with Voice & Date Support**
```python
# ai_chat/views.py
@api_view(['POST'])
def process_chat_message(request):
    """Process user chat message with AI, voice, and date support"""
    user_message = request.data.get('message', '')
    has_voice = request.data.get('has_voice', False)
    language = request.data.get('language', 'vi')
    
    if not user_message:
        return Response({'error': 'Message is required'}, status=400)
    
    # Use Gemini service with language support
    gemini = GeminiService(language)
    ai_result = gemini.categorize_transaction(user_message, has_voice)
    
    # Save chat message
    chat_message = ChatMessage.objects.create(
        user_message=user_message,
        ai_response=json.dumps(ai_result),
        has_voice_input=has_voice,
        voice_transcript=user_message if has_voice else '',
        parsed_date=ai_result.get('parsed_date')
    )
    
    # Generate response text based on language
    response_text = _generate_response_text(ai_result, language)
    
    return Response({
        'chat_id': chat_message.id,
        'ai_response': ai_result,
        'suggested_text': response_text,
        'parsed_date': ai_result.get('parsed_date')
    })

def _generate_response_text(ai_result, language):
    """Generate appropriate response text based on language"""
    if language == 'vi':
        type_labels = {
            'expense': 'Chi tiêu',
            'saving': 'Tiết kiệm',
            'investment': 'Đầu tư'
        }
        return f"{ai_result['icon']} Phân loại: {type_labels[ai_result['type']]} - {ai_result['description']} ({ai_result['amount']:,}₫)"
    else:
        type_labels = {
            'expense': 'Expense',
            'saving': 'Saving', 
            'investment': 'Investment'
        }
        return f"{ai_result['icon']} Classified as: {type_labels[ai_result['type']]} - {ai_result['description']} ({ai_result['amount']:,}₫)"

@api_view(['POST'])
def confirm_transaction(request):
    """Confirm and save transaction from AI suggestion with custom date"""
    chat_id = request.data.get('chat_id')
    transaction_data = request.data.get('transaction_data')
    custom_date = request.data.get('custom_date')  # Optional custom date
    
    # Get chat message to retrieve parsed date
    chat_message = ChatMessage.objects.get(id=chat_id)
    
    # Use custom date if provided, otherwise use parsed date, fallback to today
    if custom_date:
        transaction_date = datetime.strptime(custom_date, '%Y-%m-%d').date()
    elif chat_message.parsed_date:
        transaction_date = chat_message.parsed_date
    else:
        transaction_date = timezone.now().date()
    
    # Create transaction
    transaction = Transaction.objects.create(
        transaction_type=transaction_data['type'],
        amount=transaction_data['amount'] if transaction_data['type'] == 'expense' else transaction_data['amount'],
        description=transaction_data['description'],
        date=transaction_date,
        expense_category=transaction_data.get('category') if transaction_data['type'] == 'expense' else None,
        ai_confidence=transaction_data['confidence']
    )
    
    # Update chat message
    chat_message.suggested_transaction = transaction
    chat_message.is_confirmed = True
    chat_message.save()
    
    # Update monthly totals
    update_monthly_totals(transaction_date.year, transaction_date.month)
    
    return Response({
        'success': True, 
        'transaction_id': transaction.id,
        'transaction_date': transaction_date.isoformat()
    })
```

---

## **📊 PHASE 6: MONTHLY TOTALS CALCULATION (Day 10)**

### **6.1 Monthly Totals Service**
```python
# transactions/monthly_service.py
from django.db.models import Sum
from datetime import datetime
from .models import Transaction, MonthlyTotal

def update_monthly_totals(year, month):
    """Update monthly totals for given year/month"""
    
    # Get all transactions for the month
    transactions = Transaction.objects.filter(
        date__year=year,
        date__month=month
    )
    
    # Calculate totals
    expense_total = abs(transactions.filter(
        transaction_type='expense'
    ).aggregate(total=Sum('amount'))['total'] or 0)
    
    saving_total = transactions.filter(
        transaction_type='saving'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    investment_total = transactions.filter(
        transaction_type='investment'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Calculate net total (saving + investment - expense)
    net_total = saving_total + investment_total - expense_total
    
    # Update or create monthly total
    monthly_total, created = MonthlyTotal.objects.update_or_create(
        year=year,
        month=month,
        defaults={
            'total_expense': expense_total,
            'total_saving': saving_total,
            'total_investment': investment_total,
            'net_total': net_total
        }
    )
    
    return monthly_total

def get_current_month_totals():
    """Get current month totals for dashboard"""
    now = datetime.now()
    
    try:
        monthly_total = MonthlyTotal.objects.get(
            year=now.year,
            month=now.month
        )
        return {
            'expense': monthly_total.total_expense,
            'saving': monthly_total.total_saving,
            'investment': monthly_total.total_investment,
            'net_total': monthly_total.net_total
        }
    except MonthlyTotal.DoesNotExist:
        # Calculate and create if doesn't exist
        monthly_total = update_monthly_totals(now.year, now.month)
        return {
            'expense': monthly_total.total_expense,
            'saving': monthly_total.total_saving,
            'investment': monthly_total.investment,
            'net_total': monthly_total.net_total
        }

# API endpoint for monthly totals
@api_view(['GET'])
def get_monthly_totals(request):
    """Get monthly totals for dashboard"""
    totals = get_current_month_totals()
    
    return Response({
        'monthly_totals': totals,
        'formatted': {
            'expense': f"-{totals['expense']:,}₫",
            'saving': f"+{totals['saving']:,}₫", 
            'investment': f"+{totals['investment']:,}₫",
            'net_total': f"{'+' if totals['net_total'] >= 0 else ''}{totals['net_total']:,}₫"
        }
    })
```

### **6.2 Frontend Monthly Totals Update**
```javascript
// static/js/dashboard.js
class Dashboard {
    constructor() {
        this.loadDashboardData();
        this.setupAutoRefresh();
    }
    
    async loadDashboardData() {
        try {
            const response = await fetch('/api/monthly-totals/');
            const data = await response.json();
            
            this.updateDashboardCards(data);
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }
    }
    
    updateDashboardCards(data) {
        const totals = data.monthly_totals;
        const formatted = data.formatted;
        
        // Update expense card
        document.getElementById('expense-total').textContent = formatted.expense;
        
        // Update saving card  
        document.getElementById('saving-total').textContent = formatted.saving;
        
        // Update investment card
        document.getElementById('investment-total').textContent = formatted.investment;
        
        // Update monthly net total card
        const netTotalElement = document.getElementById('monthly-net-total');
        netTotalElement.textContent = formatted.net_total;
        
        // Update color based on positive/negative
        const netTotalCard = netTotalElement.closest('.bg-gradient-to-br');
        if (totals.net_total >= 0) {
            netTotalCard.className = netTotalCard.className.replace(
                'from-purple-50 to-indigo-50 border-purple-200',
                'from-green-50 to-emerald-50 border-green-200'
            );
            netTotalElement.className = netTotalElement.className.replace(
                'text-purple-700',
                'text-green-700'
            );
        } else {
            netTotalCard.className = netTotalCard.className.replace(
                'from-green-50 to-emerald-50 border-green-200',
                'from-red-50 to-pink-50 border-red-200'
            );
            netTotalElement.className = netTotalElement.className.replace(
                'text-green-700',
                'text-red-700'
            );
        }
    }
    
    setupAutoRefresh() {
        // Refresh dashboard every 30 seconds
        setInterval(() => {
            this.loadDashboardData();
        }, 30000);
    }
    
    // Call this after confirming transactions
    refreshDashboard() {
        this.loadDashboardData();
    }
}

// Initialize dashboard
window.dashboard = new Dashboard();
```

---

## **🚀 PHASE 7-10: REMAINING FEATURES (Day 11-17)**

### **Phase 7: Calendar Implementation** (Day 11-12)
- Continue with existing calendar logic
- Add i18n support for calendar labels
- Integrate with new monthly totals

### **Phase 8: Future Me Simulator** (Day 13-14) 
- Continue with existing future projection logic
- Add i18n support for all texts
- Enhanced calculations with monthly totals

### **Phase 9: AI Meme Generator** (Day 15)
- Continue with existing meme generation
- Add language-specific meme templates
- Support both Vietnamese and English memes

### **Phase 10: Deployment with UV** (Day 16-17)

```toml
# pyproject.toml
[project]
name = "expense-tracker-app"
version = "0.1.0"
description = "AI-powered expense tracking web application"
dependencies = [
    "django>=5.0.0",
    "djangorestframework>=3.14.0",
    "python-decouple>=3.8",
    "psycopg2-binary>=2.9.0",
    "python-dotenv>=1.0.0",
    "requests>=2.31.0",
    "pillow>=10.0.0",
    "django-cors-headers>=4.3.0",
    "whitenoise>=6.6.0",
    "gunicorn>=21.2.0",
    "google-generativeai>=0.3.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = [
    "pytest>=7.4.0",
    "pytest-django>=4.7.0",
    "black>=23.9.0",
    "flake8>=6.1.0",
]
```

```bash
# Deployment commands with UV
uv sync --frozen
uv run python manage.py collectstatic --noinput
uv run python manage.py migrate
uv run python manage.py compilemessages
```

---

## **📋 UPDATED FINAL DELIVERABLES**

1. **Enhanced Single-Page Web App** with:
   - ✅ **i18n support** (Vietnamese + English)
   - ✅ **4-card dashboard** with monthly net total
   - ✅ **Voice input** for chat interface
   - ✅ **Historical date parsing** ("hôm qua", "thứ 6 tuần trước")
   - ✅ **Simplified categories** (only expenses have categories)
   - ✅ **UV package management** instead of pip

2. **Enhanced AI Features** with:
   - ✅ **Multilingual AI processing** (Vietnamese + English)
   - ✅ **Voice transcript storage**
   - ✅ **Smart date parsing** from natural language
   - ✅ **Historical transaction support**

3. **Robust Backend** with:
   - ✅ **Monthly totals calculation**
   - ✅ **i18n API endpoints**
   - ✅ **Voice input processing**
   - ✅ **Date-aware transaction creation**

4. **Modern Tooling** with:
   - ✅ **UV for dependency management**
   - ✅ **Type hints and modern Python**
   - ✅ **Optimized deployment workflow**

**Total estimated development time: 17 days**
**Required skills: Python/Django, JavaScript, i18n, Voice APIs, UV package management, AI integration**