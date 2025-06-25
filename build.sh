#!/bin/bash
# Build script for Render deployment

echo "Starting build process..."

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Running database migrations..."
python manage.py migrate --noinput

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

echo "Build completed successfully!" 