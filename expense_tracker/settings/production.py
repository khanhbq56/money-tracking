"""
Production settings for expense_tracker project.
"""
import os
from .base import *

try:
    import dj_database_url
except ImportError:
    dj_database_url = None

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

# Allowed hosts for production
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost,127.0.0.1,*.railway.app',
    cast=lambda v: [s.strip() for s in v.split(',')]
)

# Database - use PostgreSQL in production
if dj_database_url:
    DATABASES = {
        'default': dj_database_url.parse(
            config('DATABASE_URL', default='sqlite:///db.sqlite3')
        )
    }
else:
    # Fallback to SQLite if dj_database_url is not available
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Security settings for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'

# CORS settings for production
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS', 
    default='https://yourapp.railway.app', 
    cast=lambda v: [s.strip() for s in v.split(',')]
)

# Static files settings for production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Cache configuration for production
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
    }
}

# Performance optimizations
CONN_MAX_AGE = 60  # Keep database connections alive for 60 seconds

# Compression for better performance  
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True

# Email configuration for production (use Railway's SMTP if needed)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable email SSL settings that might cause issues
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False

# Logging configuration for production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
} 