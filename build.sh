#!/bin/bash
# Build script for Render deployment

echo "=== Starting build process ==="

# Show environment info
echo "Python version: $(python --version)"
echo "DATABASE_URL set: $([[ -n "$DATABASE_URL" ]] && echo "Yes" || echo "No")"
echo "DJANGO_SETTINGS_MODULE: ${DJANGO_SETTINGS_MODULE:-Not Set}"

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Test database connection
echo "Testing database connection..."
python manage.py shell --settings=school_modernized.settings.production << EOF
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
    print('Database connection: SUCCESS')
    print(f'Database backend: {connection.vendor}')
except Exception as e:
    print(f'Database connection: FAILED - {e}')
    raise
EOF

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Running database migrations..."
python manage.py migrate --noinput --verbosity=2

echo "Creating superuser if it doesn't exist..."
python manage.py shell << EOF
from django.contrib.auth.models import User
if not User.objects.filter(username='schooladmin').exists():
    User.objects.create_superuser('schooladmin', 'admin@school.com', 'admin123')
    print('Superuser created successfully')
else:
    print('Superuser already exists')
EOF

echo "Populating sample data if database is empty..."
python manage.py shell << EOF
from core.models import Student
if Student.objects.count() == 0:
    print('Database is empty, running populate_data.py...')
    exec(open('populate_data.py').read())
    print('Sample data populated successfully')
else:
    print('Database already has data')
EOF

echo "=== Build completed successfully! ===" 