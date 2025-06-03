# 💰 Expense Tracker Web Application

A modern web application for personal finance tracking that replaces traditional Excel spreadsheets with AI-powered categorization and beautiful calendar visualization.

## 🌟 Features

### Core Functionality
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

## 🛠 Tech Stack

- **Backend**: Django 5.x + Django REST Framework
- **Frontend**: Django Templates + HTMx + Tailwind CSS
- **Database**: PostgreSQL
- **AI**: Google Gemini API
- **Calendar**: FullCalendar.js
- **Charts**: Chart.js
- **Background Tasks**: Celery + Redis
- **Deployment**: Railway / PythonAnywhere

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL
- Redis (for background tasks)
- Google Gemini API key

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
cp .env.example .env
# Edit .env with your configuration
```

5. **Database setup**
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py loaddata fixtures/categories.json
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
```

## 📊 Project Structure

```
money-tracking/
├── config/                 # Django configuration
│   ├── settings/
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── transactions/       # Transaction models and APIs
│   ├── analytics/          # Dashboard and reports
│   └── ai_features/        # AI integration and chat
├── static/                 # CSS, JS, images
├── templates/              # Django templates
├── locale/                 # Translation files
├── requirements.txt
└── README.md
```

## 🤖 AI Features

### Transaction Categorization
```python
# Example AI input/output
Input: "ăn trưa 50k"
Output: {
    "type": "expense",
    "category": "Ăn uống", 
    "amount": 50000,
    "confidence": 0.95
}
```

### Voice Input
- Web Speech API integration
- Vietnamese language support
- Real-time transcription

### Future Me Simulator
- Compound interest calculations
- Investment growth projections
- Scenario comparisons
- Goal-based planning

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

### Key Endpoints
- `GET /api/transactions/` - List transactions
- `POST /api/transactions/` - Create transaction
- `GET /api/transactions/calendar-data/` - Calendar formatted data
- `POST /api/ai/categorize/` - AI categorization
- `GET /api/analytics/dashboard/` - Dashboard data

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=apps
```

## 🚀 Deployment

### Railway Deployment

1. **Connect GitHub repository to Railway**
2. **Set environment variables in Railway dashboard**
3. **Deploy automatically on push to main branch**

### Manual Deployment

```bash
# Install production dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Start with gunicorn
gunicorn config.wsgi:application
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Gemini AI for natural language processing
- FullCalendar.js for calendar functionality
- Tailwind CSS for beautiful styling
- Django community for the amazing framework

## 📞 Support

If you have any questions or need help, please open an issue or contact [your-email@example.com].

---

Made with ❤️ for better personal finance management
