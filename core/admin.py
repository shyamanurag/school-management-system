from django.contrib import admin
from .models import (
    SchoolSettings, AcademicYear, Campus, Department, Building, Room, 
    SystemConfiguration, Subject, Grade, Teacher, Student, FeeCategory, 
    FeeStructure, FeePayment, Attendance, Exam, ExamResult, AuditLog,
    Attachment, NotificationTemplate, AdmissionSession, AIAnalytics, 
    RealTimeChat, ChatMessage, ParentPortal, MobileAppSession, AdvancedReport, 
    SmartNotification, BiometricAttendance, VirtualClassroom, VirtualClassroomParticipant,
    Employee, PayrollStructure, EmployeePayroll, LeaveType, LeaveApplication,
    PerformanceReview, TrainingProgram, TrainingEnrollment, HRAnalytics
)

@admin.register(SchoolSettings)
class SchoolSettingsAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'state', 'board_affiliation', 'principal_name']
    search_fields = ['name', 'city', 'principal_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['name', 'address', 'city', 'state', 'postal_code', 'country']
        }),
        ('Contact Details', {
            'fields': ['phone', 'email', 'website', 'logo']
        }),
        ('Principal Information', {
            'fields': ['principal_name', 'principal_email', 'principal_phone']
        }),
        ('Academic Configuration', {
            'fields': ['established_date', 'board_affiliation', 'academic_year_start_month']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'is_current', 'is_active']
    list_filter = ['is_current', 'is_active']
    search_fields = ['name']
    ordering = ['-start_date']
    date_hierarchy = 'start_date'

@admin.register(Campus)
class CampusAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'city', 'principal_name', 'is_main_campus', 'is_active']
    list_filter = ['is_main_campus', 'is_active', 'city']
    search_fields = ['name', 'code', 'city']
    ordering = ['name']

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'head_of_department', 'budget_allocation', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code']
    ordering = ['name']

@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ['name', 'campus', 'code', 'floors', 'is_active']
    list_filter = ['campus', 'is_active']
    search_fields = ['name', 'code']
    ordering = ['campus__name', 'name']

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'name', 'building', 'room_type', 'capacity', 'floor', 'is_active']
    list_filter = ['room_type', 'building__campus', 'building', 'floor', 'is_active', 'has_projector', 'has_smartboard', 'has_ac']
    search_fields = ['room_number', 'name', 'building__name']
    ordering = ['building__campus__name', 'building__name', 'room_number']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['building', 'room_number', 'name', 'room_type', 'floor']
        }),
        ('Capacity & Area', {
            'fields': ['capacity', 'area_sqft']
        }),
        ('Facilities', {
            'fields': ['has_projector', 'has_smartboard', 'has_ac']
        }),
        ('Additional Information', {
            'fields': ['description', 'is_active']
        }),
    ]

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'department', 'credit_hours', 'is_practical', 'is_active']
    list_filter = ['department', 'is_practical', 'is_active']
    search_fields = ['name', 'code']
    ordering = ['department__name', 'name']

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['name', 'section', 'academic_year', 'class_teacher', 'room', 'max_students', 'is_active']
    list_filter = ['academic_year', 'numeric_value', 'is_active']
    search_fields = ['name', 'section']
    ordering = ['academic_year', 'numeric_value', 'section']

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['user', 'employee_id', 'department', 'experience_years', 'is_active']
    list_filter = ['department', 'is_active', 'date_of_joining']
    search_fields = ['user__first_name', 'user__last_name', 'employee_id']
    filter_horizontal = ['subjects']
    date_hierarchy = 'date_of_joining'
    
    fieldsets = [
        ('Personal Information', {
            'fields': ['user', 'employee_id', 'phone', 'address', 'date_of_birth', 'photo']
        }),
        ('Professional Information', {
            'fields': ['date_of_joining', 'qualification', 'experience_years', 'department', 'subjects']
        }),
        ('Employment Details', {
            'fields': ['salary', 'is_active']
        }),
    ]

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['admission_number', 'full_name', 'grade', 'roll_number', 'parent_name', 'is_active']
    list_filter = ['grade', 'gender', 'is_active', 'admission_date']
    search_fields = ['admission_number', 'first_name', 'last_name', 'roll_number', 'parent_name']
    date_hierarchy = 'admission_date'
    ordering = ['grade', 'roll_number']
    
    fieldsets = [
        ('Student Information', {
            'fields': ['admission_number', 'roll_number', 'first_name', 'last_name', 'date_of_birth', 'gender', 'photo']
        }),
        ('Contact Information', {
            'fields': ['phone', 'email', 'address', 'emergency_contact']
        }),
        ('Academic Information', {
            'fields': ['grade', 'admission_date']
        }),
        ('Parent Information', {
            'fields': ['parent_name', 'parent_phone', 'parent_email']
        }),
        ('Status', {
            'fields': ['is_active']
        }),
    ]

