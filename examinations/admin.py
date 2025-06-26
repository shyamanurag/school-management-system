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
    list_display = ['exam_name', 'exam_type', 'school_class', 'start_date', 'end_date', 'status']
    list_filter = ['exam_type', 'school_class', 'status']
    search_fields = ['exam_name', 'exam_code']

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
    list_display = ['exam', 'subject', 'exam_date', 'start_time', 'duration_minutes']
    list_filter = ['exam', 'exam_date', 'subject']
    search_fields = ['exam__exam_name', 'subject__name']

@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam_schedule', 'marks_obtained', 'max_marks', 'percentage', 'grade']
    list_filter = ['exam_schedule__exam', 'exam_schedule__subject', 'grade']
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