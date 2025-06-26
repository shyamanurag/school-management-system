from rest_framework import serializers
from .models import (
    AcademicSession, AdmissionCriteria, ApplicationForm, DocumentSubmission,
    EntranceTest, EntranceTestResult, Interview, InterviewSchedule,
    InterviewEvaluation, AdmissionResult, AdmissionReport
)

class AcademicSessionSerializer(serializers.ModelSerializer):
    """Serializer for Academic Session model"""
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    total_applications = serializers.SerializerMethodField()
    total_criteria = serializers.SerializerMethodField()
    
    class Meta:
        model = AcademicSession
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_total_applications(self, obj):
        return obj.applications.count()
    
    def get_total_criteria(self, obj):
        return obj.admission_criteria.count()

class AdmissionCriteriaSerializer(serializers.ModelSerializer):
    """Serializer for Admission Criteria model"""
    session_name = serializers.CharField(source='session.session_name', read_only=True)
    class_name = serializers.CharField(source='school_class.name', read_only=True)
    total_applications = serializers.SerializerMethodField()
    filled_seats = serializers.SerializerMethodField()
    
    class Meta:
        model = AdmissionCriteria
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_total_applications(self, obj):
        return obj.applications.count()
    
    def get_filled_seats(self, obj):
        return obj.applications.filter(status__in=['SELECTED', 'ADMISSION_CONFIRMED']).count()

class ApplicationFormSerializer(serializers.ModelSerializer):
    """Serializer for Application Form model"""
    session_name = serializers.CharField(source='session.session_name', read_only=True)
    criteria_class_name = serializers.CharField(source='criteria.school_class.name', read_only=True)
    preferred_section_name = serializers.CharField(source='preferred_section.name', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.get_full_name', read_only=True)
    age = serializers.ReadOnlyField()
    documents_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ApplicationForm
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'application_number', 'age']
        extra_kwargs = {
            'aadhar_number': {'write_only': True},
            'parent1_income': {'write_only': True},
            'parent2_income': {'write_only': True},
        }
    
    def get_documents_count(self, obj):
        return obj.documents.count()

class DocumentSubmissionSerializer(serializers.ModelSerializer):
    """Serializer for Document Submission model"""
    application_number = serializers.CharField(source='application.application_number', read_only=True)
    student_name = serializers.CharField(source='application.full_name', read_only=True)
    verified_by_name = serializers.CharField(source='verified_by.get_full_name', read_only=True)
    
    class Meta:
        model = DocumentSubmission
        fields = '__all__'
        read_only_fields = [
            'created_at', 'updated_at', 'file_size', 'verification_status',
            'verified_by', 'verified_at'
        ]

class EntranceTestSerializer(serializers.ModelSerializer):
    """Serializer for Entrance Test model"""
    session_name = serializers.CharField(source='session.session_name', read_only=True)
    class_name = serializers.CharField(source='school_class.name', read_only=True)
    total_candidates = serializers.SerializerMethodField()
    qualified_candidates = serializers.SerializerMethodField()
    
    class Meta:
        model = EntranceTest
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_total_candidates(self, obj):
        return obj.results.count()
    
    def get_qualified_candidates(self, obj):
        return obj.results.filter(is_qualified=True).count()

class EntranceTestResultSerializer(serializers.ModelSerializer):
    """Serializer for Entrance Test Result model"""
    application_number = serializers.CharField(source='application.application_number', read_only=True)
    student_name = serializers.CharField(source='application.full_name', read_only=True)
    test_name = serializers.CharField(source='entrance_test.test_name', read_only=True)
    total_marks = serializers.IntegerField(source='entrance_test.total_marks', read_only=True)
    
    class Meta:
        model = EntranceTestResult
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'percentage', 'is_qualified']

class InterviewSerializer(serializers.ModelSerializer):
    """Serializer for Interview model"""
    session_name = serializers.CharField(source='session.session_name', read_only=True)
    panel_member_names = serializers.SerializerMethodField()
    total_schedules = serializers.SerializerMethodField()
    
    class Meta:
        model = Interview
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_panel_member_names(self, obj):
        return list(obj.interview_panel.values_list('full_name', flat=True))
    
    def get_total_schedules(self, obj):
        return obj.schedules.count()

class InterviewScheduleSerializer(serializers.ModelSerializer):
    """Serializer for Interview Schedule model"""
    application_number = serializers.CharField(source='application.application_number', read_only=True)
    student_name = serializers.CharField(source='application.full_name', read_only=True)
    interview_name = serializers.CharField(source='interview.interview_name', read_only=True)
    interview_date = serializers.DateField(source='interview.interview_date', read_only=True)
    
    class Meta:
        model = InterviewSchedule
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class InterviewEvaluationSerializer(serializers.ModelSerializer):
    """Serializer for Interview Evaluation model"""
    application_number = serializers.CharField(source='interview_schedule.application.application_number', read_only=True)
    student_name = serializers.CharField(source='interview_schedule.application.full_name', read_only=True)
    evaluator_name = serializers.CharField(source='evaluated_by.full_name', read_only=True)
    total_score = serializers.ReadOnlyField()
    percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = InterviewEvaluation
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'total_score', 'percentage']

class AdmissionResultSerializer(serializers.ModelSerializer):
    """Serializer for Admission Result model"""
    application_number = serializers.CharField(source='application.application_number', read_only=True)
    student_name = serializers.CharField(source='application.full_name', read_only=True)
    class_name = serializers.CharField(source='application.criteria.school_class.name', read_only=True)
    allocated_class_name = serializers.CharField(source='allocated_class.name', read_only=True)
    allocated_section_name = serializers.CharField(source='allocated_section.name', read_only=True)
    declared_by_name = serializers.CharField(source='declared_by.get_full_name', read_only=True)
    
    class Meta:
        model = AdmissionResult
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class AdmissionReportSerializer(serializers.ModelSerializer):
    """Serializer for Admission Report model"""
    session_name = serializers.CharField(source='session.session_name', read_only=True)
    generated_by_name = serializers.CharField(source='generated_by.get_full_name', read_only=True)
    class_filter_name = serializers.CharField(source='class_filter.name', read_only=True)
    
    class Meta:
        model = AdmissionReport
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at'] 