from rest_framework import serializers
from .models import (
    Subject, ClassSubject, Exam, ExamSchedule, StudentExamResult,
    Grade, Assignment, StudentAssignment, Timetable, Attendance,
    StudentClassAttendance, Holiday
)

class SubjectSerializer(serializers.ModelSerializer):
    """Serializer for Subject model"""
    department_name = serializers.CharField(source='department.name', read_only=True)
    total_classes = serializers.SerializerMethodField()
    
    class Meta:
        model = Subject
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def get_total_classes(self, obj):
        return obj.assigned_classes.count()

class ClassSubjectSerializer(serializers.ModelSerializer):
    """Serializer for ClassSubject model"""
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    class_name = serializers.CharField(source='school_class.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    
    class Meta:
        model = ClassSubject
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

class ExamSerializer(serializers.ModelSerializer):
    """Serializer for Exam model"""
    total_schedules = serializers.SerializerMethodField()
    completion_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Exam
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def get_total_schedules(self, obj):
        return obj.schedules.count()
    
    def get_completion_percentage(self, obj):
        total = obj.schedules.count()
        completed = obj.schedules.filter(is_completed=True).count()
        return (completed / total * 100) if total > 0 else 0

class ExamScheduleSerializer(serializers.ModelSerializer):
    """Serializer for ExamSchedule model"""
    subject_name = serializers.CharField(source='class_subject.subject.name', read_only=True)
    class_name = serializers.CharField(source='class_subject.school_class.name', read_only=True)
    exam_name = serializers.CharField(source='exam.name', read_only=True)
    invigilator_name = serializers.CharField(source='invigilator.get_full_name', read_only=True)
    room_name = serializers.CharField(source='room.name', read_only=True)
    
    class Meta:
        model = ExamSchedule
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

class StudentExamResultSerializer(serializers.ModelSerializer):
    """Serializer for StudentExamResult model"""
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    subject_name = serializers.CharField(source='exam_schedule.class_subject.subject.name', read_only=True)
    exam_name = serializers.CharField(source='exam_schedule.exam.name', read_only=True)
    
    class Meta:
        model = StudentExamResult
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'uuid')

class GradeSerializer(serializers.ModelSerializer):
    """Serializer for Grade model"""
    
    class Meta:
        model = Grade
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

class AssignmentSerializer(serializers.ModelSerializer):
    """Serializer for Assignment model"""
    subject_name = serializers.CharField(source='class_subject.subject.name', read_only=True)
    class_name = serializers.CharField(source='class_subject.school_class.name', read_only=True)
    total_submissions = serializers.SerializerMethodField()
    graded_submissions = serializers.SerializerMethodField()
    
    class Meta:
        model = Assignment
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'uuid')
    
    def get_total_submissions(self, obj):
        return obj.submissions.filter(is_submitted=True).count()
    
    def get_graded_submissions(self, obj):
        return obj.submissions.filter(is_graded=True).count()

class StudentAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for StudentAssignment model"""
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)
    assignment_max_marks = serializers.IntegerField(source='assignment.max_marks', read_only=True)
    
    class Meta:
        model = StudentAssignment
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'uuid')

class TimetableSerializer(serializers.ModelSerializer):
    """Serializer for Timetable model"""
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    class_name = serializers.CharField(source='school_class.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    room_name = serializers.CharField(source='room.name', read_only=True)
    
    class Meta:
        model = Timetable
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

class AttendanceSerializer(serializers.ModelSerializer):
    """Serializer for Attendance model"""
    subject_name = serializers.CharField(source='timetable.subject.name', read_only=True)
    class_name = serializers.CharField(source='timetable.school_class.name', read_only=True)
    section_name = serializers.CharField(source='timetable.section.name', read_only=True)
    teacher_name = serializers.CharField(source='taken_by.get_full_name', read_only=True)
    total_students = serializers.SerializerMethodField()
    present_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Attendance
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def get_total_students(self, obj):
        return obj.student_attendances.count()
    
    def get_present_count(self, obj):
        return obj.student_attendances.filter(status='PRESENT').count()

class StudentClassAttendanceSerializer(serializers.ModelSerializer):
    """Serializer for StudentClassAttendance model"""
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    subject_name = serializers.CharField(source='attendance.timetable.subject.name', read_only=True)
    class_name = serializers.CharField(source='attendance.timetable.school_class.name', read_only=True)
    date = serializers.DateField(source='attendance.date', read_only=True)
    
    class Meta:
        model = StudentClassAttendance
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

class HolidaySerializer(serializers.ModelSerializer):
    """Serializer for Holiday model"""
    duration_days = serializers.SerializerMethodField()
    
    class Meta:
        model = Holiday
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def get_duration_days(self, obj):
        if obj.end_date:
            return (obj.end_date - obj.date).days + 1
        return 1 