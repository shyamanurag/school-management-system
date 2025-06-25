"""
Production settings for Render deployment
"""
import os
import dj_database_url
from .base import *

# Security for production
DEBUG = False

# Get allowed hosts from environment variable, fallback to Render domain patterns
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'school-system-kh8s.onrender.com,.onrender.com,*').split(',')

# Ensure we include common patterns
if '*' not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.extend(['*', '.onrender.com', 'school-system-kh8s.onrender.com'])

# Database - PostgreSQL for production
DATABASES = {
    'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
}

# Static files configuration for production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Logging for production
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
    },
} 