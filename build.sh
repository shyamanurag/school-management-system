#!/usr/bin/env bash
# Build script for Render

set -o errexit  # Exit on error

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --noinput --settings=school_modernized.settings.production

echo "Running migrations..."
python manage.py migrate --settings=school_modernized.settings.production

echo "Populating database with sample data..."
python populate_data.py --settings=school_modernized.settings.production

echo "Build completed successfully!" 