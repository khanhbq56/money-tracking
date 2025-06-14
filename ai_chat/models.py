from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class ChatMessage(models.Model):
    """
    Enhanced AI chat model with voice support and date parsing.
    """
    # User relationship - link chat messages to users
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_messages',
        verbose_name=_('User')
    )
    
    user_message = models.TextField(
        verbose_name=_('User Message')
    )
    ai_response = models.TextField(
        verbose_name=_('AI Response')
    )
    suggested_transaction = models.ForeignKey(
        'transactions.Transaction', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        verbose_name=_('Suggested Transaction')
    )
    is_confirmed = models.BooleanField(
        default=False,
        verbose_name=_('Is Confirmed')
    )
    
    # Voice support
    has_voice_input = models.BooleanField(
        default=False,
        verbose_name=_('Has Voice Input')
    )
    voice_transcript = models.TextField(
        blank=True,
        verbose_name=_('Voice Transcript')
    )
    
    # Date parsing for historical transactions
    parsed_date = models.DateField(
        null=True, 
        blank=True,
        verbose_name=_('Parsed Date')
    )
    
    # Language support
    language = models.CharField(
        max_length=10,
        default='vi',
        choices=[
            ('vi', _('Vietnamese')),
            ('en', _('English')),
        ],
        verbose_name=_('Language')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    
    class Meta:
        verbose_name = _('Chat Message')
        verbose_name_plural = _('Chat Messages')
        ordering = ['-created_at']
    
    def __str__(self):
        voice_indicator = "🎤" if self.has_voice_input else "⌨️"
        confirm_indicator = "✅" if self.is_confirmed else "⏳"
        return f"{voice_indicator} {confirm_indicator} {self.user_message[:50]}..." 