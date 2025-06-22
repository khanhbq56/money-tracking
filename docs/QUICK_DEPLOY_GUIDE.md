# 🚀 Quick Deploy Guide - Currency Parsing Features

## Before You Start
✅ Code đã được push lên GitHub (commit 5224c19)  
✅ Railway project đã connected với GitHub repo  
✅ Railway CLI installed: `npm install -g @railway/cli`

## 1. Set Environment Variables

```bash
# Required for currency parsing
railway variables set GEMINI_API_KEY=your_gemini_api_key
railway variables set EXCHANGE_RATE_API_KEY=your_exchange_rate_api_key

# Verify existing variables
railway variables | grep -E "(GOOGLE_OAUTH|DATABASE_URL)"
```

## 2. Deploy & Migrate

```bash
# Auto-deploy via GitHub (if enabled) OR manual deploy
railway up

# Run migrations
railway run python manage.py migrate

# Collect static files  
railway run python manage.py collectstatic --noinput
```

## 3. Quick Test

```bash
# Health check
curl https://your-domain.railway.app/health/

# Currency service test
railway run python -c "
from transactions.currency_service import CurrencyService
print('Rate:', CurrencyService().get_usd_to_vnd_rate())
"
```

## 4. UI Testing Checklist

1. **Login** → Settings → Bank Integration
2. **TPBank sync** with "Force refresh" checked
3. **Verify**: Supercell transactions show as USD → VND conversion
4. **Check**: Transactions appear in calendar UI

## If Problems Occur

```bash
# View logs
railway logs --filter "Currency\|Import\|Error"

# Rollback if needed
railway rollback [previous-deployment-id]

# Shell access for debugging
railway shell
```

## Success Indicators

✅ Migration `0006_add_custom_bank_support` applied  
✅ Currency parsing: `$11 USD → 287,230 VND`  
✅ Force refresh works in preview mode  
✅ Import handles existing records without errors  
✅ No critical logs for 1+ hour  

**That's it!** 🎉 Your currency parsing features are live.

---
*For detailed troubleshooting, see `CURRENCY_PARSING_RAILWAY_DEPLOYMENT.md`* 