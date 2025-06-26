from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .api import (
    SubjectViewSet, ExamViewSet, AssignmentViewSet, 
    TimetableViewSet, AttendanceViewSet, HolidayViewSet
)

# Create router for API viewsets
router = DefaultRouter()
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'exams', ExamViewSet, basename='exam')
router.register(r'assignments', AssignmentViewSet, basename='assignment')
router.register(r'timetable', TimetableViewSet, basename='timetable')
router.register(r'attendance', AttendanceViewSet, basename='attendance')
router.register(r'holidays', HolidayViewSet, basename='holiday')

app_name = 'academics'

urlpatterns = [
    # Web Views
    path('', views.subject_list, name='subject_list'),
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/create/', views.subject_create, name='subject_create'),
    path('subjects/<int:pk>/', views.subject_detail, name='subject_detail'),
    path('subjects/<int:pk>/edit/', views.subject_update, name='subject_update'),
    path('subjects/<int:pk>/delete/', views.subject_delete, name='subject_delete'),
    
    # Exam management
    path('exams/', views.exam_list, name='exam_list'),
    path('exams/create/', views.exam_create, name='exam_create'),
    path('exams/<int:pk>/', views.exam_detail, name='exam_detail'),
    path('exams/<int:pk>/results/', views.exam_results, name='exam_results'),
    
    # Assignment management
    path('assignments/', views.assignment_list, name='assignment_list'),
    path('assignments/create/', views.assignment_create, name='assignment_create'),
    path('assignments/<int:pk>/', views.assignment_detail, name='assignment_detail'),
    path('assignments/<int:pk>/submissions/', views.assignment_submissions, name='assignment_submissions'),
    
    # Timetable management
    path('timetable/', views.timetable_view, name='timetable_view'),
    path('timetable/create/', views.timetable_create, name='timetable_create'),
    path('timetable/class/<int:class_id>/', views.class_timetable, name='class_timetable'),
    
    # Attendance management
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/mark/', views.attendance_mark, name='attendance_mark'),
    path('attendance/report/', views.attendance_report, name='attendance_report'),
    
    # Holiday management
    path('holidays/', views.holiday_list, name='holiday_list'),
    path('holidays/create/', views.holiday_create, name='holiday_create'),
    path('holidays/<int:pk>/edit/', views.holiday_update, name='holiday_update'),
    
    # Academic analytics
    path('analytics/', views.academic_analytics, name='academic_analytics'),
    path('analytics/performance/', views.performance_analytics, name='performance_analytics'),
    path('analytics/attendance/', views.attendance_analytics, name='attendance_analytics'),
    
    # API URLs
    path('api/', include(router.urls)),
]
