"""
URL configuration for expense_tracker project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from .health import health_check
from .debug_static import debug_static_files

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
    path('debug-static/', debug_static_files, name='debug_static'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # API endpoints (outside i18n patterns)
    path('api/', include('transactions.api_urls')),
    path('api/', include('ai_chat.urls')),
]

# Serve static and media files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Admin site configuration
admin.site.site_header = "Expense Tracker Admin"
admin.site.site_title = "Expense Tracker"
admin.site.index_title = "Welcome to Expense Tracker Administration" 