from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    # Google OAuth URLs
    path('google/login/', views.GoogleOAuthInitView.as_view(), name='google_login'),
    path('google/callback/', views.GoogleOAuthCallbackView.as_view(), name='google_callback'),
    
    # Demo login
    path('demo/login/', views.DemoLoginView.as_view(), name='demo_login'),
    
    # Logout
    path('logout/', views.logout_view, name='logout'),
    
    # Legal compliance
    path('privacy/', views.privacy_policy_view, name='privacy_policy'),
    path('terms/', views.terms_of_service_view, name='terms_of_service'),
] 