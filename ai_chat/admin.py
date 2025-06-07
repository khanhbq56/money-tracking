from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import ChatMessage


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = [
        'get_status_display', 'user_message_short', 'language', 
        'has_voice_input', 'is_confirmed', 'parsed_date', 'created_at'
    ]
    list_filter = [
        'is_confirmed', 'has_voice_input', 'language', 'parsed_date', 'created_at'
    ]
    search_fields = ['user_message', 'ai_response']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        (_('Message Content'), {
            'fields': ('user_message', 'ai_response', 'language')
        }),
        (_('Voice Input'), {
            'fields': ('has_voice_input', 'voice_transcript'),
            'classes': ('collapse',)
        }),
        (_('Transaction'), {
            'fields': ('suggested_transaction', 'is_confirmed', 'parsed_date')
        }),
        (_('Metadata'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at']
    
    def get_status_display(self, obj):
        voice_indicator = "🎤" if obj.has_voice_input else "⌨️"
        confirm_indicator = "✅" if obj.is_confirmed else "⏳"
        return f"{voice_indicator} {confirm_indicator}"
    get_status_display.short_description = _('Status')
    
    def user_message_short(self, obj):
        return obj.user_message[:100] + "..." if len(obj.user_message) > 100 else obj.user_message
    user_message_short.short_description = _('User Message')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('suggested_transaction') 