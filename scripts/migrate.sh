#!/bin/bash
set -e

echo "🔧 Manual Database Migration Script"
echo "=================================="

# Check if we have DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL not found!"
    echo "Available environment variables:"
    env | grep -E "(DATABASE|PG)" || echo "No database variables found"
    exit 1
else
    echo "✅ DATABASE_URL found: ${DATABASE_URL:0:20}..."
fi

# Test database connection
echo "🔌 Testing database connection..."
python manage.py check --database default

# Show current migration status
echo "📊 Current migration status:"
python manage.py showmigrations

# Make sure we have fresh migrations
echo "🔄 Creating fresh migrations..."
python manage.py makemigrations transactions
python manage.py makemigrations ai_chat

# Run migrations with verbose output
echo "🗄️ Running migrations..."
python manage.py migrate --verbosity=2

# Verify tables exist
echo "🔍 Verifying tables were created..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'expense_tracker.settings.production')
django.setup()
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT tablename FROM pg_tables WHERE schemaname = %s ORDER BY tablename;', ['public'])
        tables = cursor.fetchall()
        print('📋 Tables in PostgreSQL database:')
        for table in tables:
            print(f'  ✅ {table[0]}')
        
        # Test specific tables we need
        required_tables = ['transactions_transaction', 'ai_chat_chatmessage']
        for table in required_tables:
            cursor.execute('SELECT COUNT(*) FROM %s;' % table)
            count = cursor.fetchone()[0]
            print(f'  🔢 {table}: {count} records')
            
except Exception as e:
    print(f'❌ Error checking tables: {e}')
    raise
"

echo "✅ Migration completed successfully!" 