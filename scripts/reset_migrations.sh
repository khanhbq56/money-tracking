#!/bin/bash

# Reset migrations script for Railway deployment
# Fixes InconsistentMigrationHistory errors

set -e

echo "🔄 Resetting migrations to fix dependency issues..."

# First, delete migration tables data (but keep structure)
echo "🗄️ Cleaning migration history..."
python manage.py shell -c "
from django.db import connection
with connection.cursor() as cursor:
    # Clear migration history
    cursor.execute('DELETE FROM django_migrations WHERE app IN (\"admin\", \"auth\", \"contenttypes\", \"sessions\", \"authentication\", \"transactions\", \"ai_chat\");')
    print('✅ Migration history cleared')
"

# Apply migrations in correct order
echo "📊 Applying migrations in correct order..."

# 1. Core Django apps first
python manage.py migrate contenttypes --fake-initial
python manage.py migrate auth --fake-initial
python manage.py migrate sessions --fake-initial

# 2. Our custom authentication app
python manage.py migrate authentication --fake-initial

# 3. Admin (depends on auth)
python manage.py migrate admin --fake-initial

# 4. Our business logic apps
python manage.py migrate transactions
python manage.py migrate ai_chat

echo "✅ Migrations reset and applied successfully!"

# Verify migration status
echo "📋 Current migration status:"
python manage.py showmigrations 