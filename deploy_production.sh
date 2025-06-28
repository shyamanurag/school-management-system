#!/bin/bash
# Production Deployment Script for School ERP System

echo " Starting Production Deployment..."

# Environment check
if [ -z "$DJANGO_SETTINGS_MODULE" ]; then
    export DJANGO_SETTINGS_MODULE=school_modernized.settings.production
fi

echo " Environment: $DJANGO_SETTINGS_MODULE"

# Security check
echo " Running security checks..."
python manage.py check --deploy

if [ $? -ne 0 ]; then
    echo " Security checks failed. Aborting deployment."
    exit 1
fi

# Database migrations
echo "  Running database migrations..."
python manage.py migrate --noinput

if [ $? -ne 0 ]; then
    echo " Database migration failed. Aborting deployment."
    exit 1
fi

# Collect static files
echo " Collecting static files..."
python manage.py collectstatic --noinput --clear

if [ $? -ne 0 ]; then
    echo " Static file collection failed. Aborting deployment."
    exit 1
fi

# Create superuser if it doesn't exist
echo " Creating superuser if needed..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@schoolerp.com', 'admin123')
    print("Superuser created: admin/admin123")
else:
    print("Superuser already exists")
EOF

# Database optimization
echo " Optimizing database..."
python manage.py shell << EOF
from django.db import connection
cursor = connection.cursor()
cursor.execute("ANALYZE;")
print("Database analyzed and optimized")
EOF

# Clear cache
echo " Clearing cache..."
python manage.py shell << EOF
from django.core.cache import cache
cache.clear()
print("Cache cleared")
EOF

# Health check
echo " Running health checks..."
python manage.py check

if [ $? -eq 0 ]; then
    echo " Production deployment successful!"
    echo " Access your application at: http://your-domain.com"
    echo " Admin panel: http://your-domain.com/admin/"
    echo " Admin credentials: admin/admin123"
else
    echo " Health check failed!"
    exit 1
fi

echo " System Statistics:"
python manage.py shell << EOF
from core.models import Student, Teacher, SchoolSettings
from django.contrib.auth.models import User

print(f"Students: {Student.objects.count()}")
print(f"Teachers: {Teacher.objects.count()}")
print(f"Users: {User.objects.count()}")
print(f"Schools: {SchoolSettings.objects.count()}")
EOF

echo " Deployment complete!"
