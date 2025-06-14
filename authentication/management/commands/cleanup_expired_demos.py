import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from authentication.models import User

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Cleanup expired demo accounts and their associated data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed information about the cleanup process',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        verbose = options['verbose']
        
        now = timezone.now()
        
        # Find expired demo accounts
        expired_demos = User.objects.filter(
            is_demo_user=True,
            demo_expires_at__lt=now
        ).select_related()
        
        count = expired_demos.count()
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS('✅ No expired demo accounts found.')
            )
            return
            
        if verbose:
            self.stdout.write(f'🔍 Found {count} expired demo accounts:')
            for user in expired_demos:
                expired_hours = (now - user.demo_expires_at).total_seconds() / 3600
                self.stdout.write(f'  - {user.username} (expired {expired_hours:.1f}h ago)')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'🧪 DRY RUN: Would delete {count} expired demo accounts')
            )
            return
            
        # Perform cleanup
        deleted_count = 0
        error_count = 0
        
        for user in expired_demos:
            try:
                with transaction.atomic():
                    # Get transaction count before deletion
                    transaction_count = user.transaction_set.count()
                    monthly_total_count = user.monthly_totals.count()
                    
                    if verbose:
                        self.stdout.write(
                            f'🗑️ Deleting {user.username} '
                            f'(transactions: {transaction_count}, '
                            f'monthly_totals: {monthly_total_count})'
                        )
                    
                    # Delete user (cascades to related data)
                    user.delete()
                    deleted_count += 1
                    
            except Exception as e:
                error_count += 1
                logger.error(f'Error deleting demo user {user.username}: {str(e)}')
                self.stdout.write(
                    self.style.ERROR(f'❌ Error deleting {user.username}: {str(e)}')
                )
        
        # Summary
        if deleted_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Successfully deleted {deleted_count} expired demo accounts')
            )
        
        if error_count > 0:
            self.stdout.write(
                self.style.ERROR(f'❌ {error_count} errors occurred during cleanup')
            )
            
        # Log the cleanup for monitoring
        logger.info(f'Demo cleanup completed: {deleted_count} deleted, {error_count} errors') 