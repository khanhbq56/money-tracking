"""
Development settings for expense_tracker project.
"""
import os
from .base import *

# Debug mode for development
DEBUG = True

# Allow all hosts in development
ALLOWED_HOSTS = ['*']

# Database for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Static files in development
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Google OAuth settings for development
# Override base.py settings to allow development without OAuth setup
GOOGLE_OAUTH2_CLIENT_ID = os.environ.get('GOOGLE_OAUTH2_CLIENT_ID', 'development-client-id')
GOOGLE_OAUTH2_CLIENT_SECRET = os.environ.get('GOOGLE_OAUTH2_CLIENT_SECRET', 'development-client-secret')
GOOGLE_OAUTH2_REDIRECT_URI = 'http://localhost:8000/auth/oauth/google/callback/'

# Disable HTTPS requirement for OAuth in development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Session settings
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_SECURE = False  # Allow HTTP cookies in development
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# CSRF settings for development
CSRF_COOKIE_SECURE = False  # Allow HTTP in development
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

# Logging for development
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'authentication': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Email backend for development (console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Enable all CORS origins for development
CORS_ALLOW_ALL_ORIGINS = True

# Additional development settings
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
] 