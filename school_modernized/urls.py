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
    
    # Module placeholder routes
    path('students/', lambda request: render(request, 'modules/coming_soon.html', {'module': 'Students'})),
    path('academics/', lambda request: render(request, 'modules/coming_soon.html', {'module': 'Academics'})),
    path('fees/', lambda request: render(request, 'modules/coming_soon.html', {'module': 'Fees'})),
    path('teachers/', lambda request: render(request, 'modules/coming_soon.html', {'module': 'Teachers'})),
    path('exams/', lambda request: render(request, 'modules/coming_soon.html', {'module': 'Exams'})),
    path('infrastructure/', lambda request: render(request, 'modules/coming_soon.html', {'module': 'Infrastructure'})),
    path('ai-analytics/', lambda request: render(request, 'modules/coming_soon.html', {'module': 'AI Analytics'})),
    path('communication/', lambda request: render(request, 'modules/coming_soon.html', {'module': 'Communication'})),
    path('parent-portal/', lambda request: render(request, 'modules/coming_soon.html', {'module': 'Parent Portal'})),
    path('virtual-classrooms/', lambda request: render(request, 'modules/coming_soon.html', {'module': 'Virtual Classrooms'})),
    path('reports/', lambda request: render(request, 'modules/coming_soon.html', {'module': 'Reports'})),
    path('mobile-app/', lambda request: render(request, 'modules/coming_soon.html', {'module': 'Mobile App'})),
    path('biometric/', lambda request: render(request, 'modules/coming_soon.html', {'module': 'Biometric'})),
    path('system/', lambda request: render(request, 'modules/coming_soon.html', {'module': 'System'})),
    
    # Legacy/placeholder routes (for backward compatibility)
    path('library/', lambda request: render(request, 'modules/coming_soon.html', {'module': 'Library'})),
    path('hostel/', lambda request: render(request, 'modules/coming_soon.html', {'module': 'Hostel'})),
    path('transport/', lambda request: render(request, 'modules/coming_soon.html', {'module': 'Transport'})),
    path('inventory/', lambda request: render(request, 'modules/coming_soon.html', {'module': 'Inventory'})),
]

# Add media files serving in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
