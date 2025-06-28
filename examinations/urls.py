from django.urls import path
from . import views

# Web Interface URLs - MINIMAL VERSION FOR TESTING
app_name = 'examinations'

urlpatterns = [
    # Examinations Dashboard
    path('', views.examinations_dashboard, name='dashboard'),
    
    # Exam Management
    path('exams/', views.ExamListView.as_view(), name='exam-list'),
    
    # Exam Results Management
    path('results/', views.ExamResultListView.as_view(), name='result-list'),
]
