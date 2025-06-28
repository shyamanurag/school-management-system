from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for API (temporarily disabled until API ViewSets are implemented)
router = DefaultRouter()
# API ViewSets temporarily disabled
# router.register(r'subjects', SubjectViewSet, basename='academics-subject')
# router.register(r'grades', GradeViewSet, basename='academics-grade')
# router.register(r'attendance', AttendanceViewSet, basename='academics-attendance')

# Web Interface URLs - NUCLEAR REBUILD OF ACADEMICS MODULE
urlpatterns = [
    # Academics Dashboard
    path('', views.academics_dashboard, name='dashboard'),
    
    # Attendance Management
    path('attendance/', views.AttendanceListView.as_view(), name='attendance-list'),
    path('attendance/mark/', views.mark_attendance, name='mark-attendance'),
    path('attendance/reports/', views.attendance_reports, name='attendance-reports'),
    path('attendance/export/', views.export_attendance, name='export-attendance'),
    
    # Subject Management
    path('subjects/', views.SubjectListView.as_view(), name='subject-list'),
    path('subjects/<int:pk>/', views.SubjectDetailView.as_view(), name='subject-detail'),
    
    # Grade Management
    path('grades/', views.GradeListView.as_view(), name='grade-list'),
    path('grades/<int:pk>/', views.GradeDetailView.as_view(), name='grade-detail'),
    
    # API URLs (temporarily disabled)
    # path('api/', include(router.urls)),
]
