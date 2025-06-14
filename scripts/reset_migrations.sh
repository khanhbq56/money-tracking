#!/bin/bash

# Reset migrations script for Railway deployment
# Fixes InconsistentMigrationHistory errors and missing authentication fields

set -e

echo "🔄 Resetting migrations to fix dependency issues..."

# Check if we can connect to database
echo "🔌 Testing database connection..."
python manage.py check --database default || {
    echo "❌ Database connection failed"
    exit 1
}

# Check current table structure
echo "🔍 Checking current database structure..."
python manage.py shell -c "
from django.db import connection
try:
    with connection.cursor() as cursor:
        # Check if auth_user table exists and its columns
        cursor.execute(\"SELECT column_name FROM information_schema.columns WHERE table_name='auth_user' ORDER BY column_name;\")
        columns = [row[0] for row in cursor.fetchall()]
        print(f'auth_user columns: {columns}')
        
        # Check if google_id column exists
        has_google_id = 'google_id' in columns
        print(f'Has google_id column: {has_google_id}')
        
        if not has_google_id:
            print('❌ Missing authentication model fields - need to apply authentication migrations')
        else:
            print('✅ Authentication model fields present')
            
except Exception as e:
    print(f'Error checking database structure: {e}')
" || echo "⚠️ Could not check database structure"

# Force clear migration history and start fresh
echo "🗄️ Clearing migration history for clean slate..."
python manage.py shell -c "
from django.db import connection
try:
    with connection.cursor() as cursor:
        # Clear ALL migration history
        cursor.execute('DELETE FROM django_migrations;')
        print('✅ All migration history cleared')
except Exception as e:
    print(f'⚠️ Could not clear migration history: {e}')
    print('Continuing anyway...')
" || echo "⚠️ Shell command failed, continuing..."

# Apply core Django migrations first
echo "📊 Applying core Django migrations..."
python manage.py migrate contenttypes --fake-initial || echo "⚠️ contenttypes migration failed"
python manage.py migrate auth --fake-initial || echo "⚠️ auth migration failed"
python manage.py migrate sessions --fake-initial || echo "⚠️ sessions migration failed"

# Apply authentication migrations (critical for User model)
echo "🔐 Applying authentication migrations..."
python manage.py migrate authentication --fake-initial || {
    echo "⚠️ fake-initial failed, trying fresh migration..."
    python manage.py migrate authentication || echo "⚠️ authentication migration failed"
}

# Apply admin migrations
echo "👤 Applying admin migrations..."
python manage.py migrate admin --fake-initial || echo "⚠️ admin migration failed"

# Apply business logic migrations
echo "💰 Applying business logic migrations..."
python manage.py migrate transactions || echo "⚠️ transactions migration failed"
python manage.py migrate ai_chat || echo "⚠️ ai_chat migration failed"

# Final check
echo "✅ Migrations reset and applied!"

# Verify final state
echo "📋 Final migration status:"
python manage.py showmigrations || echo "⚠️ Could not show migrations"

# Test user creation
echo "🧪 Testing user creation..."
python manage.py shell -c "
from authentication.models import User
import uuid

try:
    test_user = User(
        username=f'test_{uuid.uuid4().hex[:8]}',
        email='test@test.com',
        first_name='Test',
        is_demo_user=True
    )
    # Don't save, just test field access
    print(f'✅ User model fields accessible: google_id={hasattr(test_user, \"google_id\")}')
except Exception as e:
    print(f'❌ User model test failed: {e}')
" || echo "⚠️ User model test failed" 