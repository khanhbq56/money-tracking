from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class Transaction(models.Model):
    """
    Simplified transaction model with 3 types: expense, saving, investment.
    Only expenses have categories, saving/investment are simple.
    """
    TRANSACTION_TYPES = [
        ('expense', _('🔴 Chi tiêu')),
        ('saving', _('🟢 Tiết kiệm')), 
        ('investment', _('🔵 Đầu tư'))
    ]
    
    # Simplified categories - only for expenses
    EXPENSE_CATEGORIES = [
        ('food', _('🍜 Ăn uống')),
        ('coffee', _('☕ Coffee')),
        ('transport', _('🚗 Di chuyển')),
        ('shopping', _('🛒 Mua sắm')),
        ('entertainment', _('🎬 Giải trí')),
        ('health', _('🏥 Sức khỏe')),
        ('education', _('📚 Giáo dục')),
        ('utilities', _('⚡ Tiện ích')),
        ('other', _('📦 Khác')),
    ]
    
    # Core fields
    transaction_type = models.CharField(
        max_length=20, 
        choices=TRANSACTION_TYPES,
        verbose_name=_('Transaction Type')
    )
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=0,
        verbose_name=_('Amount')
    )
    description = models.CharField(
        max_length=200,
        verbose_name=_('Description')
    )
    date = models.DateField(
        verbose_name=_('Date')
    )
    
    # Only expense has categories, saving/investment are simple
    expense_category = models.CharField(
        max_length=20, 
        choices=EXPENSE_CATEGORIES, 
        null=True, 
        blank=True,
        verbose_name=_('Expense Category')
    )
    
    # User relationship - link transactions to users
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,  # Allow existing data migration
        blank=True,
        related_name='transactions',
        verbose_name=_('User')
    )
    
    # AI related
    ai_confidence = models.FloatField(
        default=0.0,
        verbose_name=_('AI Confidence')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At')
    )
    
    class Meta:
        verbose_name = _('Transaction')
        verbose_name_plural = _('Transactions')
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount:,}₫ - {self.date}"
    
    def get_icon(self):
        """Get icon based on transaction type and category"""
        if self.transaction_type == 'expense':
            category_icons = {
                'food': '🍜', 'coffee': '☕', 'transport': '🚗',
                'shopping': '🛒', 'entertainment': '🎬', 'health': '🏥',
                'education': '📚', 'utilities': '⚡', 'other': '📦'
            }
            return category_icons.get(self.expense_category, '📦')
        elif self.transaction_type == 'saving':
            return '💰'
        elif self.transaction_type == 'investment':
            return '📈'
        return '💰'
    
    def save(self, *args, **kwargs):
        """Override save to ensure category logic"""
        # Clear expense_category if not an expense
        if self.transaction_type != 'expense':
            self.expense_category = None
        
        # Ensure amount is positive for saving/investment, negative for expense
        if self.transaction_type == 'expense' and self.amount > 0:
            self.amount = -abs(self.amount)
        elif self.transaction_type in ['saving', 'investment'] and self.amount < 0:
            self.amount = abs(self.amount)
        
        super().save(*args, **kwargs)


class MonthlyTotal(models.Model):
    """Track monthly totals for dashboard"""
    year = models.IntegerField(verbose_name=_('Year'))
    month = models.IntegerField(verbose_name=_('Month'))
    
    total_expense = models.DecimalField(
        max_digits=15, 
        decimal_places=0, 
        default=0,
        verbose_name=_('Total Expense')
    )
    total_saving = models.DecimalField(
        max_digits=15, 
        decimal_places=0, 
        default=0,
        verbose_name=_('Total Saving')
    )
    total_investment = models.DecimalField(
        max_digits=15, 
        decimal_places=0, 
        default=0,
        verbose_name=_('Total Investment')
    )
    net_total = models.DecimalField(
        max_digits=15, 
        decimal_places=0, 
        default=0,
        verbose_name=_('Net Total')
    )
    
    last_updated = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Last Updated')
    )
    
    class Meta:
        unique_together = ['year', 'month']
        verbose_name = _('Monthly Total')
        verbose_name_plural = _('Monthly Totals')
        ordering = ['-year', '-month']
    
    def __str__(self):
        return f"{self.year}/{self.month:02d} - Net: {self.net_total:,}₫" 