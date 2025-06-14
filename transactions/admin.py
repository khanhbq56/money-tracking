from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Transaction, MonthlyTotal


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'get_icon_display', 'transaction_type', 'description', 
        'amount', 'date', 'expense_category', 'ai_confidence'
    ]
    list_filter = [
        'transaction_type', 'expense_category', 'date', 'ai_confidence'
    ]
    search_fields = ['description']
    date_hierarchy = 'date'
    ordering = ['-date', '-created_at']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('transaction_type', 'amount', 'description', 'date')
        }),
        (_('Category'), {
            'fields': ('expense_category',),
            'description': _('Only required for expense transactions')
        }),
        (_('AI Information'), {
            'fields': ('ai_confidence',),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
            'description': _('Automatically managed timestamps')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_icon_display(self, obj):
        return f"{obj.get_icon()} {obj.get_transaction_type_display()}"
    get_icon_display.short_description = _('Type')
    
    def save_model(self, request, obj, form, change):
        """Override to ensure proper amount signs"""
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


@admin.register(MonthlyTotal)
class MonthlyTotalAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'year', 'month', 'total_expense', 'total_saving', 
        'total_investment', 'net_total', 'last_updated'
    ]
    list_filter = ['user', 'year', 'month']  # Added user filter
    ordering = ['-year', '-month']
    
    fieldsets = (
        (_('User & Period'), {
            'fields': ('user', 'year', 'month')
        }),
        (_('Totals'), {
            'fields': ('total_expense', 'total_saving', 'total_investment', 'net_total')
        }),
        (_('Metadata'), {
            'fields': ('last_updated',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['last_updated']
    
    def has_add_permission(self, request):
        """Monthly totals should be calculated automatically"""
        return True  # Allow manual creation for testing
    
    def get_queryset(self, request):
        """Filter by user for non-superusers"""
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(user=request.user)
        return qs


# Customize admin site
admin.site.site_header = _("Expense Tracker Administration")
admin.site.site_title = _("Expense Tracker Admin")
admin.site.index_title = _("Welcome to Expense Tracker Administration") 