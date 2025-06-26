#!/bin/bash
# Enhanced build script for Render deployment

echo "🚀 Starting build process..."

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Run database migrations with timeout
echo "🗄️  Running database migrations..."
timeout 300 python manage.py migrate --noinput || echo "⚠️ Migration timeout, will retry on startup"

# Collect static files with proper settings
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Populate comprehensive sample data if database is empty
echo "📊 Populating comprehensive sample data..."
timeout 300 python populate_data.py || echo "⚠️ Sample data population failed or skipped"

# Create superuser if needed
echo "👤 Creating admin user..."
python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='schooladmin').exists():
    User.objects.create_superuser('schooladmin', 'admin@school.edu', 'admin123')
    print('✅ Admin user created: schooladmin/admin123')
else:
    print('ℹ️ Admin user already exists')
EOF

# Make start script executable
chmod +x start.sh

echo "✅ Build completed successfully!" 