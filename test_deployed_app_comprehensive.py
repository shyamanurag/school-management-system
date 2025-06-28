"""
DEPLOYED APP COMPREHENSIVE TESTING SUITE
Tests all endpoints, APIs, authentication, and functionality
on the live Render deployment
"""

import requests
import json
import time
from urllib.parse import urljoin
import sys

class SchoolERPTester:
    def __init__(self, base_url="https://school-management-system-f1rl.onrender.com"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.test_results = []
        
    def log_test(self, test_name, status, details="", response_time=None):
        """Log test results"""
        result = {
            'test': test_name,
            'status': status,
            'details': details,
            'response_time': response_time,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        self.test_results.append(result)
        
        status_icon = "" if status == "PASS" else "" if status == "FAIL" else ""
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   {details}")
        if response_time:
            print(f"   Response time: {response_time:.2f}ms")
        print()
    
    def test_basic_connectivity(self):
        """Test basic connectivity to the deployed app"""
        print(" TESTING BASIC CONNECTIVITY...")
        
        try:
            start_time = time.time()
            response = self.session.get(self.base_url, timeout=30)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                self.log_test("App Connectivity", "PASS", 
                            f"Status: {response.status_code}, Size: {len(response.content)} bytes", 
                            response_time)
                return True
            else:
                self.log_test("App Connectivity", "FAIL", 
                            f"Status: {response.status_code}, Response: {response.text[:200]}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("App Connectivity", "FAIL", f"Connection error: {str(e)}")
            return False
    
    def test_authentication_pages(self):
        """Test authentication related pages"""
        print(" TESTING AUTHENTICATION PAGES...")
        
        auth_urls = [
            ('/login/', 'Login Page'),
            ('/logout/', 'Logout Page'),
            ('/admin/', 'Admin Page'),
        ]
        
        for url, name in auth_urls:
            try:
                start_time = time.time()
                response = self.session.get(urljoin(self.base_url, url), timeout=15)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code in [200, 302, 405]:
                    details = f"Status: {response.status_code}"
                    if response.status_code == 302:
                        details += f", Redirects to: {response.headers.get('Location', 'Unknown')}"
                    elif response.status_code == 405:
                        details += f", Method not allowed (expected for some endpoints)"
                    
                    self.log_test(name, "PASS", details, response_time)
                else:
                    self.log_test(name, "FAIL", f"Status: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                self.log_test(name, "FAIL", f"Error: {str(e)}")
    
    def test_login_functionality(self):
        """Test actual login functionality"""
        print(" TESTING LOGIN FUNCTIONALITY...")
        
        # Get login page first
        try:
            login_url = urljoin(self.base_url, '/login/')
            response = self.session.get(login_url, timeout=15)
            
            if response.status_code != 200:
                self.log_test("Login Page Access", "FAIL", f"Status: {response.status_code}")
                return False
            
            # Try to find CSRF token
            csrf_token = None
            if 'csrfmiddlewaretoken' in response.text:
                import re
                csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.text)
                if csrf_match:
                    csrf_token = csrf_match.group(1)
            
            # Attempt login with admin credentials
            login_data = {
                'username': 'admin',
                'password': 'admin123',
            }
            
            if csrf_token:
                login_data['csrfmiddlewaretoken'] = csrf_token
            
            start_time = time.time()
            login_response = self.session.post(login_url, data=login_data, timeout=15)
            response_time = (time.time() - start_time) * 1000
            
            if login_response.status_code == 302:  # Redirect after successful login
                self.log_test("Admin Login", "PASS", 
                            f"Redirected to: {login_response.headers.get('Location', 'Unknown')}", 
                            response_time)
                return True
            elif login_response.status_code == 200:
                if 'Invalid' in login_response.text or 'error' in login_response.text.lower():
                    self.log_test("Admin Login", "FAIL", "Invalid credentials or login error")
                else:
                    self.log_test("Admin Login", "WARNING", "Login page returned but no clear success/failure")
                return False
            else:
                self.log_test("Admin Login", "FAIL", f"Status: {login_response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Login Functionality", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_main_pages(self):
        """Test main application pages"""
        print(" TESTING MAIN PAGES...")
        
        main_urls = [
            ('/', 'Homepage/Dashboard'),
            ('/dashboard/', 'Dashboard Redirect'),
            ('/students/', 'Students Module'),
            ('/fees/', 'Fees Module'),
            ('/fee/', 'Fee Redirect'),
            ('/academics/', 'Academics Module'),
            ('/examinations/', 'Examinations Module'),
            ('/library/', 'Library Module'),
            ('/transport/', 'Transport Module'),
            ('/hostel/', 'Hostel Module'),
            ('/hr/', 'HR Module'),
            ('/inventory/', 'Inventory Module'),
            ('/communication/', 'Communication Module'),
        ]
        
        for url, name in main_urls:
            try:
                start_time = time.time()
                response = self.session.get(urljoin(self.base_url, url), timeout=15)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    # Check if page has actual content
                    content_indicators = ['<!DOCTYPE html>', '<html', '<body', 'dashboard', 'students', 'login']
                    has_content = any(indicator in response.text.lower() for indicator in content_indicators)
                    
                    if has_content:
                        details = f"Status: 200, Content size: {len(response.content)} bytes"
                        if 'login' in response.text.lower():
                            details += " (Redirected to login - authentication required)"
                        self.log_test(name, "PASS", details, response_time)
                    else:
                        self.log_test(name, "WARNING", "Page loads but may have minimal content", response_time)
                        
                elif response.status_code == 302:
                    redirect_location = response.headers.get('Location', 'Unknown')
                    self.log_test(name, "PASS", f"Redirects to: {redirect_location}", response_time)
                    
                elif response.status_code == 404:
                    self.log_test(name, "FAIL", "Page not found (404)")
                    
                elif response.status_code == 500:
                    self.log_test(name, "FAIL", "Server error (500)")
                    
                else:
                    self.log_test(name, "WARNING", f"Status: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                self.log_test(name, "FAIL", f"Error: {str(e)}")
    
    def test_api_endpoints(self):
        """Test API endpoints if they exist"""
        print(" TESTING API ENDPOINTS...")
        
        api_urls = [
            ('/api/', 'API Root'),
            ('/api/students/', 'Students API'),
            ('/api/academics/', 'Academics API'),
            ('/api/fees/', 'Fees API'),
            ('/api/auth/login/', 'Auth API'),
        ]
        
        for url, name in api_urls:
            try:
                start_time = time.time()
                response = self.session.get(urljoin(self.base_url, url), timeout=15)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    # Check if it's JSON response
                    try:
                        json_data = response.json()
                        self.log_test(name, "PASS", f"JSON API response, {len(json_data)} items", response_time)
                    except:
                        self.log_test(name, "PASS", f"Non-JSON response, size: {len(response.content)}", response_time)
                        
                elif response.status_code == 401:
                    self.log_test(name, "WARNING", "Authentication required (401)")
                    
                elif response.status_code == 404:
                    self.log_test(name, "WARNING", "API endpoint not found (404)")
                    
                else:
                    self.log_test(name, "WARNING", f"Status: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                self.log_test(name, "FAIL", f"Error: {str(e)}")
    
    def test_static_files(self):
        """Test static files loading"""
        print(" TESTING STATIC FILES...")
        
        static_urls = [
            ('/static/', 'Static Files Root'),
            ('/static/css/', 'CSS Files'),
            ('/static/js/', 'JavaScript Files'),
            ('/static/img/', 'Image Files'),
            ('/favicon.ico', 'Favicon'),
        ]
        
        for url, name in static_urls:
            try:
                start_time = time.time()
                response = self.session.get(urljoin(self.base_url, url), timeout=10)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    self.log_test(name, "PASS", f"Accessible, size: {len(response.content)} bytes", response_time)
                elif response.status_code == 404:
                    self.log_test(name, "WARNING", "Not found (404) - may not be needed")
                else:
                    self.log_test(name, "WARNING", f"Status: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                self.log_test(name, "WARNING", f"Error: {str(e)}")
    
    def analyze_homepage_content(self):
        """Analyze the content of the homepage to understand what's being displayed"""
        print(" ANALYZING HOMEPAGE CONTENT...")
        
        try:
            response = self.session.get(self.base_url, timeout=15)
            
            if response.status_code == 200:
                content = response.text.lower()
                
                # Check for various indicators
                indicators = {
                    'Django': 'django' in content,
                    'Login Form': 'login' in content and ('password' in content or 'username' in content),
                    'Dashboard': 'dashboard' in content,
                    'Students': 'students' in content,
                    'Teachers': 'teachers' in content,
                    'Bootstrap': 'bootstrap' in content,
                    'JavaScript': 'script' in content,
                    'CSS': 'stylesheet' in content or '.css' in content,
                    'Error Messages': 'error' in content or '500' in content or '404' in content,
                    'Database Data': any(word in content for word in ['student', 'teacher', 'grade', 'subject']),
                }
                
                analysis = []
                for indicator, present in indicators.items():
                    status = "" if present else ""
                    analysis.append(f"{status} {indicator}")
                
                self.log_test("Homepage Content Analysis", "INFO", "; ".join(analysis))
                
                # Check if it's showing actual data or empty
                if 'students: 0' in content or 'teachers: 0' in content:
                    self.log_test("Database Data Display", "WARNING", "Dashboard shows 0 records - possible data loading issue")
                elif any(word in content for word in ['student', 'teacher', 'dashboard']):
                    self.log_test("Database Data Display", "PASS", "Dashboard appears to have data")
                
            else:
                self.log_test("Homepage Analysis", "FAIL", f"Cannot access homepage: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Homepage Analysis", "FAIL", f"Error: {str(e)}")
    
    def test_database_connectivity(self):
        """Test if the database is connected and has data"""
        print(" TESTING DATABASE CONNECTIVITY...")
        
        # Try to access pages that would show database data
        try:
            # Check admin page which usually shows database info
            admin_response = self.session.get(urljoin(self.base_url, '/admin/'), timeout=15)
            
            if admin_response.status_code == 200:
                if 'django administration' in admin_response.text.lower():
                    self.log_test("Django Admin Access", "PASS", "Admin interface accessible")
                    
                    # Check for model links that indicate database connectivity
                    models = ['users', 'students', 'teachers', 'groups']
                    found_models = [model for model in models if model in admin_response.text.lower()]
                    
                    if found_models:
                        self.log_test("Database Models", "PASS", f"Found models: {', '.join(found_models)}")
                    else:
                        self.log_test("Database Models", "WARNING", "Admin page loads but no models visible")
                else:
                    self.log_test("Django Admin", "WARNING", "Admin page accessible but not standard Django admin")
            elif admin_response.status_code == 302:
                self.log_test("Django Admin", "PASS", "Admin redirects (login required)")
            else:
                self.log_test("Django Admin", "WARNING", f"Admin page status: {admin_response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Database Connectivity Test", "FAIL", f"Error: {str(e)}")
    
    def generate_comprehensive_report(self):
        """Generate a comprehensive test report"""
        print("\n" + "="*80)
        print(" COMPREHENSIVE TEST REPORT")
        print("="*80)
        
        # Count results
        total_tests = len(self.test_results)
        passed = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed = len([r for r in self.test_results if r['status'] == 'FAIL'])
        warnings = len([r for r in self.test_results if r['status'] in ['WARNING', 'INFO']])
        
        print(f" TEST SUMMARY:")
        print(f"  Total Tests: {total_tests}")
        print(f"   Passed: {passed}")
        print(f"   Failed: {failed}")
        print(f"   Warnings: {warnings}")
        print(f"  Success Rate: {(passed/total_tests*100):.1f}%")
        print()
        
        # Show critical failures
        critical_failures = [r for r in self.test_results if r['status'] == 'FAIL']
        if critical_failures:
            print(" CRITICAL ISSUES:")
            for failure in critical_failures:
                print(f"   {failure['test']}: {failure['details']}")
            print()
        
        # Show warnings
        warnings_list = [r for r in self.test_results if r['status'] == 'WARNING']
        if warnings_list:
            print(" WARNINGS/ISSUES:")
            for warning in warnings_list:
                print(f"   {warning['test']}: {warning['details']}")
            print()
        
        # Performance analysis
        response_times = [r['response_time'] for r in self.test_results if r['response_time']]
        if response_times:
            avg_response = sum(response_times) / len(response_times)
            max_response = max(response_times)
            print(f" PERFORMANCE:")
            print(f"  Average Response Time: {avg_response:.2f}ms")
            print(f"  Slowest Response: {max_response:.2f}ms")
            print()
        
        # Recommendations
        print(" RECOMMENDATIONS:")
        if failed > 0:
            print("   Fix critical failures first - app may not be fully functional")
        if any('login' in r['details'].lower() for r in self.test_results):
            print("   Many pages require authentication - ensure login is working")
        if any('404' in r['details'] for r in self.test_results):
            print("   Some URLs not found - check URL routing configuration")
        if any('0 records' in r['details'] for r in self.test_results):
            print("   Database shows empty - may need to populate sample data")
        
        print("\n" + "="*80)

def main():
    """Run comprehensive testing suite"""
    print(" STARTING DEPLOYED APP COMPREHENSIVE TESTING")
    print("="*80)
    print(f" Testing URL: https://school-management-system-f1rl.onrender.com")
    print(f" Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tester = SchoolERPTester()
    
    # Run all tests
    if tester.test_basic_connectivity():
        tester.test_authentication_pages()
        tester.test_login_functionality()
        tester.test_main_pages()
        tester.test_api_endpoints()
        tester.test_static_files()
        tester.analyze_homepage_content()
        tester.test_database_connectivity()
    else:
        print(" Basic connectivity failed. Cannot proceed with other tests.")
    
    # Generate final report
    tester.generate_comprehensive_report()

if __name__ == "__main__":
    main()
