# 💰 Expense Tracker Web Application

A modern multi-user web application for personal finance tracking that replaces traditional Excel spreadsheets with AI-powered categorization and beautiful calendar visualization.

## 🌟 Features

### Core Functionality
- **👥 Multi-User Support**: Complete user isolation with secure authentication
- **📊 3-Type Transaction System**: Expenses (🔴), Savings (🟢), Investments (🔵)
- **📅 Calendar-Based Interface**: FullCalendar.js integration with color-coded transactions
- **🤖 AI-Powered Categorization**: Google Gemini API for automatic transaction categorization
- **🌍 Multi-Language Support**: Vietnamese and English localization
- **📱 Mobile-First Design**: Responsive design with Tailwind CSS

### Advanced Features
- **🎯 Future Me Simulator**: Project your financial future with interactive scenarios
- **📈 Investment Portfolio Tracking**: Track assets, P&L, and performance
- **🎨 AI Meme Generator**: Weekly personalized financial memes
- **🗣️ Voice Input**: Speech-to-text for quick transaction entry
- **📊 Analytics Dashboard**: Charts and insights for spending patterns
- **🔐 Secure Authentication**: Google OAuth + Demo accounts with legal consent

### Multi-User Architecture
- **Complete Data Isolation**: Users only see their own transactions and data
- **Secure API Endpoints**: All APIs protected with authentication
- **User-Scoped Filtering**: Database queries automatically filtered by user
- **Scalable Design**: Supports thousands of concurrent users

## 🛠 Tech Stack

- **Backend**: Django 5.x + Django REST Framework
- **Frontend**: Django Templates + HTMx + Tailwind CSS
- **Database**: PostgreSQL (production) / SQLite (development)
- **AI**: Google Gemini API
- **Calendar**: FullCalendar.js
- **Charts**: Chart.js
- **Background Tasks**: Celery + Redis
- **Deployment**: Railway / PythonAnywhere
- **Authentication**: Google OAuth + Custom Demo System

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL (production) or SQLite (development)
- Redis (for background tasks)
- Google Gemini API key
- Google OAuth credentials (optional for OAuth login)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/money-tracking.git
cd money-tracking
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment setup**
```bash
cp env.example .env
# Edit .env with your configuration
```

5. **Database setup**
```bash
python manage.py migrate
python manage.py createsuperuser
```

6. **Run development server**
```bash
python manage.py runserver
```

### Environment Variables

Create a `.env` file in the project root:

```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost:5432/expense_tracker
GEMINI_API_KEY=your-gemini-api-key
REDIS_URL=redis://localhost:6379/0
LANGUAGE_CODE=vi
TIME_ZONE=Asia/Ho_Chi_Minh

# Multi-user settings
ENABLE_MULTI_USER=True
DEFAULT_USER_LIMIT=1000

# Google OAuth (optional)
GOOGLE_OAUTH_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-google-client-secret
```

## 📊 Project Structure

```
money-tracking/
├── docs/                   # Documentation files
│   ├── MULTI_USER_MIGRATION_PLAN.md
│   ├── LOGIN_IMPLEMENTATION_PLAN.md
│   └── GOOGLE_OAUTH_SETUP.md
├── scripts/                # Deployment and utility scripts
│   ├── build.sh           # Railway build script
│   ├── start.sh           # Railway start script
│   ├── migrate.sh         # Migration script
│   └── deploy_migrations.sh # Multi-user deployment
├── expense_tracker/        # Django configuration
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── authentication/        # User management and OAuth
├── transactions/          # Transaction models and APIs
├── ai_chat/              # AI integration and chat
├── static/               # CSS, JS, images
├── templates/            # Django templates
├── locale/               # Translation files
├── staticfiles/          # Collected static files (production)
├── requirements.txt
├── railway.toml          # Railway deployment config
└── README.md
```

## 🔐 Multi-User Architecture

