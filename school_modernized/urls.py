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
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Authentication (Demo)
    path('login/', views.simple_login, name='simple_login'),
    path('logout/', views.simple_logout, name='simple_logout'),
    
    # Landing page
    path('', views.landing_page, name='landing'),
    
    # School settings
    path('school-settings/', views.school_settings_view, name='school_settings'),
    path('departments/', views.departments_list, name='departments_list'),
    path('campuses/', views.campuses_list, name='campuses_list'),
    path('campuses/<int:campus_id>/', views.campus_detail, name='campus_detail'),
    path('rooms/', views.rooms_list, name='rooms_list'),
    path('academic-years/', views.academic_years_list, name='academic_years_list'),
    
    # Core application (Dashboard, Settings, etc.)
    path('dashboard/', include('core.urls')),
    
    # === ULTRA-PROFESSIONAL MODULES - FULLY ENABLED ===
    
    # Academic Management (Ultra-Professional) - API Only Module
    
    # Student Information System (Comprehensive)
    path('students/', include('students.urls')),
    
    # Financial Management (Advanced)
    path('fees/', include('fees.urls')),
    
    # Communication & Notifications (Multi-Channel)
    path('communication/', include('communication.urls')),
    
    # Library Management (Digital Library Platform)
    path('library/', include('library.urls')),
    
    # Transport Management (Fleet & GPS Tracking)
    path('transport/', include('transport.urls')),
    
    # Hostel Management (Residential Management)
    path('hostel/', include('hostel.urls')),
    
    # Inventory Management (Complete ERP)
    path('inventory/', include('inventory.urls')),
    
    # === ULTRA-PROFESSIONAL DASHBOARDS ===
    
    # AI Analytics Dashboard (Machine Learning Insights)
    path('analytics/', TemplateView.as_view(template_name='analytics/analytics_dashboard.html'), name='analytics_dashboard'),
    
    # Examinations Dashboard (Online Exam Platform)
    path('examinations/', TemplateView.as_view(template_name='examinations/exam_dashboard.html'), name='examinations_dashboard'),
    
    # HR Dashboard (Enterprise HRMS)
    path('hr/', TemplateView.as_view(template_name='hr/dashboard.html'), name='hr_dashboard'),
    
    # === API ENDPOINTS ===
    
    # Academic Management API (Ultra-Professional)
    path('api/academics/', include('academics.urls')),
    
    # Student Management API
    path('api/students/', include('students.urls')),
    
    # Fee Management API
    path('api/fees/', include('fees.urls')),
    
    # Library Management API
    path('api/library/', include('library.urls')),
    
    # Transport Management API
    path('api/transport/', include('transport.urls')),
    
    # Hostel Management API
    path('api/hostel/', include('hostel.urls')),
    
    # Inventory Management API
    path('api/inventory/', include('inventory.urls')),
    
    # Communication API
    path('api/communication/', include('communication.urls')),
    
    # HR Management API (Enterprise HRMS)
    path('api/hr/', include('hr.urls')),
    
    # Examinations API (Online Exam Platform)
    path('api/examinations/', include('examinations.urls')),
    
    # Admissions API (Complete Admission Management)
    path('api/admissions/', include('admissions.urls')),
    
    # AI Analytics API (Machine Learning Insights)
    path('api/analytics/', include('analytics.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers
handler404 = 'school_modernized.views.handler404'
handler500 = 'school_modernized.views.handler500'
