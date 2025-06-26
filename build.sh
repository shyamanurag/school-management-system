#!/bin/bash
# Streamlined build script for Render deployment

echo "=== Starting build process ==="

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run database migrations with timeout
echo "Running database migrations..."
timeout 300 python manage.py migrate --noinput || echo "Migration timeout, will retry on startup"

# Make start script executable
chmod +x start.sh

echo "=== Build completed successfully! ===" 