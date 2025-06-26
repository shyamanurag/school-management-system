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

router = DefaultRouter()
router.register(r'blocks', HostelBlockViewSet, basename='hostelblock')
router.register(r'rooms', HostelRoomViewSet, basename='hostelroom')
router.register(r'admissions', HostelAdmissionViewSet, basename='hosteladmission')
router.register(r'residents', HostelResidentViewSet, basename='hostelresident')
router.register(r'mess-menu', MessMenuViewSet, basename='messmenu')
router.register(r'mess-attendance', MessAttendanceViewSet, basename='messattendance')
router.register(r'visitors', HostelVisitorViewSet, basename='hostelvisitor')
router.register(r'feedback', HostelFeedbackViewSet, basename='hostelfeedback')

urlpatterns = [
    path('', include(router.urls)),
] 