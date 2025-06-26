from django.contrib import admin
from .models import (
    AcademicSession,
    AdmissionCriteria,
    ApplicationForm,
    DocumentSubmission,
    EntranceTest,
    EntranceTestResult,
    Interview,
    InterviewSchedule,
    InterviewEvaluation,
    AdmissionResult,
    AdmissionReport
)

@admin.register(AcademicSession)
class AcademicSessionAdmin(admin.ModelAdmin):
    list_display = ['name', 'school', 'application_start_date', 'application_end_date', 'is_active']
    list_filter = ['school', 'is_active']
    search_fields = ['name']

@admin.register(AdmissionCriteria)
class AdmissionCriteriaAdmin(admin.ModelAdmin):
    list_display = ['school_class', 'academic_session', 'minimum_age', 'maximum_age', 'seats_available']
    list_filter = ['school_class', 'academic_session']

@admin.register(ApplicationForm)
class ApplicationFormAdmin(admin.ModelAdmin):
    list_display = ['application_number', 'first_name', 'last_name', 'school_class', 'status']
    list_filter = ['status', 'school_class', 'academic_session']
    search_fields = ['application_number', 'first_name', 'last_name', 'father_name']
    readonly_fields = ['application_number']

@admin.register(DocumentSubmission)
class DocumentSubmissionAdmin(admin.ModelAdmin):
    list_display = ['application', 'document_type', 'document_name', 'is_verified']
    list_filter = ['document_type', 'is_verified']
    search_fields = ['application__application_number', 'document_name']

@admin.register(EntranceTest)
class EntranceTestAdmin(admin.ModelAdmin):
    list_display = ['test_name', 'school_class', 'test_date', 'total_marks', 'is_active']
    list_filter = ['school_class', 'test_date', 'is_active']
    search_fields = ['test_name']

@admin.register(AdmissionResult)
class AdmissionResultAdmin(admin.ModelAdmin):
    list_display = ['application', 'final_status', 'total_score', 'rank', 'admission_offered']
    list_filter = ['final_status', 'admission_offered']
    search_fields = ['application__application_number'] 