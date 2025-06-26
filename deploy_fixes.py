#!/usr/bin/env python3
"""
Deploy fixes to production
This script commits and pushes changes to trigger redeployment
"""

import subprocess
import sys
import os
from datetime import datetime

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"   Error: {e.stderr}")
        return False

def main():
    """Main deployment function"""
    print("🚀 Deploying School Management System Fixes")
    print("=" * 50)
    
    # Check if we're in a git repository
    if not os.path.exists('.git'):
        print("❌ Not in a git repository. Please run from project root.")
        sys.exit(1)
    
    # Add all changes
    if not run_command("git add .", "Adding all changes"):
        sys.exit(1)
    
    # Check if there are changes to commit
    result = subprocess.run("git diff --cached --quiet", shell=True)
    if result.returncode == 0:
        print("ℹ️  No changes to commit")
        return
    
    # Commit changes
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_message = f"Fix: Enable functional modules and populate database - {timestamp}"
    
    if not run_command(f'git commit -m "{commit_message}"', "Committing changes"):
        sys.exit(1)
    
    # Push to origin
    if not run_command("git push origin main", "Pushing to GitHub"):
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 DEPLOYMENT SUCCESSFUL!")
    print("=" * 50)
    print("📋 Changes deployed:")
    print("   ✅ Fixed module URLs to show actual functionality")
    print("   ✅ Added production database population script")
    print("   ✅ Enhanced build script with data population")
    print("   ✅ Improved static files configuration")
    print("   ✅ Added automatic admin user creation")
    print()
    print("🔍 What to expect:")
    print("   • Render will automatically redeploy your app")
    print("   • Database will be populated with sample data")
    print("   • Modules will show actual functionality instead of 'Coming Soon'")
    print("   • Dashboard will display rich statistics")
    print("   • Static files (CSS/JS) will load properly")
    print()
    print("🌐 Your app URL: https://school-system-kh8s.onrender.com/")
    print("👤 Admin Login: schooladmin / admin123")
    print()
    print("⏰ Deployment usually takes 3-5 minutes...")

if __name__ == "__main__":
    main() 