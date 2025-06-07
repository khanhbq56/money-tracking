from django.db.models import Sum, Q
from datetime import datetime
from decimal import Decimal
from .models import Transaction, MonthlyTotal


class MonthlyTotalService:
    """
    Service for calculating and managing monthly totals.
    """
    
    @staticmethod
    def update_monthly_totals(year, month):
        """
        Update monthly totals for given year/month.
        
        Args:
            year (int): Year to update
            month (int): Month to update (1-12)
            
        Returns:
            MonthlyTotal: Updated monthly total object
        """
        # Get all transactions for the month
        transactions = Transaction.objects.filter(
            date__year=year,
            date__month=month
        )
        
        # Calculate totals by transaction type
        expense_total = abs(transactions.filter(
            transaction_type='expense'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0'))
        
        saving_total = transactions.filter(
            transaction_type='saving'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        investment_total = transactions.filter(
            transaction_type='investment'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Calculate total money spent (all categories as positive)
        net_total = abs(expense_total) + saving_total + investment_total
        
        # Update or create monthly total
        monthly_total, created = MonthlyTotal.objects.update_or_create(
            year=year,
            month=month,
            defaults={
                'total_expense': expense_total,
                'total_saving': saving_total,
                'total_investment': investment_total,
                'net_total': net_total
            }
        )
        
        return monthly_total
    
    @staticmethod
    def get_current_month_totals():
        """
        Get current month totals for dashboard.
        
        Returns:
            dict: Current month totals with formatted values
        """
        now = datetime.now()
        
        try:
            monthly_total = MonthlyTotal.objects.get(
                year=now.year,
                month=now.month
            )
            totals = {
                'expense': monthly_total.total_expense,
                'saving': monthly_total.total_saving,
                'investment': monthly_total.total_investment,
                'net_total': monthly_total.net_total
            }
        except MonthlyTotal.DoesNotExist:
            # Calculate and create if doesn't exist
            monthly_total = MonthlyTotalService.update_monthly_totals(now.year, now.month)
            totals = {
                'expense': monthly_total.total_expense,
                'saving': monthly_total.total_saving,
                'investment': monthly_total.total_investment,
                'net_total': monthly_total.net_total
            }
        
        return totals
    
    @staticmethod
    def get_formatted_totals():
        """
        Get current month totals with Vietnamese formatting.
        
        Returns:
            dict: Formatted totals for display
        """
        totals = MonthlyTotalService.get_current_month_totals()
        
        return {
            'expense': f"-{totals['expense']:,.0f}₫",
            'saving': f"+{totals['saving']:,.0f}₫", 
            'investment': f"+{totals['investment']:,.0f}₫",
            'net_total': f"{'+' if totals['net_total'] >= 0 else ''}{totals['net_total']:,.0f}₫"
        }
    
    @staticmethod
    def refresh_all_monthly_totals():
        """
        Refresh all monthly totals based on existing transactions.
        Useful for data migration or correction.
        
        Returns:
            int: Number of monthly totals updated
        """
        # Get all unique year-month combinations from transactions
        date_combinations = Transaction.objects.dates('date', 'month')
        
        updated_count = 0
        for date in date_combinations:
            MonthlyTotalService.update_monthly_totals(date.year, date.month)
            updated_count += 1
        
        return updated_count
    
    @staticmethod
    def get_monthly_breakdown(year, month):
        """
        Get detailed breakdown for a specific month.
        
        Args:
            year (int): Year
            month (int): Month
            
        Returns:
            dict: Detailed breakdown with categories
        """
        transactions = Transaction.objects.filter(
            date__year=year,
            date__month=month
        )
        
        # Expense breakdown by category
        expense_breakdown = {}
        expenses = transactions.filter(transaction_type='expense')
        for category, display_name in Transaction.EXPENSE_CATEGORIES:
            category_total = expenses.filter(
                expense_category=category
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            
            if category_total != 0:
                expense_breakdown[category] = {
                    'name': display_name,
                    'total': abs(category_total),
                    'count': expenses.filter(expense_category=category).count()
                }
        
        # Transaction counts
        counts = {
            'expense': expenses.count(),
            'saving': transactions.filter(transaction_type='saving').count(),
            'investment': transactions.filter(transaction_type='investment').count()
        }
        
        return {
            'expense_breakdown': expense_breakdown,
            'transaction_counts': counts,
            'total_transactions': transactions.count()
        }


def update_monthly_totals_on_transaction_change(transaction):
    """
    Helper function to update monthly totals when a transaction changes.
    Can be used in signals or view logic.
    
    Args:
        transaction (Transaction): Transaction that was created/updated/deleted
    """
    MonthlyTotalService.update_monthly_totals(
        transaction.date.year,
        transaction.date.month
    ) 