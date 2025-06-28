#!/usr/bin/env python
"""
Test script to check authentication and URL access
"""
import os
import django
import requests
from requests.sessions import Session

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_modernized.settings')
django.setup()

def test_urls():
    """Test URL access with and without authentication"""
    
    # Test without authentication
    print("=== Testing without authentication ===")
    try:
        response = requests.get('http://localhost:8000/students/')
        print(f"Students without auth: {response.status_code}")
        if response.status_code == 302:
            print(f"Redirected to: {response.headers.get('Location', 'Unknown')}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test main dashboard
    try:
        response = requests.get('http://localhost:8000/')
        print(f"Main dashboard: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test login page
    try:
        response = requests.get('http://localhost:8000/login/')
        print(f"Login page: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test_urls() 