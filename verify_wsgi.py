#!/usr/bin/env python
"""
Verify WSGI module can be imported correctly
"""
import sys
import os

def main():
    print("=== WSGI Module Verification ===")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    
    # Check if the school_modernized module exists
    try:
        import school_modernized
        print(f"✅ school_modernized module found at: {school_modernized.__file__}")
    except ImportError as e:
        print(f"❌ Cannot import school_modernized: {e}")
        return False
    
    # Check if wsgi module exists
    try:
        import school_modernized.wsgi
        print(f"✅ school_modernized.wsgi module found at: {school_modernized.wsgi.__file__}")
    except ImportError as e:
        print(f"❌ Cannot import school_modernized.wsgi: {e}")
        return False
    
    # Check if application object exists
    try:
        from school_modernized.wsgi import application
        print(f"✅ WSGI application object: {application}")
        print(f"✅ Application type: {type(application)}")
    except ImportError as e:
        print(f"❌ Cannot import application from school_modernized.wsgi: {e}")
        return False
    
    print("✅ All WSGI checks passed!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 