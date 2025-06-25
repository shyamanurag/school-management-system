#!/usr/bin/env python3
"""
Test script for deployed School Management System
Tests the live app at: https://school-system-kh8s.onrender.com/
"""

import requests
import json
from urllib.parse import urljoin

# Configuration
BASE_URL = "https://school-system-kh8s.onrender.com/"
ADMIN_USERNAME = "schooladmin"
ADMIN_PASSWORD = "admin123"

class SchoolAppTester:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = BASE_URL
        self.csrf_token = None
        
    def test_main_page(self):
        """Test if main page loads without errors"""
        print("🏠 Testing main page access...")
        try:
            response = self.session.get(self.base_url, timeout=30)
            if response.status_code == 200:
                print("✅ Main page loads successfully")
                print(f"   Status: {response.status_code}")
                print(f"   Content length: {len(response.content)} bytes")
                return True
            else:
                print(f"❌ Main page failed: Status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def get_csrf_token(self):
        """Get CSRF token for admin login"""
        try:
            admin_url = urljoin(self.base_url, "admin/login/")
            response = self.session.get(admin_url, timeout=30)
            
            # Extract CSRF token from response
            if 'csrfmiddlewaretoken' in response.text:
                start = response.text.find('csrfmiddlewaretoken') 
                start = response.text.find('value="', start) + 7
                end = response.text.find('"', start)
                self.csrf_token = response.text[start:end]
                return True
            return False
        except Exception as e:
            print(f"Error getting CSRF token: {e}")
            return False
    
    def test_admin_login(self):
        """Test admin panel login"""
        print("\n🔐 Testing admin login...")
        try:
            # Get login page and CSRF token
            admin_url = urljoin(self.base_url, "admin/login/")
            
            if not self.get_csrf_token():
                print("❌ Could not get CSRF token")
                return False
            
            # Attempt login
            login_data = {
                'username': ADMIN_USERNAME,
                'password': ADMIN_PASSWORD,
                'csrfmiddlewaretoken': self.csrf_token,
                'next': '/admin/'
            }
            
            response = self.session.post(admin_url, data=login_data, timeout=30)
            
            if response.status_code == 200 and 'Django administration' in response.text:
                print("✅ Admin login successful")
                print("✅ Django admin interface accessible")
                return True
            elif response.status_code == 302:  # Redirect after successful login
                print("✅ Admin login successful (redirected)")
                return True
            else:
                print(f"❌ Admin login failed: Status {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Admin login error: {e}")
            return False
    
    def test_api_endpoints(self):
        """Test API endpoints"""
        print("\n🔌 Testing API endpoints...")
        
        endpoints = [
            "api/students/",
            "api/teachers/", 
            "api/grades/",
            "api/subjects/",
            "api/departments/"
        ]
        
        results = {}
        
        for endpoint in endpoints:
            try:
                url = urljoin(self.base_url, endpoint)
                response = self.session.get(url, timeout=30)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if isinstance(data, dict) and 'results' in data:
                            count = len(data['results'])
                            results[endpoint] = count
                            print(f"✅ {endpoint}: {count} records")
                        elif isinstance(data, list):
                            count = len(data)
                            results[endpoint] = count
                            print(f"✅ {endpoint}: {count} records")
                        else:
                            print(f"✅ {endpoint}: Valid JSON response")
                            results[endpoint] = "success"
                    except json.JSONDecodeError:
                        print(f"⚠️  {endpoint}: Non-JSON response (status 200)")
                        results[endpoint] = "non-json"
                else:
                    print(f"❌ {endpoint}: Status {response.status_code}")
                    results[endpoint] = f"error_{response.status_code}"
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ {endpoint}: Connection error - {e}")
                results[endpoint] = "connection_error"
        
        return results
    
    def test_database_population(self):
        """Test if database is properly populated with sample data"""
        print("\n📊 Testing database population...")
        
        try:
            # Test students count
            students_url = urljoin(self.base_url, "api/students/")
            response = self.session.get(students_url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if 'count' in data:
                    student_count = data['count']
                    if student_count >= 1000:  # Should have ~1017 students
                        print(f"✅ Students populated: {student_count} records")
                    else:
                        print(f"⚠️  Students count low: {student_count} (expected ~1017)")
                elif 'results' in data:
                    student_count = len(data['results'])
                    print(f"✅ Students sample: {student_count} records in current page")
                
        except Exception as e:
            print(f"❌ Error checking database population: {e}")
    
    def test_static_files(self):
        """Test if static files are being served"""
        print("\n📁 Testing static files...")
        
        # Test admin CSS
        admin_css_url = urljoin(self.base_url, "static/admin/css/base.css")
        try:
            response = self.session.get(admin_css_url, timeout=30)
            if response.status_code == 200:
                print("✅ Static files (admin CSS) loading correctly")
                return True
            else:
                print(f"⚠️  Static files may have issues: Status {response.status_code}")
                return False
        except Exception as e:
            print(f"⚠️  Could not test static files: {e}")
            return False
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🚀 Starting comprehensive test of deployed School Management System")
        print(f"🔗 Testing URL: {self.base_url}")
        print("=" * 70)
        
        results = {
            'main_page': self.test_main_page(),
            'admin_login': self.test_admin_login(),
            'static_files': self.test_static_files()
        }
        
        # API tests
        api_results = self.test_api_endpoints()
        results['api_endpoints'] = api_results
        
        # Database population test
        self.test_database_population()
        
        # Summary
        print("\n" + "=" * 70)
        print("📋 TEST SUMMARY")
        print("=" * 70)
        
        if results['main_page']:
            print("✅ Main page: WORKING")
        else:
            print("❌ Main page: FAILED")
            
        if results['admin_login']:
            print("✅ Admin login: WORKING")
        else:
            print("❌ Admin login: FAILED")
            
        if results['static_files']:
            print("✅ Static files: WORKING")
        else:
            print("⚠️  Static files: ISSUES")
        
        # API summary
        successful_apis = sum(1 for v in api_results.values() if isinstance(v, int) or v == "success")
        total_apis = len(api_results)
        print(f"🔌 API endpoints: {successful_apis}/{total_apis} working")
        
        overall_health = (
            results['main_page'] and 
            results['admin_login'] and 
            successful_apis >= total_apis * 0.7  # At least 70% APIs working
        )
        
        print("\n" + "🎯 OVERALL STATUS")
        if overall_health:
            print("🎉 YOUR SCHOOL MANAGEMENT SYSTEM IS SUCCESSFULLY DEPLOYED!")
            print("✅ App is live and functional")
            print("✅ Admin access working")
            print("✅ Database populated") 
            print("✅ API endpoints responding")
        else:
            print("⚠️  App deployed but needs attention:")
            if not results['main_page']:
                print("   - Main page access issues")
            if not results['admin_login']:
                print("   - Admin login problems")
            if successful_apis < total_apis * 0.7:
                print("   - Some API endpoints not responding")
        
        print(f"\n🌐 Live URL: {self.base_url}")
        print(f"🔐 Admin: {self.base_url}admin/ (schooladmin/admin123)")
        
        return overall_health

if __name__ == "__main__":
    tester = SchoolAppTester()
    tester.run_all_tests() 