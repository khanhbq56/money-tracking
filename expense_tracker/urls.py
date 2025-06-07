"""
URL configuration for expense_tracker project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', include('transactions.urls')),
    path('api/', include('ai_chat.urls')),
]

# Add i18n patterns for main app
urlpatterns += i18n_patterns(
    # Main app views will be added later
    path('', include('transactions.urls', namespace='main')),
    prefix_default_language=False,
)

# Serve static and media files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Admin site configuration
admin.site.site_header = "Expense Tracker Admin"
admin.site.site_title = "Expense Tracker"
admin.site.index_title = "Welcome to Expense Tracker Administration" 