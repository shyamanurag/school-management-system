#!/bin/bash
# Startup script for Render deployment

echo "=== Django App Startup ==="
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Django settings: ${DJANGO_SETTINGS_MODULE:-Not Set}"

# Test WSGI import before starting gunicorn
echo "Testing WSGI import..."
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_modernized.settings.production')
from school_modernized.wsgi import application
print('✅ WSGI application imported successfully')
print(f'Application: {application}')
"

if [ $? -eq 0 ]; then
    echo "✅ WSGI test passed. Starting gunicorn..."
    exec gunicorn --bind 0.0.0.0:$PORT --timeout 120 --workers 1 school_modernized.wsgi:application
else
    echo "❌ WSGI test failed. Cannot start application."
    exit 1
fi 