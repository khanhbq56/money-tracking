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
    path('chat/', views.process_chat_message, name='process_chat'),
    path('confirm/', views.confirm_transaction, name='confirm_transaction'),
    path('calendar/<int:year>/<int:month>/', views.get_calendar_data, name='calendar_data'),
    path('monthly-totals/', views.get_monthly_totals, name='monthly_totals'),
    path('daily-summary/<str:date>/', views.get_daily_summary, name='daily_summary'),
    
    # i18n translation endpoint
    path('translations/<str:language>/', views.get_translations, name='translations'),
] 