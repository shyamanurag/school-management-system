from django.urls import path, include
from rest_framework.routers import DefaultRouter
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
    # API URLs - Primary functionality
    path('', include(router.urls)),
]
