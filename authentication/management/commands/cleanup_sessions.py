from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session
from django.utils import timezone
from authentication.models import User
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Clean up expired sessions and demo accounts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No actual deletions will occur'))
        
        # Clean up expired sessions
        expired_sessions = Session.objects.filter(expire_date__lt=timezone.now())
        session_count = expired_sessions.count()
        
        if session_count > 0:
            if not dry_run:
                expired_sessions.delete()
            self.stdout.write(
                self.style.SUCCESS(f'{"Would delete" if dry_run else "Deleted"} {session_count} expired sessions')
            )
        else:
            self.stdout.write('No expired sessions found')
        
        # Clean up expired demo accounts
        expired_demos = User.objects.filter(
            is_demo_user=True,
            demo_expires_at__lt=timezone.now()
        )
        demo_count = expired_demos.count()
        
        if demo_count > 0:
            if not dry_run:
                # Delete transactions first (cascade should handle this, but be explicit)
                for user in expired_demos:
                    user.transactions.all().delete()
                    logger.info(f'Deleted transactions for expired demo user: {user.username}')
                
                # Delete demo users
                expired_demos.delete()
            
            self.stdout.write(
                self.style.SUCCESS(f'{"Would delete" if dry_run else "Deleted"} {demo_count} expired demo accounts')
            )
        else:
            self.stdout.write('No expired demo accounts found')
        
        # Clean up demo accounts without expiration date (safety cleanup)
        orphaned_demos = User.objects.filter(
            is_demo_user=True,
            demo_expires_at__isnull=True,
            date_joined__lt=timezone.now() - timezone.timedelta(days=2)  # Older than 2 days
        )
        orphaned_count = orphaned_demos.count()
        
        if orphaned_count > 0:
            if not dry_run:
                for user in orphaned_demos:
                    user.transactions.all().delete()
                    logger.info(f'Deleted transactions for orphaned demo user: {user.username}')
                
                orphaned_demos.delete()
            
            self.stdout.write(
                self.style.WARNING(f'{"Would delete" if dry_run else "Deleted"} {orphaned_count} orphaned demo accounts')
            )
        else:
            self.stdout.write('No orphaned demo accounts found')
        
        self.stdout.write(self.style.SUCCESS('Session cleanup completed successfully')) 