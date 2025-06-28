from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='simple_login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    
    # Core system URLs - SAFE
    path('', include('core.urls')),
    
    # Redirects for common paths (temporarily redirect to admin until modules are fixed)
    path('dashboard/', RedirectView.as_view(url='/', permanent=False)),
    path('fee/', RedirectView.as_view(url='/admin/', permanent=False)),
    path('fees/', RedirectView.as_view(url='/admin/', permanent=False)),
    path('students/', RedirectView.as_view(url='/admin/', permanent=False)),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
