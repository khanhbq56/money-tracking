from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AiChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_chat'
    verbose_name = _('AI Chat') 
 