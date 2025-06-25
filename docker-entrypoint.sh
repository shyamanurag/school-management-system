#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting School Management System...${NC}"

# Wait for database to be ready
echo -e "${YELLOW}Waiting for database...${NC}"
while ! nc -z "${DB_HOST:-db}" "${DB_PORT:-5432}"; do
  echo -e "${YELLOW}Database is unavailable - sleeping${NC}"
  sleep 1
done
echo -e "${GREEN}Database is ready!${NC}"

# Wait for Redis to be ready
echo -e "${YELLOW}Waiting for Redis...${NC}"
REDIS_HOST=$(echo $REDIS_URL | cut -d'/' -f3 | cut -d':' -f1)
REDIS_PORT=$(echo $REDIS_URL | cut -d'/' -f3 | cut -d':' -f2)
while ! nc -z "${REDIS_HOST:-redis}" "${REDIS_PORT:-6379}"; do
  echo -e "${YELLOW}Redis is unavailable - sleeping${NC}"
  sleep 1
done
echo -e "${GREEN}Redis is ready!${NC}"

# Apply database migrations
echo -e "${YELLOW}Applying database migrations...${NC}"
python manage.py migrate --noinput

# Create cache table
echo -e "${YELLOW}Creating cache table...${NC}"
python manage.py createcachetable || true

# Create superuser if it doesn't exist
echo -e "${YELLOW}Creating superuser...${NC}"
python manage.py shell -c "
from django.contrib.auth import get_user_model
from django.conf import settings
import os

User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@school.edu')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f'Superuser {username} created successfully')
else:
    print(f'Superuser {username} already exists')
" || true

# Load initial data
echo -e "${YELLOW}Loading initial data...${NC}"
python manage.py loaddata initial_data.json || true

# Collect static files (if not done in build)
if [ "$COLLECT_STATIC" = "true" ]; then
    echo -e "${YELLOW}Collecting static files...${NC}"
    python manage.py collectstatic --noinput
fi

# Start Celery worker in background (if enabled)
if [ "$START_CELERY" = "true" ]; then
    echo -e "${YELLOW}Starting Celery worker...${NC}"
    celery -A school_modernized worker --loglevel=info --detach
fi

# Start Celery beat in background (if enabled)
if [ "$START_CELERY_BEAT" = "true" ]; then
    echo -e "${YELLOW}Starting Celery beat...${NC}"
    celery -A school_modernized beat --loglevel=info --detach
fi

echo -e "${GREEN}Initialization complete!${NC}"

# Execute the main command
exec "$@" 