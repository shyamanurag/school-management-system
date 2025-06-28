"""
DASHBOARD FIX VERIFICATION SCRIPT
Run this when the server is back online to confirm fixes are working
"""
import requests
import re

def verify_fix():
    print(" Verifying Dashboard Fix...")
    print("=" * 40)
    
    try:
        # Test authentication flow
        session = requests.Session()
        
        # Get login page
        login_page = session.get("https://school-management-system-f1rl.onrender.com/")
        print(f"Homepage Status: {login_page.status_code}")
        
        if login_page.status_code == 200:
            # Extract CSRF token
            csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', login_page.text)
            
            if csrf_match:
                csrf_token = csrf_match.group(1)
                
                # Login
                login_data = {
                    'username': 'admin',
                    'password': 'admin123',
                    'csrfmiddlewaretoken': csrf_token
                }
                
                dashboard = session.post(
                    "https://school-management-system-f1rl.onrender.com/login/",
                    data=login_data,
                    allow_redirects=True
                )
                
                if dashboard.status_code == 200 and '/login/' not in dashboard.url:
                    print(" Login successful!")
                    
                    # Check for actual data
                    content = dashboard.text
                    
                    # Look for student/teacher counts
                    numbers = re.findall(r'<p style="font-size: 24px[^>]*>(\d+)</p>', content)
                    
                    if numbers:
                        student_count = int(numbers[0]) if len(numbers) > 0 else 0
                        teacher_count = int(numbers[1]) if len(numbers) > 1 else 0
                        user_count = int(numbers[2]) if len(numbers) > 2 else 0
                        
                        print(f" Dashboard Data:")
                        print(f"   Students: {student_count}")
                        print(f"   Teachers: {teacher_count}")
                        print(f"   Users: {user_count}")
                        
                        if student_count > 0 and teacher_count > 0:
                            print(" SUCCESS! Dashboard now shows REAL DATA!")
                            return True
                        else:
                            print(" Still showing zeros - investigate further")
                            return False
                    else:
                        print(" Could not extract dashboard numbers")
                        return False
                else:
                    print(f" Login failed: {dashboard.status_code}")
                    return False
            else:
                print(" CSRF token not found")
                return False
        else:
            print(f" Server error: {login_page.status_code}")
            return False
            
    except Exception as e:
        print(f" Error: {e}")
        return False

if __name__ == "__main__":
    success = verify_fix()
    if success:
        print("\n FIX VERIFICATION SUCCESSFUL! ")
    else:
        print("\n Additional troubleshooting may be needed")
