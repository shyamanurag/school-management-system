from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

class TimeStampedModel(models.Model):
    """Abstract base model with timestamps"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class UUIDModel(models.Model):
    """Abstract base model with UUID primary key"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    class Meta:
        abstract = True

class SchoolSettings(TimeStampedModel):
    """Single School Configuration"""
    name = models.CharField(max_length=200, help_text="School Name")
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='India')
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to='school_logos/', blank=True, null=True)
    principal_name = models.CharField(max_length=200)
    principal_email = models.EmailField()
    principal_phone = models.CharField(max_length=20)
    established_date = models.DateField()
    board_affiliation = models.CharField(max_length=100, choices=[
        ('CBSE', 'Central Board of Secondary Education'),
        ('ICSE', 'Indian Certificate of Secondary Education'),
        ('STATE', 'State Board'),
        ('IB', 'International Baccalaureate'),
        ('IGCSE', 'International General Certificate of Secondary Education'),
    ])
    academic_year_start_month = models.IntegerField(default=4, validators=[MinValueValidator(1), MaxValueValidator(12)])
    
    class Meta:
        verbose_name = 'School Settings'
        verbose_name_plural = 'School Settings'
    
    def __str__(self):
        return self.name

class AcademicYear(TimeStampedModel):
    """Academic Year Management"""
    name = models.CharField(max_length=50, unique=True)  # e.g., "2023-24"
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return self.name

class Campus(TimeStampedModel):
    """Campus Management"""
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    principal_name = models.CharField(max_length=200)
    is_main_campus = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = 'Campuses'
    
    def __str__(self):
        return self.name

class Department(TimeStampedModel):
    """Academic Departments"""
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    head_of_department = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    budget_allocation = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class Building(TimeStampedModel):
    """Building/Block Management"""
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name='buildings')
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    floors = models.IntegerField(default=1)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['campus', 'code']
    
    def __str__(self):
        return f"{self.campus.name} - {self.name}"

class Room(TimeStampedModel):
    """Room/Classroom Management"""
    ROOM_TYPES = [
        ('CLASSROOM', 'Classroom'),
        ('LAB', 'Laboratory'),
        ('LIBRARY', 'Library'),
        ('OFFICE', 'Office'),
        ('AUDITORIUM', 'Auditorium'),
        ('CAFETERIA', 'Cafeteria'),
        ('SPORTS', 'Sports Room'),
        ('MEDICAL', 'Medical Room'),
        ('STORE', 'Store Room'),
        ('OTHER', 'Other'),
    ]
    
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=50)
    name = models.CharField(max_length=200, blank=True, null=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='CLASSROOM')
    floor = models.IntegerField(default=1)
    capacity = models.IntegerField(default=30)
    area_sqft = models.FloatField(blank=True, null=True)
    has_projector = models.BooleanField(default=False)
    has_smartboard = models.BooleanField(default=False)
    has_ac = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['building', 'room_number']
    
    def __str__(self):
        return f"{self.building.name} - {self.room_number}"

class Subject(TimeStampedModel):
    """Subject Management"""
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='subjects')
    description = models.TextField(blank=True, null=True)
    credit_hours = models.IntegerField(default=1)
    is_practical = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class Grade(TimeStampedModel):
    """Grade/Class Management"""
    name = models.CharField(max_length=50)  # e.g., "Grade 1", "Class X"
    numeric_value = models.IntegerField()  # 1, 2, 3... 12
    section = models.CharField(max_length=10)  # A, B, C
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='grades')
    class_teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='taught_classes')
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    max_students = models.IntegerField(default=40)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['name', 'section', 'academic_year']
        ordering = ['numeric_value', 'section']
    
    def __str__(self):
        return f"{self.name}-{self.section} ({self.academic_year})"

class Teacher(TimeStampedModel):
    """Teacher Profile"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=50, unique=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    date_of_birth = models.DateField()
    date_of_joining = models.DateField()
    qualification = models.CharField(max_length=200)
    experience_years = models.IntegerField(default=0)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    subjects = models.ManyToManyField(Subject, blank=True, related_name='teachers')
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    photo = models.ImageField(upload_to='teacher_photos/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"

class Student(TimeStampedModel):
    """Student Profile"""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    admission_number = models.CharField(max_length=50, unique=True)
    roll_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField()
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='students')
    admission_date = models.DateField()
    parent_name = models.CharField(max_length=200)
    parent_phone = models.CharField(max_length=20)
    parent_email = models.EmailField(blank=True, null=True)
    emergency_contact = models.CharField(max_length=20)
    photo = models.ImageField(upload_to='student_photos/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['roll_number', 'grade']
        ordering = ['grade', 'roll_number']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.admission_number})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class FeeCategory(TimeStampedModel):
    """Fee Categories"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = 'Fee Categories'
    
    def __str__(self):
        return self.name

