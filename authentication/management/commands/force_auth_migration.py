"""
Django management command to force apply authentication model migrations
Useful when standard migration process fails on production
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Force apply authentication model migrations when standard process fails'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force apply even if migrations seem applied',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔧 Force applying authentication migrations...'))
        
        try:
            # Check current auth_user table structure
            self.check_table_structure()
            
            # Force apply authentication migrations
            self.force_apply_migrations(options['force'])
            
            # Verify the result
            self.verify_migration_result()
            
            self.stdout.write(self.style.SUCCESS('✅ Authentication migrations applied successfully!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Migration failed: {str(e)}'))
            raise CommandError(f'Migration failed: {str(e)}')

    def check_table_structure(self):
        """Check current auth_user table structure"""
        self.stdout.write('🔍 Checking current table structure...')
        
        with connection.cursor() as cursor:
            try:
                cursor.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name='auth_user' 
                    ORDER BY column_name;
                """)
                columns = cursor.fetchall()
                
                self.stdout.write(f'📋 Current auth_user columns: {len(columns)}')
                for col_name, col_type in columns:
                    self.stdout.write(f'  - {col_name}: {col_type}')
                
                # Check for custom fields
                custom_fields = ['google_id', 'is_demo_user', 'profile_picture', 
                               'privacy_policy_accepted', 'terms_accepted', 'demo_expires_at']
                missing_fields = []
                
                existing_columns = [col[0] for col in columns]
                for field in custom_fields:
                    if field not in existing_columns:
                        missing_fields.append(field)
                
                if missing_fields:
                    self.stdout.write(self.style.WARNING(f'⚠️ Missing custom fields: {missing_fields}'))
                else:
                    self.stdout.write(self.style.SUCCESS('✅ All custom fields present'))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Could not check table structure: {str(e)}'))

    def force_apply_migrations(self, force=False):
        """Force apply authentication migrations"""
        self.stdout.write('🚀 Applying authentication migrations...')
        
        try:
            with transaction.atomic():
                # Clear authentication migration history if force
                if force:
                    self.stdout.write('🗄️ Clearing authentication migration history...')
                    with connection.cursor() as cursor:
                        cursor.execute("DELETE FROM django_migrations WHERE app='authentication';")
                
                # Apply authentication migrations
                call_command('migrate', 'authentication', verbosity=2, interactive=False)
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Migration command failed: {str(e)}'))
            raise

    def verify_migration_result(self):
        """Verify that migrations were applied correctly"""
        self.stdout.write('🧪 Verifying migration result...')
        
        try:
            from authentication.models import User
            import uuid
            
            # Test User model with custom fields
            test_user = User(
                username=f'test_{uuid.uuid4().hex[:8]}',
                email='test@verification.test',
                first_name='Test User',
                is_demo_user=True
            )
            
            # Check all custom fields are accessible
            custom_fields = ['google_id', 'is_demo_user', 'profile_picture', 
                           'privacy_policy_accepted', 'terms_accepted', 'demo_expires_at']
            
            for field in custom_fields:
                if hasattr(test_user, field):
                    self.stdout.write(f'  ✅ {field}: OK')
                else:
                    self.stdout.write(f'  ❌ {field}: MISSING')
                    raise Exception(f'Missing field: {field}')
            
            self.stdout.write(self.style.SUCCESS('✅ User model verification passed'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Verification failed: {str(e)}'))
            raise 