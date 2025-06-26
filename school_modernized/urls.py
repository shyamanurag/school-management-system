"""
URL configuration for school_modernized project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render, redirect
from core.views import dashboard

def redirect_to_dashboard(request):
    """Redirect root URL to dashboard"""
    return redirect('dashboard')

urlpatterns = [
    # Root redirect to dashboard
    path('', redirect_to_dashboard, name='home'),
    
    # Admin interface
    path('admin/', admin.site.urls),
    
    # Core application URLs (main dashboard and features)
    path('dashboard/', dashboard, name='dashboard'),
    
    # Core application URLs
    path('core/', include('core.urls', namespace='core')),
    
    # Main functional modules
    path('students/', include('students.urls')),
    path('academics/', include('academics.urls')),
    path('fees/', include('fees.urls')),
    path('communication/', include('communication.urls')),
    path('library/', include('library.urls')),
    path('hostel/', include('hostel.urls')),
    path('transport/', include('transport.urls')),
    path('inventory/', include('inventory.urls')),
    
    # RESTORED ULTRA-PROFESSIONAL MODULES
    # Teachers/HR Module - Complete HRMS
    path('teachers/', include('core.hr_urls', namespace='hr')),
    path('hr/', include('core.hr_urls', namespace='hr-main')),
    
    # Examinations Module - Complete Online Exam Platform  
    path('exams/', lambda request: render(request, 'examinations/exam_dashboard.html')),
    path('examinations/', lambda request: render(request, 'examinations/exam_dashboard.html')),
    
    # Analytics & Reports - AI Analytics Platform
    path('ai-analytics/', lambda request: render(request, 'analytics/analytics_dashboard.html')),
    path('analytics/', lambda request: render(request, 'analytics/analytics_dashboard.html')),
    path('reports/', lambda request: render(request, 'analytics/reports_dashboard.html')),
    
    # Infrastructure Management (from core models)
    path('infrastructure/', lambda request: render(request, 'core/infrastructure_dashboard.html')),
    
    # Parent Portal (notifications + communication)
    path('parent-portal/', lambda request: render(request, 'notifications/parent_portal.html')),
    
    # Virtual Classrooms (communication + analytics)
    path('virtual-classrooms/', lambda request: render(request, 'communication/virtual_classrooms.html')),
    
    # Mobile App Interface
    path('mobile-app/', lambda request: render(request, 'core/mobile_app_dashboard.html')),
    
    # Biometric Integration
    path('biometric/', lambda request: render(request, 'core/biometric_dashboard.html')),
    
    # API endpoints (already included in individual apps)
    path('api/', include('students.urls')),
    path('api/', include('fees.urls')),
    path('api/', include('hostel.urls')),
    path('api/', include('library.urls')),
    path('api/', include('inventory.urls')),
    path('api/', include('transport.urls')),
    path('api/', include('communication.urls')),
]

# Add media files serving in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
