from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for viewsets
router = DefaultRouter()
router.register(r'chat-messages', views.ChatMessageViewSet, basename='chatmessage')

app_name = 'ai_chat'

urlpatterns = [
    # ViewSet URLs for chat messages
    path('', include(router.urls)),
    
    # Chat processing endpoints
    path('chat/process/', views.process_chat_message, name='process-chat'),
    path('chat/confirm/', views.confirm_transaction, name='confirm-transaction'),
    
    # i18n translation endpoint
    path('translations/<str:language_code>/', views.get_translations, name='translations'),
] 