@admin.register(FeeCategory)
class FeeCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']

@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ['grade', 'category', 'amount', 'academic_year', 'due_date', 'is_active']
    list_filter = ['academic_year', 'category', 'is_active']
    search_fields = ['grade__name', 'category__name']
    date_hierarchy = 'due_date'

@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ['student', 'fee_structure', 'amount_due', 'amount_paid', 'status', 'payment_date']
    list_filter = ['status', 'payment_method', 'payment_date']
    search_fields = ['student__first_name', 'student__last_name', 'student__admission_number']
    date_hierarchy = 'payment_date'

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'status', 'marked_by']
    list_filter = ['status', 'date', 'student__grade']
    search_fields = ['student__first_name', 'student__last_name', 'student__admission_number']
    date_hierarchy = 'date'

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['name', 'exam_type', 'academic_year', 'start_date', 'end_date', 'total_marks', 'is_active']
    list_filter = ['exam_type', 'academic_year', 'is_active']
    search_fields = ['name']
    date_hierarchy = 'start_date'

@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam', 'subject', 'marks_obtained', 'total_marks', 'grade']
    list_filter = ['exam', 'subject', 'grade']
    search_fields = ['student__first_name', 'student__last_name', 'student__admission_number']

@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(admin.ModelAdmin):
    list_display = ['key', 'data_type', 'is_sensitive', 'created_at']
    list_filter = ['data_type', 'is_sensitive']
    search_fields = ['key', 'description']
    ordering = ['key']
    
    fieldsets = [
        ('Configuration', {
            'fields': ['key', 'value', 'data_type']
        }),
        ('Metadata', {
            'fields': ['description', 'is_sensitive']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]

@admin.register(AIAnalytics)
class AIAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['analysis_type', 'target_student', 'target_grade', 'confidence_score', 'is_automated', 'created_at']
    list_filter = ['analysis_type', 'is_automated', 'created_at']
    search_fields = ['analysis_type', 'target_student__full_name', 'target_grade__name']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Analysis Details', {
            'fields': ('analysis_type', 'target_student', 'target_grade', 'confidence_score')
        }),
        ('Data & Insights', {
            'fields': ('analysis_data', 'insights', 'recommendations'),
            'classes': ('collapse',)
        }),
        ('Configuration', {
            'fields': ('is_automated', 'next_analysis_date'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(RealTimeChat)
class RealTimeChatAdmin(admin.ModelAdmin):
    list_display = ['name', 'chat_type', 'is_group', 'message_count', 'last_message_at', 'is_archived']
    list_filter = ['chat_type', 'is_group', 'is_private', 'is_archived', 'created_at']
    search_fields = ['name', 'description']
    filter_horizontal = ['participants', 'admin_users']
    readonly_fields = ['message_count', 'last_message_at', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'chat_type')
        }),
        ('Participants', {
            'fields': ('participants', 'admin_users', 'max_participants')
        }),
        ('Settings', {
            'fields': ('is_group', 'allow_file_sharing', 'allow_voice_messages', 'is_moderated')
        }),
        ('Privacy & Status', {
            'fields': ('is_private', 'is_archived', 'archived_at')
        }),
        ('Activity', {
            'fields': ('message_count', 'last_message_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'chat_room', 'message_type', 'content_preview', 'is_edited', 'is_deleted', 'created_at']
    list_filter = ['message_type', 'is_edited', 'is_deleted', 'created_at']
    search_fields = ['sender__username', 'content', 'chat_room__name']
    readonly_fields = ['created_at', 'updated_at', 'edited_at', 'deleted_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if obj.content and len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'
    
    fieldsets = (
        ('Message Details', {
            'fields': ('chat_room', 'sender', 'message_type', 'content')
        }),
        ('Attachments', {
            'fields': ('attachment', 'thumbnail'),
            'classes': ('collapse',)
        }),
        ('Reply & Reactions', {
            'fields': ('reply_to', 'reactions'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_edited', 'edited_at', 'is_deleted', 'deleted_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ParentPortal)
class ParentPortalAdmin(admin.ModelAdmin):
    list_display = ['parent_user', 'preferred_communication_method', 'login_count', 'last_activity', 'app_version']
    list_filter = ['preferred_communication_method', 'last_app_login', 'created_at']
    search_fields = ['parent_user__username', 'parent_user__first_name', 'parent_user__last_name']
    readonly_fields = ['login_count', 'last_activity', 'created_at', 'updated_at']
    fieldsets = (
        ('User Information', {
            'fields': ('parent_user',)
        }),
        ('Portal Preferences', {
            'fields': ('dashboard_layout', 'notification_preferences', 'privacy_settings')
        }),
        ('Communication', {
            'fields': ('preferred_communication_method', 'emergency_contacts')
        }),
        ('Mobile App', {
            'fields': ('device_tokens', 'app_version', 'last_app_login')
        }),
        ('Activity Tracking', {
            'fields': ('login_count', 'last_activity', 'feature_usage_stats'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(MobileAppSession)
class MobileAppSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'app_type', 'app_version', 'os_version', 'is_active', 'session_start']
    list_filter = ['app_type', 'is_active', 'session_start', 'os_version']
    search_fields = ['user__username', 'device_token', 'app_version']
    readonly_fields = ['session_start', 'created_at', 'updated_at']
    fieldsets = (
        ('User & App Info', {
            'fields': ('user', 'app_type', 'app_version', 'os_version')
        }),
        ('Device Information', {
            'fields': ('device_info', 'device_token')
        }),
        ('Session Details', {
            'fields': ('session_start', 'session_end', 'is_active')
        }),
        ('Location', {
            'fields': ('last_latitude', 'last_longitude', 'location_updated_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(AdvancedReport)
class AdvancedReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'format', 'is_scheduled', 'use_ai_insights', 'last_generated', 'generation_count']
    list_filter = ['category', 'format', 'is_scheduled', 'use_ai_insights', 'ai_analysis_level', 'created_at']
    search_fields = ['name', 'description']
    filter_horizontal = ['recipients']
    readonly_fields = ['last_generated', 'generation_count', 'average_generation_time', 'created_at', 'updated_at']
    fieldsets = (
        ('Report Configuration', {
            'fields': ('name', 'description', 'category', 'format')
        }),
        ('Data Sources & Filters', {
            'fields': ('filters', 'parameters', 'data_sources'),
            'classes': ('collapse',)
        }),
        ('AI Enhancement', {
            'fields': ('use_ai_insights', 'ai_analysis_level')
        }),
        ('Scheduling', {
            'fields': ('is_scheduled', 'schedule_expression', 'next_run')
        }),
        ('Recipients', {
            'fields': ('recipients', 'recipient_groups'),
            'classes': ('collapse',)
        }),
        ('Execution Tracking', {
            'fields': ('last_generated', 'generation_count', 'average_generation_time'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(SmartNotification)
class SmartNotificationAdmin(admin.ModelAdmin):
    list_display = ['trigger_type', 'recipient', 'priority_score', 'is_sent', 'is_read', 'delivery_time_preference', 'created_at']
    list_filter = ['trigger_type', 'delivery_time_preference', 'is_sent', 'is_read', 'is_acted_upon', 'language_preference']
    search_fields = ['title', 'message', 'recipient__username']
    readonly_fields = ['sent_at', 'read_at', 'action_taken_at', 'created_at', 'updated_at']
    fieldsets = (
        ('Notification Details', {
            'fields': ('trigger_type', 'recipient', 'title', 'message')
        }),
        ('AI Configuration', {
            'fields': ('priority_score', 'action_items', 'personalization_data')
        }),
        ('Delivery Settings', {
            'fields': ('preferred_channels', 'delivery_time_preference', 'language_preference')
        }),
        ('Tracking', {
            'fields': ('is_sent', 'sent_at', 'is_read', 'read_at', 'is_acted_upon', 'action_taken_at'),
            'classes': ('collapse',)
        }),
        ('AI Learning', {
            'fields': ('effectiveness_score',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(BiometricAttendance)
class BiometricAttendanceAdmin(admin.ModelAdmin):
    list_display = ['user', 'biometric_type', 'template_quality', 'is_active', 'is_primary', 'last_used', 'usage_count']
    list_filter = ['biometric_type', 'is_active', 'is_primary', 'enrollment_device', 'created_at']
    search_fields = ['user__username', 'enrollment_device', 'enrollment_location']
    readonly_fields = ['last_used', 'usage_count', 'created_at', 'updated_at']
    fieldsets = (
        ('User & Type', {
            'fields': ('user', 'biometric_type', 'template_quality')
        }),
        ('Enrollment Details', {
            'fields': ('enrollment_device', 'enrollment_location', 'enrollment_verified_by')
        }),
        ('Status', {
            'fields': ('is_active', 'is_primary')
        }),
        ('Usage Tracking', {
            'fields': ('last_used', 'usage_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Hide sensitive biometric template field
    exclude = ['biometric_template']

@admin.register(VirtualClassroom)
class VirtualClassroomAdmin(admin.ModelAdmin):
    list_display = ['title', 'class_type', 'platform', 'host', 'scheduled_start', 'scheduled_end', 'is_active']
    list_filter = ['class_type', 'platform', 'is_active', 'is_recorded', 'scheduled_start']
    search_fields = ['title', 'description', 'host__username', 'meeting_id']
    readonly_fields = ['actual_start', 'actual_end', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'class_type', 'host')
        }),
        ('Platform Details', {
            'fields': ('platform', 'meeting_id', 'meeting_password', 'meeting_url')
        }),
        ('Scheduling', {
            'fields': ('scheduled_start', 'scheduled_end', 'actual_start', 'actual_end')
        }),
        ('Participants', {
            'fields': ('max_participants',)
        }),
        ('Settings', {
            'fields': ('is_recorded', 'recording_url', 'allow_chat', 'allow_screen_sharing', 'require_approval')
        }),
        ('Recurrence', {
            'fields': ('is_recurring', 'recurrence_pattern'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(VirtualClassroomParticipant)
class VirtualClassroomParticipantAdmin(admin.ModelAdmin):
    list_display = ['user', 'virtual_classroom', 'role', 'attendance_status', 'joined_at', 'total_duration', 'session_rating']
    list_filter = ['role', 'attendance_status', 'session_rating', 'virtual_classroom__class_type']
    search_fields = ['user__username', 'virtual_classroom__title']
    readonly_fields = ['total_duration', 'created_at', 'updated_at']
    fieldsets = (
        ('Participant Info', {
            'fields': ('virtual_classroom', 'user', 'role')
        }),
        ('Attendance', {
            'fields': ('attendance_status', 'joined_at', 'left_at', 'total_duration')
        }),
        ('Participation Metrics', {
            'fields': ('chat_messages_count', 'questions_asked', 'screen_share_duration'),
            'classes': ('collapse',)
        }),
        ('Feedback', {
            'fields': ('session_rating', 'feedback'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['action_type', 'model_name', 'object_id', 'user', 'created_at']
    list_filter = ['action_type', 'model_name', 'risk_level', 'created_at']
    search_fields = ['model_name', 'object_id', 'user__username', 'description']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = [
        ('Action Details', {
            'fields': ['action_type', 'model_name', 'object_id', 'description']
        }),
        ('User Information', {
            'fields': ['user', 'session_key', 'ip_address', 'user_agent']
        }),
        ('Changes', {
            'fields': ['changes'],
            'classes': ['collapse']
        }),
        ('Risk Assessment', {
            'fields': ['risk_level']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]

@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'template_type', 'is_active', 'created_at']
    list_filter = ['template_type', 'is_active', 'created_at']
    search_fields = ['name', 'subject', 'body']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = [
        ('Template Information', {
            'fields': ['name', 'template_type', 'subject']
        }),
        ('Content', {
            'fields': ['body', 'variables']
        }),
        ('Status', {
            'fields': ['is_active']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]

# ==================== HR ADMIN CONFIGURATIONS ====================

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'full_name', 'designation', 'department', 'employment_status', 'date_of_joining', 'years_of_service']
    list_filter = ['employment_type', 'employment_status', 'department', 'marital_status', 'date_of_joining']
    search_fields = ['employee_id', 'user__first_name', 'user__last_name', 'designation', 'phone']
    date_hierarchy = 'date_of_joining'
    ordering = ['employee_id']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['user', 'employee_id', 'photo']
        }),
        ('Personal Details', {
            'fields': ['date_of_birth', 'gender', 'marital_status', 'nationality', 'blood_group']
        }),
        ('Contact Information', {
            'fields': ['personal_email', 'phone', 'alternate_phone', 'current_address', 'permanent_address']
        }),
        ('Emergency Contact', {
            'fields': ['emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relation']
        }),
        ('Employment Details', {
            'fields': ['employment_type', 'employment_status', 'date_of_joining', 'date_of_leaving', 
                      'probation_period_months', 'probation_end_date', 'confirmation_date']
        }),
        ('Organizational Details', {
            'fields': ['department', 'designation', 'reporting_manager', 'work_location']
        }),
        ('Professional Information', {
            'fields': ['qualification', 'experience_before_joining', 'skills', 'certifications']
        }),
        ('Compensation', {
            'fields': ['basic_salary', 'gross_salary', 'ctc']
        }),
        ('Bank Details', {
            'fields': ['bank_name', 'bank_account_number', 'bank_ifsc_code', 'bank_branch'],
            'classes': ['collapse']
        }),
        ('Government IDs', {
            'fields': ['pan_number', 'aadhar_number', 'passport_number', 'driving_license'],
            'classes': ['collapse']
        }),
        ('HR Tracking', {
            'fields': ['last_promotion_date', 'last_increment_date', 'performance_rating']
        }),
    ]
    
    readonly_fields = ['years_of_service']

@admin.register(PayrollStructure)
class PayrollStructureAdmin(admin.ModelAdmin):
    list_display = ['name', 'component_type', 'calculation_type', 'fixed_amount', 'percentage', 'is_mandatory', 'is_active']
    list_filter = ['component_type', 'calculation_type', 'is_taxable', 'is_mandatory', 'is_active']
    search_fields = ['name']
    ordering = ['component_type', 'name']
    
    fieldsets = [
        ('Component Details', {
            'fields': ['name', 'component_type', 'calculation_type']
        }),
        ('Calculation Configuration', {
            'fields': ['fixed_amount', 'percentage', 'formula']
        }),
        ('Applicability', {
            'fields': ['is_taxable', 'is_mandatory', 'is_active']
        }),
        ('Limits', {
            'fields': ['minimum_amount', 'maximum_amount']
        }),
    ]

@admin.register(EmployeePayroll)
class EmployeePayrollAdmin(admin.ModelAdmin):
    list_display = ['employee', 'pay_period_start', 'pay_period_end', 'gross_salary', 'net_salary', 'is_processed', 'is_paid']
    list_filter = ['pay_period_start', 'is_processed', 'is_paid', 'payment_method']
    search_fields = ['employee__employee_id', 'employee__user__first_name', 'employee__user__last_name']
    date_hierarchy = 'pay_period_start'
    ordering = ['-pay_period_start', 'employee__employee_id']
    
    fieldsets = [
        ('Employee & Period', {
            'fields': ['employee', 'pay_period_start', 'pay_period_end']
        }),
        ('Salary Components', {
            'fields': ['basic_salary', 'allowances', 'deductions', 'benefits']
        }),
        ('Calculated Amounts', {
            'fields': ['gross_salary', 'total_deductions', 'net_salary']
        }),
        ('Attendance Impact', {
            'fields': ['working_days', 'present_days', 'absent_days', 'leave_days', 'overtime_hours', 'overtime_amount']
        }),
        ('Payment Details', {
            'fields': ['payment_date', 'payment_method', 'payment_reference']
        }),
        ('Status', {
            'fields': ['is_processed', 'is_paid', 'remarks']
        }),
    ]

@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'max_days_per_year', 'is_paid', 'requires_approval', 'is_active']
    list_filter = ['is_paid', 'requires_approval', 'carry_forward_allowed', 'applicable_to_probation', 'is_active']
    search_fields = ['name', 'code']
    ordering = ['name']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['name', 'code', 'description']
        }),
        ('Leave Configuration', {
            'fields': ['max_days_per_year', 'max_consecutive_days', 'carry_forward_allowed', 'carry_forward_max_days']
        }),
        ('Eligibility', {
            'fields': ['min_service_months', 'applicable_to_probation']
        }),
        ('Processing', {
            'fields': ['requires_approval', 'advance_notice_days']
        }),
        ('Compensation', {
            'fields': ['is_paid', 'salary_deduction_percentage']
        }),
        ('Status', {
            'fields': ['is_active']
        }),
    ]

@admin.register(LeaveApplication)
class LeaveApplicationAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'start_date', 'end_date', 'total_days', 'status', 'applied_by']
    list_filter = ['status', 'leave_type', 'start_date', 'approved_by']
    search_fields = ['employee__employee_id', 'employee__user__first_name', 'employee__user__last_name', 'reason']
    date_hierarchy = 'start_date'
    ordering = ['-start_date']
    
    fieldsets = [
        ('Leave Details', {
            'fields': ['employee', 'leave_type', 'start_date', 'end_date', 'total_days']
        }),
        ('Application Information', {
            'fields': ['reason', 'contact_during_leave', 'emergency_contact', 'applied_by']
        }),
        ('Approval Workflow', {
            'fields': ['status', 'approved_by', 'approval_date', 'approval_remarks']
        }),
        ('HR Processing', {
            'fields': ['hr_processed_by', 'hr_processing_date']
        }),
        ('Leave Balance', {
            'fields': ['leave_balance_before', 'leave_balance_after'],
            'classes': ['collapse']
        }),
    ]

@admin.register(PerformanceReview)
class PerformanceReviewAdmin(admin.ModelAdmin):
    list_display = ['employee', 'review_type', 'review_period_start', 'overall_rating', 'status', 'due_date']
    list_filter = ['review_type', 'status', 'review_period_start', 'reviewer']
    search_fields = ['employee__employee_id', 'employee__user__first_name', 'employee__user__last_name']
    date_hierarchy = 'review_period_start'
    ordering = ['-review_period_start']
    
    fieldsets = [
        ('Review Information', {
            'fields': ['employee', 'review_type', 'review_period_start', 'review_period_end', 'due_date']
        }),
        ('Participants', {
            'fields': ['reviewer', 'hr_reviewer']
        }),
        ('Performance Metrics', {
            'fields': ['goals_achievement', 'competency_ratings', 'kpi_scores']
        }),
        ('Ratings', {
            'fields': ['overall_rating', 'manager_rating', 'self_rating']
        }),
        ('Feedback', {
            'fields': ['strengths', 'areas_for_improvement', 'manager_comments', 'employee_comments', 'hr_comments']
        }),
        ('Development Plan', {
            'fields': ['development_goals', 'training_recommendations', 'career_aspirations']
        }),
        ('Workflow Status', {
            'fields': ['status', 'self_assessment_completed', 'manager_review_completed', 
                      'hr_review_completed', 'employee_acknowledged', 'completed_date']
        }),
    ]

@admin.register(TrainingProgram)
class TrainingProgramAdmin(admin.ModelAdmin):
    list_display = ['name', 'training_type', 'delivery_mode', 'start_date', 'duration_hours', 'max_participants', 'is_active']
    list_filter = ['training_type', 'delivery_mode', 'start_date', 'is_mandatory', 'certification_provided', 'is_active']
    search_fields = ['name', 'trainer_name', 'trainer_organization']
    date_hierarchy = 'start_date'
    ordering = ['start_date']
    
    fieldsets = [
        ('Program Information', {
            'fields': ['name', 'description', 'training_type', 'delivery_mode']
        }),
        ('Training Details', {
            'fields': ['duration_hours', 'trainer_name', 'trainer_organization']
        }),
        ('Scheduling', {
            'fields': ['start_date', 'end_date', 'registration_deadline']
        }),
        ('Logistics', {
            'fields': ['venue', 'max_participants', 'cost_per_participant']
        }),
        ('Requirements', {
            'fields': ['prerequisites', 'target_audience', 'learning_objectives']
        }),
        ('Materials & Certification', {
            'fields': ['training_materials', 'certification_provided', 'certificate_validity_months']
        }),
        ('Status', {
            'fields': ['is_active', 'is_mandatory']
        }),
    ]

@admin.register(TrainingEnrollment)
class TrainingEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['employee', 'training_program', 'status', 'attendance_percentage', 'final_score', 'certificate_issued']
    list_filter = ['status', 'training_program__training_type', 'certificate_issued', 'enrollment_date']
    search_fields = ['employee__employee_id', 'employee__user__first_name', 'employee__user__last_name', 'training_program__name']
    date_hierarchy = 'enrollment_date'
    ordering = ['-enrollment_date']
    
    fieldsets = [
        ('Enrollment Information', {
            'fields': ['employee', 'training_program', 'enrollment_date', 'status']
        }),
        ('Attendance', {
            'fields': ['attendance_percentage']
        }),
        ('Assessment', {
            'fields': ['pre_assessment_score', 'post_assessment_score', 'final_score']
        }),
        ('Feedback', {
            'fields': ['training_feedback', 'trainer_rating', 'content_rating', 'overall_rating']
        }),
        ('Certification', {
            'fields': ['certificate_issued', 'certificate_number', 'certificate_issue_date', 'certificate_expiry_date']
        }),
        ('Approval', {
            'fields': ['approved_by', 'approval_date'],
            'classes': ['collapse']
        }),
    ]

@admin.register(HRAnalytics)
class HRAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['analytics_type', 'department', 'analysis_period_start', 'analysis_period_end', 'risk_score', 'is_automated']
    list_filter = ['analytics_type', 'department', 'is_automated', 'is_confidential', 'analysis_period_start']
    search_fields = ['analytics_type', 'department__name']
    filter_horizontal = ['shared_with']
    date_hierarchy = 'analysis_period_start'
    ordering = ['-created_at']
    
    fieldsets = [
        ('Analysis Information', {
            'fields': ['analytics_type', 'department', 'analysis_period_start', 'analysis_period_end']
        }),
        ('Metrics & Data', {
            'fields': ['metrics_data', 'kpi_scores', 'benchmarks']
        }),
        ('Insights & Recommendations', {
            'fields': ['key_insights', 'recommendations', 'action_items']
        }),
        ('Trend Analysis', {
            'fields': ['trend_data', 'forecast_data'],
            'classes': ['collapse']
        }),
        ('Risk Assessment', {
            'fields': ['risk_factors', 'risk_score']
        }),
        ('Generation & Sharing', {
            'fields': ['generated_by', 'is_automated', 'shared_with', 'is_confidential']
        }),
    ] 