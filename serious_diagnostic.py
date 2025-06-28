"""
SERIOUS DIAGNOSTIC SCRIPT - Examine actual homepage content
"""
import requests
import re
from html import unescape

def analyze_homepage():
    """Deep analysis of what's actually being served"""
    print(" DEEP HOMEPAGE ANALYSIS")
    print("=" * 50)
    
    try:
        # Get the actual homepage
        response = requests.get("https://school-management-system-f1rl.onrender.com/", timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Content Length: {len(response.content)} bytes")
        print()
        
        if response.status_code == 200:
            content = response.text
            
            # Check for login redirect
            if '/login/' in response.url:
                print(" REDIRECTED TO LOGIN PAGE")
                print(f"Final URL: {response.url}")
                
                # Analyze login page content
                print("\n LOGIN PAGE ANALYSIS:")
                if 'csrfmiddlewaretoken' in content:
                    print(" CSRF token present")
                else:
                    print(" Missing CSRF token")
                
                if 'username' in content and 'password' in content:
                    print(" Login form present")
                else:
                    print(" Login form missing")
                    
            else:
                print(" ANALYZING DASHBOARD CONTENT:")
                
                # Look for specific dashboard elements
                indicators = {
                    'Ultra-Professional': 'Ultra-Professional' in content,
                    'Enterprise': 'Enterprise' in content or 'enterprise' in content,
                    'Students count': any(word in content for word in ['students:', 'Students:', 'student count']),
                    'Teachers count': any(word in content for word in ['teachers:', 'Teachers:', 'teacher count']),
                    'Professional stats': 'professional_stats' in content,
                    'Academic stats': 'academic_stats' in content,
                    'Financial stats': 'financial_stats' in content,
                    'AI Analytics': 'ai_insights' in content or 'AI' in content,
                    'Error handling': 'error' in content.lower(),
                    'Template name': 'dashboard.html' in content
                }
                
                print("\n CONTENT INDICATORS:")
                for indicator, present in indicators.items():
                    status = "" if present else ""
                    print(f"{status} {indicator}")
                
                # Extract any visible text content
                print("\n VISIBLE TEXT SAMPLE:")
                # Remove HTML tags for readability
                text_content = re.sub(r'<[^>]+>', '', content)
                # Get first 500 chars of visible text
                visible_text = ' '.join(text_content.split())[:500]
                print(visible_text)
                
                # Check for specific error messages
                print("\n ERROR DETECTION:")
                error_patterns = [
                    'Server Error',
                    'Django administration',
                    'Page not found',
                    'TemplateDoenNotExist',
                    'Database error',
                    'Internal Server Error'
                ]
                
                for pattern in error_patterns:
                    if pattern.lower() in content.lower():
                        print(f" Found: {pattern}")
                    else:
                        print(f" No {pattern}")
        
        else:
            print(f" HTTP ERROR: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except Exception as e:
        print(f" ERROR: {e}")

if __name__ == "__main__":
    analyze_homepage()
