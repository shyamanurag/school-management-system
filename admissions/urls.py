from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import (
    AcademicSessionViewSet, AdmissionCriteriaViewSet, ApplicationFormViewSet,
    DocumentSubmissionViewSet, EntranceTestViewSet, InterviewViewSet,
    AdmissionResultViewSet, AdmissionReportViewSet
)

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'academic-sessions', AcademicSessionViewSet, basename='admission-session')
router.register(r'admission-criteria', AdmissionCriteriaViewSet, basename='admission-criteria')
router.register(r'applications', ApplicationFormViewSet, basename='admission-application')
router.register(r'documents', DocumentSubmissionViewSet, basename='admission-document')
router.register(r'entrance-tests', EntranceTestViewSet, basename='entrance-test')
router.register(r'interviews', InterviewViewSet, basename='admission-interview')
router.register(r'admission-results', AdmissionResultViewSet, basename='admission-result')
router.register(r'admission-reports', AdmissionReportViewSet, basename='admission-report')

# The API URLs are determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
] 