from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import (
    SubjectViewSet, ExamTypeViewSet, ExamScheduleViewSet, ExamViewSet,
    QuestionBankViewSet, OnlineExamViewSet, StudentExamAttemptViewSet,
    ExamResultViewSet, GradingSchemeViewSet, HallTicketViewSet,
    ExamReportViewSet
)

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'subjects', SubjectViewSet, basename='exam-subject')
router.register(r'exam-types', ExamTypeViewSet, basename='exam-type')
router.register(r'exam-schedules', ExamScheduleViewSet, basename='exam-schedule')
router.register(r'exams', ExamViewSet, basename='exam')
router.register(r'question-bank', QuestionBankViewSet, basename='question-bank')
router.register(r'online-exams', OnlineExamViewSet, basename='online-exam')
router.register(r'exam-attempts', StudentExamAttemptViewSet, basename='exam-attempt')
router.register(r'exam-results', ExamResultViewSet, basename='exam-result')
router.register(r'grading-schemes', GradingSchemeViewSet, basename='grading-scheme')
router.register(r'hall-tickets', HallTicketViewSet, basename='hall-ticket')
router.register(r'exam-reports', ExamReportViewSet, basename='exam-report')

# The API URLs are determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
] 