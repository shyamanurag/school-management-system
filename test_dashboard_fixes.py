"""
POST-FIX VERIFICATION SCRIPT
Test dashboard with actual data display
"""
import requests
import re
from html import unescape

def test_dashboard_after_fixes():
    """Test dashboard to verify fixes are working"""
    print(" TESTING DASHBOARD AFTER FIXES")
    print("=" * 50)
    
    try:
        # Test homepage redirect behavior
        print("1. Testing homepage access...")
        response = requests.get("https://school-management-system-f1rl.onrender.com/", 
                              timeout=30, allow_redirects=True)
        
        print(f"   Status: {response.status_code}")
        print(f"   Final URL: {response.url}")
        
        if '/login/' in response.url:
            print("    Correctly redirected to login")
            
            # Test login page content
            content = response.text
            print("\n2. Testing login page content...")
            
            login_checks = {
                'CSRF token': 'csrfmiddlewaretoken' in content,
                'Username field': 'name="username"' in content,
                'Password field': 'name="password"' in content,
                'Demo credentials': 'admin/admin123' in content,
                'Login form': '<form method="post">' in content
            }
            
            for check, passed in login_checks.items():
                status = "" if passed else ""
                print(f"   {status} {check}")
            
            # Try login to test authentication
            print("\n3. Testing login functionality...")
            
            # Extract CSRF token
            csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', content)
            if csrf_match:
                csrf_token = csrf_match.group(1)
                print(f"    CSRF token extracted: {csrf_token[:10]}...")
                
                # Attempt login
                login_data = {
                    'username': 'admin',
                    'password': 'admin123',
                    'csrfmiddlewaretoken': csrf_token
                }
                
                session = requests.Session()
                login_response = session.post(
                    "https://school-management-system-f1rl.onrender.com/login/",
                    data=login_data,
                    timeout=30,
                    allow_redirects=True
                )
                
                print(f"   Login Status: {login_response.status_code}")
                print(f"   Login Final URL: {login_response.url}")
                
                if login_response.status_code == 200 and '/login/' not in login_response.url:
                    print("    Login successful - redirected to dashboard")
                    
                    # Test dashboard content for actual data
                    print("\n4. Testing dashboard data display...")
                    dashboard_content = login_response.text
                    
                    # Look for actual numbers instead of zeros
                    data_indicators = {
                        'Student count display': 'Students</h3>' in dashboard_content,
                        'Teacher count display': 'Teachers</h3>' in dashboard_content,
                        'User count display': 'Users</h3>' in dashboard_content,
                        'Non-zero values': not all(f'>{i}</p>' in dashboard_content for i in range(5)),
                        'Welcome message': 'Welcome,' in dashboard_content,
                        'School ERP title': 'School ERP' in dashboard_content
                    }
                    
                    for indicator, present in data_indicators.items():
                        status = "" if present else ""
                        print(f"   {status} {indicator}")
                    
                    # Extract visible numbers
                    print("\n5. Extracting dashboard statistics...")
                    number_pattern = r'<p style="font-size: 24px[^>]*>(\d+)</p>'
                    numbers = re.findall(number_pattern, dashboard_content)
                    
                    if numbers:
                        print(f"    Statistics found: {numbers}")
                        if any(int(num) > 0 for num in numbers):
                            print("    NON-ZERO DATA DETECTED!")
                        else:
                            print("    All values still showing as zero")
                    else:
                        print("    No statistics found in expected format")
                        
                else:
                    print("    Login failed or stuck on login page")
                    print(f"   Response content sample: {login_response.text[:200]}")
            else:
                print("    CSRF token not found")
        else:
            print("    Not redirected to login - unexpected behavior")
            
    except Exception as e:
        print(f" ERROR: {e}")

if __name__ == "__main__":
    test_dashboard_after_fixes()