class FeeStructure(TimeStampedModel):
    """Fee Structure for different grades"""
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='fee_structures')
    category = models.ForeignKey(FeeCategory, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    due_date = models.DateField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['grade', 'category', 'academic_year']
    
    def __str__(self):
        return f"{self.grade} - {self.category} - ₹{self.amount}"

class FeePayment(TimeStampedModel):
    """Fee Payment Records"""
    PAYMENT_STATUS = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('PARTIAL', 'Partially Paid'),
        ('OVERDUE', 'Overdue'),
    ]
    
    PAYMENT_METHOD = [
        ('CASH', 'Cash'),
        ('CARD', 'Card'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('CHEQUE', 'Cheque'),
        ('ONLINE', 'Online'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fee_payments')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_date = models.DateField(blank=True, null=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD, blank=True, null=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='PENDING')
    remarks = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.student} - {self.fee_structure.category} - {self.status}"

class Attendance(TimeStampedModel):
    """Student Attendance"""
    ATTENDANCE_STATUS = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LATE', 'Late'),
        ('EXCUSED', 'Excused'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=20, choices=ATTENDANCE_STATUS)
    remarks = models.TextField(blank=True, null=True)
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        unique_together = ['student', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.student} - {self.date} - {self.status}"

class Exam(TimeStampedModel):
    """Exam Management"""
    EXAM_TYPES = [
        ('UNIT_TEST', 'Unit Test'),
        ('MIDTERM', 'Mid Term'),
        ('FINAL', 'Final Exam'),
        ('ANNUAL', 'Annual Exam'),
        ('PRACTICAL', 'Practical Exam'),
    ]
    
    name = models.CharField(max_length=200)
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPES)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='exams')
    start_date = models.DateField()
    end_date = models.DateField()
    total_marks = models.IntegerField(default=100)
    passing_marks = models.IntegerField(default=35)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.academic_year})"

