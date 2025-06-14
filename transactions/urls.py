from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    # Main page view (for template rendering)
    path('', views.index, name='index'),
    # Test auth page
    path('test-auth/', views.test_auth, name='test_auth'),
] 