#!/usr/bin/env python
"""
Test script to verify WSGI configuration works correctly
"""
import os
import sys

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_wsgi_import():
    """Test that WSGI application can be imported successfully"""
    try:
        print("Testing WSGI application import...")
        
        # Set environment
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_modernized.settings.production')
        
        # Try to import the WSGI application
        from school_modernized.wsgi import application
        
        print("✅ WSGI application imported successfully!")
        print(f"Application object: {application}")
        
        # Test Django setup
        import django
        django.setup()
        print("✅ Django setup completed!")
        
        # Test database connection
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        print(f"✅ Database connection test: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ WSGI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_wsgi_import()
    sys.exit(0 if success else 1) 