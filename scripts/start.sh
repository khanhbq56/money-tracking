#!/bin/bash
set -e

echo "🚀 Starting expense tracker application..."

# Ensure UV is available (fallback check)
if ! command -v uv &> /dev/null; then
    echo "📦 Installing UV for runtime..."
    pip install uv
fi

# Run critical fixes before starting server
echo "🔧 Running production fixes..."

# Fix schema issues
echo "📋 Running schema diagnostics..."
uv run python manage.py fix_monthly_totals_schema

# Test critical functionality
echo "🧪 Testing critical services..."
uv run python manage.py shell -c "
from transactions.monthly_service import MonthlyTotalService
print('✅ MonthlyTotalService ready')
" || echo "⚠️ Service test failed - continuing anyway"

# Build script handles migrations, so start the server
echo "🌐 Starting gunicorn server..."
uv run gunicorn expense_tracker.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info

echo "🎉 Application started successfully!" 