#!/bin/bash

# Railway Production Start Script
# This script runs before starting the Django server

echo "🚀 Railway Production Start - Running fixes..."

# 1. Apply migrations
echo "📦 Applying migrations..."
python manage.py migrate --verbosity=2

# 2. Run schema fix
echo "🔧 Running schema fix..."
python manage.py fix_monthly_totals_schema

# 3. Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# 4. Test critical functionality
echo "🧪 Testing critical functions..."
python manage.py shell -c "
from transactions.monthly_service import MonthlyTotalService
from authentication.models import User
print('✅ Services import successfully')
if User.objects.exists():
    user = User.objects.first()
    try:
        totals = MonthlyTotalService.get_current_month_totals(user)
        print(f'✅ Monthly totals API working: {totals}')
    except Exception as e:
        print(f'❌ Monthly totals error: {e}')
else:
    print('⚠️ No users found for testing')
"

echo "✅ Pre-start checks completed!"

# 5. Start the server
echo "🌟 Starting Django server..."
python -m gunicorn expense_tracker.wsgi:application --bind 0.0.0.0:$PORT 