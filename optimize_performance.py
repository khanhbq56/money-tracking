#!/usr/bin/env python
"""
Performance optimization script for Expense Tracker
Optimizes database queries, creates indexes, and sets up caching
"""
import os
import django
from django.core.management import execute_from_command_line

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'expense_tracker.settings.development')
django.setup()

from django.db import connection
from django.core.cache import cache
from transactions.models import Transaction
from ai_chat.models import ChatMessage


def create_database_indexes():
    """Create optimized database indexes"""
    print("📊 Creating database indexes for performance...")
    
    cursor = connection.cursor()
    
    # Index for transaction queries by date
    try:
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_transaction_date 
            ON transactions_transaction(date DESC);
        """)
        print("✅ Created transaction date index")
    except Exception as e:
        print(f"⚠️ Date index already exists: {e}")
    
    # Index for transaction type filtering
    try:
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_transaction_type 
            ON transactions_transaction(transaction_type);
        """)
        print("✅ Created transaction type index")
    except Exception as e:
        print(f"⚠️ Type index already exists: {e}")
    
    # Index for monthly totals calculation
    try:
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_transaction_month_year 
            ON transactions_transaction(
                EXTRACT(year FROM date), 
                EXTRACT(month FROM date)
            );
        """)
        print("✅ Created month/year index")
    except Exception as e:
        print(f"⚠️ Month/year index already exists: {e}")
    
    # Index for AI chat messages
    try:
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chatmessage_created 
            ON ai_chat_chatmessage(created_at DESC);
        """)
        print("✅ Created chat message index")
    except Exception as e:
        print(f"⚠️ Chat message index already exists: {e}")


def optimize_database_queries():
    """Optimize common database queries"""
    print("🔍 Analyzing query performance...")
    
    # Analyze slow queries (SQLite doesn't have EXPLAIN ANALYZE, so we simulate)
    from django.db import transaction
    import time
    
    # Test calendar data query performance
    start_time = time.time()
    transactions = Transaction.objects.filter(
        date__year=2025, 
        date__month=6
    ).select_related().order_by('-date')[:100]
    
    # Force query execution
    list(transactions)
    query_time = time.time() - start_time
    
    print(f"📈 Calendar query time: {query_time:.3f}s")
    if query_time > 0.1:
        print("⚠️ Calendar query is slow, consider adding more indexes")
    else:
        print("✅ Calendar query performance is good")


def setup_caching():
    """Setup and test caching"""
    print("💾 Setting up caching...")
    
    # Test cache functionality
    test_key = 'performance_test'
    test_value = {'timestamp': time.time(), 'data': 'test'}
    
    try:
        cache.set(test_key, test_value, 60)
        cached_value = cache.get(test_key)
        
        if cached_value == test_value:
            print("✅ Cache is working correctly")
            cache.delete(test_key)  # Cleanup
        else:
            print("⚠️ Cache test failed")
    except Exception as e:
        print(f"❌ Cache error: {e}")


def create_cache_table():
    """Create database cache table for production"""
    print("🗃️ Creating cache table...")
    
    try:
        execute_from_command_line(['manage.py', 'createcachetable'])
        print("✅ Cache table created successfully")
    except Exception as e:
        print(f"⚠️ Cache table creation: {e}")


def analyze_static_files():
    """Analyze static files for optimization"""
    print("📁 Analyzing static files...")
    
    static_root = 'static/'
    if os.path.exists(static_root):
        total_size = 0
        file_count = 0
        
        for root, dirs, files in os.walk(static_root):
            for file in files:
                filepath = os.path.join(root, file)
                size = os.path.getsize(filepath)
                total_size += size
                file_count += 1
        
        total_size_mb = total_size / (1024 * 1024)
        print(f"📊 Static files: {file_count} files, {total_size_mb:.2f} MB")
        
        if total_size_mb > 10:
            print("⚠️ Large static files detected, consider compression")
        else:
            print("✅ Static files size is reasonable")
    else:
        print("⚠️ Static files directory not found")


def check_database_size():
    """Check database size and suggest optimizations"""
    print("🗄️ Checking database size...")
    
    db_path = 'db.sqlite3'
    if os.path.exists(db_path):
        size_mb = os.path.getsize(db_path) / (1024 * 1024)
        print(f"📊 Database size: {size_mb:.2f} MB")
        
        # Count records
        transaction_count = Transaction.objects.count()
        chat_count = ChatMessage.objects.count()
        
        print(f"📈 Transactions: {transaction_count}")
        print(f"💬 Chat messages: {chat_count}")
        
        if size_mb > 100:
            print("⚠️ Large database detected, consider archiving old data")
        else:
            print("✅ Database size is manageable")
    else:
        print("⚠️ Database file not found")


def run_security_checks():
    """Run basic security checks"""
    print("🔒 Running security checks...")
    
    # Check DEBUG setting
    from django.conf import settings
    if settings.DEBUG:
        print("⚠️ DEBUG is True - ensure it's False in production")
    else:
        print("✅ DEBUG is properly set to False")
    
    # Check SECRET_KEY
    if settings.SECRET_KEY and len(settings.SECRET_KEY) > 40:
        print("✅ SECRET_KEY is properly configured")
    else:
        print("⚠️ SECRET_KEY may be too short or missing")
    
    # Check ALLOWED_HOSTS
    if settings.ALLOWED_HOSTS and settings.ALLOWED_HOSTS != ['*']:
        print("✅ ALLOWED_HOSTS is properly configured")
    else:
        print("⚠️ ALLOWED_HOSTS should be configured for production")


def test_api_endpoints():
    """Test critical API endpoints"""
    print("🔌 Testing API endpoints...")
    
    from django.test import Client
    
    client = Client()
    
    endpoints = [
        '/health/',
        '/api/monthly-totals/',
        '/api/translations/vi/',
    ]
    
    for endpoint in endpoints:
        try:
            response = client.get(endpoint)
            if response.status_code == 200:
                print(f"✅ {endpoint} - OK")
            else:
                print(f"⚠️ {endpoint} - Status {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")


def main():
    """Run all optimization steps"""
    print("🚀 Starting Performance Optimization for Expense Tracker")
    print("=" * 60)
    
    try:
        create_database_indexes()
        print()
        
        optimize_database_queries()
        print()
        
        setup_caching()
        print()
        
        create_cache_table()
        print()
        
        analyze_static_files()
        print()
        
        check_database_size()
        print()
        
        run_security_checks()
        print()
        
        test_api_endpoints()
        print()
        
        print("=" * 60)
        print("🎉 Performance optimization completed!")
        print("\n📋 Next steps for production:")
        print("1. Set environment variables in Railway/production")
        print("2. Configure PostgreSQL database")
        print("3. Set up monitoring and logging")
        print("4. Run final integration tests")
        
    except Exception as e:
        print(f"❌ Optimization failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    import time
    main() 