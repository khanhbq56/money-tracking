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
- **📅 Calendar Interface**: FullCalendar.js integration with color-coded transactions
- **🎯 Future Projection**: Interactive scenarios and financial planning
- **🗣️ Voice Input**: Speech-to-text for quick transaction entry

### 🌍 User Experience
- **Multi-Language Support**: Vietnamese and English localization
- **📱 Mobile-First Design**: Responsive design with Tailwind CSS
- **🎨 AI Meme Generator**: Weekly personalized financial memes
- **📊 Analytics Dashboard**: Charts and insights for spending patterns

## 🛠 Technology Stack

- **Backend**: Django 5.x + Django REST Framework
- **Package Manager**: UV (ultrafast Python package installer)
- **Frontend**: Django Templates + Tailwind CSS + JavaScript
- **Database**: PostgreSQL (production) / SQLite (development)
- **AI**: Google Gemini API
- **Calendar**: FullCalendar.js
- **Charts**: Chart.js
- **Authentication**: Google OAuth + Custom Demo System
- **Deployment**: Railway.app

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
│   ├── MULTI_USER_MIGRATION_PLAN.md
│   ├── LOGIN_IMPLEMENTATION_PLAN.md
│   └── GOOGLE_OAUTH_SETUP.md
├── scripts/                        # 🔧 Deployment Scripts
│   ├── build.sh                   # Railway build script
│   ├── start.sh                   # Railway start script
│   ├── migrate.sh                 # Database migration
│   └── deploy_migrations.sh       # Multi-user deployment
├── expense_tracker/                # ⚙️ Django Configuration
│   ├── settings/
│   │   ├── base.py               # Base settings
│   │   ├── development.py        # Development settings
│   │   └── production.py         # Production settings
│   ├── urls.py                   # URL routing
│   └── wsgi.py                   # WSGI application
├── authentication/                 # 🔐 User Management
├── transactions/                   # 💰 Transaction Management
├── ai_chat/                       # 🤖 AI Integration
├── static/                        # 🎨 Static Assets
├── templates/                     # 📄 HTML Templates
├── locale/                        # 🌍 Translations
├── staticfiles/                   # 📁 Collected Static Files
├── requirements.txt               # 📦 Python Dependencies
├── pyproject.toml                 # 🔧 UV Configuration
├── railway.toml                   # 🚀 Railway Config
└── README.md                      # 📋 This File
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
- `GET /api/transactions/` - List user's transactions
- `POST /api/transactions/` - Create transaction for current user
- `GET /api/chat/calendar/{year}/{month}/` - Calendar data for user
- `POST /api/chat/process/` - AI categorization for user
- `GET /api/monthly-totals/` - User's monthly totals
- `POST /api/chat/confirm/` - Confirm AI-suggested transaction

## 🧪 Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=.

# Test specific app
uv run python manage.py test authentication
uv run python manage.py test transactions

# Test multi-user isolation
uv run python manage.py test authentication.tests.MultiUserIsolationTestCase
```

## 🚀 Deployment

### Railway Deployment (Recommended)

1. **Fork this repository**
2. **Connect to Railway**
   - Go to [Railway.app](https://railway.app)
   - Create new project from GitHub repo
3. **Set environment variables**:
   ```env
   DJANGO_SETTINGS_MODULE=expense_tracker.settings.production
   GEMINI_API_KEY=your-gemini-key
   ENABLE_MULTI_USER=true
   DEFAULT_USER_LIMIT=1000
   ```
4. **Deploy automatically** - Railway will use `railway.toml` configuration

### Manual Production Deployment

```bash
# Install dependencies
uv sync --frozen

# Set production environment
export DJANGO_SETTINGS_MODULE=expense_tracker.settings.production

# Run deployment migrations
chmod +x scripts/deploy_migrations.sh
uv run ./scripts/deploy_migrations.sh

# Collect static files
uv run python manage.py collectstatic --noinput

# Start with gunicorn
uv run gunicorn expense_tracker.wsgi:application
```

### Migration from Single-User Version

If upgrading from v1.x:

```bash
# 1. Backup your database
pg_dump your_database > backup.sql

# 2. Run migration script
chmod +x scripts/deploy_migrations.sh
uv run ./scripts/deploy_migrations.sh

# 3. Verify data integrity
uv run python manage.py shell -c "
from transactions.models import Transaction
print(f'Total transactions: {Transaction.objects.count()}')
print(f'Users with transactions: {Transaction.objects.values_list(\"user\", flat=True).distinct().count()}')
"
```

## 📊 Performance

### Optimizations
- **Database**: Connection pooling and optimized queries
- **Caching**: Redis support for production
- **Static Files**: Whitenoise for efficient serving
- **Compression**: Gzip compression enabled
- **Indexes**: Database indexes on user foreign keys

### Monitoring
```bash
# Check application health
curl https://your-app.railway.app/health/

# Monitor logs
railway logs --tail

# Check database connections
uv run python manage.py dbshell -c "SELECT count(*) FROM pg_stat_activity;"
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Install development dependencies**
   ```bash
   uv sync --dev
   ```
4. **Make your changes**
5. **Run tests**
   ```bash
   uv run pytest
   ```
6. **Commit your changes**
   ```bash
   git commit -m 'Add amazing feature'
   ```
7. **Push to your branch**
   ```bash
   git push origin feature/amazing-feature
   ```
8. **Open a Pull Request**

### Development Guidelines
- All new APIs must include authentication
- Database queries must filter by user
- Write tests for multi-user scenarios
- Follow the established security patterns
- Use UV for dependency management

## 📋 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♀️ Support & Community

- 📧 **Email**: support@money-tracking.app
- 📖 **Documentation**: Browse the `/docs/` folder
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/yourusername/money-tracking/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/money-tracking/discussions)
- 🚀 **Feature Requests**: [GitHub Issues](https://github.com/yourusername/money-tracking/issues/new)

## 🏆 Acknowledgments

- **Google Gemini AI** for natural language processing
- **Railway.app** for seamless deployment
- **UV** for ultrafast Python package management
- **Django Community** for the amazing framework
- **Tailwind CSS** for beautiful styling
- **FullCalendar.js** for calendar functionality

---

**Made with ❤️ for better personal finance management**

*Transform your financial tracking from spreadsheets to AI-powered insights!*
