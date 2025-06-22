# Railway Deployment Guide - Currency Parsing & Force Refresh Features

## Overview
Hướng dẫn deploy tính năng Currency Parsing và Force Refresh mới lên Railway production environment.

## Pre-deployment Checklist

### ✅ **1. Code Changes Verification**
- [x] Currency parsing improvements in `bank_email_parser.py`
- [x] Force refresh support in `bank_integration_service.py`  
- [x] Frontend enhancements in `bank-integration.js`
- [x] New database migration `0006_add_custom_bank_support.py`
- [x] Enhanced currency service `currency_service.py`

### ✅ **2. Database Migrations**
New migration includes:
```sql
-- Update BankEmailTransaction model with new fields
-- Add indexes for better query performance
-- Update UserBankConfig with additional options
```

### ✅ **3. Environment Variables**
Cần verify các environment variables sau trong Railway:

```env
# Gemini AI (for currency parsing)
GEMINI_API_KEY=your_gemini_api_key

# Exchange Rate API (for USD→VND conversion)  
EXCHANGE_RATE_API_KEY=your_exchange_rate_api_key
EXCHANGE_RATE_BASE_URL=https://api.exchangerate-api.com/v4/latest/

# Gmail OAuth (existing)
GOOGLE_OAUTH_CLIENT_ID=your_client_id
GOOGLE_OAUTH_CLIENT_SECRET=your_client_secret
GOOGLE_OAUTH_REDIRECT_URI=https://your-domain.railway.app/auth/oauth/google/callback/

# Database (Railway auto-configured)
DATABASE_URL=postgresql://...

# Django Settings
DEBUG=False
ALLOWED_HOSTS=your-domain.railway.app,*.railway.app
SECRET_KEY=your_secret_key
```

## Railway Deployment Steps

### **Step 1: Verify Railway Environment**

```bash
# 1. Check Railway CLI installation
railway version

# 2. Login to Railway
railway login

# 3. Connect to your project
railway link [your-project-id]
```

### **Step 2: Environment Variables Setup**

```bash
# Add/update environment variables
railway variables set GEMINI_API_KEY=your_gemini_api_key
railway variables set EXCHANGE_RATE_API_KEY=your_exchange_rate_api_key

# Verify all variables are set
railway variables
```

### **Step 3: Deploy Code**

```bash
# Option A: Auto-deploy (if GitHub integration enabled)
# Just push to main branch, Railway will auto-deploy

# Option B: Manual deploy via Railway CLI
railway up
```

### **Step 4: Run Database Migrations**

```bash
# Connect to Railway shell
railway shell

# Inside Railway container:
python manage.py migrate

# Verify migration status
python manage.py showmigrations transactions
```

Expected output:
```
transactions
 [X] 0001_initial
 [X] 0002_transaction_user  
 [X] 0003_add_user_to_monthly_total
 [X] 0004_alter_monthlytotal_user_alter_transaction_user
 [X] 0005_add_bank_integration_models
 [X] 0006_add_custom_bank_support
```

### **Step 5: Collect Static Files**

```bash
# Inside Railway container:
python manage.py collectstatic --noinput
```

### **Step 6: Verify Deployment**

#### **A. Health Check**
```bash
curl https://your-domain.railway.app/health/
```

#### **B. Bank Integration Test**
1. Login to your app
2. Go to Settings → Bank Integration
3. Test Gmail connection
4. Try TPBank sync preview với force refresh
5. Verify currency conversion works correctly

#### **C. Currency API Test**
```bash
# Inside Railway shell:
python manage.py shell

# Test currency service:
>>> from transactions.currency_service import CurrencyService
>>> cs = CurrencyService()
>>> cs.get_usd_to_vnd_rate()
26111.9873
>>> cs.convert_usd_to_vnd(11)
287231.86
```

## Post-Deployment Testing

### **1. Currency Parsing Test**
Test với các loại transactions:

```
✅ Foreign merchants (USD):
   - FS *SUPERCELLSTORE: $11 → 287,230 VND  
   - AMZN: $25 → 652,800 VND
   - GOOGLE PLAY: $5 → 130,560 VND

✅ Vietnamese merchants (VND):
   - SHOPEEPAY: 50,000 VND
   - GRABPAY: 120,000 VND
   - MOMO: 75,000 VND
```

### **2. Force Refresh Test**
1. Sync tháng 5/2025 lần đầu
2. Enable force refresh checkbox  
3. Sync lại → should reprocess existing emails
4. Verify transactions appear in calendar

### **3. Error Handling Test**
1. Test với invalid dates
2. Test với malformed email content
3. Test với network failures (currency API down)

## Rollback Plan

Nếu có vấn đề sau deployment:

### **Option 1: Quick Rollback**
```bash
# Rollback to previous deployment
railway rollback [previous-deployment-id]
```

### **Option 2: Disable New Features**
```bash
# Temporarily disable bank integration
railway variables set BANK_INTEGRATION_ENABLED=False

# Or disable specific features
railway variables set FORCE_REFRESH_ENABLED=False
railway variables set CURRENCY_CONVERSION_ENABLED=False
```

### **Option 3: Database Rollback**
```bash
# Rollback migration if needed (CAREFUL!)
railway shell
python manage.py migrate transactions 0005
```

## Monitoring & Logs

### **Check Deployment Logs**
```bash
# View real-time logs
railway logs

# Filter for currency parsing
railway logs --filter "Currency debug"

# Filter for import issues  
railway logs --filter "Import"
```

### **Key Metrics to Monitor**
1. **Currency Detection Accuracy**: Should be 95%+
2. **Import Success Rate**: Should be near 100%
3. **API Response Times**: Currency API calls
4. **Error Rates**: Failed parsing, import errors

## Troubleshooting Common Issues

### **Issue 1: Currency API Timeout**
```bash
# Check API key and connectivity
curl "https://api.exchangerate-api.com/v4/latest/USD"

# Verify environment variable
railway variables | grep EXCHANGE_RATE
```

### **Issue 2: Force Refresh Not Working**
```bash
# Check frontend sends correct parameter
railway logs --filter "force_refresh"

# Verify backend processes parameter
railway logs --filter "Force refresh mode"
```

### **Issue 3: Migration Failures**
```bash
# Check migration status
railway shell
python manage.py showmigrations --plan

# Manual migration if needed
python manage.py migrate transactions 0006 --fake
```

### **Issue 4: Currency Parsing Wrong**
```bash
# Test AI parsing directly
railway shell
python manage.py shell

>>> from transactions.bank_email_parser import BankEmailAIParser
>>> parser = BankEmailAIParser()
>>> # Test with sample email content
```

## Success Criteria

✅ **Deployment considered successful when**:
1. All migrations applied successfully
2. Currency detection working (USD vs VND)
3. Force refresh functional in preview mode
4. Import process handles existing records
5. UI displays currency conversion correctly
6. No critical errors in logs for 1 hour

## Emergency Contacts

- **Railway Support**: support@railway.app
- **GitHub Repository**: https://github.com/khanhbq56/money-tracking
- **API Status Pages**:
  - Exchange Rate API: https://exchangerate-api.com/
  - Google APIs: https://status.cloud.google.com/

## Next Steps After Deployment

1. **Monitor performance** for 24-48 hours
2. **Collect user feedback** on currency accuracy  
3. **Update documentation** based on production experience
4. **Plan next enhancements** (multi-currency support, etc.)

---

**Deployment Date**: [Fill when deployed]  
**Deployed By**: [Your name]  
**Version**: Currency Parsing v1.0 (commit: 5224c19) 