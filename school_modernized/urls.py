from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication URLs (fixed logout to allow GET)
    path('login/', auth_views.LoginView.as_view(template_name='simple_login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    
    # Core system URLs
    path('', include('core.urls')),
    path('dashboard/', RedirectView.as_view(url='/', permanent=False)),
    
    # Module URLs
    path('students/', include('students.urls')),
    path('academics/', include('academics.urls')), 
    path('fees/', include('fees.urls')),
    path('fee/', RedirectView.as_view(url='/fees/', permanent=False)),
    path('examinations/', include('examinations.urls')),
    path('library/', include('library.urls')),
    path('transport/', include('transport.urls')),
    path('hostel/', include('hostel.urls')),
    path('hr/', include('hr.urls')),
    path('inventory/', include('inventory.urls')),
    path('communication/', include('communication.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
