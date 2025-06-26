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
    
    # Dashboard configuration
    layout_config = models.JSONField(default=dict)
    widgets = models.JSONField(default=list)
    
    # User access
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_dashboards')
    is_public = models.BooleanField(default=False)
    allowed_users = models.ManyToManyField(User, blank=True, related_name='accessible_dashboards')
    
    def __str__(self):
        return f"{self.school.name} - {self.name}"

class Report(TimeStampedModel):
    """Analytics reports"""
    REPORT_TYPES = [
        ('STUDENT_PERFORMANCE', 'Student Performance'),
        ('ATTENDANCE', 'Attendance Report'),
        ('FINANCIAL', 'Financial Report'),
        ('TEACHER_PERFORMANCE', 'Teacher Performance'),
        ('CLASS_ANALYSIS', 'Class Analysis'),
        ('TREND_ANALYSIS', 'Trend Analysis'),
        ('CUSTOM', 'Custom Report'),
    ]
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('GENERATING', 'Generating'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='reports')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    
    # Report configuration
    parameters = models.JSONField(default=dict)
    filters = models.JSONField(default=dict)
    
    # Generated data
    report_data = models.JSONField(default=dict)
    generated_at = models.DateTimeField(blank=True, null=True)
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_reports')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    file_path = models.CharField(max_length=500, blank=True, null=True)
    
    def __str__(self):
        return f"{self.school.name} - {self.name}"

class Metric(TimeStampedModel):
    """System metrics tracking"""
    METRIC_TYPES = [
        ('COUNTER', 'Counter'),
        ('GAUGE', 'Gauge'),
        ('HISTOGRAM', 'Histogram'),
        ('SUMMARY', 'Summary'),
    ]
    
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='metrics')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPES)
    
    # Value tracking
    current_value = models.FloatField(default=0)
    target_value = models.FloatField(blank=True, null=True)
    unit = models.CharField(max_length=50, blank=True, null=True)
    
    # Historical data
    historical_data = models.JSONField(default=list)
    
    # Configuration
    is_active = models.BooleanField(default=True)
    update_frequency = models.CharField(max_length=20, default='DAILY')
    
    def __str__(self):
        return f"{self.school.name} - {self.name}: {self.current_value}"

class AnalyticsEvent(UUIDModel, TimeStampedModel):
    """Analytics events tracking"""
    EVENT_TYPES = [
        ('USER_LOGIN', 'User Login'),
        ('USER_LOGOUT', 'User Logout'),
        ('PAGE_VIEW', 'Page View'),
        ('FEATURE_USAGE', 'Feature Usage'),
        ('ERROR_OCCURRED', 'Error Occurred'),
        ('PERFORMANCE_METRIC', 'Performance Metric'),
    ]
    
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='analytics_events')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=40, blank=True, null=True)
    
    # Event details
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    event_name = models.CharField(max_length=200)
    event_data = models.JSONField(default=dict)
    
    # Context
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    referrer = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.event_name} - {self.created_at}"

class StudentAnalytics(UUIDModel, TimeStampedModel):
    """Student-specific analytics"""
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='student_analytics')
    student_id = models.IntegerField()  # Reference to student
    academic_year = models.CharField(max_length=20)
    
    # Performance metrics
    performance_data = models.JSONField(default=dict)
    attendance_rate = models.FloatField(default=0.0)
    grade_average = models.FloatField(default=0.0)
    
    # Behavioral analytics
    engagement_score = models.FloatField(default=0.0)
    participation_rate = models.FloatField(default=0.0)
    
    # Predictions
    risk_factors = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)
    
    def __str__(self):
        return f"Student {self.student_id} Analytics - {self.academic_year}"

class TeacherAnalytics(UUIDModel, TimeStampedModel):
    """Teacher-specific analytics"""
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='teacher_analytics')
    teacher_id = models.IntegerField()  # Reference to teacher
    academic_year = models.CharField(max_length=20)
    
    # Teaching metrics
    teaching_data = models.JSONField(default=dict)
    student_performance_avg = models.FloatField(default=0.0)
    class_attendance_avg = models.FloatField(default=0.0)
    
    # Workload analytics
    workload_score = models.FloatField(default=0.0)
    efficiency_rating = models.FloatField(default=0.0)
    
    # Professional development
    training_completed = models.JSONField(default=list)
    areas_for_improvement = models.JSONField(default=list)
    
    def __str__(self):
        return f"Teacher {self.teacher_id} Analytics - {self.academic_year}"
