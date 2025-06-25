from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericRelation
from core.models import TimeStampedModel, School, UUIDModel, AcademicYear, Attachment
from students.models import Student
from hr.models import Employee
from decimal import Decimal
import uuid

class HostelBlock(TimeStampedModel):
    """Hostel blocks/buildings"""
    BLOCK_TYPES = [
        ('BOYS', 'Boys Hostel'),
        ('GIRLS', 'Girls Hostel'),
        ('MIXED', 'Mixed Hostel'),
        ('STAFF', 'Staff Quarters'),
    ]
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='hostel_blocks')
    
    # Block details
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    block_type = models.CharField(max_length=20, choices=BLOCK_TYPES)
    description = models.TextField(blank=True, null=True)
    
    # Capacity
    total_floors = models.IntegerField()
    total_rooms = models.IntegerField()
    total_capacity = models.IntegerField()
    current_occupancy = models.IntegerField(default=0)
    
    # Infrastructure
    has_common_room = models.BooleanField(default=True)
    has_study_hall = models.BooleanField(default=True)
    has_mess = models.BooleanField(default=False)
    has_kitchen = models.BooleanField(default=False)
    has_laundry = models.BooleanField(default=True)
    has_medical_room = models.BooleanField(default=False)
    has_recreation_room = models.BooleanField(default=True)
    
    # Safety and security
    has_cctv = models.BooleanField(default=True)
    has_security_guard = models.BooleanField(default=True)
    has_fire_safety = models.BooleanField(default=True)
    has_emergency_exit = models.BooleanField(default=True)
    
    # Warden
    warden = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_blocks')
    assistant_warden = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='assisted_blocks')
    
    # Contact
    office_phone = models.CharField(max_length=20, blank=True, null=True)
    emergency_phone = models.CharField(max_length=20, blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['school', 'code']
        ordering = ['name']
    
    def __str__(self):
        return f"{self.school.name} - {self.name}"
    
    @property
    def occupancy_percentage(self):
        if self.total_capacity > 0:
            return (self.current_occupancy / self.total_capacity) * 100
        return 0
    
    @property
    def available_capacity(self):
        return self.total_capacity - self.current_occupancy

class HostelRoom(UUIDModel, TimeStampedModel):
    """Individual hostel rooms"""
    ROOM_TYPES = [
        ('SINGLE', 'Single Occupancy'),
        ('DOUBLE', 'Double Occupancy'),
        ('TRIPLE', 'Triple Occupancy'),
        ('DORMITORY', 'Dormitory'),
        ('SUITE', 'Suite'),
    ]
    
    ROOM_STATUS = [
        ('AVAILABLE', 'Available'),
        ('OCCUPIED', 'Occupied'),
        ('MAINTENANCE', 'Under Maintenance'),
        ('RESERVED', 'Reserved'),
        ('OUT_OF_ORDER', 'Out of Order'),
    ]
    
    block = models.ForeignKey(HostelBlock, on_delete=models.CASCADE, related_name='rooms')
    
    # Room identification
    room_number = models.CharField(max_length=20)
    floor_number = models.IntegerField()
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES)
    
    # Capacity
    total_beds = models.IntegerField()
    occupied_beds = models.IntegerField(default=0)
    
    # Room details
    area_sqft = models.FloatField(blank=True, null=True)
    
    # Amenities
    has_attached_bathroom = models.BooleanField(default=True)
    has_balcony = models.BooleanField(default=False)
    has_ac = models.BooleanField(default=False)
    has_fan = models.BooleanField(default=True)
    has_study_table = models.BooleanField(default=True)
    has_cupboard = models.BooleanField(default=True)
    has_wifi = models.BooleanField(default=True)
    
    # Furniture count
    beds_count = models.IntegerField()
    tables_count = models.IntegerField()
    chairs_count = models.IntegerField()
    cupboards_count = models.IntegerField()
    
    # Maintenance
    last_maintenance_date = models.DateField(blank=True, null=True)
    next_maintenance_due = models.DateField(blank=True, null=True)
    
    # Pricing
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status
    status = models.CharField(max_length=20, choices=ROOM_STATUS, default='AVAILABLE')
    
    # Photos
    room_photo = models.ImageField(upload_to='room_photos/', blank=True, null=True)
    
    class Meta:
        unique_together = ['block', 'room_number']
        ordering = ['block', 'floor_number', 'room_number']
    
    def __str__(self):
        return f"{self.block.name} - Room {self.room_number}"
    
    @property
    def available_beds(self):
        return self.total_beds - self.occupied_beds
    
    @property
    def is_available(self):
        return self.status == 'AVAILABLE' and self.available_beds > 0

