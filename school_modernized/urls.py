from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

# Professional URL Configuration for Ultra-Professional Educational ERP Platform
urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication URLs with enhanced security
    path('login/', auth_views.LoginView.as_view(template_name='simple_login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    
    # Core system URLs - Professional Dashboard and Features
    path('', include('core.urls')),
    
    # Professional Module URLs with error handling
    # Only include modules that have working URL configurations
    path('dashboard/', RedirectView.as_view(url='/', permanent=False)),
    
    # Gradually add module URLs back with error handling
    # These will be enabled one by one after verification
    
    # Core redirects for common paths
    path('fee/', RedirectView.as_view(url='/admin/', permanent=False)),
    path('fees/', RedirectView.as_view(url='/admin/', permanent=False)),
    path('students/', RedirectView.as_view(url='/admin/', permanent=False)),
    path('academics/', RedirectView.as_view(url='/admin/', permanent=False)),
    path('examinations/', RedirectView.as_view(url='/admin/', permanent=False)),
    path('library/', RedirectView.as_view(url='/admin/', permanent=False)),
    path('transport/', RedirectView.as_view(url='/admin/', permanent=False)),
    path('hostel/', RedirectView.as_view(url='/admin/', permanent=False)),
    path('hr/', RedirectView.as_view(url='/admin/', permanent=False)),
    path('inventory/', RedirectView.as_view(url='/admin/', permanent=False)),
    path('communication/', RedirectView.as_view(url='/admin/', permanent=False)),
]

# Static and media files for development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
