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
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL and DATABASE_URL.strip():
    try:
        # Use PostgreSQL from environment
        DATABASES = {
            'default': dj_database_url.parse(DATABASE_URL)
        }
        print(f"Using PostgreSQL database from DATABASE_URL")
    except Exception as e:
        print(f"Error parsing DATABASE_URL: {e}")
        # Force PostgreSQL configuration if DATABASE_URL parsing fails
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': os.environ.get('DB_NAME', 'school_system'),
                'USER': os.environ.get('DB_USER', 'school_admin'),
                'PASSWORD': os.environ.get('DB_PASSWORD', ''),
                'HOST': os.environ.get('DB_HOST', 'localhost'),
                'PORT': os.environ.get('DB_PORT', '5432'),
            }
        }
else:
    # Fallback to SQLite for development/testing only
    print("Warning: Using SQLite database - not recommended for production")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Static files configuration for production
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Additional static files directories
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Static files storage with whitenoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'uploads')

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