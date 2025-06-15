from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    # OAuth login flow
    path('oauth/google/', views.GoogleOAuthInitView.as_view(), name='google_oauth_init'),
    path('oauth/google/callback/', views.GoogleOAuthCallbackView.as_view(), name='google_oauth_callback'),
    
    # Demo account
    path('demo/login/', views.DemoLoginView.as_view(), name='demo_login'),
    
    # Session management
    path('session/status/', views.session_status_view, name='session_status'),
    
    # Logout
    path('logout/', views.logout_view, name='logout'),
    
    # Legal pages
    path('privacy/', views.privacy_policy_view, name='privacy_policy'),
    path('terms/', views.terms_of_service_view, name='terms_of_service'),
] 