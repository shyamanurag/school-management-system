from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .api import StudentViewSet

router = DefaultRouter()
router.register(r'students', StudentViewSet)

urlpatterns = [
    # Web interface URLs
    path('', views.StudentListView.as_view(), name='student-list'),
    path('add/', views.StudentCreateView.as_view(), name='student-add'),
    path('<int:pk>/edit/', views.StudentUpdateView.as_view(), name='student-edit'),
    path('<int:pk>/delete/', views.StudentDeleteView.as_view(), name='student-delete'),
    path('<int:pk>/', views.StudentDetailView.as_view(), name='student-detail'),
    
    # API URLs - moved to separate path to avoid conflicts
    path('api/', include(router.urls)),
]
