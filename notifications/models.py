from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from core.models import TimeStampedModel, School, UUIDModel
from phonenumber_field.modelfields import PhoneNumberField

class NotificationChannel(TimeStampedModel):
    """Notification delivery channels"""
    CHANNEL_TYPES = [
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
        ('PUSH', 'Push Notification'),
        ('IN_APP', 'In-App Notification'),
        ('WHATSAPP', 'WhatsApp'),
        ('TELEGRAM', 'Telegram'),
    ]
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='notification_channels')
    name = models.CharField(max_length=100)
    channel_type = models.CharField(max_length=20, choices=CHANNEL_TYPES)
    configuration = models.JSONField(default=dict)  # API keys, endpoints, etc.
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    rate_limit_per_minute = models.IntegerField(default=60)
    
    class Meta:
        unique_together = ['school', 'name']
    
    def __str__(self):
        return f"{self.school.name} - {self.name} ({self.channel_type})"

class NotificationTemplate(TimeStampedModel):
    """Notification templates"""
    TEMPLATE_CATEGORIES = [
        ('ACADEMIC', 'Academic'),
        ('FINANCIAL', 'Financial'),
        ('DISCIPLINARY', 'Disciplinary'),
        ('ATTENDANCE', 'Attendance'),
        ('EXAMINATION', 'Examination'),
        ('EVENT', 'Event'),
        ('EMERGENCY', 'Emergency'),
        ('SYSTEM', 'System'),
        ('CUSTOM', 'Custom'),
    ]
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='notification_templates')
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=TEMPLATE_CATEGORIES)
    channel = models.ForeignKey(NotificationChannel, on_delete=models.CASCADE, related_name='templates')
    subject_template = models.CharField(max_length=500, blank=True, null=True)
    body_template = models.TextField()
    variables = models.JSONField(default=list)  # Available template variables
    priority_level = models.CharField(max_length=10, choices=[
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ], default='MEDIUM')
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.school.name} - {self.name}"

