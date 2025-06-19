from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    # OAuth login flow
    path('oauth/google/', views.GoogleOAuthInitView.as_view(), name='google_oauth_init'),
    path('oauth/google/callback/', views.GoogleOAuthCallbackView.as_view(), name='google_oauth_callback'),
    
    # Backward compatibility route for Google OAuth callback
    path('google/callback/', views.GoogleOAuthCallbackView.as_view(), name='google_oauth_callback_compat'),
    
    # Demo account
    path('demo/login/', views.DemoLoginView.as_view(), name='demo_login'),
    
    # Session management
    path('session/status/', views.session_status_view, name='session_status'),
    
    # Logout
    path('logout/', views.logout_view, name='logout'),
    
    # Legal pages
    path('privacy/', views.privacy_policy_view, name='privacy_policy'),
    path('terms/', views.terms_of_service_view, name='terms_of_service'),
    
    # Separate Gmail OAuth for Bank Integration (NEW)
    path('gmail-oauth/initiate/', views.GmailOAuthInitiateView.as_view(), name='gmail_oauth_initiate'),
    path('gmail-oauth/callback/', views.GmailOAuthCallbackView.as_view(), name='gmail_oauth_callback'),
    path('gmail-oauth/revoke/', views.GmailPermissionRevokeView.as_view(), name='gmail_permission_revoke'),

] 