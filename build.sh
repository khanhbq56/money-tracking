#!/bin/bash
set -e

echo "🚀 Starting Railway build process..."

# Check if UV is installed, install if not
if ! command -v uv &> /dev/null; then
    echo "📦 UV not found, installing via pip..."
    pip install uv
    echo "✅ UV installed successfully"
else
    echo "✅ UV already available"
fi

# Install dependencies with UV
echo "📥 Installing dependencies with UV..."
uv sync --frozen

# Collect static files
echo "📁 Collecting static files..."
uv run python manage.py collectstatic --noinput

# Run database migrations
echo "🗄️ Running database migrations..."
uv run python manage.py migrate

# Compile translation files
echo "🌍 Compiling translation messages..."
uv run python manage.py compilemessages

echo "🎉 Build completed successfully!" 