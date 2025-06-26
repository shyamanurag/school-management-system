from django.contrib import admin
from .models import (
    AcademicSession,
    AdmissionCriteria,
    ApplicationForm,
    DocumentSubmission,
    EntranceTest,
    Interview,
    InterviewEvaluation,
    AdmissionResult
)

@admin.register(AcademicSession)
class AcademicSessionAdmin(admin.ModelAdmin):
    list_display = ['session_name', 'school', 'academic_year', 'application_start_date', 'application_end_date', 'is_active']
    list_filter = ['school', 'is_active', 'academic_year']
    search_fields = ['session_name', 'school__name']

@admin.register(AdmissionCriteria)
class AdmissionCriteriaAdmin(admin.ModelAdmin):
    list_display = ['session', 'school_class', 'minimum_age_years', 'maximum_age_years', 'total_seats']
    list_filter = ['school_class', 'session']
    search_fields = ['session__session_name', 'school_class__name']

@admin.register(ApplicationForm)
class ApplicationFormAdmin(admin.ModelAdmin):
    list_display = ['application_number', 'first_name', 'last_name', 'session', 'status']
    list_filter = ['status', 'session', 'criteria']
    search_fields = ['application_number', 'first_name', 'last_name', 'email']

@admin.register(DocumentSubmission)
class DocumentSubmissionAdmin(admin.ModelAdmin):
    list_display = ['application', 'document_type', 'created_at', 'verification_status']
    list_filter = ['document_type', 'verification_status']
    search_fields = ['application__application_number', 'document_name']

@admin.register(EntranceTest)
class EntranceTestAdmin(admin.ModelAdmin):
    list_display = ['test_name', 'session', 'school_class', 'test_date', 'duration_minutes']
    list_filter = ['test_date', 'session', 'school_class']
    search_fields = ['test_name']

@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ['interview_name', 'session', 'interview_date', 'start_time', 'end_time']
    list_filter = ['interview_date', 'session']
    search_fields = ['interview_name']

@admin.register(InterviewEvaluation)
class InterviewEvaluationAdmin(admin.ModelAdmin):
    list_display = ['interview_schedule', 'evaluated_by', 'total_score', 'recommendation']
    list_filter = ['recommendation', 'evaluated_by']

@admin.register(AdmissionResult)
class AdmissionResultAdmin(admin.ModelAdmin):
    list_display = ['application', 'result_status', 'merit_rank', 'total_score', 'declared_date']
    list_filter = ['result_status', 'declared_date']
    search_fields = ['application__application_number'] 