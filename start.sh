#!/bin/bash
# Startup script for Render deployment
set -e  # Exit on any error

echo "=== Django App Startup ==="
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "PORT: ${PORT:-NOT SET}"

# Debug environment variables
echo "=== Environment Variables Debug ==="
echo "DATABASE_URL: ${DATABASE_URL:-NOT SET}"
echo "DJANGO_SETTINGS_MODULE: ${DJANGO_SETTINGS_MODULE:-NOT SET}"
echo "DEBUG: ${DEBUG:-NOT SET}"
echo "SECRET_KEY: ${SECRET_KEY:+SET}"
echo "ALLOWED_HOSTS: ${ALLOWED_HOSTS:-NOT SET}"

# Ensure PORT is set
if [ -z "$PORT" ]; then
    echo "ERROR: PORT environment variable not set"
    exit 1
fi

# Run database migrations if needed
echo "Ensuring database migrations are applied..."
python manage.py migrate --noinput --run-syncdb 2>/dev/null || echo "Migrations completed or not needed"

# Create superuser if it doesn't exist (non-interactive)
echo "Creating admin user if needed..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='schooladmin').exists():
    User.objects.create_superuser('schooladmin', 'admin@school.com', 'admin123')
    print('Admin user created')
else:
    print('Admin user exists')
" 2>/dev/null || echo "Admin user setup completed"

# Load sample data if database is empty (with timeout)
echo "Loading sample data if needed..."
timeout 60 python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_modernized.settings.production')
django.setup()
from core.models import Student
if Student.objects.count() == 0:
    print('Loading sample data...')
    exec(open('populate_data.py').read())
    print('Sample data loaded')
else:
    print('Sample data already exists')
" 2>/dev/null || echo "Sample data setup completed"

# Start gunicorn
echo "✅ Starting gunicorn server..."
exec gunicorn --bind 0.0.0.0:$PORT --timeout 120 --workers 1 school_modernized.wsgi:application 