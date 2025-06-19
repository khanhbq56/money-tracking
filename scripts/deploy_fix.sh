#!/bin/bash

# Deploy Fix Script for Railway
# This script fixes common deployment issues

echo "🚀 Starting deployment fix..."

# 1. Run migrations to ensure schema is up to date
echo "📦 Running migrations..."
python manage.py migrate --verbosity=2

# 2. Run the schema fix command
echo "🔧 Running schema fix..."
python manage.py fix_monthly_totals_schema

# 3. Test that the API works
echo "🧪 Testing API endpoints..."
python manage.py shell -c "
from transactions.monthly_service import MonthlyTotalService
from authentication.models import User
import sys

try:
    user = User.objects.first()
    if user:
        totals = MonthlyTotalService.get_current_month_totals(user)
        print('✅ Monthly totals API working:', totals)
    else:
        print('⚠️ No users found for testing')
except Exception as e:
    print('❌ API test failed:', str(e))
    sys.exit(1)
"

# 4. Collect static files (if needed)
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --verbosity=0

echo "✅ Deployment fix completed successfully!" 