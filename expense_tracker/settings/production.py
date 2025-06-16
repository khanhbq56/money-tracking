"""
Production settings for expense_tracker project.
Multi-user support enabled for production deployment.
"""
import os
from .base import *

try:
    import dj_database_url
except ImportError:
    dj_database_url = None

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# Allowed hosts - add Railway domain
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'healthcheck.railway.app',
    'money-tracking-production.up.railway.app',
    '.railway.app',  # Allow all Railway subdomains
]

# Get from environment or use defaults
env_hosts = os.environ.get('ALLOWED_HOSTS', '')
if env_hosts:
    additional_hosts = [host.strip() for host in env_hosts.split(',') if host.strip()]
    ALLOWED_HOSTS.extend(additional_hosts)

# Multi-user configuration for production
ENABLE_MULTI_USER = config('ENABLE_MULTI_USER', default=True, cast=bool)
DEFAULT_USER_LIMIT = config('DEFAULT_USER_LIMIT', default=1000, cast=int)

# Enhanced user session settings for multi-user
# Override base.py session settings for production
SESSION_COOKIE_AGE = 86400  # 24 hours max
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Force re-login after browser close
SESSION_SAVE_EVERY_REQUEST = True

# Google OAuth Settings - support both naming conventions
GOOGLE_OAUTH_CLIENT_ID = (
    os.environ.get('GOOGLE_OAUTH_CLIENT_ID') or 
    os.environ.get('GOOGLE_OAUTH2_CLIENT_ID')
)
GOOGLE_OAUTH_CLIENT_SECRET = (
    os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET') or 
    os.environ.get('GOOGLE_OAUTH2_CLIENT_SECRET')
)
GOOGLE_OAUTH_REDIRECT_URI = (
    os.environ.get('GOOGLE_OAUTH_REDIRECT_URI') or 
    os.environ.get('GOOGLE_OAUTH2_REDIRECT_URI') or
    'https://money-tracking-production.up.railway.app/auth/oauth/google/callback/'
)

# Database - use Railway's PostgreSQL if available, otherwise SQLite
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL and dj_database_url:
    # Use PostgreSQL from Railway
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL)
    }
    # Connection pooling for multi-user
    DATABASES['default']['CONN_MAX_AGE'] = 300
else:
    # Fallback to SQLite for development/testing
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Security settings for production
SECURE_SSL_REDIRECT = True  # Enable HTTPS redirect
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Health check exemption for Railway (specific paths only)
SECURE_SSL_REDIRECT_EXEMPT = ['/health/', '/healthcheck/']

# CSRF settings optimized for production
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = False  # Allow JavaScript access to CSRF token via cookie as fallback
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = [
    'https://money-tracking-production.up.railway.app',
    'https://*.railway.app',
]

# Session settings
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# CORS settings for production
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS', 
    default='https://money-tracking-production.up.railway.app', 
    cast=lambda v: [s.strip() for s in v.split(',')]
)

# Static files settings for production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Whitenoise configuration
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True

# Ensure static files directory exists
import os
STATIC_ROOT = BASE_DIR / 'staticfiles'
if not os.path.exists(STATIC_ROOT):
    os.makedirs(STATIC_ROOT, exist_ok=True)

# Static files configuration
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Cache configuration for production with Redis support
CACHE_URL = config('REDIS_URL', default=None)
if CACHE_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': CACHE_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }

# Performance optimizations for multi-user
CONN_MAX_AGE = 60  # Keep database connections alive for 60 seconds

# Compression for better performance  
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True

# Email configuration for production (use Railway's SMTP if needed)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable email SSL settings that might cause issues
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False

# Enhanced logging configuration for production multi-user
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'transactions': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'ai_chat': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'authentication': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Add Railway middleware at the beginning
MIDDLEWARE = [
    'expense_tracker.middleware.RailwayMiddleware',
    'expense_tracker.middleware.HealthCheckMiddleware',
] + [m for m in MIDDLEWARE if m not in [
    'expense_tracker.middleware.RailwayMiddleware',
    'expense_tracker.middleware.HealthCheckMiddleware'
]] 