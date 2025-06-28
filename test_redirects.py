import requests
import sys

def test_redirect(path, name):
    """Test a specific redirect path"""
    url = f"https://school-management-system-f1rl.onrender.com{path}"
    try:
        response = requests.get(url, timeout=15, allow_redirects=False)
        print(f" {name}: {response.status_code}")
        
        if 'Location' in response.headers:
            redirect_to = response.headers['Location']
            print(f"   Redirects to: {redirect_to}")
            
            # Test the redirect target
            if redirect_to.startswith('/'):
                final_response = requests.get(f"https://school-management-system-f1rl.onrender.com{redirect_to}", timeout=15)
                print(f"   Final status: {final_response.status_code}")
            
        print()
        
    except Exception as e:
        print(f" {name}: ERROR - {e}")
        print()

# Test key redirects
test_redirect("/students/", "Students Module")
test_redirect("/fees/", "Fees Module") 
test_redirect("/dashboard/", "Dashboard Redirect")
test_redirect("/", "Homepage")
