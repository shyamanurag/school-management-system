from django.urls import path
from django.http import HttpResponse
from . import views

def test_students_view(request):
    """Simple test view to verify URL routing works"""
    return HttpResponse("✅ STUDENTS MODULE WORKING! URL routing is functional.")

urlpatterns = [
    # TEMPORARY TEST - Core student views (these exist)
    path('', test_students_view, name='student-list'),
    path('original/', views.StudentListView.as_view(), name='student-list-original'),
    path('<int:pk>/', views.StudentDetailView.as_view(), name='student-detail'),
    path('dashboard/', views.student_dashboard, name='student-dashboard'),
    path('create/', views.StudentCreateView.as_view(), name='student-create'),
    path('<int:pk>/edit/', views.StudentUpdateView.as_view(), name='student-update'),
    
    # Export and analytics (these exist)
    path('export/', views.export_students, name='export-students'),
    path('analytics/api/', views.student_analytics_api, name='student-analytics-api'),
    
    # Enhanced features (implementation views exist)
    path('<int:student_id>/documents/', views.student_document_management, name='student-document-management'),
    path('<int:student_id>/medical/', views.student_medical_records, name='student-medical-records'),
    path('<int:student_id>/parent-portal/', views.student_parent_portal, name='student-parent-portal'),
    path('<int:student_id>/transfer-withdrawal/', views.student_transfer_withdrawal, name='student-transfer-withdrawal'),
    path('<int:student_id>/id-card/', views.student_id_card_generation, name='student-id-card'),
    path('<int:student_id>/biometric/', views.biometric_attendance_management, name='student-biometric-attendance'),
    path('<int:student_id>/virtual-classroom/', views.virtual_classroom_integration, name='student-virtual-classroom'),
    path('<int:student_id>/alumni/', views.student_alumni_management, name='student-alumni-management'),
    path('<int:student_id>/analytics/', views.comprehensive_student_analytics, name='student-comprehensive-analytics'),
    
    # Bulk operations (basic implementation)
    path('bulk-operations/', views.bulk_student_operations, name='bulk-student-operations'),
]
