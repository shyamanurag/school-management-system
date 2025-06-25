from django.contrib import admin
from .models import *

@admin.register(ExaminationType)
class ExaminationTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'school', 'is_active']
    list_filter = ['school', 'is_active']
    search_fields = ['name', 'code']

@admin.register(Examination)
class ExaminationAdmin(admin.ModelAdmin):
    list_display = ['name', 'exam_type', 'session', 'start_date', 'end_date', 'status']
    list_filter = ['exam_type', 'session', 'status']
    search_fields = ['name', 'code']

@admin.register(QuestionBank)
class QuestionBankAdmin(admin.ModelAdmin):
    list_display = ['question_text_preview', 'subject', 'difficulty_level', 'question_type', 'created_by']
    list_filter = ['subject', 'difficulty_level', 'question_type', 'is_active']
    search_fields = ['question_text']
    
    def question_text_preview(self, obj):
        return obj.question_text[:50] + "..." if len(obj.question_text) > 50 else obj.question_text
    question_text_preview.short_description = 'Question'

@admin.register(ExamSchedule)
class ExamScheduleAdmin(admin.ModelAdmin):
    list_display = ['examination', 'subject', 'exam_date', 'start_time', 'duration_minutes', 'room']
    list_filter = ['examination', 'exam_date', 'subject']
    search_fields = ['examination__name', 'subject__name']

@admin.register(StudentExamRegistration)
class StudentExamRegistrationAdmin(admin.ModelAdmin):
    list_display = ['student', 'examination', 'registration_date', 'is_registered', 'hall_ticket_number']
    list_filter = ['examination', 'is_registered', 'registration_date']
    search_fields = ['student__admission_number', 'student__first_name', 'hall_ticket_number']

@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'examination', 'subject', 'marks_obtained', 'max_marks', 'percentage', 'grade']
    list_filter = ['examination', 'subject', 'grade']
    search_fields = ['student__admission_number', 'student__first_name']

@admin.register(OnlineExam)
class OnlineExamAdmin(admin.ModelAdmin):
    list_display = ['exam_name', 'subject', 'total_questions', 'duration_minutes', 'start_datetime', 'is_active']
    list_filter = ['subject', 'difficulty_level', 'is_active']
    search_fields = ['exam_name']

@admin.register(StudentExamAttempt)
class StudentExamAttemptAdmin(admin.ModelAdmin):
    list_display = ['student', 'online_exam', 'start_time', 'end_time', 'total_score', 'percentage', 'status']
    list_filter = ['online_exam', 'status', 'start_time']
    search_fields = ['student__admission_number', 'student__first_name'] 