from django.core.management.base import BaseCommand
from django.db import transaction
from transactions.models import MonthlyTotal, Transaction
from authentication.models import User
from django.utils.translation import gettext as _


class Command(BaseCommand):
    help = 'Migrate existing MonthlyTotal data to per-user structure'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be migrated without actually migrating',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write('🔄 Starting MonthlyTotal to per-user migration...')
        
        # Get all existing MonthlyTotal records (without user)
        old_monthly_totals = MonthlyTotal.objects.filter(user__isnull=True)
        
        if not old_monthly_totals.exists():
            self.stdout.write(
                self.style.SUCCESS('✅ No old MonthlyTotal records found. Migration already complete!')
            )
            return
        
        self.stdout.write(f'📊 Found {old_monthly_totals.count()} old MonthlyTotal records to migrate')
        
        # Get all users with transactions
        users_with_transactions = User.objects.filter(
            transactions__isnull=False
        ).distinct()
        
        self.stdout.write(f'👥 Found {users_with_transactions.count()} users with transactions')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('🔍 DRY RUN MODE - No data will be changed')
            )
            self._show_dry_run_preview(old_monthly_totals, users_with_transactions)
            return
        
        # Perform migration
        try:
            with transaction.atomic():
                # Step 1: Delete old MonthlyTotal records (without user)
                self.stdout.write('🗑️  Deleting old MonthlyTotal records...')
                deleted_count = old_monthly_totals.delete()[0]
                self.stdout.write(f'   Deleted {deleted_count} old records')
                
                # Step 2: Recreate MonthlyTotal for each user
                self.stdout.write('🔄 Recreating MonthlyTotal records per user...')
                created_count = 0
                
                for user in users_with_transactions:
                    # Get unique year-month combinations for this user
                    user_dates = Transaction.objects.filter(user=user).dates('date', 'month')
                    
                    for date in user_dates:
                        # Calculate totals for this user and month
                        monthly_total = self._calculate_monthly_total_for_user(user, date.year, date.month)
                        
                        # Create MonthlyTotal record
                        MonthlyTotal.objects.create(
                            user=user,
                            year=date.year,
                            month=date.month,
                            total_expense=monthly_total['expense'],
                            total_saving=monthly_total['saving'],
                            total_investment=monthly_total['investment'],
                            net_total=monthly_total['net_total']
                        )
                        created_count += 1
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Migration completed successfully!\n'
                        f'   📊 Deleted: {deleted_count} old records\n'
                        f'   📊 Created: {created_count} new per-user records'
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Migration failed: {str(e)}')
            )
            raise
    
    def _show_dry_run_preview(self, old_monthly_totals, users_with_transactions):
        """Show what would be migrated in dry-run mode"""
        self.stdout.write('\n📋 Migration Preview:')
        self.stdout.write(f'   🗑️  Will delete: {old_monthly_totals.count()} old MonthlyTotal records')
        
        total_new_records = 0
        for user in users_with_transactions:
            user_dates = Transaction.objects.filter(user=user).dates('date', 'month')
            user_record_count = user_dates.count()
            total_new_records += user_record_count
            
            self.stdout.write(f'   👤 {user.email}: {user_record_count} monthly records')
        
        self.stdout.write(f'   ➕ Will create: {total_new_records} new per-user records')
    
    def _calculate_monthly_total_for_user(self, user, year, month):
        """Calculate monthly totals for specific user and month"""
        from decimal import Decimal
        from django.db.models import Sum
        
        transactions = Transaction.objects.filter(
            user=user,
            date__year=year,
            date__month=month
        )
        
        # Calculate totals
        expense_total = abs(transactions.filter(
            transaction_type='expense'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0'))
        
        saving_total = abs(transactions.filter(
            transaction_type='saving'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0'))
        
        investment_total = abs(transactions.filter(
            transaction_type='investment'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0'))
        
        # Calculate net total
        net_total = expense_total + saving_total + investment_total
        
        return {
            'expense': expense_total,
            'saving': saving_total,
            'investment': investment_total,
            'net_total': net_total
        } 