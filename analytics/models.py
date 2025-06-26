from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from core.models import TimeStampedModel, SchoolSettings, UUIDModel
import json

class Dashboard(TimeStampedModel):
    """Custom dashboards for different roles"""
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='dashboards')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dashboards', null=True, blank=True)
    role_based = models.CharField(max_length=50, blank=True, null=True)  # For role-based dashboards
    layout_config = models.JSONField(default=dict)  # Dashboard layout configuration
    widgets = models.JSONField(default=list)  # List of widget configurations
    is_default = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.school.name} - {self.name}"

class Report(TimeStampedModel):
    """Custom report definitions"""
    REPORT_TYPES = [
        ('STUDENT', 'Student Report'),
        ('ACADEMIC', 'Academic Report'),
        ('FINANCIAL', 'Financial Report'),
        ('ATTENDANCE', 'Attendance Report'),
        ('LIBRARY', 'Library Report'),
        ('TRANSPORT', 'Transport Report'),
        ('HOSTEL', 'Hostel Report'),
        ('INVENTORY', 'Inventory Report'),
        ('CUSTOM', 'Custom Report'),
    ]
    
    REPORT_FORMATS = [
        ('PDF', 'PDF'),
        ('EXCEL', 'Excel'),
        ('CSV', 'CSV'),
        ('HTML', 'HTML'),
    ]
    
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='reports')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    query_config = models.JSONField(default=dict)  # Database query configuration
    filters = models.JSONField(default=dict)  # Available filters
    columns = models.JSONField(default=list)  # Report columns
    format_config = models.JSONField(default=dict)  # Formatting options
    is_scheduled = models.BooleanField(default=False)
    schedule_config = models.JSONField(default=dict)  # Schedule configuration
    recipients = models.JSONField(default=list)  # Email recipients for scheduled reports
    
    def __str__(self):
        return f"{self.school.name} - {self.name}"

class ReportExecution(UUIDModel, TimeStampedModel):
    """Track report executions"""
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='executions')
    executed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    parameters = models.JSONField(default=dict)  # Parameters used for execution
    execution_time = models.FloatField()  # Execution time in seconds
    file_path = models.CharField(max_length=500, blank=True, null=True)
    file_size = models.BigIntegerField(default=0)
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'Pending'),
        ('RUNNING', 'Running'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ], default='PENDING')
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.report.name} - {self.created_at}"

class Metric(TimeStampedModel):
    """System metrics and KPIs"""
    METRIC_TYPES = [
        ('COUNT', 'Count'),
        ('SUM', 'Sum'),
        ('AVERAGE', 'Average'),
        ('PERCENTAGE', 'Percentage'),
        ('RATIO', 'Ratio'),
    ]
    
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='metrics')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPES)
    calculation_config = models.JSONField(default=dict)  # How to calculate the metric
    target_value = models.FloatField(blank=True, null=True)
    warning_threshold = models.FloatField(blank=True, null=True)
    critical_threshold = models.FloatField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.school.name} - {self.name}"

class MetricValue(TimeStampedModel):
    """Historical metric values"""
    metric = models.ForeignKey(Metric, on_delete=models.CASCADE, related_name='values')
    value = models.FloatField()
    date = models.DateField()
    additional_data = models.JSONField(default=dict, blank=True)
    
    class Meta:
        unique_together = ['metric', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.metric.name} - {self.date}: {self.value}"

class AnalyticsEvent(UUIDModel, TimeStampedModel):
    """Track user interactions and system events for analytics"""
    EVENT_CATEGORIES = [
        ('USER_ACTION', 'User Action'),
        ('SYSTEM_EVENT', 'System Event'),
        ('ACADEMIC_EVENT', 'Academic Event'),
        ('FINANCIAL_EVENT', 'Financial Event'),
        ('COMMUNICATION_EVENT', 'Communication Event'),
    ]
    
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='analytics_events')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=40, blank=True, null=True)
    event_name = models.CharField(max_length=100)
    event_category = models.CharField(max_length=20, choices=EVENT_CATEGORIES)
    properties = models.JSONField(default=dict)  # Event properties
    value = models.FloatField(blank=True, null=True)  # Numerical value if applicable
    page_url = models.URLField(blank=True, null=True)
    referrer = models.URLField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['school', 'event_name']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['event_category']),
        ]
    
    def __str__(self):
        return f"{self.event_name} - {self.created_at}"

class StudentAnalytics(UUIDModel, TimeStampedModel):
    """Student-specific analytics"""
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='student_analytics')
    student_id = models.IntegerField()  # Reference to student
    academic_year = models.CharField(max_length=20)
    
    # Academic Performance
    overall_grade = models.CharField(max_length=5, blank=True, null=True)
    overall_percentage = models.FloatField(blank=True, null=True)
    rank_in_class = models.IntegerField(blank=True, null=True)
    rank_in_grade = models.IntegerField(blank=True, null=True)
    
    # Attendance
    total_days = models.IntegerField(default=0)
    present_days = models.IntegerField(default=0)
    absent_days = models.IntegerField(default=0)
    late_days = models.IntegerField(default=0)
    attendance_percentage = models.FloatField(default=0)
    
    # Behavioral Analytics
    disciplinary_actions = models.IntegerField(default=0)
    awards_received = models.IntegerField(default=0)
    extracurricular_participation = models.IntegerField(default=0)
    
    # Engagement Metrics
    library_books_issued = models.IntegerField(default=0)
    online_learning_hours = models.FloatField(default=0)
    assignment_submission_rate = models.FloatField(default=0)
    
    # Financial
    fees_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fees_pending = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    class Meta:
        unique_together = ['school', 'student_id', 'academic_year']
    
    def __str__(self):
        return f"Student {self.student_id} Analytics - {self.academic_year}"

class TeacherAnalytics(UUIDModel, TimeStampedModel):
    """Teacher-specific analytics"""
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='teacher_analytics')
    teacher_id = models.IntegerField()  # Reference to teacher
    academic_year = models.CharField(max_length=20)
    
    # Teaching Load
    total_classes = models.IntegerField(default=0)
    total_students = models.IntegerField(default=0)
    subjects_taught = models.IntegerField(default=0)
    
    # Performance Metrics
    average_class_performance = models.FloatField(blank=True, null=True)
    student_pass_rate = models.FloatField(blank=True, null=True)
    student_satisfaction_score = models.FloatField(blank=True, null=True)
    
    # Engagement
    assignments_given = models.IntegerField(default=0)
    parent_meetings_conducted = models.IntegerField(default=0)
    professional_development_hours = models.FloatField(default=0)
    
    # Attendance
    classes_conducted = models.IntegerField(default=0)
    classes_missed = models.IntegerField(default=0)
    substitute_classes_taken = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['school', 'teacher_id', 'academic_year']
    
    def __str__(self):
        return f"Teacher {self.teacher_id} Analytics - {self.academic_year}"
