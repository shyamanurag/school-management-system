from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import (
    HostelBlockViewSet,
    HostelRoomViewSet,
    HostelAdmissionViewSet,
    HostelResidentViewSet,
    MessMenuViewSet,
    MessAttendanceViewSet,
    HostelVisitorViewSet,
    HostelFeedbackViewSet
)
from . import views

router = DefaultRouter()
router.register(r'blocks', HostelBlockViewSet, basename='hostelblock')
router.register(r'rooms', HostelRoomViewSet, basename='hostelroom')
router.register(r'admissions', HostelAdmissionViewSet, basename='hosteladmission')
router.register(r'residents', HostelResidentViewSet, basename='hostelresident')
router.register(r'mess-menu', MessMenuViewSet, basename='messmenu')
router.register(r'mess-attendance', MessAttendanceViewSet, basename='messattendance')
router.register(r'visitors', HostelVisitorViewSet, basename='hostelvisitor')
router.register(r'feedback', HostelFeedbackViewSet, basename='hostelfeedback')

# Web Interface URLs - NUCLEAR REBUILD OF HOSTEL MODULE
urlpatterns = [
    # Hostel Dashboard
    path('', views.hostel_dashboard, name='dashboard'),
    
    # Hostel Management
    path('hostels/', views.HostelListView.as_view(), name='hostel-list'),
    path('hostels/<int:pk>/', views.HostelDetailView.as_view(), name='hostel-detail'),
    
    # Room Management
    path('rooms/', views.RoomListView.as_view(), name='room-list'),
    path('rooms/<int:pk>/', views.RoomDetailView.as_view(), name='room-detail'),
    
    # Student Allocation
    path('allocate/', views.allocate_room, name='allocate-room'),
    path('allocations/', views.AllocationListView.as_view(), name='allocation-list'),
    path('allocations/<int:allocation_id>/deallocate/', views.deallocate_room, name='deallocate-room'),
    
    # Reports
    path('reports/', views.hostel_reports, name='reports'),
    path('export/', views.export_hostel_data, name='export-data'),
    
    # API URLs (temporarily disabled)
    # path('api/', include(router.urls)),
] 