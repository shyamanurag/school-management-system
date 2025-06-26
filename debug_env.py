#!/usr/bin/env python
"""
Debug script to check environment variables
"""
import os

print("=== Environment Variables Debug ===")
print(f"DATABASE_URL: {os.environ.get('DATABASE_URL', 'NOT SET')}")
print(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE', 'NOT SET')}")
print(f"DEBUG: {os.environ.get('DEBUG', 'NOT SET')}")
print(f"SECRET_KEY: {'SET' if os.environ.get('SECRET_KEY') else 'NOT SET'}")
print(f"ALLOWED_HOSTS: {os.environ.get('ALLOWED_HOSTS', 'NOT SET')}")

# Test database configuration
if os.environ.get('DATABASE_URL'):
    print("\n=== Testing Django Settings ===")
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_modernized.settings.production')
        import django
        django.setup()
        from django.conf import settings
        print(f"Database ENGINE: {settings.DATABASES['default']['ENGINE']}")
        print(f"Database NAME: {settings.DATABASES['default']['NAME']}")
        print(f"Database HOST: {settings.DATABASES['default'].get('HOST', 'Not set')}")
    except Exception as e:
        print(f"Django setup failed: {e}")
else:
    print("\n❌ DATABASE_URL not found - Django will use SQLite") 