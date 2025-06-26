from rest_framework import serializers
from .models import (
    Subject, ExamType, ExamSchedule, Exam, QuestionBank, OnlineExam,
    StudentExamAttempt, ExamResult, GradingScheme, HallTicket, ExamReport
)

class SubjectSerializer(serializers.ModelSerializer):
    """Serializer for Subject model"""
    applicable_class_names = serializers.SerializerMethodField()
    subject_head_name = serializers.CharField(source='subject_head.full_name', read_only=True)
    total_marks = serializers.ReadOnlyField()
    
    class Meta:
        model = Subject
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'total_marks']
    
    def get_applicable_class_names(self, obj):
        return list(obj.applicable_classes.values_list('name', flat=True))

class ExamTypeSerializer(serializers.ModelSerializer):
    """Serializer for Exam Type model"""
    total_schedules = serializers.SerializerMethodField()
    
    class Meta:
        model = ExamType
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_total_schedules(self, obj):
        return obj.schedules.count()

class ExamScheduleSerializer(serializers.ModelSerializer):
    """Serializer for Exam Schedule model"""
    exam_type_name = serializers.CharField(source='exam_type.name', read_only=True)
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    applicable_class_names = serializers.SerializerMethodField()
    total_exams = serializers.SerializerMethodField()
    
    class Meta:
        model = ExamSchedule
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_applicable_class_names(self, obj):
        return list(obj.applicable_classes.values_list('name', flat=True))
    
    def get_total_exams(self, obj):
        return obj.exams.count()

class ExamSerializer(serializers.ModelSerializer):
    """Serializer for Exam model"""
    schedule_name = serializers.CharField(source='schedule.schedule_name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    class_name = serializers.CharField(source='school_class.name', read_only=True)
    section_names = serializers.SerializerMethodField()
    invigilator_names = serializers.SerializerMethodField()
    verified_by_name = serializers.CharField(source='verified_by.get_full_name', read_only=True)
    total_results = serializers.SerializerMethodField()
    
    class Meta:
        model = Exam
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_section_names(self, obj):
        return list(obj.sections.values_list('name', flat=True))
    
    def get_invigilator_names(self, obj):
        return list(obj.invigilators.values_list('full_name', flat=True))
    
    def get_total_results(self, obj):
        return obj.results.count()

class QuestionBankSerializer(serializers.ModelSerializer):
    """Serializer for Question Bank model"""
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    class_name = serializers.CharField(source='school_class.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.get_full_name', read_only=True)
    
    class Meta:
        model = QuestionBank
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'times_used', 'average_score', 'is_approved', 'reviewed_by']
        extra_kwargs = {
            'correct_answer': {'write_only': True},
            'correct_option': {'write_only': True},
        }

class OnlineExamSerializer(serializers.ModelSerializer):
    """Serializer for Online Exam model"""
    exam_name = serializers.CharField(source='exam.exam_name', read_only=True)
    exam_date = serializers.DateField(source='exam.exam_date', read_only=True)
    exam_duration = serializers.IntegerField(source='exam.duration_minutes', read_only=True)
    total_attempts = serializers.SerializerMethodField()
    
    class Meta:
        model = OnlineExam
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_total_attempts(self, obj):
        return obj.attempts.count()

class StudentExamAttemptSerializer(serializers.ModelSerializer):
    """Serializer for Student Exam Attempt model"""
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    exam_name = serializers.CharField(source='online_exam.exam.exam_name', read_only=True)
    exam_date = serializers.DateField(source='online_exam.exam.exam_date', read_only=True)
    exam_total_marks = serializers.IntegerField(source='online_exam.exam.total_marks', read_only=True)
    
    class Meta:
        model = StudentExamAttempt
        fields = '__all__'
        read_only_fields = [
            'created_at', 'updated_at', 'actual_duration_minutes',
            'total_marks_obtained', 'percentage', 'browser_info', 'device_info', 'ip_address'
        ]

class ExamResultSerializer(serializers.ModelSerializer):
    """Serializer for Exam Result model"""
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_roll_number = serializers.CharField(source='student.roll_number', read_only=True)
    exam_name = serializers.CharField(source='exam.exam_name', read_only=True)
    subject_name = serializers.CharField(source='exam.subject.name', read_only=True)
    class_name = serializers.CharField(source='student.current_class.name', read_only=True)
    section_name = serializers.CharField(source='student.section.name', read_only=True)
    entered_by_name = serializers.CharField(source='entered_by.get_full_name', read_only=True)
    verified_by_name = serializers.CharField(source='verified_by.get_full_name', read_only=True)
    
    class Meta:
        model = ExamResult
        fields = '__all__'
        read_only_fields = [
            'created_at', 'updated_at', 'total_marks_obtained', 'percentage',
            'is_passed', 'grade_points', 'rank_in_class', 'rank_in_section'
        ]

class GradingSchemeSerializer(serializers.ModelSerializer):
    """Serializer for Grading Scheme model"""
    applicable_class_names = serializers.SerializerMethodField()
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    
    class Meta:
        model = GradingScheme
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_applicable_class_names(self, obj):
        return list(obj.applicable_classes.values_list('name', flat=True))

class HallTicketSerializer(serializers.ModelSerializer):
    """Serializer for Hall Ticket model"""
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_roll_number = serializers.CharField(source='student.roll_number', read_only=True)
    class_name = serializers.CharField(source='student.current_class.name', read_only=True)
    section_name = serializers.CharField(source='student.section.name', read_only=True)
    schedule_name = serializers.CharField(source='exam_schedule.schedule_name', read_only=True)
    
    class Meta:
        model = HallTicket
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'hall_ticket_number', 'digital_signature', 'verification_code']

class ExamReportSerializer(serializers.ModelSerializer):
    """Serializer for Exam Report model"""
    schedule_name = serializers.CharField(source='exam_schedule.schedule_name', read_only=True)
    generated_by_name = serializers.CharField(source='generated_by.get_full_name', read_only=True)
    class_filter_name = serializers.CharField(source='class_filter.name', read_only=True)
    subject_filter_name = serializers.CharField(source='subject_filter.name', read_only=True)
    section_filter_name = serializers.CharField(source='section_filter.name', read_only=True)
    
    class Meta:
        model = ExamReport
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at'] 