class HostelAdmission(UUIDModel, TimeStampedModel):
    """Student hostel admissions"""
    ADMISSION_STATUS = [
        ('APPLIED', 'Applied'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('WAITLISTED', 'Waitlisted'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    MEAL_PREFERENCE = [
        ('VEG', 'Vegetarian'),
        ('NON_VEG', 'Non-Vegetarian'),
        ('JAIN', 'Jain'),
        ('VEGAN', 'Vegan'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='hostel_applications')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='hostel_applications')
    
    # Application details
    application_number = models.CharField(max_length=50, unique=True)
    application_date = models.DateField(auto_now_add=True)
    
    # Preferences
    preferred_block = models.ForeignKey(HostelBlock, on_delete=models.CASCADE, related_name='admission_preferences')
    room_type_preference = models.CharField(max_length=20, choices=HostelRoom.ROOM_TYPES)
    meal_preference = models.CharField(max_length=20, choices=MEAL_PREFERENCE, default='VEG')
    
    # Medical information
    medical_conditions = models.TextField(blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    medications = models.TextField(blank=True, null=True)
    special_dietary_requirements = models.TextField(blank=True, null=True)
    
    # Emergency contact
    local_guardian_name = models.CharField(max_length=200, blank=True, null=True)
    local_guardian_phone = PhoneNumberField(blank=True, null=True)
    local_guardian_address = models.TextField(blank=True, null=True)
    local_guardian_relation = models.CharField(max_length=50, blank=True, null=True)
    
    # Fees
    hostel_fee = models.DecimalField(max_digits=10, decimal_places=2)
    mess_fee = models.DecimalField(max_digits=10, decimal_places=2)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2)
    total_fee = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status
    status = models.CharField(max_length=20, choices=ADMISSION_STATUS, default='APPLIED')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_hostel_admissions')
    approval_date = models.DateField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    # Room allocation
    allocated_room = models.ForeignKey(HostelRoom, on_delete=models.SET_NULL, null=True, blank=True, related_name='allocations')
    bed_number = models.CharField(max_length=10, blank=True, null=True)
    allocation_date = models.DateField(blank=True, null=True)
    
    # Check-in/out
    check_in_date = models.DateField(blank=True, null=True)
    check_out_date = models.DateField(blank=True, null=True)
    
    # Documents
    attachments = GenericRelation(Attachment)
    
    def save(self, *args, **kwargs):
        self.total_fee = self.hostel_fee + self.mess_fee + self.security_deposit
        super().save(*args, **kwargs)
    
    class Meta:
        unique_together = ['student', 'academic_year']
        ordering = ['-application_date']
    
    def __str__(self):
        return f"{self.application_number} - {self.student.full_name}"

class HostelResident(TimeStampedModel):
    """Current hostel residents"""
    admission = models.OneToOneField(HostelAdmission, on_delete=models.CASCADE, related_name='resident_record')
    room = models.ForeignKey(HostelRoom, on_delete=models.CASCADE, related_name='current_residents')
    bed_number = models.CharField(max_length=10)
    
    # Check-in details
    check_in_date = models.DateField()
    expected_check_out_date = models.DateField()
    
    # Room inventory issued
    inventory_issued = models.JSONField(default=list, help_text="List of items issued")
    key_issued = models.BooleanField(default=False)
    id_card_issued = models.BooleanField(default=False)
    
    # Fees payment
    last_fee_payment_date = models.DateField(blank=True, null=True)
    next_fee_due_date = models.DateField()
    outstanding_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['room', 'bed_number']
    
    def __str__(self):
        return f"{self.admission.student.full_name} - {self.room}"

class MessMenu(TimeStampedModel):
    """Mess menu management"""
    MEAL_TYPES = [
        ('BREAKFAST', 'Breakfast'),
        ('LUNCH', 'Lunch'),
        ('EVENING_SNACK', 'Evening Snack'),
        ('DINNER', 'Dinner'),
    ]
    
    DAYS_OF_WEEK = [
        ('MONDAY', 'Monday'),
        ('TUESDAY', 'Tuesday'),
        ('WEDNESDAY', 'Wednesday'),
        ('THURSDAY', 'Thursday'),
        ('FRIDAY', 'Friday'),
        ('SATURDAY', 'Saturday'),
        ('SUNDAY', 'Sunday'),
    ]
    
    block = models.ForeignKey(HostelBlock, on_delete=models.CASCADE, related_name='mess_menus')
    
    # Menu details
    day_of_week = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES)
    week_number = models.IntegerField(default=1, help_text="Week 1-4 for monthly rotation")
    
    # Menu items
    vegetarian_menu = models.TextField()
    non_vegetarian_menu = models.TextField(blank=True, null=True)
    jain_menu = models.TextField(blank=True, null=True)
    special_menu = models.TextField(blank=True, null=True)
    
    # Timing
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    # Nutritional information
    calories_per_serving = models.IntegerField(blank=True, null=True)
    protein_grams = models.FloatField(blank=True, null=True)
    carbs_grams = models.FloatField(blank=True, null=True)
    fat_grams = models.FloatField(blank=True, null=True)
    
    # Cost
    cost_per_plate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Effective period
    effective_from = models.DateField()
    effective_to = models.DateField(blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['block', 'day_of_week', 'meal_type', 'week_number']
        ordering = ['day_of_week', 'meal_type']
    
    def __str__(self):
        return f"{self.block.name} - {self.day_of_week} {self.meal_type}"

class MessAttendance(UUIDModel, TimeStampedModel):
    """Student mess attendance tracking"""
    resident = models.ForeignKey(HostelResident, on_delete=models.CASCADE, related_name='mess_attendance')
    date = models.DateField()
    
    # Meal attendance
    breakfast_attended = models.BooleanField(default=False)
    lunch_attended = models.BooleanField(default=False)
    evening_snack_attended = models.BooleanField(default=False)
    dinner_attended = models.BooleanField(default=False)
    
    # Special requests
    special_meal_request = models.TextField(blank=True, null=True)
    dietary_restriction_note = models.TextField(blank=True, null=True)
    
    # Guest meals
    guest_meals = models.IntegerField(default=0)
    guest_meal_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        unique_together = ['resident', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.resident.admission.student.full_name} - {self.date}"

class HostelVisitor(UUIDModel, TimeStampedModel):
    """Visitor management system"""
    VISITOR_TYPES = [
        ('PARENT', 'Parent/Guardian'),
        ('RELATIVE', 'Relative'),
        ('FRIEND', 'Friend'),
        ('OFFICIAL', 'Official Visit'),
        ('VENDOR', 'Vendor/Service Provider'),
        ('OTHER', 'Other'),
    ]
    
    VISIT_STATUS = [
        ('SCHEDULED', 'Scheduled'),
        ('CHECKED_IN', 'Checked In'),
        ('CHECKED_OUT', 'Checked Out'),
        ('CANCELLED', 'Cancelled'),
        ('NO_SHOW', 'No Show'),
    ]
    
    resident = models.ForeignKey(HostelResident, on_delete=models.CASCADE, related_name='visitors')
    
    # Visitor details
    visitor_name = models.CharField(max_length=200)
    visitor_phone = PhoneNumberField()
    visitor_email = models.EmailField(blank=True, null=True)
    visitor_type = models.CharField(max_length=20, choices=VISITOR_TYPES)
    relation_to_student = models.CharField(max_length=100)
    
    # Visit details
    visit_date = models.DateField()
    visit_time = models.TimeField()
    expected_duration_hours = models.FloatField(default=2.0)
    purpose_of_visit = models.TextField()
    
    # Check-in/out
    actual_check_in_time = models.DateTimeField(blank=True, null=True)
    actual_check_out_time = models.DateTimeField(blank=True, null=True)
    
    # Approval
    approval_required = models.BooleanField(default=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_visits')
    approval_date = models.DateTimeField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    # Security
    id_proof_type = models.CharField(max_length=50, blank=True, null=True)
    id_proof_number = models.CharField(max_length=50, blank=True, null=True)
    visitor_photo = models.ImageField(upload_to='visitor_photos/', blank=True, null=True)
    
    # Items carried
    items_carried_in = models.TextField(blank=True, null=True)
    items_carried_out = models.TextField(blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=VISIT_STATUS, default='SCHEDULED')
    
    # Security staff
    checked_in_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='checked_in_visitors')
    checked_out_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='checked_out_visitors')
    
    # Remarks
    remarks = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-visit_date', '-visit_time']
    
    def __str__(self):
        return f"{self.visitor_name} visiting {self.resident.admission.student.full_name} on {self.visit_date}"

class HostelDisciplinary(UUIDModel, TimeStampedModel):
    """Disciplinary actions and violations"""
    VIOLATION_TYPES = [
        ('NOISE_DISTURBANCE', 'Noise Disturbance'),
        ('ROOM_DAMAGE', 'Room/Property Damage'),
        ('UNAUTHORIZED_ABSENCE', 'Unauthorized Absence'),
        ('VIOLATION_OF_TIMINGS', 'Violation of Hostel Timings'),
        ('SMOKING_DRINKING', 'Smoking/Drinking'),
        ('RAGGING', 'Ragging'),
        ('FIGHTING', 'Fighting/Violence'),
        ('THEFT', 'Theft'),
        ('MISUSE_OF_FACILITIES', 'Misuse of Facilities'),
        ('CLEANLINESS_ISSUES', 'Cleanliness Issues'),
        ('UNAUTHORIZED_GUESTS', 'Unauthorized Guests'),
        ('MISUSE_OF_INTERNET', 'Misuse of Internet/WiFi'),
        ('OTHER', 'Other'),
    ]
    
    SEVERITY_LEVELS = [
        ('MINOR', 'Minor'),
        ('MODERATE', 'Moderate'),
        ('MAJOR', 'Major'),
        ('SEVERE', 'Severe'),
    ]
    
    ACTION_TYPES = [
        ('WARNING', 'Warning'),
        ('FINE', 'Fine'),
        ('ROOM_RESTRICTION', 'Room Restriction'),
        ('HOSTEL_RESTRICTION', 'Hostel Restriction'),
        ('COMMUNITY_SERVICE', 'Community Service'),
        ('SUSPENSION', 'Temporary Suspension'),
        ('EXPULSION', 'Expulsion from Hostel'),
        ('COUNSELING', 'Mandatory Counseling'),
        ('PARENTAL_MEETING', 'Parental Meeting'),
    ]
    
    resident = models.ForeignKey(HostelResident, on_delete=models.CASCADE, related_name='disciplinary_actions')
    
    # Incident details
    incident_date = models.DateField()
    incident_time = models.TimeField(blank=True, null=True)
    violation_type = models.CharField(max_length=30, choices=VIOLATION_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    
    # Description
    incident_description = models.TextField()
    location = models.CharField(max_length=200, blank=True, null=True)
    witnesses = models.TextField(blank=True, null=True)
    
    # Reporting
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_incidents')
    reported_date = models.DateField(auto_now_add=True)
    
    # Investigation
    investigated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='investigated_incidents')
    investigation_notes = models.TextField(blank=True, null=True)
    investigation_completed = models.BooleanField(default=False)
    
    # Action taken
    action_type = models.CharField(max_length=30, choices=ACTION_TYPES, blank=True, null=True)
    action_description = models.TextField(blank=True, null=True)
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    action_start_date = models.DateField(blank=True, null=True)
    action_end_date = models.DateField(blank=True, null=True)
    
    # Resolution
    action_taken_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='disciplinary_actions_taken')
    is_resolved = models.BooleanField(default=False)
    resolution_date = models.DateField(blank=True, null=True)
    
    # Parent notification
    parents_notified = models.BooleanField(default=False)
    notification_date = models.DateField(blank=True, null=True)
    
    # Repeat offense tracking
    is_repeat_offense = models.BooleanField(default=False)
    previous_offense_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-incident_date']
    
    def __str__(self):
        return f"{self.resident.admission.student.full_name} - {self.violation_type} - {self.incident_date}"

class HostelFeedback(UUIDModel, TimeStampedModel):
    """Student and parent feedback"""
    FEEDBACK_TYPES = [
        ('ROOM_FACILITIES', 'Room Facilities'),
        ('MESS_FOOD', 'Mess Food Quality'),
        ('CLEANLINESS', 'Cleanliness'),
        ('SECURITY', 'Security'),
        ('STAFF_BEHAVIOR', 'Staff Behavior'),
        ('WIFI_INTERNET', 'WiFi/Internet'),
        ('RECREATIONAL_FACILITIES', 'Recreational Facilities'),
        ('MEDICAL_FACILITIES', 'Medical Facilities'),
        ('GENERAL', 'General Feedback'),
        ('COMPLAINT', 'Complaint'),
        ('SUGGESTION', 'Suggestion'),
    ]
    
    FEEDBACK_STATUS = [
        ('OPEN', 'Open'),
        ('ACKNOWLEDGED', 'Acknowledged'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    ]
    
    RATING_CHOICES = [
        (1, 'Very Poor'),
        (2, 'Poor'),
        (3, 'Average'),
        (4, 'Good'),
        (5, 'Excellent'),
    ]
    
    # Feedback source
    resident = models.ForeignKey(HostelResident, on_delete=models.CASCADE, null=True, blank=True, related_name='feedback')
    parent_name = models.CharField(max_length=200, blank=True, null=True)
    parent_phone = PhoneNumberField(blank=True, null=True)
    parent_email = models.EmailField(blank=True, null=True)
    
    # Feedback details
    feedback_type = models.CharField(max_length=30, choices=FEEDBACK_TYPES)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    rating = models.IntegerField(choices=RATING_CHOICES, blank=True, null=True)
    
    # Attachments
    attachments = GenericRelation(Attachment)
    
    # Response
    status = models.CharField(max_length=20, choices=FEEDBACK_STATUS, default='OPEN')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_feedback')
    response = models.TextField(blank=True, null=True)
    response_date = models.DateField(blank=True, null=True)
    responded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='responded_feedback')
    
    # Follow-up
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(blank=True, null=True)
    
    # Anonymous feedback
    is_anonymous = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        if self.resident:
            return f"{self.resident.admission.student.full_name} - {self.feedback_type} - {self.subject}"
        else:
            return f"{self.parent_name} - {self.feedback_type} - {self.subject}"

class HostelReport(UUIDModel, TimeStampedModel):
    """Hostel reports and analytics"""
    REPORT_TYPES = [
        ('OCCUPANCY', 'Occupancy Report'),
        ('DAILY_ATTENDANCE', 'Daily Attendance'),
        ('MESS_CONSUMPTION', 'Mess Consumption'),
        ('VISITOR_LOG', 'Visitor Log'),
        ('DISCIPLINARY_SUMMARY', 'Disciplinary Summary'),
        ('MAINTENANCE_SUMMARY', 'Maintenance Summary'),
        ('FINANCIAL_SUMMARY', 'Financial Summary'),
        ('FEEDBACK_ANALYSIS', 'Feedback Analysis'),
        ('MONTHLY_SUMMARY', 'Monthly Summary'),
        ('ANNUAL_REPORT', 'Annual Report'),
    ]
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='hostel_reports')
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_hostel_reports')
    
    # Report parameters
    from_date = models.DateField()
    to_date = models.DateField()
    report_data = models.JSONField(default=dict)
    
    # Filters
    block_filter = models.ForeignKey(HostelBlock, on_delete=models.SET_NULL, null=True, blank=True)
    room_filter = models.ForeignKey(HostelRoom, on_delete=models.SET_NULL, null=True, blank=True)
    
    # File
    report_file = models.FileField(upload_to='hostel_reports/', blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.school.name} - {self.report_type} - {self.from_date} to {self.to_date}"
