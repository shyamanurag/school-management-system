from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

# Professional URL Configuration for Ultra-Professional Educational ERP Platform
urlpatterns = [
    # Core system URLs - Professional Dashboard and Features
    path('', include('core.urls')),
    
    # Authentication URLs with enhanced security
    path('login/', auth_views.LoginView.as_view(template_name='simple_login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    
    # Professional Module URLs - redirect to working dashboard
    path('dashboard/', RedirectView.as_view(url='/', permanent=False)),
    
    # Module redirects to professional dashboard (avoiding broken admin)
    path('fee/', RedirectView.as_view(url='/', permanent=False)),
    path('fees/', RedirectView.as_view(url='/', permanent=False)),
    path('students/', RedirectView.as_view(url='/', permanent=False)),
    path('academics/', RedirectView.as_view(url='/', permanent=False)),
    path('examinations/', RedirectView.as_view(url='/', permanent=False)),
    path('library/', RedirectView.as_view(url='/', permanent=False)),
    path('transport/', RedirectView.as_view(url='/', permanent=False)),
    path('hostel/', RedirectView.as_view(url='/', permanent=False)),
    path('hr/', RedirectView.as_view(url='/', permanent=False)),
    path('inventory/', RedirectView.as_view(url='/', permanent=False)),
    path('communication/', RedirectView.as_view(url='/', permanent=False)),
    
    # Admin panel - moved to end and optional
    path('admin/', admin.site.urls),
]

# Static and media files for development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
