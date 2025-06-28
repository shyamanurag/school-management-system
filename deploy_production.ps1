# Production Deployment Script for School ERP System

Write-Host " Starting Production Deployment..." -ForegroundColor Green

# Set environment
$env:DJANGO_SETTINGS_MODULE = "school_modernized.settings.production"
Write-Host " Environment: Production" -ForegroundColor Blue

# Security check
Write-Host " Running security checks..." -ForegroundColor Yellow
python manage.py check --deploy --settings=school_modernized.settings.production

if ($LASTEXITCODE -ne 0) {
    Write-Host " Security checks failed!" -ForegroundColor Red
    exit 1
}

# Database migrations
Write-Host " Running migrations..." -ForegroundColor Yellow
python manage.py migrate --settings=school_modernized.settings.production

# Collect static files
Write-Host " Collecting static files..." -ForegroundColor Yellow
python manage.py collectstatic --noinput --settings=school_modernized.settings.production

# Create superuser
Write-Host " Setting up admin user..." -ForegroundColor Yellow
python manage.py createsuperuser --noinput --username admin --email admin@schoolerp.com --settings=school_modernized.settings.production 2>

# Final check
Write-Host " Final health check..." -ForegroundColor Yellow
python manage.py check --settings=school_modernized.settings.production

if ($LASTEXITCODE -eq 0) {
    Write-Host " Production deployment successful!" -ForegroundColor Green
    Write-Host " System is ready for production use" -ForegroundColor Green
} else {
    Write-Host " Deployment failed!" -ForegroundColor Red
}
