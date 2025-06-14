#!/bin/bash
set -e

echo "🚀 Starting expense tracker application..."

# Ensure UV is available (fallback check)
if ! command -v uv &> /dev/null; then
    echo "📦 Installing UV for runtime..."
    pip install uv
fi

# CRITICAL: Ensure migrations are run before starting server
echo "🔄 Checking database migrations..."
if [ ! -z "$DATABASE_URL" ]; then
    echo "📡 PostgreSQL detected, ensuring migrations..."
    uv run python manage.py migrate --verbosity=1 || {
        echo "⚠️ Standard migration failed, trying manual approach..."
        chmod +x migrate.sh
        uv run bash migrate.sh
    }
    echo "✅ Database migrations completed"
else
    echo "⚠️ No DATABASE_URL found, skipping migrations"
fi

# Start the application with gunicorn via UV
echo "🌐 Starting gunicorn server..."
uv run gunicorn expense_tracker.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info

echo "🎉 Application started successfully!" 