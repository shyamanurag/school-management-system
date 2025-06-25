"""
Production settings for Render deployment
"""
import os
import dj_database_url
from .base import *

# Security for production
DEBUG = False

# Fallback ALLOWED_HOSTS for Render deployment
ALLOWED_HOSTS = [
    '*',  # Allow all hosts as fallback
    'school-system-kh8s.onrender.com',
    '.onrender.com',
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
]

# Force ALLOWED_HOSTS even if environment variable is not set
if 'onrender.com' in os.environ.get('RENDER_EXTERNAL_URL', ''):
    ALLOWED_HOSTS = ['*']  # Force allow all for Render

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