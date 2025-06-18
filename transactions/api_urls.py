from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from ai_chat.views import process_chat_message
from authentication.views import (
    BankIntegrationStatusView, BankIntegrationEnableView, 
    BankIntegrationDisableView, GmailPermissionStatusView
)

# Create router for viewsets
router = DefaultRouter()
router.register(r'transactions', views.TransactionViewSet, basename='transaction')

app_name = 'transactions_api'

urlpatterns = [
    # ViewSet URLs (includes CRUD operations) - Include router at root level
    path('', include(router.urls)),
    
    # Calendar data endpoint
    path('calendar-data/', views.calendar_data, name='calendar-data'),
    
    # Monthly totals endpoints
    path('monthly-totals/', views.monthly_totals, name='monthly-totals'),
    path('monthly-totals/refresh/', views.refresh_monthly_totals, name='refresh-monthly-totals'),
    path('monthly-breakdown/', views.monthly_breakdown, name='monthly-breakdown'),
    
    # Today summary
    path('today-summary/', views.today_summary, name='today-summary'),
    
    # Future projection endpoints (Phase 8)
    path('future-projection/', views.future_projection, name='future-projection'),
    path('monthly-analysis/', views.monthly_analysis, name='monthly-analysis'),
    
    # Chat processing endpoint
    path('chat/process/', process_chat_message, name='chat-process'),
    
    # Bank Integration API (Phase 1)
    path('bank-integration/status/', BankIntegrationStatusView.as_view(), name='bank-integration-status'),
    path('bank-integration/enable/', BankIntegrationEnableView.as_view(), name='bank-integration-enable'),
    path('bank-integration/disable/', BankIntegrationDisableView.as_view(), name='bank-integration-disable'),
    path('bank-integration/gmail-status/', GmailPermissionStatusView.as_view(), name='gmail-permission-status'),
    
    # Bank Sync API (Phase 2)
    path('bank-integration/sync/', views.BankSyncView.as_view(), name='bank-sync'),
    path('bank-integration/sync-history/', views.BankSyncHistoryView.as_view(), name='bank-sync-history'),
    path('bank-integration/test/', views.BankIntegrationTestView.as_view(), name='bank-integration-test'),
] 