#!/usr/bin/env python3
"""
Debug test script to see exact error messages
"""

import requests

BASE_URL = "https://school-system-kh8s.onrender.com/"

def debug_main_page():
    """Get detailed error information from main page"""
    print("🔍 Debugging main page response...")
    
    try:
        response = requests.get(BASE_URL, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Content Length: {len(response.content)}")
        print("\n📄 Response Content (first 1000 chars):")
        print("-" * 50)
        print(response.text[:1000])
        print("-" * 50)
        
        if "DisallowedHost" in response.text:
            print("\n❌ CONFIRMED: DisallowedHost error still present")
            print("📋 ACTION NEEDED: Update ALLOWED_HOSTS environment variable on Render")
        elif response.status_code == 400:
            print("\n❌ Status 400 - Bad Request detected")
        elif response.status_code == 200:
            print("\n✅ App is working correctly!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def debug_admin_page():
    """Get detailed error information from admin page"""
    print("\n🔍 Debugging admin page response...")
    
    try:
        admin_url = BASE_URL + "admin/"
        response = requests.get(admin_url, timeout=30)
        print(f"Admin Status Code: {response.status_code}")
        print(f"Admin Content Length: {len(response.content)}")
        
        if response.status_code == 200:
            print("✅ Admin page accessible")
        else:
            print(f"❌ Admin page error: {response.status_code}")
            print("First 500 chars of admin response:")
            print(response.text[:500])
            
    except Exception as e:
        print(f"❌ Admin Error: {e}")

if __name__ == "__main__":
    print("🚀 Debugging deployed app issues...")
    print(f"🔗 URL: {BASE_URL}")
    print("=" * 60)
    
    debug_main_page()
    debug_admin_page()
    
    print("\n" + "=" * 60)
    print("💡 NEXT STEPS:")
    print("1. Check Render dashboard environment variables")
    print("2. Ensure ALLOWED_HOSTS includes your domain")
    print("3. Redeploy after environment variable changes")
    print("4. If needed, trigger manual deployment") 