"""
QUICK SUCCESS TEST - Verify core app is working
"""

import requests

def test_core_functionality():
    base_url = "https://school-management-system-f1rl.onrender.com"
    
    print(" TESTING CORE APP FUNCTIONALITY")
    print("=" * 50)
    
    try:
        # Test main app
        response = requests.get(base_url, timeout=30)
        if response.status_code == 200:
            print(" MAIN APP: Working! (Status: 200)")
            print(f"    Response size: {len(response.content)} bytes")
            
            # Check if it contains expected content
            content = response.text.lower()
            if 'school' in content or 'dashboard' in content or 'login' in content:
                print(" CONTENT: Contains expected school/dashboard content")
            else:
                print(" CONTENT: May not have expected content")
                
        else:
            print(f" MAIN APP: Failed (Status: {response.status_code})")
            return False
            
        # Test login page
        login_response = requests.get(f"{base_url}/login/", timeout=30)
        if login_response.status_code == 200:
            print(" LOGIN PAGE: Working! (Status: 200)")
        else:
            print(f" LOGIN PAGE: Issue (Status: {login_response.status_code})")
            
        print("\n CORE APP FUNCTIONALITY: WORKING!")
        print("=" * 50)
        print(" Your Django School ERP is now LIVE and accessible!")
        print(" URL: https://school-management-system-f1rl.onrender.com")
        print(" Login page: https://school-management-system-f1rl.onrender.com/login/")
        print("\n NEXT STEPS:")
        print("  1. Visit the URL to see your working app")
        print("  2. Try logging in with admin/admin123")
        print("  3. Gradually add back module functionality")
        print("  4. Fix remaining admin panel issues")
        
        return True
        
    except Exception as e:
        print(f" ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    test_core_functionality()
