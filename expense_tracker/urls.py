"""
URL configuration for expense_tracker project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from .health import health_check
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

import ai_chat.views
import authentication.views

# Main app views (template rendering) - MUST come first
urlpatterns = i18n_patterns(
    path('', include('transactions.urls')),
    prefix_default_language=False,
)

# Basic views for Railway deployment
from django.http import HttpResponse

def basic_health(request):
    return HttpResponse("OK", content_type="text/plain")

# Add non-i18n patterns
urlpatterns += [
    # Basic health check
    path('', basic_health, name='basic_health'),
    path('health/', health_check, name='health_check'),


    
    # Admin
    path('admin/', admin.site.urls),
    
    # Authentication endpoints
    path('auth/', include('authentication.urls')),
    
    # API endpoints (outside i18n patterns)
    path('api/', include('transactions.api_urls')),
    path('api/chat/', include('ai_chat.urls')),  # Main AI chat endpoints
    
    # API aliases for frontend compatibility
    path('api/meme/weekly/', ai_chat.views.generate_weekly_meme, name='meme_weekly_alias'),
    
    # Settings page (new)
    path('settings/', authentication.views.settings_view, name='settings'),
    
    # Legal pages
    path('legal/privacy/', TemplateView.as_view(template_name='legal/privacy_policy.html'), name='privacy_policy'),
    path('legal/terms/', TemplateView.as_view(template_name='legal/terms_of_service.html'), name='terms_of_service'),
]

# Serve static and media files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Admin site configuration
admin.site.site_header = "Expense Tracker Admin"
admin.site.site_title = "Expense Tracker"
admin.site.index_title = "Welcome to Expense Tracker Administration"

def health_check(request):
    """Health check endpoint for Railway"""
    return JsonResponse({'status': 'healthy'}) 