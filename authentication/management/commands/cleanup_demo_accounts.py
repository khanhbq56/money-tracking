from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from authentication.models import User
from transactions.models import Transaction


class Command(BaseCommand):
    help = 'Clean up expired demo accounts and their associated data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting anything',
        )
        parser.add_argument(
            '--grace-period',
            type=int,
            default=1,
            help='Additional hours to wait before cleanup (default: 1 hour grace period)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        grace_period = options['grace_period']
        
        # Calculate cutoff time with grace period
        cutoff_time = timezone.now() - timezone.timedelta(hours=grace_period)
        
        # Find expired demo accounts
        expired_demo_users = User.objects.filter(
            is_demo_user=True,
            demo_expires_at__lt=cutoff_time
        )
        
        if not expired_demo_users.exists():
            self.stdout.write(
                self.style.SUCCESS('No expired demo accounts found.')
            )
            return
        
        # Count associated data
        expired_user_ids = list(expired_demo_users.values_list('id', flat=True))
        transaction_count = Transaction.objects.filter(user_id__in=expired_user_ids).count()
        
        self.stdout.write(
            f'Found {expired_demo_users.count()} expired demo accounts '
            f'with {transaction_count} associated transactions'
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No data will be deleted')
            )
            for user in expired_demo_users:
                user_transactions = Transaction.objects.filter(user=user).count()
                expired_hours = (timezone.now() - user.demo_expires_at).total_seconds() / 3600
                self.stdout.write(
                    f'  - {user.email} (expired {expired_hours:.1f}h ago, '
                    f'{user_transactions} transactions)'
                )
            return
        
        # Perform cleanup in a transaction
        try:
            with transaction.atomic():
                # Delete associated transactions first
                deleted_transactions = Transaction.objects.filter(
                    user_id__in=expired_user_ids
                ).delete()
                
                # Delete demo users
                deleted_users = expired_demo_users.delete()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully cleaned up:\n'
                        f'  - {deleted_users[0]} demo users\n'
                        f'  - {deleted_transactions[0]} transactions'
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during cleanup: {str(e)}')
            )
            raise
        
        # Show cleanup summary
        remaining_demo_users = User.objects.filter(is_demo_user=True).count()
        self.stdout.write(
            f'Remaining active demo accounts: {remaining_demo_users}'
        ) 