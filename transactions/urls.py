from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    # Main app view (will be implemented in Phase 3)
    path('', views.index, name='index'),
    
    # API endpoints will be added in Phase 2
    # path('api/transactions/', views.transaction_list, name='transaction_list'),
    # path('api/monthly-totals/', views.monthly_totals, name='monthly_totals'),
    # path('api/calendar-data/', views.calendar_data, name='calendar_data'),
] 