### User Authentication
- **Google OAuth**: Secure authentication with Google accounts
- **Demo Accounts**: Temporary accounts for testing (auto-expire)
- **Legal Consent**: Terms of service and privacy policy acceptance
- **Session Management**: Secure session handling with CSRF protection

### Data Isolation
```python
# All API endpoints filter by current user
transactions = Transaction.objects.filter(user=request.user)
monthly_totals = MonthlyTotal.objects.filter(user=request.user)
chat_messages = ChatMessage.objects.filter(user=request.user)
```

### Security Features
- Authentication required for all data access
- User-scoped database queries
- CSRF protection on all forms
- Secure session cookies
- SQL injection prevention

## 🤖 AI Features

### Transaction Categorization
```python
# Example AI input/output
Input: "ăn trưa 50k"
Output: {
    "type": "expense",
    "category": "Ăn uống", 
    "amount": 50000,
    "confidence": 0.95,
    "user_id": "current_user"  # Automatically scoped
}
```

### Voice Input
- Web Speech API integration
- Vietnamese language support
- Real-time transcription
- User-specific conversation history

### Future Me Simulator
- Compound interest calculations
- Investment growth projections
- Scenario comparisons
- Goal-based planning
- Per-user personalized projections

## 🌍 Internationalization

The application supports Vietnamese and English:

```bash
# Generate translation files
python manage.py makemessages -l vi
python manage.py makemessages -l en

# Compile translations
python manage.py compilemessages
```

## 📱 API Documentation

API documentation is available at `/api/docs/` when running the development server.

### Key Endpoints (All require authentication)
- `GET /api/transactions/` - List user's transactions
- `POST /api/transactions/` - Create transaction for current user
- `GET /api/chat/calendar/{year}/{month}/` - Calendar data for user
- `POST /api/chat/process/` - AI categorization for user
- `GET /api/monthly-totals/` - User's monthly totals
- `POST /api/chat/confirm/` - Confirm AI-suggested transaction

### Authentication
```javascript
// All API calls require CSRF token and authentication
fetch('/api/transactions/', {
    headers: {
        'X-CSRFToken': getCSRFToken(),
        'Content-Type': 'application/json',
    },
    credentials: 'same-origin'
})
```

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=apps

# Test multi-user isolation
python manage.py test authentication.tests
python manage.py test transactions.tests
```

## 🚀 Deployment

### Railway Deployment (Recommended)

1. **Connect GitHub repository to Railway**
2. **Set environment variables in Railway dashboard**
3. **Deploy automatically on push to main branch**

Environment variables for Railway:
```env
DJANGO_SETTINGS_MODULE=expense_tracker.settings.production
DATABASE_URL=postgresql://...  # Provided by Railway
REDIS_URL=redis://...          # Provided by Railway
GEMINI_API_KEY=your-key
ENABLE_MULTI_USER=true
DEFAULT_USER_LIMIT=1000
```

### Manual Production Deployment

```bash
# Install production dependencies
pip install -r requirements.txt

# Set environment variables
export DJANGO_SETTINGS_MODULE=expense_tracker.settings.production

# Run migrations with multi-user support
chmod +x scripts/deploy_migrations.sh
./scripts/deploy_migrations.sh

# Collect static files
python manage.py collectstatic --noinput

# Start with gunicorn
gunicorn expense_tracker.wsgi:application
```

## 🔄 Migration to Multi-User

If upgrading from single-user version:

1. **Backup your database**
2. **Run migration script**:
```bash
chmod +x scripts/deploy_migrations.sh
./scripts/deploy_migrations.sh
```
3. **Verify data integrity**
4. **Update environment variables**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- All new APIs must include authentication
- Database queries must filter by user
- Write tests for multi-user scenarios
- Follow the established security patterns

## 📋 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋‍♀️ Support

- 📧 Email: support@money-tracking.app
- 📖 Documentation: `/docs/`
- 🐛 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions
