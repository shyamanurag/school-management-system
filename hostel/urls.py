from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .api import HostelViewSet, RoomTypeViewSet, HostelRoomViewSet, HostelAssignmentViewSet

router = DefaultRouter()
router.register(r'api/hostels', HostelViewSet)
router.register(r'api/roomtypes', RoomTypeViewSet)
router.register(r'api/hostelrooms', HostelRoomViewSet)
router.register(r'api/hostelassignments', HostelAssignmentViewSet)

urlpatterns = [
    path('', views.HostelListView.as_view(), name='hostel-list'),
    path('add/', views.HostelCreateView.as_view(), name='hostel-add'),
    path('<int:pk>/edit/', views.HostelUpdateView.as_view(), name='hostel-edit'),
    path('<int:pk>/delete/', views.HostelDeleteView.as_view(), name='hostel-delete'),
    path('', include(router.urls)),
]
