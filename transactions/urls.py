from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for viewsets
router = DefaultRouter()
router.register(r'transactions', views.TransactionViewSet, basename='transaction')

app_name = 'transactions'

urlpatterns = [
    # ViewSet URLs (includes CRUD operations)
    path('', include(router.urls)),
    
    # Calendar data endpoint
    path('calendar-data/', views.calendar_data, name='calendar-data'),
    
    # Monthly totals endpoints
    path('monthly-totals/', views.monthly_totals, name='monthly-totals'),
    path('monthly-totals/refresh/', views.refresh_monthly_totals, name='refresh-monthly-totals'),
    path('monthly-breakdown/', views.monthly_breakdown, name='monthly-breakdown'),
    
    # Today summary
    path('today-summary/', views.today_summary, name='today-summary'),
    
    # Main page view (for template rendering)
    path('dashboard/', views.index, name='dashboard'),
] 