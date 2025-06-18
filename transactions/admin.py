from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Transaction, MonthlyTotal, UserGmailPermission, UserBankConfig, BankEmailTransaction


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
        'user', 'year', 'month', 'expense_amount', 'saving_amount', 
        'investment_amount', 'total_amount', 'transaction_count', 'updated_at'
    ]
    list_filter = ['user', 'year', 'month']  # Added user filter
    ordering = ['-year', '-month']
    
    fieldsets = (
        (_('User & Period'), {
            'fields': ('user', 'year', 'month')
        }),
        (_('Totals'), {
            'fields': ('expense_amount', 'saving_amount', 'investment_amount', 'total_amount', 'transaction_count')
        }),
        (_('Metadata'), {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['updated_at']
    
    def has_add_permission(self, request):
        """Monthly totals should be calculated automatically"""
        return True  # Allow manual creation for testing
    
    def get_queryset(self, request):
        """Filter by user for non-superusers"""
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(user=request.user)
        return qs


# =============================================================================
# BANK INTEGRATION ADMIN (Phase 1)
# =============================================================================

@admin.register(UserGmailPermission)
class UserGmailPermissionAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'has_gmail_permission', 'permission_granted_at', 
        'permission_last_used', 'token_status'
    ]
    list_filter = ['has_gmail_permission', 'permission_granted_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    ordering = ['-permission_granted_at']
    
    fieldsets = (
        (_('User'), {
            'fields': ('user',)
        }),
        (_('Permission Status'), {
            'fields': ('has_gmail_permission', 'permission_granted_at', 'permission_last_used')
        }),
        (_('Token Information'), {
            'fields': ('gmail_token_expires_at',),
            'classes': ('collapse',)
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'token_status']
    
    def token_status(self, obj):
        if not obj.has_gmail_permission:
            return "❌ No Permission"
        elif obj.is_token_expired():
            return "⚠️ Token Expired"
        else:
            return "✅ Valid Token"
    token_status.short_description = _('Token Status')


@admin.register(UserBankConfig)
class UserBankConfigAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'bank_code', 'is_enabled', 'last_sync_at', 
        'last_successful_sync', 'sync_error_count'
    ]
    list_filter = ['bank_code', 'is_enabled', 'sync_error_count']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    ordering = ['-last_sync_at']
    
    fieldsets = (
        (_('User & Bank'), {
            'fields': ('user', 'bank_code')
        }),
        (_('Integration Settings'), {
            'fields': ('is_enabled', 'account_suffix', 'sync_start_date', 'sender_email_pattern')
        }),
        (_('Sync Status'), {
            'fields': ('last_sync_at', 'last_successful_sync', 'sync_error_count', 'last_sync_error'),
            'classes': ('collapse',)
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(BankEmailTransaction)
class BankEmailTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'bank_config', 'description', 'amount', 'transaction_type', 
        'date', 'ai_confidence', 'is_processed', 'email_date'
    ]
    list_filter = [
        'bank_config__bank_code', 'transaction_type', 'is_processed', 
        'parsing_method', 'date', 'email_date'
    ]
    search_fields = ['description', 'email_subject', 'email_message_id']
    date_hierarchy = 'email_date'
    ordering = ['-email_date', '-created_at']
    
    fieldsets = (
        (_('Email Information'), {
            'fields': ('email_message_id', 'email_date', 'email_subject')
        }),
        (_('Transaction Data'), {
            'fields': ('transaction_type', 'amount', 'description', 'date', 'expense_category')
        }),
        (_('AI Processing'), {
            'fields': ('ai_confidence', 'parsing_method'),
            'classes': ('collapse',)
        }),
        (_('Processing Status'), {
            'fields': ('is_processed', 'processed_at', 'transaction_id', 'processing_error', 'retry_count'),
            'classes': ('collapse',)
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'processed_at']
    
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