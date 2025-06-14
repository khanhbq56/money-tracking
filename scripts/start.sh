#!/bin/bash
set -e

echo "🚀 Starting expense tracker application..."

# Ensure UV is available (fallback check)
if ! command -v uv &> /dev/null; then
    echo "📦 Installing UV for runtime..."
    pip install uv
fi

# Build script handles all migrations, so just start the server
echo "🌐 Starting gunicorn server..."
uv run gunicorn expense_tracker.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info

echo "🎉 Application started successfully!" 