class ExamResult(TimeStampedModel):
    """Exam Results"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exam_results')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='results')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    total_marks = models.DecimalField(max_digits=5, decimal_places=2)
    grade = models.CharField(max_length=5, blank=True, null=True)  # A+, A, B+, etc.
    remarks = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ['student', 'exam', 'subject']
    
    def __str__(self):
        return f"{self.student} - {self.exam} - {self.subject}"
    
    @property
    def percentage(self):
        return (self.marks_obtained / self.total_marks) * 100 if self.total_marks > 0 else 0

class SystemConfiguration(TimeStampedModel):
    """System-wide configuration settings"""
    key = models.CharField(max_length=200, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True, null=True)
    data_type = models.CharField(max_length=20, choices=[
        ('STRING', 'String'),
        ('INTEGER', 'Integer'),
        ('FLOAT', 'Float'),
        ('BOOLEAN', 'Boolean'),
        ('JSON', 'JSON'),
        ('DATE', 'Date'),
        ('DATETIME', 'DateTime'),
    ], default='STRING')
    is_sensitive = models.BooleanField(default=False)
    
    def __str__(self):
        return self.key

class AuditLog(UUIDModel, TimeStampedModel):
    """Comprehensive audit logging"""
    ACTION_TYPES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('VIEW', 'View'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('EXPORT', 'Export'),
        ('IMPORT', 'Import'),
        ('BACKUP', 'Backup'),
        ('RESTORE', 'Restore'),
    ]
    
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='audit_logs')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True, null=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    model_name = models.CharField(max_length=100, blank=True, null=True)
    object_id = models.CharField(max_length=100, blank=True, null=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_pk = models.CharField(max_length=255, blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_pk')
    changes = models.JSONField(default=dict, blank=True)  # Store field changes
    description = models.TextField(blank=True, null=True)
    risk_level = models.CharField(max_length=20, choices=[
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ], default='LOW')
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['school', 'action_type']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['ip_address']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.action_type} - {self.created_at}"

class Attachment(UUIDModel, TimeStampedModel):
    """Generic file attachment model"""
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='attachments')
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='attachments/%Y/%m/%d/')
    file_size = models.BigIntegerField()
    file_type = models.CharField(max_length=100)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    description = models.TextField(blank=True, null=True)
    is_public = models.BooleanField(default=False)
    download_count = models.IntegerField(default=0)
    
    class Meta:
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]
    
    def __str__(self):
        return self.name

class NotificationTemplate(TimeStampedModel):
    """Template for notifications (SMS/Email)"""
    TEMPLATE_TYPES = [
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
        ('PUSH', 'Push Notification'),
        ('IN_APP', 'In-App Notification'),
    ]
    
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='notification_templates')
    name = models.CharField(max_length=200)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    subject = models.CharField(max_length=255, blank=True, null=True)  # For emails
    body = models.TextField()
    variables = models.JSONField(default=list, help_text="List of available variables")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['school', 'name', 'template_type']
    
    def __str__(self):
        return f"{self.school.name} - {self.name} ({self.template_type})"

class AdmissionSession(TimeStampedModel):
    """Admission session for different academic years"""
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='admission_sessions')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='admission_sessions')
    name = models.CharField(max_length=200)  # "2024-25 Admission"
    
    # Application dates
    application_start_date = models.DateField()
    application_end_date = models.DateField()
    
    # Admission process dates
    entrance_test_date = models.DateField(blank=True, null=True)
    interview_start_date = models.DateField(blank=True, null=True)
    interview_end_date = models.DateField(blank=True, null=True)
    merit_list_date = models.DateField(blank=True, null=True)
    admission_start_date = models.DateField(blank=True, null=True)
    admission_end_date = models.DateField(blank=True, null=True)
    
    # Configuration
    online_application_enabled = models.BooleanField(default=True)
    entrance_test_required = models.BooleanField(default=False)
    interview_required = models.BooleanField(default=False)
    
    # Application fee
    application_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['school', 'academic_year']
    
    def __str__(self):
        return f"{self.school.name} - {self.name}"

class AIAnalytics(TimeStampedModel):
    """AI-powered analytics and insights"""
    ANALYSIS_TYPES = [
        ('STUDENT_PERFORMANCE', 'Student Performance Analysis'),
        ('ATTENDANCE_PREDICTION', 'Attendance Prediction'),
        ('FEE_COLLECTION_FORECAST', 'Fee Collection Forecast'),
        ('TEACHER_WORKLOAD', 'Teacher Workload Analysis'),
        ('RESOURCE_OPTIMIZATION', 'Resource Optimization'),
        ('BEHAVIORAL_ANALYSIS', 'Student Behavioral Analysis'),
        ('ACADEMIC_RISK', 'Academic Risk Assessment'),
        ('PARENT_ENGAGEMENT', 'Parent Engagement Analysis'),
    ]
    
    analysis_type = models.CharField(max_length=30, choices=ANALYSIS_TYPES)
    target_student = models.ForeignKey('Student', on_delete=models.CASCADE, null=True, blank=True)
    target_grade = models.ForeignKey('Grade', on_delete=models.CASCADE, null=True, blank=True)
    analysis_data = models.JSONField(default=dict)
    insights = models.JSONField(default=dict)
    recommendations = models.JSONField(default=list)
    confidence_score = models.FloatField(default=0.0)  # 0-1 confidence
    is_automated = models.BooleanField(default=True)
    next_analysis_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "AI Analytics"
        verbose_name_plural = "AI Analytics"
    
    def __str__(self):
        return f"{self.analysis_type} - {self.confidence_score:.2f}"

class RealTimeChat(UUIDModel, TimeStampedModel):
    """Real-time chat system for school community"""
    CHAT_TYPES = [
        ('DIRECT', 'Direct Message'),
        ('GROUP', 'Group Chat'),
        ('CLASS_GROUP', 'Class Group'),
        ('TEACHER_PARENT', 'Teacher-Parent'),
        ('STUDENT_TEACHER', 'Student-Teacher'),
        ('PARENT_ADMIN', 'Parent-Admin'),
        ('EMERGENCY', 'Emergency Chat'),
    ]
    
    chat_type = models.CharField(max_length=20, choices=CHAT_TYPES)
    name = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    participants = models.ManyToManyField(User, related_name='chat_rooms')
    admin_users = models.ManyToManyField(User, related_name='admin_chat_rooms', blank=True)
    
    # Group settings
    is_group = models.BooleanField(default=False)
    max_participants = models.IntegerField(default=50)
    allow_file_sharing = models.BooleanField(default=True)
    allow_voice_messages = models.BooleanField(default=True)
    is_moderated = models.BooleanField(default=False)
    
    # Privacy settings
    is_private = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)
    
    # Activity tracking
    last_message_at = models.DateTimeField(null=True, blank=True)
    message_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-last_message_at']
    
    def __str__(self):
        return self.name or f"{self.chat_type} Chat"

class ChatMessage(UUIDModel, TimeStampedModel):
    """Individual chat messages"""
    MESSAGE_TYPES = [
        ('TEXT', 'Text'),
        ('IMAGE', 'Image'),
        ('FILE', 'File'),
        ('VOICE', 'Voice Message'),
        ('VIDEO', 'Video'),
        ('LOCATION', 'Location'),
        ('SYSTEM', 'System Message'),
    ]
    
    chat_room = models.ForeignKey(RealTimeChat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_chat_messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='TEXT')
    
    # Content
    content = models.TextField(blank=True, null=True)
    attachment = models.FileField(upload_to='chat_attachments/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='chat_thumbnails/', blank=True, null=True)
    
    # Message status
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    # Reply functionality
    reply_to = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    # Reactions
    reactions = models.JSONField(default=dict)  # {emoji: [user_ids]}
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}..."

class ParentPortal(TimeStampedModel):
    """Advanced parent portal with comprehensive features"""
    parent_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent_portal')
    
    # Portal preferences
    dashboard_layout = models.JSONField(default=dict)
    notification_preferences = models.JSONField(default=dict)
    privacy_settings = models.JSONField(default=dict)
    
    # Mobile app settings
    device_tokens = models.JSONField(default=list)  # For push notifications
    app_version = models.CharField(max_length=20, blank=True, null=True)
    last_app_login = models.DateTimeField(null=True, blank=True)
    
    # Communication preferences
    preferred_communication_method = models.CharField(max_length=20, choices=[
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
        ('PUSH', 'Push Notification'),
        ('WHATSAPP', 'WhatsApp'),
        ('IN_APP', 'In-App Only'),
    ], default='EMAIL')
    
    # Emergency contacts
    emergency_contacts = models.JSONField(default=list)
    
    # Portal activity
    login_count = models.IntegerField(default=0)
    last_activity = models.DateTimeField(null=True, blank=True)
    feature_usage_stats = models.JSONField(default=dict)
    
    class Meta:
        verbose_name = "Parent Portal"
        verbose_name_plural = "Parent Portals"
    
    def __str__(self):
        return f"Portal - {self.parent_user.get_full_name()}"

class MobileAppSession(UUIDModel, TimeStampedModel):
    """Mobile app session tracking"""
    APP_TYPES = [
        ('PARENT', 'Parent App'),
        ('STUDENT', 'Student App'),
        ('TEACHER', 'Teacher App'),
        ('ADMIN', 'Admin App'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mobile_sessions')
    app_type = models.CharField(max_length=10, choices=APP_TYPES)
    device_info = models.JSONField(default=dict)
    app_version = models.CharField(max_length=20)
    os_version = models.CharField(max_length=50)
    device_token = models.CharField(max_length=255, unique=True)
    
    # Session data
    session_start = models.DateTimeField(auto_now_add=True)
    session_end = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Location (if permitted)
    last_latitude = models.FloatField(null=True, blank=True)
    last_longitude = models.FloatField(null=True, blank=True)
    location_updated_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Mobile App Session"
        verbose_name_plural = "Mobile App Sessions"
    
    def __str__(self):
        return f"{self.user.username} - {self.app_type} ({self.app_version})"

class AdvancedReport(UUIDModel, TimeStampedModel):
    """Advanced reporting system with AI insights"""
    REPORT_CATEGORIES = [
        ('ACADEMIC', 'Academic Performance'),
        ('FINANCIAL', 'Financial Analysis'),
        ('ATTENDANCE', 'Attendance Analytics'),
        ('BEHAVIORAL', 'Behavioral Analysis'),
        ('OPERATIONAL', 'Operational Efficiency'),
        ('PREDICTIVE', 'Predictive Analytics'),
        ('COMPARATIVE', 'Comparative Analysis'),
        ('CUSTOM', 'Custom Report'),
    ]
    
    REPORT_FORMATS = [
        ('PDF', 'PDF Document'),
        ('EXCEL', 'Excel Spreadsheet'),
        ('CSV', 'CSV File'),
        ('JSON', 'JSON Data'),
        ('DASHBOARD', 'Interactive Dashboard'),
        ('PRESENTATION', 'PowerPoint Presentation'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=20, choices=REPORT_CATEGORIES)
    
    # Report configuration
    filters = models.JSONField(default=dict)
    parameters = models.JSONField(default=dict)
    data_sources = models.JSONField(default=list)
    
    # Output settings
    format = models.CharField(max_length=20, choices=REPORT_FORMATS, default='PDF')
    template = models.CharField(max_length=100, blank=True, null=True)
    
    # Scheduling
    is_scheduled = models.BooleanField(default=False)
    schedule_expression = models.CharField(max_length=100, blank=True, null=True)  # Cron expression
    next_run = models.DateTimeField(null=True, blank=True)
    
    # Recipients
    recipients = models.ManyToManyField(User, blank=True, related_name='subscribed_reports')
    recipient_groups = models.JSONField(default=list)
    
    # AI Enhancement
    use_ai_insights = models.BooleanField(default=False)
    ai_analysis_level = models.CharField(max_length=20, choices=[
        ('BASIC', 'Basic Analysis'),
        ('ADVANCED', 'Advanced Analysis'),
        ('PREDICTIVE', 'Predictive Analysis'),
        ('PRESCRIPTIVE', 'Prescriptive Analysis'),
    ], default='BASIC')
    
    # Execution tracking
    last_generated = models.DateTimeField(null=True, blank=True)
    generation_count = models.IntegerField(default=0)
    average_generation_time = models.FloatField(default=0.0)  # seconds
    
    class Meta:
        verbose_name = "Advanced Report"
        verbose_name_plural = "Advanced Reports"
    
    def __str__(self):
        return f"{self.name} ({self.category})"

class SmartNotification(UUIDModel, TimeStampedModel):
    """AI-powered smart notifications"""
    NOTIFICATION_TRIGGERS = [
        ('ACADEMIC_ALERT', 'Academic Performance Alert'),
        ('ATTENDANCE_WARNING', 'Attendance Warning'),
        ('FEE_REMINDER', 'Fee Payment Reminder'),
        ('EXAM_PREPARATION', 'Exam Preparation Reminder'),
        ('BEHAVIORAL_CONCERN', 'Behavioral Concern'),
        ('ACHIEVEMENT_RECOGNITION', 'Achievement Recognition'),
        ('PARENT_MEETING', 'Parent Meeting Request'),
        ('CUSTOM_TRIGGER', 'Custom Trigger'),
    ]
    
    DELIVERY_CHANNELS = [
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
        ('PUSH', 'Push Notification'),
        ('IN_APP', 'In-App Notification'),
        ('WHATSAPP', 'WhatsApp'),
        ('VOICE_CALL', 'Voice Call'),
        ('CHATBOT', 'Chatbot Message'),
    ]
    
    trigger_type = models.CharField(max_length=30, choices=NOTIFICATION_TRIGGERS)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='smart_notifications')
    
    # AI-generated content
    title = models.CharField(max_length=200)
    message = models.TextField()
    action_items = models.JSONField(default=list)
    priority_score = models.FloatField(default=0.5)  # 0-1 AI-calculated priority
    
    # Delivery settings
    preferred_channels = models.JSONField(default=list)
    delivery_time_preference = models.CharField(max_length=20, choices=[
        ('IMMEDIATE', 'Immediate'),
        ('MORNING', 'Morning (8-10 AM)'),
        ('AFTERNOON', 'Afternoon (1-3 PM)'),
        ('EVENING', 'Evening (6-8 PM)'),
        ('WEEKEND', 'Weekend Only'),
    ], default='IMMEDIATE')
    
    # Personalization
    personalization_data = models.JSONField(default=dict)
    language_preference = models.CharField(max_length=10, default='en')
    
    # Tracking
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    is_acted_upon = models.BooleanField(default=False)
    action_taken_at = models.DateTimeField(null=True, blank=True)
    
    # AI learning
    effectiveness_score = models.FloatField(null=True, blank=True)  # User feedback
    
    class Meta:
        verbose_name = "Smart Notification"
        verbose_name_plural = "Smart Notifications"
        ordering = ['-priority_score', '-created_at']
    
    def __str__(self):
        return f"{self.trigger_type} - {self.recipient.username}"

class BiometricAttendance(TimeStampedModel):
    """Biometric attendance system integration"""
    BIOMETRIC_TYPES = [
        ('FINGERPRINT', 'Fingerprint'),
        ('FACE_RECOGNITION', 'Face Recognition'),
        ('IRIS_SCAN', 'Iris Scan'),
        ('PALM_PRINT', 'Palm Print'),
        ('VOICE_RECOGNITION', 'Voice Recognition'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='biometric_data')
    biometric_type = models.CharField(max_length=20, choices=BIOMETRIC_TYPES)
    
    # Biometric data (encrypted)
    biometric_template = models.BinaryField()
    template_quality = models.FloatField(default=0.0)  # Quality score
    
    # Device information
    enrollment_device = models.CharField(max_length=100)
    enrollment_location = models.CharField(max_length=100, blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_primary = models.BooleanField(default=False)
    last_used = models.DateTimeField(null=True, blank=True)
    usage_count = models.IntegerField(default=0)
    
    # Security
    enrollment_verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_biometrics')
    
    class Meta:
        unique_together = ['user', 'biometric_type', 'is_primary']
        verbose_name = "Biometric Attendance"
        verbose_name_plural = "Biometric Attendance Records"
    
    def __str__(self):
        return f"{self.user.username} - {self.biometric_type}"

class VirtualClassroom(UUIDModel, TimeStampedModel):
    """Virtual classroom management"""
    PLATFORM_TYPES = [
        ('ZOOM', 'Zoom'),
        ('GOOGLE_MEET', 'Google Meet'),
        ('MICROSOFT_TEAMS', 'Microsoft Teams'),
        ('WEBEX', 'Cisco Webex'),
        ('CUSTOM', 'Custom Platform'),
    ]
    
    CLASS_TYPES = [
        ('LIVE_LECTURE', 'Live Lecture'),
        ('TUTORIAL', 'Tutorial Session'),
        ('EXAM', 'Online Exam'),
        ('PARENT_MEETING', 'Parent-Teacher Meeting'),
        ('STAFF_MEETING', 'Staff Meeting'),
        ('WEBINAR', 'Webinar'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    class_type = models.CharField(max_length=20, choices=CLASS_TYPES)
    
    # Platform details
    platform = models.CharField(max_length=20, choices=PLATFORM_TYPES)
    meeting_id = models.CharField(max_length=100)
    meeting_password = models.CharField(max_length=50, blank=True, null=True)
    meeting_url = models.URLField()
    
    # Scheduling
    scheduled_start = models.DateTimeField()
    scheduled_end = models.DateTimeField()
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    
    # Participants
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_virtual_classes')
    participants = models.ManyToManyField(User, through='VirtualClassroomParticipant', related_name='virtual_classes')
    max_participants = models.IntegerField(default=100)
    
    # Settings
    is_recorded = models.BooleanField(default=False)
    recording_url = models.URLField(blank=True, null=True)
    allow_chat = models.BooleanField(default=True)
    allow_screen_sharing = models.BooleanField(default=True)
    require_approval = models.BooleanField(default=False)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern = models.JSONField(default=dict, blank=True, null=True)
    
    class Meta:
        verbose_name = "Virtual Classroom"
        verbose_name_plural = "Virtual Classrooms"
        ordering = ['scheduled_start']
    
    def __str__(self):
        return f"{self.title} - {self.scheduled_start.strftime('%Y-%m-%d %H:%M')}"

class VirtualClassroomParticipant(TimeStampedModel):
    """Virtual classroom participant tracking"""
    PARTICIPANT_ROLES = [
        ('HOST', 'Host'),
        ('CO_HOST', 'Co-Host'),
        ('PRESENTER', 'Presenter'),
        ('PARTICIPANT', 'Participant'),
        ('OBSERVER', 'Observer'),
    ]
    
    virtual_classroom = models.ForeignKey(VirtualClassroom, on_delete=models.CASCADE, related_name='participant_records')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='virtual_class_participations')
    role = models.CharField(max_length=15, choices=PARTICIPANT_ROLES, default='PARTICIPANT')
    
    # Attendance tracking
    joined_at = models.DateTimeField(null=True, blank=True)
    left_at = models.DateTimeField(null=True, blank=True)
    total_duration = models.DurationField(null=True, blank=True)
    
    # Participation metrics
    chat_messages_count = models.IntegerField(default=0)
    questions_asked = models.IntegerField(default=0)
    screen_share_duration = models.DurationField(null=True, blank=True)
    
    # Status
    attendance_status = models.CharField(max_length=20, choices=[
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LATE', 'Late'),
        ('LEFT_EARLY', 'Left Early'),
        ('TECHNICAL_ISSUES', 'Technical Issues'),
    ], default='ABSENT')
    
    # Feedback
    session_rating = models.IntegerField(null=True, blank=True, choices=[(i, i) for i in range(1, 6)])
    feedback = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ['virtual_classroom', 'user']
        verbose_name = "Virtual Classroom Participant"
        verbose_name_plural = "Virtual Classroom Participants"
    
    def __str__(self):
        return f"{self.user.username} - {self.virtual_classroom.title}"

# ==================== HR MANAGEMENT MODELS ====================

class Employee(TimeStampedModel):
    """Comprehensive Employee Profile"""
    EMPLOYMENT_TYPES = [
        ('FULL_TIME', 'Full Time'),
        ('PART_TIME', 'Part Time'),
        ('CONTRACT', 'Contract'),
        ('TEMPORARY', 'Temporary'),
        ('INTERN', 'Intern'),
        ('CONSULTANT', 'Consultant'),
    ]
    
    EMPLOYMENT_STATUS = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('TERMINATED', 'Terminated'),
        ('RESIGNED', 'Resigned'),
        ('RETIRED', 'Retired'),
        ('ON_LEAVE', 'On Leave'),
        ('SUSPENDED', 'Suspended'),
    ]
    
    MARITAL_STATUS = [
        ('SINGLE', 'Single'),
        ('MARRIED', 'Married'),
        ('DIVORCED', 'Divorced'),
        ('WIDOWED', 'Widowed'),
    ]
    
    # Basic Information
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    employee_id = models.CharField(max_length=50, unique=True)
    
    # Personal Details
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS, default='SINGLE')
    nationality = models.CharField(max_length=100, default='Indian')
    blood_group = models.CharField(max_length=5, blank=True, null=True)
    photo = models.ImageField(upload_to='employee_photos/', blank=True, null=True)
    
    # Contact Information
    personal_email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20)
    alternate_phone = models.CharField(max_length=20, blank=True, null=True)
    current_address = models.TextField()
    permanent_address = models.TextField(blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=200)
    emergency_contact_phone = models.CharField(max_length=20)
    emergency_contact_relation = models.CharField(max_length=50)
    
    # Employment Details
    employment_type = models.CharField(max_length=15, choices=EMPLOYMENT_TYPES, default='FULL_TIME')
    employment_status = models.CharField(max_length=15, choices=EMPLOYMENT_STATUS, default='ACTIVE')
    date_of_joining = models.DateField()
    date_of_leaving = models.DateField(blank=True, null=True)
    probation_period_months = models.IntegerField(default=6)
    probation_end_date = models.DateField(blank=True, null=True)
    confirmation_date = models.DateField(blank=True, null=True)
    
    # Organizational Details
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    designation = models.CharField(max_length=200)
    reporting_manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates')
    work_location = models.ForeignKey(Campus, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Professional Details
    qualification = models.TextField()
    experience_before_joining = models.IntegerField(default=0, help_text="Years of experience before joining")
    skills = models.JSONField(default=list)
    certifications = models.JSONField(default=list)
    
    # Compensation
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gross_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ctc = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # Cost to Company
    
    # Bank Details
    bank_name = models.CharField(max_length=200, blank=True, null=True)
    bank_account_number = models.CharField(max_length=50, blank=True, null=True)
    bank_ifsc_code = models.CharField(max_length=20, blank=True, null=True)
    bank_branch = models.CharField(max_length=200, blank=True, null=True)
    
    # Government IDs
    pan_number = models.CharField(max_length=20, blank=True, null=True)
    aadhar_number = models.CharField(max_length=20, blank=True, null=True)
    passport_number = models.CharField(max_length=20, blank=True, null=True)
    driving_license = models.CharField(max_length=20, blank=True, null=True)
    
    # HR Tracking
    last_promotion_date = models.DateField(blank=True, null=True)
    last_increment_date = models.DateField(blank=True, null=True)
    performance_rating = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    
    class Meta:
        ordering = ['employee_id']
        verbose_name = "Employee"
        verbose_name_plural = "Employees"
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"
    
    @property
    def full_name(self):
        return self.user.get_full_name()
    
    @property
    def years_of_service(self):
        from datetime import date
        if self.date_of_leaving:
            end_date = self.date_of_leaving
        else:
            end_date = date.today()
        return (end_date - self.date_of_joining).days // 365

class PayrollStructure(TimeStampedModel):
    """Payroll structure and salary components"""
    COMPONENT_TYPES = [
        ('EARNING', 'Earning'),
        ('DEDUCTION', 'Deduction'),
        ('BENEFIT', 'Benefit'),
        ('ALLOWANCE', 'Allowance'),
        ('TAX', 'Tax'),
    ]
    
    CALCULATION_TYPES = [
        ('FIXED', 'Fixed Amount'),
        ('PERCENTAGE_BASIC', 'Percentage of Basic'),
        ('PERCENTAGE_GROSS', 'Percentage of Gross'),
        ('FORMULA', 'Custom Formula'),
    ]
    
    name = models.CharField(max_length=200)
    component_type = models.CharField(max_length=15, choices=COMPONENT_TYPES)
    calculation_type = models.CharField(max_length=20, choices=CALCULATION_TYPES, default='FIXED')
    
    # Calculation details
    fixed_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    percentage = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    formula = models.TextField(blank=True, null=True, help_text="Python expression for calculation")
    
    # Applicability
    is_taxable = models.BooleanField(default=True)
    is_mandatory = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Limits
    minimum_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    maximum_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    class Meta:
        ordering = ['component_type', 'name']
        verbose_name = "Payroll Structure"
        verbose_name_plural = "Payroll Structures"
    
    def __str__(self):
        return f"{self.name} ({self.component_type})"

class EmployeePayroll(TimeStampedModel):
    """Monthly payroll for employees"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payrolls')
    pay_period_start = models.DateField()
    pay_period_end = models.DateField()
    
    # Salary components
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    allowances = models.JSONField(default=dict)  # {"hra": 5000, "da": 2000}
    deductions = models.JSONField(default=dict)  # {"pf": 1800, "tax": 3000}
    benefits = models.JSONField(default=dict)    # {"medical": 1500, "transport": 1000}
    
    # Calculated amounts
    gross_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Attendance impact
    working_days = models.IntegerField(default=30)
    present_days = models.IntegerField(default=30)
    absent_days = models.IntegerField(default=0)
    leave_days = models.IntegerField(default=0)
    overtime_hours = models.FloatField(default=0.0)
    overtime_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Payment details
    payment_date = models.DateField(blank=True, null=True)
    payment_method = models.CharField(max_length=20, choices=[
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('CASH', 'Cash'),
        ('CHEQUE', 'Cheque'),
    ], default='BANK_TRANSFER')
    payment_reference = models.CharField(max_length=100, blank=True, null=True)
    
    # Status
    is_processed = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    remarks = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ['employee', 'pay_period_start', 'pay_period_end']
        ordering = ['-pay_period_start']
        verbose_name = "Employee Payroll"
        verbose_name_plural = "Employee Payrolls"
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.pay_period_start.strftime('%B %Y')}"

