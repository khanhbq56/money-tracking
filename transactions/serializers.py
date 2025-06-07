from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import Transaction, MonthlyTotal


class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for Transaction model with validation and computed fields.
    """
    icon = serializers.ReadOnlyField(source='get_icon')
    transaction_type_display = serializers.ReadOnlyField(source='get_transaction_type_display')
    expense_category_display = serializers.SerializerMethodField()
    formatted_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'transaction_type', 'transaction_type_display',
            'amount', 'formatted_amount', 'description', 'date',
            'expense_category', 'expense_category_display', 'icon',
            'ai_confidence', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_expense_category_display(self, obj):
        """Get display name for expense category"""
        if obj.expense_category and obj.transaction_type == 'expense':
            return obj.get_expense_category_display()
        return None
    
    def get_formatted_amount(self, obj):
        """Format amount with Vietnamese currency style"""
        amount = abs(obj.amount)
        if obj.transaction_type == 'expense':
            return f"-{amount:,.0f}₫"
        else:
            return f"+{amount:,.0f}₫"
    
    def validate(self, data):
        """Custom validation for transaction data"""
        transaction_type = data.get('transaction_type')
        expense_category = data.get('expense_category')
        amount = data.get('amount')
        
        # Validate expense category
        if transaction_type == 'expense' and not expense_category:
            raise serializers.ValidationError({
                'expense_category': _('Expense category is required for expense transactions.')
            })
        
        if transaction_type != 'expense' and expense_category:
            # Clear expense_category for non-expense transactions
            data['expense_category'] = None
        
        # Validate amount
        if not amount or amount == 0:
            raise serializers.ValidationError({
                'amount': _('Amount must be greater than 0.')
            })
        
        return data


class TransactionCreateSerializer(TransactionSerializer):
    """
    Specialized serializer for creating transactions from AI suggestions.
    """
    custom_date = serializers.DateField(required=False, help_text=_('Custom date for historical transactions'))
    
    class Meta(TransactionSerializer.Meta):
        fields = TransactionSerializer.Meta.fields + ['custom_date']
    
    def create(self, validated_data):
        """Create transaction with custom date handling"""
        custom_date = validated_data.pop('custom_date', None)
        if custom_date:
            validated_data['date'] = custom_date
        
        return super().create(validated_data)


class TransactionListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for list views and calendar data.
    """
    icon = serializers.ReadOnlyField(source='get_icon')
    formatted_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'transaction_type', 'amount', 'formatted_amount',
            'description', 'date', 'expense_category', 'icon'
        ]
    
    def get_formatted_amount(self, obj):
        """Format amount for display"""
        amount = abs(obj.amount)
        if obj.transaction_type == 'expense':
            return f"-{amount/1000:.0f}k"
        else:
            return f"+{amount/1000:.0f}k"


class MonthlyTotalSerializer(serializers.ModelSerializer):
    """
    Serializer for MonthlyTotal model with formatted amounts.
    """
    formatted_expense = serializers.SerializerMethodField()
    formatted_saving = serializers.SerializerMethodField()
    formatted_investment = serializers.SerializerMethodField()
    formatted_net_total = serializers.SerializerMethodField()
    
    class Meta:
        model = MonthlyTotal
        fields = [
            'year', 'month', 'total_expense', 'total_saving',
            'total_investment', 'net_total', 'last_updated',
            'formatted_expense', 'formatted_saving',
            'formatted_investment', 'formatted_net_total'
        ]
        read_only_fields = ['last_updated']
    
    def get_formatted_expense(self, obj):
        """Format expense total"""
        return f"-{obj.total_expense:,.0f}₫"
    
    def get_formatted_saving(self, obj):
        """Format saving total"""
        return f"+{obj.total_saving:,.0f}₫"
    
    def get_formatted_investment(self, obj):
        """Format investment total"""
        return f"+{obj.total_investment:,.0f}₫"
    
    def get_formatted_net_total(self, obj):
        """Format net total with proper sign"""
        sign = "+" if obj.net_total >= 0 else ""
        return f"{sign}{obj.net_total:,.0f}₫"


class CalendarDataSerializer(serializers.Serializer):
    """
    Serializer for calendar data aggregation.
    """
    date = serializers.DateField()
    transactions = TransactionListSerializer(many=True)
    daily_total = serializers.DecimalField(max_digits=15, decimal_places=0)
    formatted_daily_total = serializers.SerializerMethodField()
    expense_count = serializers.IntegerField()
    saving_count = serializers.IntegerField()
    investment_count = serializers.IntegerField()
    
    def get_formatted_daily_total(self, obj):
        """Format daily total with proper sign"""
        total = obj['daily_total']
        if total == 0:
            return "0₫"
        sign = "+" if total > 0 else ""
        return f"{sign}{total:,.0f}₫" 