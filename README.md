# 💰 Money Tracking Web Application

A modern multi-user web application for personal finance tracking that replaces traditional Excel spreadsheets with AI-powered categorization and beautiful calendar visualization.

## 🌟 Key Features

### 👥 Multi-User Architecture
- **Complete Data Isolation**: Users only see their own transactions and data
- **Secure Authentication**: Google OAuth + Demo accounts with legal consent
- **Scalable Design**: Supports thousands of concurrent users
- **User-Scoped APIs**: All endpoints filtered by authenticated user

### 💡 Smart Finance Management
- **📊 3-Type Transaction System**: Expenses (🔴), Savings (🟢), Investments (🔵)
- **🤖 AI-Powered Categorization**: Google Gemini API for automatic transaction categorization
- **📅 Calendar Interface**: Custom-built calendar with color-coded transactions
- **🎯 Future Projection**: Interactive scenarios and financial planning
- **🗣️ Voice Input**: Speech-to-text for quick transaction entry

### 🌍 User Experience
- **Multi-Language Support**: Vietnamese and English localization
- **📱 Mobile-First Design**: Responsive design with Tailwind CSS
- **🎨 AI Meme Generator**: Weekly personalized financial memes
- **📊 Analytics Dashboard (Future)**: Charts and insights for spending patterns

## 🛠 Technology Stack

- **Backend**: Django 5.x, Django REST Framework, Celery
- **Package Manager**: UV (ultrafast Python package installer)
- **Frontend**: Django Templates, Tailwind CSS (via CDN), Vanilla JavaScript
- **Database**: PostgreSQL (production) / SQLite (development)
- **AI**: Google Gemini API, NLTK
- **Caching**: Redis
- **Calendar**: Custom-built JavaScript component
- **Authentication**: Google OAuth + Custom Demo System
- **Deployment**: Railway.app with Gunicorn & Whitenoise

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- UV package manager
- PostgreSQL (production) or SQLite (development)
- Google Gemini API key
- Google OAuth credentials (optional)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/money-tracking.git
cd money-tracking
```

2. **Install UV (if not already installed)**
```bash
# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip
pip install uv
```

3. **Install dependencies with UV**
```bash
uv sync
```

4. **Environment setup**
```bash
cp env.example .env
# Edit .env with your configuration
```

5. **Database setup**
```bash
uv run python manage.py migrate
uv run python manage.py createsuperuser
```

6. **Run development server**
```bash
uv run python manage.py runserver
```

Visit `http://localhost:8000` to access the application.

### Environment Variables

Create a `.env` file in the project root:

```env
# Basic Configuration
DEBUG=True
SECRET_KEY=your-secret-key-here
LANGUAGE_CODE=vi
TIME_ZONE=Asia/Ho_Chi_Minh

# Database (PostgreSQL for production, SQLite for development)
DATABASE_URL=postgresql://user:pass@localhost:5432/expense_tracker

# AI Integration
GEMINI_API_KEY=your-gemini-api-key

# Multi-user Settings
ENABLE_MULTI_USER=True
DEFAULT_USER_LIMIT=1000

# Google OAuth (Optional)
GOOGLE_OAUTH2_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH2_CLIENT_SECRET=your-google-client-secret

# Cache (Optional - Redis for production)
REDIS_URL=redis://localhost:6379/0
```

## 📊 Project Structure

```
money-tracking/
├── docs/                           # 📖 Documentation
│   ├── CHANGELOG.md               # Version history
│   └── ...
├── scripts/                        # 🔧 Deployment Scripts
│   ├── build.sh
│   └── start.sh
├── expense_tracker/                # ⚙️ Django Configuration
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   └── urls.py
├── authentication/                 # 🔐 User Management & Google OAuth
│   ├── management/
│   │   └── commands/
│   │       └── cleanup_expired_demos.py
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── transactions/                   # 💰 Transaction & Monthly Total Management
│   ├── management/
│   │   └── commands/
│   │       └── setup_initial_data.py
│   ├── models.py
│   ├── views.py
│   └── api_urls.py
├── ai_chat/                        # 🤖 AI Integration (Gemini, Voice, Memes)
│   ├── views.py
│   └── gemini_service.py
├── static/                         # 🎨 Static Assets
│   ├── css/
│   ├── js/
│   │   └── translations/
│   └── images/
│       └── flags/
├── templates/                      # 📄 HTML Templates
│   ├── base.html
│   ├── index.html
│   ├── includes/
│   │   └── _language_switcher.html
│   └── legal/
│       ├── privacy_policy.html
│       └── terms_of_service.html
├── locale/                         # 🌍 Translations (en, vi)
│   ├── en/LC_MESSAGES/
│   └── vi/LC_MESSAGES/
├── .env.example                    # Example environment variables
├── manage.py                       # Django management script
├── requirements.txt                # 📦 Python Dependencies
├── pyproject.toml                  # 🔧 UV Configuration
├── railway.toml                    # 🚀 Railway Config
├── LOGIN_IMPLEMENTATION_PLAN.md    # 📋 Login Implementation Plan
└── GOOGLE_OAUTH_SETUP.md          # 📋 Google OAuth Setup
```

## 🔐 Multi-User Security

### Authentication System
- **Google OAuth**: Secure login with Google accounts
- **Demo Accounts**: Temporary accounts for testing (auto-expire in 24 hours)
- **Legal Consent**: Terms of service and privacy policy acceptance required
- **Session Management**: Secure session handling with CSRF protection

### Data Isolation
```python
# All database queries are automatically filtered by user
transactions = Transaction.objects.filter(user=request.user)
monthly_totals = MonthlyTotal.objects.filter(user=request.user)
chat_messages = ChatMessage.objects.filter(user=request.user)
```

### Security Features
- ✅ Authentication required for all data access
- ✅ User-scoped database queries
- ✅ CSRF protection on all forms
- ✅ Secure session cookies
- ✅ SQL injection prevention
- ✅ Rate limiting (future enhancement)

## 🤖 AI Features

### Intelligent Transaction Processing
```python
# Example AI categorization
Input: "ăn trưa hôm nay 75k"
Output: {
    "type": "expense",
    "category": "Ăn uống",
    "amount": 75000,
    "description": "Ăn trưa",
    "confidence": 0.95
}
```

### Voice Input Support
- Web Speech API integration
- Vietnamese and English support
- Real-time transcription
- Hands-free transaction entry

### Future Financial Projections
- Compound interest calculations
- Investment growth scenarios
- Goal-based financial planning
- Personalized recommendations

## 🌍 Internationalization

The application supports Vietnamese and English:

```bash
# Generate translation files
uv run python manage.py makemessages -l vi
uv run python manage.py makemessages -l en

# Compile translations
uv run python manage.py compilemessages
```

## 📱 API Documentation

### Authentication Required Endpoints
All API endpoints require user authentication and return user-scoped data.

```javascript
// Example authenticated API call
fetch('/api/transactions/', {
    headers: {
        'X-CSRFToken': getCSRFToken(),
        'Content-Type': 'application/json',
    },
    credentials: 'same-origin'
})
```

### Key Endpoints
- `GET /api/transactions/` - List all transactions for the authenticated user.
- `POST /api/transactions/` - Create a new transaction for the current user.
- `GET /api/chat/calendar/{year}/{month}/` - Get calendar data with daily transaction totals for the user.
- `POST /api/chat/process/` - Process natural language input using AI for transaction creation.
- `GET /api/monthly-totals/` - Retrieve aggregated monthly totals (expense, saving, investment) for the user.
- `POST /api/chat/confirm/` - Confirm an AI-suggested transaction.

<!-- EOF -->
