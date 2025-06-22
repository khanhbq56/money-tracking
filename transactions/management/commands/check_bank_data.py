from django.core.management.base import BaseCommand
from transactions.models import Transaction, BankEmailTransaction


class Command(BaseCommand):
    help = 'Check bank transaction data in database'

    def handle(self, *args, **options):
        # Check transaction counts
        total_transactions = Transaction.objects.count()
        bank_email_transactions = BankEmailTransaction.objects.count()
        bank_transactions = Transaction.objects.filter(description__icontains='[Bank]').count()

        # Check recent bank email transactions
        recent_bank_emails = BankEmailTransaction.objects.filter(
            is_processed=True,
            transaction_id__isnull=False
        ).count()

        self.stdout.write("📊 Database Status:")
        self.stdout.write(f"Total Transactions: {total_transactions}")
        self.stdout.write(f"Bank Email Transactions: {bank_email_transactions}")
        self.stdout.write(f"Bank Transactions (with [Bank] prefix): {bank_transactions}")
        self.stdout.write(f"Processed Bank Emails (linked to transactions): {recent_bank_emails}")

        # Show recent bank email transactions
        self.stdout.write("\n📧 Recent Bank Email Transactions:")
        for bet in BankEmailTransaction.objects.order_by('-created_at')[:5]:
            self.stdout.write(f"  - {bet.id}: {bet.description[:50]}... | Confidence: {bet.ai_confidence} | Processed: {bet.is_processed} | Has Transaction: {bet.transaction_id is not None}")

        # Show recent transactions
        self.stdout.write("\n💳 Recent Transactions:")
        for t in Transaction.objects.order_by('-created_at')[:5]:
            self.stdout.write(f"  - {t.id}: {t.description[:50]}... | Type: {t.transaction_type} | Amount: {t.amount}")
            
        # Check unprocessed bank emails
        unprocessed = BankEmailTransaction.objects.filter(is_processed=False).count()
        self.stdout.write(f"\n⚠️ Unprocessed Bank Emails: {unprocessed}") 