# API Endpoints Reference

## 📊 **Dashboard APIs (WORKING)**

### Monthly Totals
- **URL**: `/api/monthly-totals/`
- **Method**: GET
- **Status**: ✅ Working
- **Response**: 
```json
{
  "monthly_totals": {
    "expense": 300000.0,
    "saving": 200000.0, 
    "investment": 150000.0,
    "net_total": 650000.0
  },
  "formatted": {
    "expense": "-300,000₫",
    "saving": "+200,000₫",
    "investment": "+150,000₫", 
    "net_total": "+650,000₫"
  },
  "year": 2025,
  "month": 6
}
```

### Today Summary
- **URL**: `/api/today-summary/`
- **Method**: GET
- **Status**: ✅ Working
- **Response**:
```json
{
  "date": "2025-06-08",
  "transactions": [],
  "totals": {
    "expense": "-0₫",
    "saving": "+0₫", 
    "investment": "+0₫",
    "daily_total": "+0₫"
  },
  "transaction_count": 0
}
```

## 💰 **Transaction APIs**

### Transaction CRUD
- **URL**: `/api/transactions/`
- **Methods**: GET, POST, PUT, DELETE
- **Status**: ✅ Working

### Calendar Data  
- **URL**: `/api/calendar-data/`
- **Method**: GET
- **Status**: ❌ 500 Error (needs fixing)

## 🔮 **Future Projection APIs**

### Future Projection
- **URL**: `/api/future-projection/?months=12`
- **Method**: GET
- **Status**: ✅ Working

### Monthly Analysis
- **URL**: `/api/monthly-analysis/?year=2025&month=6`
- **Method**: GET  
- **Status**: ✅ Working

## 🤖 **AI Chat APIs**

### Weekly Meme
- **URL**: `/api/ai_chat/meme/weekly/`
- **Method**: GET
- **Status**: ✅ Working

### Monthly Totals (AI)
- **URL**: `/api/ai_chat/monthly-totals/`
- **Method**: GET
- **Status**: ❌ 500 Error (import issue)

### Chat Processing
- **URL**: `/api/chat/process/`
- **Method**: POST
- **Status**: ✅ Working

## 🔧 **URL Mapping Structure**

```
Main URLs (expense_tracker/urls.py):
├── path('api/', include('transactions.api_urls'))  → /api/...
├── path('api/ai_chat/', include('ai_chat.urls'))   → /api/ai_chat/...
├── path('api/meme/', include('ai_chat.urls'))      → /api/meme/... (alias)
└── path('api/chat/', include('ai_chat.urls'))      → /api/chat/... (alias)

Transaction API URLs (transactions/api_urls.py):
├── path('transactions/', ...)                      → /api/transactions/
├── path('monthly-totals/', ...)                    → /api/monthly-totals/
├── path('today-summary/', ...)                     → /api/today-summary/
├── path('calendar-data/', ...)                     → /api/calendar-data/
├── path('future-projection/', ...)                 → /api/future-projection/
└── path('monthly-analysis/', ...)                  → /api/monthly-analysis/

AI Chat URLs (ai_chat/urls.py):
├── path('meme/weekly/', ...)                       → /api/ai_chat/meme/weekly/
├── path('monthly-totals/', ...)                    → /api/ai_chat/monthly-totals/
└── path('chat/process/', ...)                      → /api/ai_chat/chat/process/
```

## ⚠️ **Common 404 Errors to Avoid**

### ❌ Wrong URLs:
- `/api/transactions/monthly-totals/` (doesn't exist)
- `/api/transactions/today-summary/` (doesn't exist)
- `/api/meme/weekly/` (alias not working)

### ✅ Correct URLs:
- `/api/monthly-totals/` 
- `/api/today-summary/`
- `/api/ai_chat/meme/weekly/`

## 🧪 **Testing Commands**

```bash
# Test dashboard APIs
python -c "import requests; print(requests.get('http://127.0.0.1:8000/api/monthly-totals/').json())"
python -c "import requests; print(requests.get('http://127.0.0.1:8000/api/today-summary/').json())"

# Run full test suite
python test_api_endpoints.py
```

## 📱 **Frontend Usage**

### Dashboard.js
```javascript
// ✅ Correct API calls
const monthlyData = await fetch('/api/monthly-totals/');
const todayData = await fetch('/api/today-summary/');

// ❌ Wrong API calls (will cause 404)
const wrongData = await fetch('/api/transactions/monthly-totals/'); // Don't use!
```

## 🔄 **Real-time Updates**

When transactions are added/updated, dashboard automatically refreshes via:
1. Event bus system (`window.eventBus`)
2. `transactionAdded` events trigger dashboard refresh
3. Auto-refresh every 30 seconds

## 🛡️ **Error Prevention**

1. **Always use `test_api_endpoints.py`** before deploying
2. **Check URL patterns** in both main and app-specific URLs
3. **Verify includes** in main `urls.py` 
4. **Test with real HTTP calls** not just Django URL reverse

---

*Last updated: 2025-06-08* 