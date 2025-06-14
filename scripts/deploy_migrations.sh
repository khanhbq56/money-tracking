#!/bin/bash

# Multi-user deployment migration script for Railway
# Ensures all multi-user migrations are applied correctly

set -e  # Exit on any error

echo "🚀 Starting multi-user deployment migrations..."

# Apply all migrations
echo "📊 Applying database migrations..."
python manage.py migrate --no-input

# Create superuser if needed (for admin access)
echo "👤 Setting up admin user..."
python manage.py shell -c "
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

# Verify multi-user setup
echo "🔍 Verifying multi-user setup..."
python manage.py shell -c "
from transactions.models import Transaction, MonthlyTotal
from ai_chat.models import ChatMessage
from authentication.models import User

# Check User model custom fields
user_has_google_id = hasattr(User, 'google_id')
user_has_demo_flag = hasattr(User, 'is_demo_user')
print(f'User.google_id field: {"✅" if user_has_google_id else "❌"}')
print(f'User.is_demo_user field: {"✅" if user_has_demo_flag else "❌"}')

# Check Transaction model
tx_has_user = hasattr(Transaction._meta.get_field('user'), 'related_model')
print(f'Transaction.user field: {"✅" if tx_has_user else "❌"}')

# Check MonthlyTotal model  
mt_has_user = hasattr(MonthlyTotal._meta.get_field('user'), 'related_model')
print(f'MonthlyTotal.user field: {"✅" if mt_has_user else "❌"}')

# Check ChatMessage model
cm_has_user = hasattr(ChatMessage._meta.get_field('user'), 'related_model')
print(f'ChatMessage.user field: {"✅" if cm_has_user else "❌"}')

print('🎉 Multi-user deployment verification complete!')
"

echo "✅ Multi-user deployment migrations completed successfully!" 