from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from transactions.models import Transaction, MonthlyTotal
from ai_chat.models import ChatMessage


class Command(BaseCommand):
    help = 'Set up initial sample data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before creating new data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Transaction.objects.all().delete()
            ChatMessage.objects.all().delete()
            MonthlyTotal.objects.all().delete()

        self.stdout.write('Creating sample transactions...')
        
        # Create sample transactions for current month
        today = date.today()
        
        # Sample expenses
        Transaction.objects.create(
            transaction_type='expense',
            amount=-50000,
            description='Ăn trưa',
            date=today - timedelta(days=2),
            expense_category='food',
            ai_confidence=0.95
        )
        
        Transaction.objects.create(
            transaction_type='expense',
            amount=-25000,
            description='Coffee',
            date=today - timedelta(days=1),
            expense_category='coffee',
            ai_confidence=0.98
        )
        
        Transaction.objects.create(
            transaction_type='expense',
            amount=-200000,
            description='Xăng xe',
            date=today - timedelta(days=3),
            expense_category='transport',
            ai_confidence=0.90
        )
        
        # Sample savings
        Transaction.objects.create(
            transaction_type='saving',
            amount=200000,
            description='Tiết kiệm',
            date=today - timedelta(days=1),
            ai_confidence=0.99
        )
        
        Transaction.objects.create(
            transaction_type='saving',
            amount=500000,
            description='Gửi ngân hàng',
            date=today - timedelta(days=5),
            ai_confidence=0.95
        )
        
        # Sample investments
        Transaction.objects.create(
            transaction_type='investment',
            amount=1000000,
            description='Mua cổ phiếu VIC',
            date=today - timedelta(days=4),
            ai_confidence=0.92
        )
        
        # Create sample chat messages
        ChatMessage.objects.create(
            user_message='coffee 25k',
            ai_response='☕ Phân loại: Chi tiêu - Coffee (25,000₫)',
            language='vi',
            has_voice_input=False,
            is_confirmed=True
        )
        
        ChatMessage.objects.create(
            user_message='tiết kiệm 200k',
            ai_response='💰 Phân loại: Tiết kiệm - Ngân hàng (200,000₫)',
            language='vi',
            has_voice_input=True,
            voice_transcript='tiết kiệm hai trăm nghìn',
            is_confirmed=True
        )
        
        # Calculate and create monthly totals
        from django.db.models import Sum
        
        current_month_transactions = Transaction.objects.filter(
            date__year=today.year,
            date__month=today.month
        )
        
        expense_total = abs(current_month_transactions.filter(
            transaction_type='expense'
        ).aggregate(total=Sum('amount'))['total'] or 0)
        
        saving_total = current_month_transactions.filter(
            transaction_type='saving'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        investment_total = current_month_transactions.filter(
            transaction_type='investment'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Calculate total money spent (all categories as positive)
        net_total = expense_total + saving_total + investment_total
        
        MonthlyTotal.objects.update_or_create(
            year=today.year,
            month=today.month,
            defaults={
                'total_expense': expense_total,
                'total_saving': saving_total,
                'total_investment': investment_total,
                'net_total': net_total
            }
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created sample data!\n'
                f'Transactions: {Transaction.objects.count()}\n'
                f'Chat Messages: {ChatMessage.objects.count()}\n'
                f'Monthly Totals: {MonthlyTotal.objects.count()}\n'
                f'Current Month Net Total: {net_total:,}₫'
            )
        ) 