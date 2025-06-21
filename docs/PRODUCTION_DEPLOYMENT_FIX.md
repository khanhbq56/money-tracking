# Production Deployment Fix Guide

## Issue Description

The production deployment was failing with database schema errors:

```
psycopg2.errors.UndefinedColumn: column transactions_monthlytotal.total_amount does not exist
```

This occurred because:
1. Migration 0005 changed field names in `MonthlyTotal` model
2. Code was updated to use new field names, but some service files still used old names
3. Production database schema was inconsistent

## Root Cause

**Field Name Changes in Migration 0005:**
- `total_expense` → `expense_amount`
- `total_saving` → `saving_amount` 
- `total_investment` → `investment_amount`
- `net_total` (removed) → `total_amount` (added)
- `last_updated` → `updated_at`

**Files using old field names:**
- `transactions/monthly_service.py`
- `transactions/serializers.py`

## Solution Applied

### 1. Code Fixes

**Fixed `transactions/monthly_service.py`:**
```python
# OLD (causing errors)
defaults={
    'total_expense': expense_total,
    'total_saving': saving_total,
    'total_investment': investment_total,
    'net_total': net_total
}

# NEW (correct)
defaults={
    'expense_amount': expense_total,
    'saving_amount': saving_total,
    'investment_amount': investment_total,
    'total_amount': net_total,
    'transaction_count': transactions.count()
}
```

**Fixed `transactions/serializers.py`:**
```python
# Updated field names and property access
fields = [
    'year', 'month', 'expense_amount', 'saving_amount',
    'investment_amount', 'total_amount', 'transaction_count', 'updated_at',
    # ...
]
```

### 2. Database Schema Fix Command

Created `transactions/management/commands/fix_monthly_totals_schema.py`:

```bash
# Run this command on production to diagnose and fix schema issues
python manage.py fix_monthly_totals_schema
```

**Features:**
- ✅ Supports both SQLite (development) and PostgreSQL (production)
- ✅ Diagnoses current database schema
- ✅ Shows applied migrations
- ✅ Identifies field name mismatches
- ✅ Tests MonthlyTotal creation
- ✅ Auto-applies missing migrations

### 3. Deployment Fix Script

Created `scripts/deploy_fix.sh`:

```bash
# Complete deployment fix process
bash scripts/deploy_fix.sh
```

**What it does:**
1. Runs all migrations
2. Fixes schema issues
3. Tests API functionality
4. Collects static files

## Deployment Instructions

### For Railway Production:

1. **Run the deploy fix script:**
   ```bash
   bash scripts/deploy_fix.sh
   ```

2. **Or run commands manually:**
   ```bash
   # Apply migrations
   python manage.py migrate --verbosity=2
   
   # Fix schema issues
   python manage.py fix_monthly_totals_schema
   
   # Test API
   python manage.py shell -c "from transactions.monthly_service import MonthlyTotalService; print('OK')"
   ```

### Expected Output:

```
🚀 Starting deployment fix...
📦 Running migrations...
Operations to perform:
  Apply all migrations: transactions, authentication, ai_chat
Running migrations:
  No migrations to apply.

🔧 Running schema fix...
📋 Current columns: expense_amount, investment_amount, saving_amount, total_amount, transaction_count, updated_at, user_id, year, month, id
📁 Applied migrations: 0001_initial, 0002_transaction_user, 0003_add_user_to_monthly_total, 0004_alter_monthlytotal_user_alter_transaction_user, 0005_add_bank_integration_models
✅ Database schema is correct
✅ MonthlyTotal test successful

🧪 Testing API endpoints...
✅ Monthly totals API working: {'expense': 0, 'saving': 0, 'investment': 0, 'net_total': 0}

📁 Collecting static files...
✅ Deployment fix completed successfully!
```

## Verification

After deployment, verify the fixes work:

1. **Check API endpoints:**
   ```bash
   curl https://your-app.railway.app/api/monthly-totals/
   ```

2. **Check database schema:**
   ```bash
   python manage.py fix_monthly_totals_schema
   ```

3. **Test transaction creation:**
   - Login to the app
   - Create a test transaction
   - Verify monthly totals update correctly

## Prevention

To prevent similar issues in the future:

1. **Migration Process:**
   - Always test migrations in staging environment first
   - Run `python manage.py check` before deployment
   - Review field name changes carefully

