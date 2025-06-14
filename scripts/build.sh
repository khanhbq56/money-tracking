#!/bin/bash
set -e

echo "🚀 Starting Railway build process with multi-user support..."

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

# Create staticfiles directory and collect static files
echo "📁 Creating staticfiles directory..."
mkdir -p staticfiles

echo "📁 Collecting static files..."
uv run python manage.py collectstatic --noinput --verbosity=2

echo "📋 Listing collected static files..."
ls -la staticfiles/
ls -la staticfiles/js/ || echo "No js directory found"
ls -la staticfiles/css/ || echo "No css directory found"

# Test database connection first
echo "🔌 Testing database connection..."
uv run python manage.py check --database default

# Make fresh migrations to ensure all models are included
echo "🔄 Making fresh migrations..."
uv run python manage.py makemigrations --verbosity=2 --dry-run
uv run python manage.py makemigrations --verbosity=2

# Run database migrations with error handling
echo "🗄️ Running database migrations..."
uv run python manage.py migrate --verbosity=2 --run-syncdb

# If migrations fail, try reset approach
if [ $? -ne 0 ]; then
    echo "⚠️ Standard migration failed, trying reset approach..."
    if [ -f "scripts/reset_migrations.sh" ]; then
        chmod +x scripts/reset_migrations.sh
        uv run bash scripts/reset_migrations.sh
    else
        echo "🔄 Fallback to migrate script..."
        uv run bash scripts/migrate.sh
    fi
fi

# Show migration status
echo "📊 Migration status:"
uv run python manage.py showmigrations

# Verify tables were created
echo "🔍 Verifying database tables..."
uv run python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'expense_tracker.settings.production')
django.setup()
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute(\"SELECT tablename FROM pg_tables WHERE schemaname = 'public';\")
    tables = cursor.fetchall()
    print('📋 Tables in database:')
    for table in tables:
        print(f'  ✅ {table[0]}')
"

# Run multi-user deployment verification
echo "🔐 Running multi-user deployment verification..."
if [ -f "scripts/deploy_migrations.sh" ]; then
    chmod +x scripts/deploy_migrations.sh
    uv run bash scripts/deploy_migrations.sh
else
    echo "⚠️ Multi-user deployment script not found, running basic setup..."
    
    # Create superuser if needed
    echo "👤 Setting up admin user..."
    uv run python manage.py shell -c "
from authentication.models import User
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        email='admin@money-tracking.app',
        password='admin123',
        first_name='Admin',
        last_name='User'
    )
    print('✅ Superuser created')
else:
    print('✅ Superuser already exists')
"
fi

# Create cache table
echo "💾 Creating cache table..."
uv run python manage.py createcachetable

# Compile translation files
echo "🌍 Compiling translation messages..."
uv run python manage.py compilemessages

echo "🎉 Multi-user build completed successfully!" 