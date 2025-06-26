from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from core.models import TimeStampedModel, SchoolSettings, UUIDModel
import uuid

class UserProfile(TimeStampedModel):
    """Extended user profile with comprehensive information"""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('P', 'Prefer not to say'),
    ]
    
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='user_profiles')
    employee_id = models.CharField(max_length=50, blank=True, null=True)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True, null=True)
    
    # Contact Information
    phone_primary = PhoneNumberField(blank=True, null=True)
    phone_secondary = PhoneNumberField(blank=True, null=True)
    email_personal = models.EmailField(blank=True, null=True)
    
    # Address Information
    current_address = models.TextField(blank=True, null=True)
    permanent_address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, default='India')
    
    # Government IDs
    aadhar_number = models.CharField(max_length=12, blank=True, null=True, unique=True)
    pan_number = models.CharField(max_length=10, blank=True, null=True, unique=True)
    passport_number = models.CharField(max_length=20, blank=True, null=True)
    driving_license = models.CharField(max_length=20, blank=True, null=True)
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=200, blank=True, null=True)
    emergency_contact_phone = PhoneNumberField(blank=True, null=True)
    emergency_contact_relation = models.CharField(max_length=50, blank=True, null=True)
    
    # Profile Details
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    biography = models.TextField(blank=True, null=True)
    qualification = models.CharField(max_length=500, blank=True, null=True)
    experience_years = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    # System Settings
    preferred_language = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, default='Asia/Kolkata')
    theme_preference = models.CharField(max_length=20, choices=[
        ('LIGHT', 'Light'),
        ('DARK', 'Dark'),
        ('AUTO', 'Auto'),
    ], default='LIGHT')
    
    # Status
    is_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    joined_date = models.DateField(auto_now_add=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    last_activity = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['school', 'employee_id']),
            models.Index(fields=['aadhar_number']),
            models.Index(fields=['pan_number']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.username})"
    
    @property
    def full_name(self):
        names = [self.user.first_name, self.middle_name, self.user.last_name]
        return ' '.join(filter(None, names))

class Role(TimeStampedModel):
    """Custom role management system"""
    ROLE_TYPES = [
        ('ADMIN', 'Administrator'),
        ('PRINCIPAL', 'Principal'),
        ('VICE_PRINCIPAL', 'Vice Principal'),
        ('TEACHER', 'Teacher'),
        ('STUDENT', 'Student'),
        ('PARENT', 'Parent'),
        ('ACCOUNTANT', 'Accountant'),
        ('LIBRARIAN', 'Librarian'),
        ('TRANSPORT_MANAGER', 'Transport Manager'),
        ('HOSTEL_WARDEN', 'Hostel Warden'),
        ('NURSE', 'Nurse'),
        ('SECURITY', 'Security'),
        ('MAINTENANCE', 'Maintenance'),
        ('RECEPTIONIST', 'Receptionist'),
        ('HR', 'Human Resources'),
        ('IT_SUPPORT', 'IT Support'),
        ('CUSTOM', 'Custom Role'),
    ]
    
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='roles')
    name = models.CharField(max_length=100)
    role_type = models.CharField(max_length=20, choices=ROLE_TYPES)
    description = models.TextField(blank=True, null=True)
    permissions = models.JSONField(default=list)  # List of permission codes
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    hierarchy_level = models.IntegerField(default=0, help_text="Higher number = higher authority")
    
    class Meta:
        unique_together = ['school', 'name']
        ordering = ['-hierarchy_level', 'name']
    
    def __str__(self):
        return f"{self.school.name} - {self.name}"

class Permission(TimeStampedModel):
    """Granular permission system"""
    PERMISSION_CATEGORIES = [
        ('USER', 'User Management'),
        ('STUDENT', 'Student Management'),
        ('TEACHER', 'Teacher Management'),
        ('ACADEMIC', 'Academic Management'),
        ('FINANCE', 'Financial Management'),
        ('LIBRARY', 'Library Management'),
        ('TRANSPORT', 'Transport Management'),
        ('HOSTEL', 'Hostel Management'),
        ('INVENTORY', 'Inventory Management'),
        ('COMMUNICATION', 'Communication'),
        ('REPORTS', 'Reports & Analytics'),
        ('SYSTEM', 'System Configuration'),
    ]
    
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=20, choices=PERMISSION_CATEGORIES)
    is_system_permission = models.BooleanField(default=False)  # Cannot be deleted
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class UserRole(TimeStampedModel):
    """User role assignments"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='role_assignments')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='user_assignments')
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='role_assignments_made')
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ['user', 'role']
    
    def __str__(self):
        return f"{self.user.username} - {self.role.name}"

class LoginSession(UUIDModel, TimeStampedModel):
    """Track user login sessions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    device_info = models.JSONField(default=dict)
    location_info = models.JSONField(default=dict, blank=True)
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    force_logout = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-login_time']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_key']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.login_time}"

class SecurityEvent(UUIDModel, TimeStampedModel):
    """Security-related events logging"""
    EVENT_TYPES = [
        ('LOGIN_SUCCESS', 'Successful Login'),
        ('LOGIN_FAILED', 'Failed Login'),
        ('PASSWORD_CHANGE', 'Password Changed'),
        ('PASSWORD_RESET', 'Password Reset'),
        ('ACCOUNT_LOCKED', 'Account Locked'),
        ('ACCOUNT_UNLOCKED', 'Account Unlocked'),
        ('SUSPICIOUS_ACTIVITY', 'Suspicious Activity'),
        ('PRIVILEGE_ESCALATION', 'Privilege Escalation'),
        ('DATA_EXPORT', 'Data Export'),
        ('SYSTEM_ACCESS', 'System Access'),
    ]
    
    SEVERITY_LEVELS = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='security_events')
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS, default='LOW')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    session_key = models.CharField(max_length=40, blank=True, null=True)
    description = models.TextField()
    metadata = models.JSONField(default=dict)
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_security_events')
    resolved_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event_type', 'severity']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['school', 'severity']),
        ]
    
    def __str__(self):
        return f"{self.event_type} - {self.user} - {self.created_at}"

class TwoFactorAuth(TimeStampedModel):
    """Two-factor authentication management"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='two_factor_auth')
    is_enabled = models.BooleanField(default=False)
    secret_key = models.CharField(max_length=32, blank=True, null=True)
    backup_codes = models.JSONField(default=list)  # List of backup codes
    last_used_code = models.CharField(max_length=6, blank=True, null=True)
    last_used_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - 2FA {'Enabled' if self.is_enabled else 'Disabled'}"

class PasswordHistory(TimeStampedModel):
    """Track password history to prevent reuse"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_history')
    password_hash = models.CharField(max_length=128)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.created_at}"