2. **Code Reviews:**
   - Check for hardcoded field names in services
   - Use model properties instead of direct field access when possible
   - Add tests for critical database operations

3. **Deployment Testing:**
   - Run schema fix command as part of CI/CD
   - Test API endpoints after migration
   - Monitor error logs during deployment

## Related Files

- `transactions/models.py` - MonthlyTotal model definition
- `transactions/migrations/0005_add_bank_integration_models.py` - Migration that changed field names
- `transactions/monthly_service.py` - Service using the model (fixed)
- `transactions/serializers.py` - API serializers (fixed)
- `transactions/management/commands/fix_monthly_totals_schema.py` - Diagnostic tool
- `scripts/deploy_fix.sh` - Complete deployment fix script

## Commit History

- `35cbc5f` - Fix MonthlyTotal field name mismatch and database schema issues
- `e4e7035` - Add deployment fix script to resolve production schema issues  
- `d9cd1af` - Add SQLite support to schema fix command 

## Critical Production Issues Fixed

### 1. ❌ Gmail OAuth Redirect Issue (FIXED)

**Problem**: When deployed, Gmail bank integration redirects to localhost instead of production domain.

**Root Cause**: 
- `SITE_URL` environment variable missing in production
- Gmail OAuth uses `SITE_URL` for redirect URI instead of `GOOGLE_OAUTH2_REDIRECT_URI`
- Default `SITE_URL` is `http://localhost:8000`

**Solution**: 
1. Add `SITE_URL=https://money-tracking-production.up.railway.app` to Railway environment variables
2. Update Google Cloud Console OAuth redirect URIs to include both:
   - `https://money-tracking-production.up.railway.app/auth/oauth/google/callback/` (Login OAuth)
   - `https://money-tracking-production.up.railway.app/auth/oauth/google/callback/` (Gmail OAuth - same endpoint)

**Files Changed**:
- `docs/railway-env-fix.txt` - Added `SITE_URL` configuration

### 2. ✅ Monthly Totals Schema Fix (COMPLETED)

**Problem**: Production database missing `user_id` column in `monthly_totals` table.

**Root Cause**: Migration 0003 added `user` field but wasn't applied in production.

**Solution**: 
1. Created `fix_monthly_totals_schema.py` management command
2. Added proper error handling and schema validation
3. Updated `MonthlyTotalSerializer` to handle both old and new schemas

**Files Changed**:
- `transactions/management/commands/fix_monthly_totals_schema.py` - New management command
- `transactions/serializers.py` - Backwards compatibility for schemas
- `transactions/monthly_service.py` - User-aware monthly calculations

### 3. ✅ Multi-User Deployment Scripts (COMPLETED)

**Problem**: Railway deployment scripts not optimized for multi-user production.

**Solution**:
1. Updated `railway-start.sh` with proper multi-user migration sequence
2. Created `scripts/deploy_fix.sh` for one-time production fixes
3. Enhanced error handling and logging

**Files Changed**:
- `railway-start.sh` - Multi-user deployment sequence
- `scripts/deploy_fix.sh` - Production fix automation
- `scripts/start.sh` - Local development improvements

## Next Deployment Steps

### 1. Update Railway Environment Variables

Add this to your Railway project environment variables:
```
SITE_URL=https://money-tracking-production.up.railway.app
```

### 2. Update Google Cloud Console

In your Google Cloud Console OAuth configuration:
1. Go to "Credentials" → Your OAuth 2.0 Client ID
2. Add to "Authorized redirect URIs":
   ```
   https://money-tracking-production.up.railway.app/auth/oauth/google/callback/
   ```
3. Save changes

### 3. Deploy and Test

1. Deploy to Railway with updated environment variables
2. Test login OAuth (should work as before)  
3. Test Gmail OAuth for bank integration (should now redirect correctly)

## Testing Checklist

- [ ] User can log in with Google OAuth
- [ ] Settings page loads correctly
- [ ] Gmail permission request redirects to production domain (not localhost)
- [ ] Bank integration enables/disables properly
- [ ] Monthly totals display correctly for all users
- [ ] No database schema errors in logs

## Monitoring

Monitor these logs after deployment:
- Gmail OAuth initiation and callback logs
- Database schema validation logs
- User authentication and session logs
- Bank integration enable/disable logs

---

**Status**: Ready for production deployment
**Last Updated**: Current deployment
**Priority**: HIGH - Fixes critical OAuth redirect issue