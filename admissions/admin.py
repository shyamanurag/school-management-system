from django.contrib import admin
from .models import *

@admin.register(AdmissionInquiry)
class AdmissionInquiryAdmin(admin.ModelAdmin):
    list_display = ['inquiry_number', 'student_name', 'class_seeking_admission', 'status', 'created_at']
    list_filter = ['status', 'admission_session', 'inquiry_source']
    search_fields = ['inquiry_number', 'student_name', 'father_name', 'mother_name']
    readonly_fields = ['inquiry_number']

@admin.register(AdmissionApplication)
class AdmissionApplicationAdmin(admin.ModelAdmin):
    list_display = ['application_number', 'full_name', 'class_applying_for', 'status', 'submitted_date']
    list_filter = ['status', 'admission_session', 'priority_category']
    search_fields = ['application_number', 'first_name', 'last_name', 'father_name']
    readonly_fields = ['application_number']

@admin.register(AdmissionDocument)
class AdmissionDocumentAdmin(admin.ModelAdmin):
    list_display = ['application', 'document_type', 'document_name', 'is_verified', 'created_at']
    list_filter = ['document_type', 'is_verified', 'is_mandatory']
    search_fields = ['application__application_number', 'document_name']

@admin.register(EntranceTest)
class EntranceTestAdmin(admin.ModelAdmin):
    list_display = ['test_name', 'admission_session', 'school_class', 'test_date', 'results_declared']
    list_filter = ['admission_session', 'school_class', 'results_declared']
    search_fields = ['test_name']

@admin.register(MeritList)
class MeritListAdmin(admin.ModelAdmin):
    list_display = ['list_name', 'admission_session', 'school_class', 'category', 'is_published']
    list_filter = ['admission_session', 'school_class', 'category', 'list_type']
    search_fields = ['list_name'] 