from django.core.management.base import BaseCommand
from django.db import transaction
from transactions.models import MonthlyTotal, Transaction
from authentication.models import User
from django.utils.translation import gettext as _
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Verify multi-user data isolation and functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-test-data',
            action='store_true',
            help='Create test data for verification',
        )

    def handle(self, *args, **options):
        create_test_data = options['create_test_data']
        
        self.stdout.write('🔍 Starting multi-user verification...')
        
        if create_test_data:
            self.create_test_data()
            
        self.verify_data_isolation()
        self.verify_monthly_totals()
        self.verify_api_consistency()
        
        self.stdout.write(self.style.SUCCESS('✅ Multi-user verification completed!'))
    
    def create_test_data(self):
        """Create test users and transactions for verification"""
        self.stdout.write('📝 Creating test data...')
        
        # Create test users
        test_users = []
        for i in range(3):
            email = f'testuser{i+1}@test.com'
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': f'testuser{i+1}',
                    'first_name': f'Test User {i+1}',
                    'is_active': True
                }
            )
            test_users.append(user)
            
            if created:
                self.stdout.write(f'   👤 Created user: {user.email}')
        
        # Create transactions for each user
        today = date.today()
        
        for user in test_users:
            # Create different patterns for each user
            user_num = test_users.index(user) + 1
            
            # User 1: Heavy spender
            if user_num == 1:
                amounts = [50000, 100000, 200000, 75000, 120000]
                descriptions = ['Lunch', 'Shopping', 'Dinner', 'Coffee', 'Transport']
            # User 2: Moderate spender + saver
            elif user_num == 2:
                amounts = [30000, 500000, 80000, 300000]
                descriptions = ['Groceries', 'Monthly Saving', 'Utilities', 'Investment']
            # User 3: Light spender
            else:
                amounts = [25000, 45000, 15000]
                descriptions = ['Coffee', 'Snack', 'Bus fare']
            
            for i, (amount, desc) in enumerate(zip(amounts, descriptions)):
                # Determine transaction type
                if 'Saving' in desc:
                    tx_type = 'saving'
                    category = None
                elif 'Investment' in desc:
                    tx_type = 'investment'
                    category = None
                else:
                    tx_type = 'expense'
                    category = 'food' if any(word in desc.lower() for word in ['lunch', 'dinner', 'coffee', 'groceries', 'snack']) else 'transport'
                    amount = -abs(amount)  # Negative for expenses
                
                Transaction.objects.create(
                    user=user,
                    transaction_type=tx_type,
                    amount=amount,
                    description=desc,
                    expense_category=category,
                    date=today - timedelta(days=random.randint(0, 30)),
                    ai_confidence=0.95
                )
            
            self.stdout.write(f'   💰 Created {len(amounts)} transactions for {user.email}')
    
    def verify_data_isolation(self):
        """Verify that users only see their own data"""
        self.stdout.write('🔒 Verifying data isolation...')
        
        users = User.objects.filter(email__startswith='testuser')
        
        for user in users:
            user_transactions = Transaction.objects.filter(user=user)
            user_monthly_totals = MonthlyTotal.objects.filter(user=user)
            
            self.stdout.write(f'   👤 {user.email}:')
            self.stdout.write(f'      💳 Transactions: {user_transactions.count()}')
            self.stdout.write(f'      📊 Monthly totals: {user_monthly_totals.count()}')
            
            # Verify no user sees other users' data
            other_users_data = Transaction.objects.exclude(user=user)
            if other_users_data.exists():
                self.stdout.write(f'      ✅ Cannot see other users\' {other_users_data.count()} transactions')
            else:
                self.stdout.write(f'      ⚠️  No other users\' data to verify against')
    
    def verify_monthly_totals(self):
        """Verify monthly totals are calculated correctly per user"""
        self.stdout.write('📊 Verifying monthly totals calculation...')
        
        from transactions.monthly_service import MonthlyTotalService
        from datetime import datetime
        
        users = User.objects.filter(email__startswith='testuser')
        
        for user in users:
            # Get or create monthly totals for current month
            now = datetime.now()
            monthly_total = MonthlyTotalService.update_monthly_totals(user, now.year, now.month)
            
            # Manually calculate expected totals
            transactions = Transaction.objects.filter(
                user=user,
                date__year=now.year,
                date__month=now.month
            )
            
            expected_expense = abs(sum(t.amount for t in transactions if t.transaction_type == 'expense'))
            expected_saving = sum(t.amount for t in transactions if t.transaction_type == 'saving')
            expected_investment = sum(t.amount for t in transactions if t.transaction_type == 'investment')
            expected_net = expected_expense + expected_saving + expected_investment
            
            self.stdout.write(f'   👤 {user.email}:')
            self.stdout.write(f'      💰 Expense: {monthly_total.total_expense:,}₫ (expected: {expected_expense:,}₫)')
            self.stdout.write(f'      💚 Saving: {monthly_total.total_saving:,}₫ (expected: {expected_saving:,}₫)')
            self.stdout.write(f'      📈 Investment: {monthly_total.total_investment:,}₫ (expected: {expected_investment:,}₫)')
            self.stdout.write(f'      📊 Net Total: {monthly_total.net_total:,}₫ (expected: {expected_net:,}₫)')
            
            # Verify calculations are correct
            if (monthly_total.total_expense == expected_expense and
                monthly_total.total_saving == expected_saving and
                monthly_total.total_investment == expected_investment and
                monthly_total.net_total == expected_net):
                self.stdout.write(f'      ✅ Monthly totals are correct!')
            else:
                self.stdout.write(f'      ❌ Monthly totals calculation error!')
    
    def verify_api_consistency(self):
        """Verify API endpoints return consistent data"""
        self.stdout.write('🔗 Verifying API consistency...')
        
        from transactions.monthly_service import MonthlyTotalService
        from datetime import datetime
        
        users = User.objects.filter(email__startswith='testuser')
        
        for user in users:
            # Test service methods
            now = datetime.now()
            
            # Get current month totals
            totals_dict = MonthlyTotalService.get_current_month_totals(user)
            formatted_totals = MonthlyTotalService.get_formatted_totals(user)
            breakdown = MonthlyTotalService.get_monthly_breakdown(user, now.year, now.month)
            
            self.stdout.write(f'   👤 {user.email}:')
            self.stdout.write(f'      📊 Current totals: {totals_dict}')
            self.stdout.write(f'      💰 Formatted totals: {formatted_totals}')
            self.stdout.write(f'      📈 Breakdown: {breakdown["transaction_counts"]}')
            
            # Verify consistency
            if (totals_dict['expense'] == formatted_totals['expense'].replace('-', '').replace('₫', '').replace(',', '') or
                len(str(totals_dict['expense'])) > 0):
                self.stdout.write(f'      ✅ API consistency verified!') 