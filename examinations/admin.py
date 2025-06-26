from django.contrib import admin
from .models import (
    Subject,
    ExamType,
    ExamSchedule,
    Exam,
    QuestionBank,
    OnlineExam,
    StudentExamAttempt,
    ExamResult,
    GradingScheme,
    HallTicket,
    ExamReport
)

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'school', 'subject_type', 'is_active']
    list_filter = ['school', 'subject_type', 'is_active']
    search_fields = ['name', 'code']

@admin.register(ExamType)
class ExamTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'school', 'weightage_percentage', 'is_active']
    list_filter = ['school', 'is_active']
    search_fields = ['name', 'code']

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['exam_name', 'subject', 'school_class', 'exam_date', 'is_completed', 'is_cancelled']
    list_filter = ['subject', 'school_class', 'is_completed', 'is_cancelled']
    search_fields = ['exam_name']

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
    list_display = ['schedule_name', 'exam_type', 'start_date', 'end_date', 'is_published']
    list_filter = ['exam_type', 'start_date', 'is_published']
    search_fields = ['schedule_name']

@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam', 'total_marks_obtained', 'percentage', 'grade', 'is_passed']
    list_filter = ['exam__schedule__exam_type', 'exam__subject', 'grade', 'is_passed']
    search_fields = ['student__admission_number', 'student__first_name']

@admin.register(OnlineExam)
class OnlineExamAdmin(admin.ModelAdmin):
    list_display = ['exam', 'total_questions', 'auto_submit', 'randomize_questions', 'full_screen_required']
    list_filter = ['auto_submit', 'randomize_questions', 'full_screen_required']
    search_fields = ['exam__exam_name']

@admin.register(StudentExamAttempt)
class StudentExamAttemptAdmin(admin.ModelAdmin):
    list_display = ['student', 'online_exam', 'start_time', 'end_time', 'total_marks_obtained', 'percentage', 'status']
    list_filter = ['online_exam', 'status', 'start_time']
    search_fields = ['student__admission_number', 'student__first_name']

@admin.register(GradingScheme)
class GradingSchemeAdmin(admin.ModelAdmin):
    list_display = ['name', 'school', 'academic_year', 'is_percentage_based', 'is_active']
    list_filter = ['school', 'academic_year', 'is_percentage_based', 'is_active']
    search_fields = ['name']

@admin.register(HallTicket)
class HallTicketAdmin(admin.ModelAdmin):
    list_display = ['hall_ticket_number', 'student', 'exam_schedule', 'exam_center', 'is_issued']
    list_filter = ['exam_schedule', 'is_issued', 'issued_date']
    search_fields = ['hall_ticket_number', 'student__first_name', 'student__admission_number']

@admin.register(ExamReport)
class ExamReportAdmin(admin.ModelAdmin):
    list_display = ['report_type', 'exam_schedule', 'generated_by', 'created_at']
    list_filter = ['report_type', 'exam_schedule', 'created_at']
    search_fields = ['report_type'] 