class Notification(UUIDModel, TimeStampedModel):
    """Individual notifications"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('DELIVERED', 'Delivered'),
        ('READ', 'Read'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='notifications')
    template = models.ForeignKey(NotificationTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_notifications')
    
    # Message content
    subject = models.CharField(max_length=500, blank=True, null=True)
    message = models.TextField()
    attachment_url = models.URLField(blank=True, null=True)
    
    # Delivery details
    channel = models.ForeignKey(NotificationChannel, on_delete=models.CASCADE)
    recipient_email = models.EmailField(blank=True, null=True)
    recipient_phone = PhoneNumberField(blank=True, null=True)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Scheduling
    scheduled_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    priority_level = models.CharField(max_length=10, choices=[
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ], default='MEDIUM')
    metadata = models.JSONField(default=dict)
    external_id = models.CharField(max_length=200, blank=True, null=True)  # External service ID
    error_message = models.TextField(blank=True, null=True)
    retry_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'status']),
            models.Index(fields=['school', 'status']),
            models.Index(fields=['scheduled_at']),
        ]
    
    def __str__(self):
        return f"{self.recipient.username} - {self.subject}"

class NotificationGroup(TimeStampedModel):
    """Group notifications for batch sending"""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='notification_groups')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    template = models.ForeignKey(NotificationTemplate, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_groups_sent')
    
    # Recipients
    recipient_users = models.ManyToManyField(User, blank=True, related_name='notification_groups_received')
    recipient_roles = models.JSONField(default=list)  # Role-based recipients
    recipient_filters = models.JSONField(default=dict)  # Dynamic recipient filters
    
    # Content
    subject = models.CharField(max_length=500, blank=True, null=True)
    message = models.TextField()
    template_variables = models.JSONField(default=dict)
    
    # Scheduling
    scheduled_at = models.DateTimeField(null=True, blank=True)
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Statistics
    total_recipients = models.IntegerField(default=0)
    successful_sends = models.IntegerField(default=0)
    failed_sends = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.school.name} - {self.name}"

class AnnouncementBoard(TimeStampedModel):
    """School announcement board"""
    ANNOUNCEMENT_TYPES = [
        ('GENERAL', 'General'),
        ('ACADEMIC', 'Academic'),
        ('SPORTS', 'Sports'),
        ('CULTURAL', 'Cultural'),
        ('HOLIDAY', 'Holiday'),
        ('EXAMINATION', 'Examination'),
        ('ADMISSION', 'Admission'),
        ('EMERGENCY', 'Emergency'),
    ]
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='announcements')
    title = models.CharField(max_length=300)
    content = models.TextField()
    announcement_type = models.CharField(max_length=20, choices=ANNOUNCEMENT_TYPES, default='GENERAL')
    
    # Targeting
    target_roles = models.JSONField(default=list)  # Which roles can see this
    target_classes = models.JSONField(default=list)  # Which classes can see this
    target_users = models.ManyToManyField(User, blank=True, related_name='targeted_announcements')
    
    # Scheduling
    publish_date = models.DateTimeField()
    expiry_date = models.DateTimeField(null=True, blank=True)
    
    # Display options
    is_pinned = models.BooleanField(default=False)
    is_urgent = models.BooleanField(default=False)
    allow_comments = models.BooleanField(default=True)
    
    # Attachments
    attachment = models.FileField(upload_to='announcements/', blank=True, null=True)
    
    # Statistics
    view_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-is_pinned', '-is_urgent', '-publish_date']
    
    def __str__(self):
        return f"{self.school.name} - {self.title}"

class AnnouncementView(TimeStampedModel):
    """Track who viewed announcements"""
    announcement = models.ForeignKey(AnnouncementBoard, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='announcement_views')
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['announcement', 'user']
    
    def __str__(self):
        return f"{self.user.username} viewed {self.announcement.title}"

class Message(UUIDModel, TimeStampedModel):
    """Internal messaging system"""
    MESSAGE_TYPES = [
        ('DIRECT', 'Direct Message'),
        ('GROUP', 'Group Message'),
        ('BROADCAST', 'Broadcast'),
    ]
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='DIRECT')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipients = models.ManyToManyField(User, through='MessageRecipient', related_name='received_messages')
    
    subject = models.CharField(max_length=500, blank=True, null=True)
    content = models.TextField()
    attachment = models.FileField(upload_to='messages/', blank=True, null=True)
    
    # Threading
    parent_message = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    thread_id = models.UUIDField(null=True, blank=True)
    
    # Status
    is_draft = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Priority
    priority = models.CharField(max_length=10, choices=[
        ('LOW', 'Low'),
        ('NORMAL', 'Normal'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ], default='NORMAL')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.sender.username} - {self.subject}"

class MessageRecipient(TimeStampedModel):
    """Message recipient details"""
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    is_starred = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['message', 'recipient']
    
    def __str__(self):
        return f"{self.recipient.username} - {self.message.subject}"

class EmergencyAlert(UUIDModel, TimeStampedModel):
    """Emergency alert system"""
    ALERT_LEVELS = [
        ('INFO', 'Information'),
        ('WARNING', 'Warning'),
        ('CRITICAL', 'Critical'),
        ('EMERGENCY', 'Emergency'),
    ]
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='emergency_alerts')
    title = models.CharField(max_length=200)
    message = models.TextField()
    alert_level = models.CharField(max_length=10, choices=ALERT_LEVELS, default='INFO')
    
    # Targeting
    target_all = models.BooleanField(default=True)
    target_roles = models.JSONField(default=list)
    target_classes = models.JSONField(default=list)
    
    # Status
    is_active = models.BooleanField(default=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Delivery channels
    send_email = models.BooleanField(default=True)
    send_sms = models.BooleanField(default=True)
    send_push = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.school.name} - {self.title} ({self.alert_level})"
