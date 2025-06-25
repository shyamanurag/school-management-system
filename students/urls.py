from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .api import StudentViewSet

router = DefaultRouter()
router.register(r'api/students', StudentViewSet)

urlpatterns = [
    path('', views.StudentListView.as_view(), name='student-list'),
    path('', include(router.urls)),
]
