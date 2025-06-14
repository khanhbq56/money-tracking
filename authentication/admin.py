from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for custom User model"""
    
    # Display fields in user list
    list_display = [
        'email', 'username', 'first_name', 'last_name', 
        'is_demo_user', 'is_staff', 'is_active', 'date_joined'
    ]
    
    # Filters in admin sidebar
    list_filter = [
        'is_staff', 'is_superuser', 'is_active', 
        'is_demo_user', 'date_joined'
    ]
    
    # Search fields
    search_fields = ['email', 'username', 'first_name', 'last_name']
    
    # Ordering
    ordering = ['-date_joined']
    
    # Fieldsets for user detail page
    fieldsets = (
        (None, {
            'fields': ('email', 'username', 'password')
        }),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'profile_picture')
        }),
        (_('Account Type'), {
            'fields': ('is_demo_user', 'demo_expires_at')
        }),
        (_('Google OAuth'), {
            'fields': ('google_id',),
            'classes': ('collapse',)
        }),
        (_('Legal Consent'), {
            'fields': (
                'privacy_policy_accepted', 'privacy_policy_accepted_at',
                'terms_accepted', 'terms_accepted_at'
            ),
            'classes': ('collapse',)
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        (_('Security'), {
            'fields': ('last_login_ip',),
            'classes': ('collapse',)
        }),
    )
    
    # Fieldsets for add user page
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
        (_('Account Type'), {
            'fields': ('is_demo_user',)
        }),
    )
    
    # Read-only fields
    readonly_fields = [
        'created_at', 'updated_at', 'date_joined', 'last_login',
        'privacy_policy_accepted_at', 'terms_accepted_at'
    ]
    
    # Actions
    actions = ['mark_as_demo', 'mark_as_regular', 'reset_legal_consent']
    
    def mark_as_demo(self, request, queryset):
        """Mark selected users as demo accounts"""
        queryset.update(is_demo_user=True)
        self.message_user(request, _('Selected users marked as demo accounts.'))
    mark_as_demo.short_description = _('Mark as demo accounts')
    
    def mark_as_regular(self, request, queryset):
        """Mark selected users as regular accounts"""
        queryset.update(is_demo_user=False, demo_expires_at=None)
        self.message_user(request, _('Selected users marked as regular accounts.'))
    mark_as_regular.short_description = _('Mark as regular accounts')
    
    def reset_legal_consent(self, request, queryset):
        """Reset legal consent for selected users"""
        queryset.update(
            privacy_policy_accepted=False,
            privacy_policy_accepted_at=None,
            terms_accepted=False,
            terms_accepted_at=None
        )
        self.message_user(request, _('Legal consent reset for selected users.'))
    reset_legal_consent.short_description = _('Reset legal consent') 