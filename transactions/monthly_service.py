from django.db.models import Sum, Q
from datetime import datetime
from decimal import Decimal
from .models import Transaction, MonthlyTotal


class MonthlyTotalService:
    """
    Service for calculating and managing monthly totals.
    """
    
    @staticmethod
    def update_monthly_totals(user, year, month):
        """
        Update monthly totals for given user, year/month.
        
        Args:
            user: User instance
            year (int): Year to update
            month (int): Month to update (1-12)
            
        Returns:
            MonthlyTotal: Updated monthly totals instance
        """
        # Get all transactions for the user and month
        transactions = Transaction.objects.filter(
            user=user,  # CRITICAL: Filter by user
            date__year=year,
            date__month=month
        )
        
        # Calculate totals
        expense_total = abs(transactions.filter(
            transaction_type='expense'
        ).aggregate(total=Sum('amount'))['total'] or 0)
        
        saving_total = abs(transactions.filter(
            transaction_type='saving'
        ).aggregate(total=Sum('amount'))['total'] or 0)
        
        investment_total = abs(transactions.filter(
            transaction_type='investment'
        ).aggregate(total=Sum('amount'))['total'] or 0)
        
        # Calculate net total (tổng của tất cả loại giao dịch)
        net_total = expense_total + saving_total + investment_total
        
        # Create or update MonthlyTotal record
        monthly_total, created = MonthlyTotal.objects.get_or_create(
            user=user,
            year=year,
            month=month,
            defaults={
                'total_expense': expense_total,
                'total_saving': saving_total,
                'total_investment': investment_total,
            'net_total': net_total
        }
        )
        
        # Update if exists
        if not created:
            monthly_total.total_expense = expense_total
            monthly_total.total_saving = saving_total
            monthly_total.total_investment = investment_total
            monthly_total.net_total = net_total
            monthly_total.save()
        
        return monthly_total
    
    @staticmethod
    def get_current_month_totals(user):
        """
        Get current month totals for specific user.
        
        Args:
            user: User instance
        
        Returns:
            dict: Current month totals
        """
        now = datetime.now()
        monthly_total = MonthlyTotalService.update_monthly_totals(user, now.year, now.month)
        
        return {
            'expense': monthly_total.total_expense,
            'saving': monthly_total.total_saving,
            'investment': monthly_total.total_investment,
            'net_total': monthly_total.net_total
        }
    
    @staticmethod
    def get_formatted_totals(user):
        """
        Get current month totals with Vietnamese formatting for specific user.
        
        Args:
            user: User instance
        
        Returns:
            dict: Formatted totals for display
        """
        totals = MonthlyTotalService.get_current_month_totals(user)
        
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
        from authentication.models import User
        
        # Get all users who have transactions
        users_with_transactions = User.objects.filter(
            transactions__isnull=False
        ).distinct()
        
        updated_count = 0
        for user in users_with_transactions:
            # Get all unique year-month combinations for this user
            user_date_combinations = Transaction.objects.filter(user=user).dates('date', 'month')
            
            for date in user_date_combinations:
                MonthlyTotalService.update_monthly_totals(user, date.year, date.month)
            updated_count += 1
        
        return updated_count
    
    @staticmethod
    def get_monthly_breakdown(user, year, month):
        """
        Get detailed breakdown for a specific month and user.
        
        Args:
            user: User instance
            year (int): Year
            month (int): Month
            
        Returns:
            dict: Detailed breakdown with categories
        """
        transactions = Transaction.objects.filter(
            user=user,  # CRITICAL: Filter by user
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
        transaction.user,  # CRITICAL: Pass user
        transaction.date.year,
        transaction.date.month
    )

def get_month_totals(user, year, month):
    """Get totals for specific month and user"""
    monthly_total = MonthlyTotalService.update_monthly_totals(user, year, month)
    return {
        'expense': monthly_total.total_expense,
        'saving': monthly_total.total_saving,
        'investment': monthly_total.total_investment,
        'net_total': monthly_total.net_total
    } 