class LeaveType(TimeStampedModel):
    """Types of leaves available"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    
    # Leave configuration
    max_days_per_year = models.IntegerField(default=0)
    max_consecutive_days = models.IntegerField(default=0)
    carry_forward_allowed = models.BooleanField(default=False)
    carry_forward_max_days = models.IntegerField(default=0)
    
    # Eligibility
    min_service_months = models.IntegerField(default=0)
    applicable_to_probation = models.BooleanField(default=False)
    
    # Processing
    requires_approval = models.BooleanField(default=True)
    advance_notice_days = models.IntegerField(default=1)
    
    # Compensation
    is_paid = models.BooleanField(default=True)
    salary_deduction_percentage = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Leave Type"
        verbose_name_plural = "Leave Types"
    
    def __str__(self):
        return self.name

class LeaveApplication(TimeStampedModel):
    """Employee leave applications"""
    LEAVE_STATUS = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled'),
        ('WITHDRAWN', 'Withdrawn'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_applications')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    
    # Leave period
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.IntegerField()
    
    # Application details
    reason = models.TextField()
    contact_during_leave = models.CharField(max_length=20, blank=True, null=True)
    emergency_contact = models.CharField(max_length=200, blank=True, null=True)
    
    # Approval workflow
    status = models.CharField(max_length=15, choices=LEAVE_STATUS, default='PENDING')
    applied_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applied_leaves')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves')
    approval_date = models.DateTimeField(blank=True, null=True)
    approval_remarks = models.TextField(blank=True, null=True)
    
    # HR processing
    hr_processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_leaves')
    hr_processing_date = models.DateTimeField(blank=True, null=True)
    
    # Leave balance impact
    leave_balance_before = models.IntegerField(default=0)
    leave_balance_after = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = "Leave Application"
        verbose_name_plural = "Leave Applications"
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.leave_type.name} ({self.start_date} to {self.end_date})"

class PerformanceReview(TimeStampedModel):
    """Employee performance reviews"""
    REVIEW_TYPES = [
        ('ANNUAL', 'Annual Review'),
        ('HALF_YEARLY', 'Half Yearly'),
        ('QUARTERLY', 'Quarterly'),
        ('MONTHLY', 'Monthly'),
        ('PROBATION', 'Probation Review'),
        ('PROJECT', 'Project Review'),
    ]
    
    REVIEW_STATUS = [
        ('DRAFT', 'Draft'),
        ('SELF_ASSESSMENT', 'Self Assessment'),
        ('MANAGER_REVIEW', 'Manager Review'),
        ('HR_REVIEW', 'HR Review'),
        ('COMPLETED', 'Completed'),
        ('ACKNOWLEDGED', 'Acknowledged'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='performance_reviews')
    review_type = models.CharField(max_length=15, choices=REVIEW_TYPES)
    review_period_start = models.DateField()
    review_period_end = models.DateField()
    
    # Review participants
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conducted_reviews')
    hr_reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='hr_reviews')
    
    # Performance metrics
    goals_achievement = models.JSONField(default=dict)  # {"goal_1": {"target": 100, "achieved": 95}}
    competency_ratings = models.JSONField(default=dict)  # {"communication": 4, "leadership": 3}
    kpi_scores = models.JSONField(default=dict)  # {"attendance": 95, "quality": 88}
    
    # Overall ratings
    overall_rating = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    manager_rating = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    self_rating = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    
    # Feedback
    strengths = models.TextField(blank=True, null=True)
    areas_for_improvement = models.TextField(blank=True, null=True)
    manager_comments = models.TextField(blank=True, null=True)
    employee_comments = models.TextField(blank=True, null=True)
    hr_comments = models.TextField(blank=True, null=True)
    
    # Development plan
    development_goals = models.JSONField(default=list)
    training_recommendations = models.JSONField(default=list)
    career_aspirations = models.TextField(blank=True, null=True)
    
    # Status and workflow
    status = models.CharField(max_length=20, choices=REVIEW_STATUS, default='DRAFT')
    self_assessment_completed = models.BooleanField(default=False)
    manager_review_completed = models.BooleanField(default=False)
    hr_review_completed = models.BooleanField(default=False)
    employee_acknowledged = models.BooleanField(default=False)
    
    # Dates
    due_date = models.DateField()
    completed_date = models.DateField(blank=True, null=True)
    
    class Meta:
        unique_together = ['employee', 'review_type', 'review_period_start']
        ordering = ['-review_period_start']
        verbose_name = "Performance Review"
        verbose_name_plural = "Performance Reviews"
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.review_type} ({self.review_period_start})"

class TrainingProgram(TimeStampedModel):
    """Training and development programs"""
    TRAINING_TYPES = [
        ('TECHNICAL', 'Technical Training'),
        ('SOFT_SKILLS', 'Soft Skills'),
        ('LEADERSHIP', 'Leadership Development'),
        ('COMPLIANCE', 'Compliance Training'),
        ('ORIENTATION', 'New Employee Orientation'),
        ('SAFETY', 'Safety Training'),
        ('PRODUCT', 'Product Training'),
    ]
    
    DELIVERY_MODES = [
        ('CLASSROOM', 'Classroom'),
        ('ONLINE', 'Online'),
        ('WEBINAR', 'Webinar'),
        ('WORKSHOP', 'Workshop'),
        ('ON_JOB', 'On-the-Job'),
        ('EXTERNAL', 'External Training'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    training_type = models.CharField(max_length=15, choices=TRAINING_TYPES)
    delivery_mode = models.CharField(max_length=15, choices=DELIVERY_MODES)
    
    # Training details
    duration_hours = models.IntegerField()
    trainer_name = models.CharField(max_length=200)
    trainer_organization = models.CharField(max_length=200, blank=True, null=True)
    
    # Scheduling
    start_date = models.DateField()
    end_date = models.DateField()
    registration_deadline = models.DateField()
    
    # Logistics
    venue = models.CharField(max_length=200, blank=True, null=True)
    max_participants = models.IntegerField(default=30)
    cost_per_participant = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Requirements
    prerequisites = models.TextField(blank=True, null=True)
    target_audience = models.TextField(blank=True, null=True)
    learning_objectives = models.JSONField(default=list)
    
    # Materials
    training_materials = models.JSONField(default=list)
    certification_provided = models.BooleanField(default=False)
    certificate_validity_months = models.IntegerField(blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_mandatory = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['start_date']
        verbose_name = "Training Program"
        verbose_name_plural = "Training Programs"
    
    def __str__(self):
        return self.name

class TrainingEnrollment(TimeStampedModel):
    """Employee training enrollments"""
    ENROLLMENT_STATUS = [
        ('REGISTERED', 'Registered'),
        ('CONFIRMED', 'Confirmed'),
        ('ATTENDED', 'Attended'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
        ('NO_SHOW', 'No Show'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='training_enrollments')
    training_program = models.ForeignKey(TrainingProgram, on_delete=models.CASCADE, related_name='enrollments')
    
    # Enrollment details
    enrollment_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=15, choices=ENROLLMENT_STATUS, default='REGISTERED')
    
    # Attendance
    attendance_percentage = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Assessment
    pre_assessment_score = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    post_assessment_score = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    final_score = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Feedback
    training_feedback = models.TextField(blank=True, null=True)
    trainer_rating = models.IntegerField(blank=True, null=True, choices=[(i, i) for i in range(1, 6)])
    content_rating = models.IntegerField(blank=True, null=True, choices=[(i, i) for i in range(1, 6)])
    overall_rating = models.IntegerField(blank=True, null=True, choices=[(i, i) for i in range(1, 6)])
    
    # Certification
    certificate_issued = models.BooleanField(default=False)
    certificate_number = models.CharField(max_length=100, blank=True, null=True)
    certificate_issue_date = models.DateField(blank=True, null=True)
    certificate_expiry_date = models.DateField(blank=True, null=True)
    
    # Approval workflow
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_trainings')
    approval_date = models.DateField(blank=True, null=True)
    
    class Meta:
        unique_together = ['employee', 'training_program']
        ordering = ['-enrollment_date']
        verbose_name = "Training Enrollment"
        verbose_name_plural = "Training Enrollments"
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.training_program.name}"

class HRAnalytics(TimeStampedModel):
    """Advanced HR Analytics and Insights"""
    ANALYTICS_TYPES = [
        ('EMPLOYEE_TURNOVER', 'Employee Turnover Analysis'),
        ('PERFORMANCE_TRENDS', 'Performance Trends'),
        ('ATTENDANCE_PATTERNS', 'Attendance Patterns'),
        ('COMPENSATION_ANALYSIS', 'Compensation Analysis'),
        ('TRAINING_EFFECTIVENESS', 'Training Effectiveness'),
        ('RECRUITMENT_METRICS', 'Recruitment Metrics'),
        ('ENGAGEMENT_SURVEY', 'Employee Engagement'),
        ('DIVERSITY_INCLUSION', 'Diversity & Inclusion'),
        ('SUCCESSION_PLANNING', 'Succession Planning'),
        ('WORKFORCE_PLANNING', 'Workforce Planning'),
    ]
    
    analytics_type = models.CharField(max_length=25, choices=ANALYTICS_TYPES)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    
    # Analysis period
    analysis_period_start = models.DateField()
    analysis_period_end = models.DateField()
    
    # Metrics and KPIs
    metrics_data = models.JSONField(default=dict)
    kpi_scores = models.JSONField(default=dict)
    benchmarks = models.JSONField(default=dict)
    
    # Insights and recommendations
    key_insights = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)
    action_items = models.JSONField(default=list)
    
    # Trend analysis
    trend_data = models.JSONField(default=dict)
    forecast_data = models.JSONField(default=dict)
    
    # Risk assessment
    risk_factors = models.JSONField(default=list)
    risk_score = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(10)])
    
    # Generated by
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_automated = models.BooleanField(default=True)
    
    # Sharing and access
    shared_with = models.ManyToManyField(User, blank=True, related_name='accessible_hr_analytics')
    is_confidential = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "HR Analytics"
        verbose_name_plural = "HR Analytics"
    
    def __str__(self):
        return f"{self.analytics_type} - {self.analysis_period_start} to {self.analysis_period_end}"
