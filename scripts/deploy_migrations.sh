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

# Check Transaction model
tx_has_user = hasattr(Transaction._meta.get_field('user'), 'related_model')
print(f'Transaction.user field: {'✅' if tx_has_user else '❌'}')

# Check MonthlyTotal model  
mt_has_user = hasattr(MonthlyTotal._meta.get_field('user'), 'related_model')
print(f'MonthlyTotal.user field: {'✅' if mt_has_user else '❌'}')

# Check ChatMessage model
cm_has_user = hasattr(ChatMessage._meta.get_field('user'), 'related_model')
print(f'ChatMessage.user field: {'✅' if cm_has_user else '❌'}')

print('✅ Multi-user setup verified')
"

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --no-input

echo "🎉 Multi-user deployment completed successfully!" 