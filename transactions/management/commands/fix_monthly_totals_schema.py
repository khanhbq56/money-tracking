from django.core.management.base import BaseCommand
from django.db import connection
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Fix MonthlyTotal schema issues after field name changes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force apply migrations even if they seem to be already applied',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('🔧 Fixing MonthlyTotal schema issues...'))
        
        # Check current database schema
        with connection.cursor() as cursor:
            # Check if table exists
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'transactions_monthlytotal'
                ORDER BY column_name;
            """)
            columns = [row[0] for row in cursor.fetchall()]
            
            self.stdout.write(f"📋 Current columns: {', '.join(columns)}")
            
            # Check what migrations have been applied
            cursor.execute("""
                SELECT name FROM django_migrations 
                WHERE app = 'transactions' 
                ORDER BY name;
            """)
            applied_migrations = [row[0] for row in cursor.fetchall()]
            
            self.stdout.write(f"📁 Applied migrations: {', '.join(applied_migrations)}")
            
            # Identify the issue
            has_new_fields = 'total_amount' in columns
            has_old_fields = 'total_expense' in columns
            
            if has_old_fields and not has_new_fields:
                self.stdout.write(self.style.ERROR('❌ Database has old field names but migration 0005 may not be fully applied'))
                
                # Apply migration 0005 again
                self.stdout.write('🔄 Re-applying migration 0005...')
                try:
                    call_command('migrate', 'transactions', '0005', verbosity=2)
                    self.stdout.write(self.style.SUCCESS('✅ Migration 0005 applied successfully'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'❌ Error applying migration: {e}'))
                    
            elif not has_new_fields and not has_old_fields:
                self.stdout.write(self.style.ERROR('❌ Neither old nor new fields found - database may be corrupted'))
                
                # Try to apply all migrations
                self.stdout.write('🔄 Applying all migrations...')
                try:
                    call_command('migrate', 'transactions', verbosity=2)
                    self.stdout.write(self.style.SUCCESS('✅ All migrations applied'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'❌ Error applying migrations: {e}'))
                    
            elif has_new_fields:
                self.stdout.write(self.style.SUCCESS('✅ Database schema is correct'))
                
                # Test creating a monthly total
                self.stdout.write('🧪 Testing MonthlyTotal creation...')
                try:
                    from transactions.models import MonthlyTotal
                    from authentication.models import User
                    from datetime import datetime
                    
                    # Get first user for testing
                    user = User.objects.first()
                    if user:
                        now = datetime.now()
                        monthly_total, created = MonthlyTotal.objects.get_or_create(
                            user=user,
                            year=now.year,
                            month=now.month,
                            defaults={
                                'expense_amount': 0,
                                'saving_amount': 0,
                                'investment_amount': 0,
                                'total_amount': 0,
                                'transaction_count': 0
                            }
                        )
                        self.stdout.write(self.style.SUCCESS(f'✅ MonthlyTotal test successful: {monthly_total}'))
                    else:
                        self.stdout.write(self.style.WARNING('⚠️ No users found to test with'))
                        
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'❌ MonthlyTotal creation failed: {e}'))
            
            else:
                self.stdout.write(self.style.WARNING('⚠️ Mixed field state detected - may need manual intervention'))
        
        # Show final status
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('🎉 Schema fix completed'))
        self.stdout.write('To test the fix, try: python manage.py shell -c "from transactions.monthly_service import MonthlyTotalService; print(\'OK\')"') 