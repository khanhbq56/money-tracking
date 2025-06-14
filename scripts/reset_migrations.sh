#!/bin/bash

# Reset migrations script for Railway deployment
# Fixes InconsistentMigrationHistory errors

set -e

echo "🔄 Resetting migrations to fix dependency issues..."

# Check if we can connect to database
echo "🔌 Testing database connection..."
python manage.py check --database default || {
    echo "❌ Database connection failed"
    exit 1
}

# First, try to fake all initial migrations
echo "🗄️ Attempting to fake initial migrations..."
python manage.py migrate --fake-initial || {
    echo "⚠️ Fake initial failed, clearing migration history..."
    
    # Clear migration history for problematic apps
    python manage.py shell -c "
from django.db import connection
try:
    with connection.cursor() as cursor:
        # Clear migration history for specific apps causing issues
        cursor.execute('DELETE FROM django_migrations WHERE app IN (\"admin\", \"auth\", \"contenttypes\", \"sessions\", \"authentication\", \"transactions\", \"ai_chat\");')
        print('✅ Migration history cleared')
except Exception as e:
    print(f'⚠️ Could not clear migration history: {e}')
    print('Continuing with force sync...')
" || echo "⚠️ Shell command failed, continuing..."

    # Force sync database structure
    echo "🔧 Force syncing database..."
    python manage.py migrate --run-syncdb --fake-initial
}

echo "✅ Migrations reset and applied successfully!"

# Verify migration status
echo "📋 Final migration status:"
python manage.py showmigrations || echo "⚠️ Could not show migrations, but continuing..." 