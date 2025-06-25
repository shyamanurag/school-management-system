from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericRelation
from core.models import TimeStampedModel, School, UUIDModel, AcademicYear, Campus, Attachment
import uuid

class Category(TimeStampedModel):
    """Student categories (General, OBC, SC, ST, etc.) - Indian Education System"""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='student_categories')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    fee_discount_percentage = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    is_reserved_category = models.BooleanField(default=False)
    reservation_percentage = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Indian Education System specific
    is_rte_category = models.BooleanField(default=False, help_text="Right to Education quota")
    government_scholarship_eligible = models.BooleanField(default=False)
    caste_verification_required = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['school', 'code']
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return f"{self.school.name} - {self.name}"

class SchoolClass(TimeStampedModel):
    """Enhanced Class model for Indian education system"""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='classes')
    name = models.CharField(max_length=50)  # "Class 1", "Class 10", "Pre-KG"
    code = models.CharField(max_length=10)  # "1", "10", "PKG"
    
    # Indian Education System
    is_primary = models.BooleanField(default=False)  # Classes 1-5
    is_upper_primary = models.BooleanField(default=False)  # Classes 6-8
    is_secondary = models.BooleanField(default=False)  # Classes 9-10
    is_higher_secondary = models.BooleanField(default=False)  # Classes 11-12
    is_pre_primary = models.BooleanField(default=False)  # Pre-KG, LKG, UKG
    
    # Board affiliation
    board_type = models.CharField(max_length=20, choices=[
        ('CBSE', 'Central Board of Secondary Education'),
        ('ICSE', 'Indian Certificate of Secondary Education'),
        ('STATE', 'State Board'),
        ('IB', 'International Baccalaureate'),
        ('CAMBRIDGE', 'Cambridge International'),
    ], default='CBSE')
    
    # Academic configuration
    promotion_criteria = models.TextField(blank=True, null=True)
    minimum_attendance_required = models.FloatField(default=75.0)
    
    # Capacity and fees
    maximum_students = models.IntegerField(default=40)
    class_teacher_required = models.BooleanField(default=True)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['school', 'code']
        verbose_name_plural = 'Classes'
        ordering = ['code']
    
    def __str__(self):
        return f"{self.school.name} - {self.name}"

class Section(TimeStampedModel):
    """Class sections"""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='sections')
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='sections')
    name = models.CharField(max_length=10)  # "A", "B", "C"
    
    # Capacity
    maximum_students = models.IntegerField(default=40)
    current_strength = models.IntegerField(default=0)
    
    # Staff assignment
    class_teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_sections')
    
    # Academic year
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='sections')
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['school_class', 'name', 'academic_year']
        ordering = ['school_class', 'name']
    
    def __str__(self):
        return f"{self.school_class.name} - {self.name}"

class Student(UUIDModel, TimeStampedModel):
    """Comprehensive student model for Indian Education System"""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]
    
    TRANSPORT_CHOICES = [
        ('BUS', 'School Bus'),
        ('PRIVATE', 'Private Vehicle'),
        ('WALKING', 'Walking'),
        ('BICYCLE', 'Bicycle'),
        ('PUBLIC', 'Public Transport'),
        ('AUTO', 'Auto Rickshaw'),
    ]
    
    ADMISSION_TYPE_CHOICES = [
        ('REGULAR', 'Regular Admission'),
        ('RTE', 'RTE Quota'),
        ('MANAGEMENT', 'Management Quota'),
        ('SPORTS', 'Sports Quota'),
        ('NRI', 'NRI Quota'),
        ('STAFF_WARD', 'Staff Ward'),
        ('TRANSFER', 'Transfer Admission'),
    ]
    
    # Basic Information
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='students')
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='student_profile')
    
    # Identity
    admission_number = models.CharField(max_length=50, unique=True)
    roll_number = models.CharField(max_length=20, blank=True, null=True)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    place_of_birth = models.CharField(max_length=200, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True, null=True)
    
    # Academic Information
    admission_date = models.DateField()
    admission_type = models.CharField(max_length=20, choices=ADMISSION_TYPE_CHOICES, default='REGULAR')
    current_class = models.ForeignKey(SchoolClass, on_delete=models.SET_NULL, null=True, blank=True, related_name='current_students')
    current_section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True, related_name='current_students')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='students')
    
    # Category and Background
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    religion = models.CharField(max_length=50, blank=True, null=True)
    caste = models.CharField(max_length=50, blank=True, null=True)
    sub_caste = models.CharField(max_length=50, blank=True, null=True)
    nationality = models.CharField(max_length=50, default='Indian')
    mother_tongue = models.CharField(max_length=50, blank=True, null=True)
    
    # Indian Government IDs and Numbers
    aadhar_number = models.CharField(
        max_length=12, 
        blank=True, 
        null=True,
        validators=[RegexValidator(r'^\d{12}$', 'Aadhar number must be 12 digits')]
    )
    pen_number = models.CharField(max_length=20, blank=True, null=True, help_text="Permanent Education Number")
    samagra_id = models.CharField(max_length=15, blank=True, null=True, help_text="Samagra ID (MP)")
    udise_number = models.CharField(max_length=20, blank=True, null=True, help_text="UDISE Student ID")
    birth_certificate_number = models.CharField(max_length=50, blank=True, null=True)
    
    # Contact Information
    email = models.EmailField(blank=True, null=True)
    phone_number = PhoneNumberField(blank=True, null=True)
    
    # Address Information
    current_address = models.TextField()
    permanent_address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=50, default='India')
    
    # Parent/Guardian Information (Enhanced for Indian system)
    father_name = models.CharField(max_length=200)
    father_occupation = models.CharField(max_length=100, blank=True, null=True)
    father_designation = models.CharField(max_length=100, blank=True, null=True)
    father_office_address = models.TextField(blank=True, null=True)
    father_phone = PhoneNumberField(blank=True, null=True)
    father_email = models.EmailField(blank=True, null=True)
    father_qualification = models.CharField(max_length=100, blank=True, null=True)
    father_annual_income = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    father_aadhar = models.CharField(max_length=12, blank=True, null=True)
    father_pan = models.CharField(max_length=10, blank=True, null=True)
    
    mother_name = models.CharField(max_length=200)
    mother_occupation = models.CharField(max_length=100, blank=True, null=True)
    mother_designation = models.CharField(max_length=100, blank=True, null=True)
    mother_office_address = models.TextField(blank=True, null=True)
    mother_phone = PhoneNumberField(blank=True, null=True)
    mother_email = models.EmailField(blank=True, null=True)
    mother_qualification = models.CharField(max_length=100, blank=True, null=True)
    mother_annual_income = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    mother_aadhar = models.CharField(max_length=12, blank=True, null=True)
    mother_pan = models.CharField(max_length=10, blank=True, null=True)
    
    guardian_name = models.CharField(max_length=200, blank=True, null=True)
    guardian_relation = models.CharField(max_length=50, blank=True, null=True)
    guardian_phone = PhoneNumberField(blank=True, null=True)
    guardian_email = models.EmailField(blank=True, null=True)
    guardian_address = models.TextField(blank=True, null=True)
    guardian_aadhar = models.CharField(max_length=12, blank=True, null=True)
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=200)
    emergency_contact_phone = PhoneNumberField()
    emergency_contact_relation = models.CharField(max_length=50)
    emergency_contact_address = models.TextField(blank=True, null=True)
    
    # Medical Information
    height = models.FloatField(blank=True, null=True, help_text="Height in cm")
    weight = models.FloatField(blank=True, null=True, help_text="Weight in kg")
    medical_conditions = models.TextField(blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    medications = models.TextField(blank=True, null=True)
    special_needs = models.TextField(blank=True, null=True)
    vaccination_status = models.TextField(blank=True, null=True)
    
    # Academic History
    previous_school_name = models.CharField(max_length=200, blank=True, null=True)
    previous_school_address = models.TextField(blank=True, null=True)
    previous_school_board = models.CharField(max_length=50, blank=True, null=True)
    previous_class = models.CharField(max_length=50, blank=True, null=True)
    previous_school_marks = models.TextField(blank=True, null=True)
    tc_number = models.CharField(max_length=50, blank=True, null=True)  # Transfer Certificate
    tc_date = models.DateField(blank=True, null=True)
    tc_issued_by = models.CharField(max_length=200, blank=True, null=True)
    
    # Financial Information
    family_annual_income = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    bpl_status = models.BooleanField(default=False, help_text="Below Poverty Line")
    bpl_card_number = models.CharField(max_length=20, blank=True, null=True)
    is_minority = models.BooleanField(default=False)
    rte_student = models.BooleanField(default=False, help_text="RTE 25% quota student")
    scholarship_eligible = models.BooleanField(default=False)
    
    # Transport and Hostel
    transport_mode = models.CharField(max_length=20, choices=TRANSPORT_CHOICES, default='WALKING')
    bus_route = models.CharField(max_length=100, blank=True, null=True)
    pickup_point = models.CharField(max_length=200, blank=True, null=True)
    pickup_time = models.TimeField(blank=True, null=True)
    drop_time = models.TimeField(blank=True, null=True)
    bus_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    is_hosteller = models.BooleanField(default=False)
    hostel_room_number = models.CharField(max_length=20, blank=True, null=True)
    hostel_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Bank Details (for scholarships, fee refunds)
    bank_account_number = models.CharField(max_length=30, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    bank_branch = models.CharField(max_length=100, blank=True, null=True)
    ifsc_code = models.CharField(max_length=11, blank=True, null=True)
    
    # Files and Photos
    profile_photo = models.ImageField(upload_to='student_photos/', blank=True, null=True)
    attachments = GenericRelation(Attachment)
    
    # Status and Flags
    is_active = models.BooleanField(default=True)
    is_alumni = models.BooleanField(default=False)
    is_promoted = models.BooleanField(default=False)
    is_transferred = models.BooleanField(default=False)
    is_detained = models.BooleanField(default=False)
    transfer_date = models.DateField(blank=True, null=True)
    graduation_date = models.DateField(blank=True, null=True)
    
    # Additional Information
    hobbies = models.TextField(blank=True, null=True)
    special_talents = models.TextField(blank=True, null=True)
    extracurricular_activities = models.TextField(blank=True, null=True)
    achievements = models.TextField(blank=True, null=True)
    disciplinary_actions = models.TextField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    
    # House system (common in Indian schools)
    house = models.CharField(max_length=50, blank=True, null=True, help_text="House name (Red, Blue, Green, Yellow)")
    
    class Meta:
        ordering = ['first_name', 'last_name']
        indexes = [
            models.Index(fields=['school', 'admission_number']),
            models.Index(fields=['current_class', 'current_section']),
            models.Index(fields=['aadhar_number']),
            models.Index(fields=['pen_number']),
            models.Index(fields=['is_active']),
            models.Index(fields=['rte_student']),
            models.Index(fields=['admission_type']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.admission_number})"
    
    @property
    def full_name(self):
        names = [self.first_name, self.middle_name, self.last_name]
        return ' '.join(filter(None, names))
    
    @property
    def age(self):
        today = timezone.now().date()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
    
    @property
    def current_class_section(self):
        if self.current_class and self.current_section:
            return f"{self.current_class.name} - {self.current_section.name}"
        return None

class StudentPromotion(TimeStampedModel):
    """Track student promotions between classes"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='promotions')
    from_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='promoted_from')
    from_section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='promoted_from')
    to_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='promoted_to')
    to_section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='promoted_to')
    academic_year_from = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='promotions_from')
    academic_year_to = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='promotions_to')
    promotion_date = models.DateField()
    result_status = models.CharField(max_length=20, choices=[
        ('PROMOTED', 'Promoted'),
        ('DETAINED', 'Detained'),
        ('PASSED', 'Passed'),
        ('FAILED', 'Failed'),
    ])
    remarks = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-promotion_date']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.from_class} to {self.to_class}"

class StudentDocument(UUIDModel, TimeStampedModel):
    """Student document management for Indian education compliance"""
    DOCUMENT_TYPES = [
        ('BIRTH_CERTIFICATE', 'Birth Certificate'),
        ('AADHAR_CARD', 'Aadhar Card'),
        ('PAN_CARD', 'PAN Card'),
        ('PASSPORT', 'Passport'),
        ('TRANSFER_CERTIFICATE', 'Transfer Certificate'),
        ('MARK_SHEET', 'Mark Sheet'),
        ('MIGRATION_CERTIFICATE', 'Migration Certificate'),
        ('CASTE_CERTIFICATE', 'Caste Certificate'),
        ('INCOME_CERTIFICATE', 'Income Certificate'),
        ('DOMICILE_CERTIFICATE', 'Domicile Certificate'),
        ('BPL_CERTIFICATE', 'BPL Certificate'),
        ('DISABILITY_CERTIFICATE', 'Disability Certificate'),
        ('MINORITY_CERTIFICATE', 'Minority Certificate'),
        ('MEDICAL_CERTIFICATE', 'Medical Certificate'),
        ('VACCINATION_CARD', 'Vaccination Card'),
        ('PHOTO', 'Photograph'),
        ('FATHER_AADHAR', 'Father\'s Aadhar'),
        ('MOTHER_AADHAR', 'Mother\'s Aadhar'),
        ('PARENT_INCOME_PROOF', 'Parent Income Proof'),
        ('BANK_PASSBOOK', 'Bank Passbook Copy'),
        ('OTHER', 'Other'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES)
    document_name = models.CharField(max_length=200)
    file = models.FileField(upload_to='student_documents/')
    file_size = models.BigIntegerField()
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_documents')
    verified_at = models.DateTimeField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    is_mandatory = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.document_name}"

class StudentAttendance(TimeStampedModel):
    """Daily attendance tracking"""
    ATTENDANCE_STATUS = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LATE', 'Late'),
        ('HALF_DAY', 'Half Day'),
        ('SICK', 'Sick Leave'),
        ('EXCUSED', 'Excused Absence'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=15, choices=ATTENDANCE_STATUS)
    check_in_time = models.TimeField(blank=True, null=True)
    check_out_time = models.TimeField(blank=True, null=True)
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    remarks = models.TextField(blank=True, null=True)
    parent_notified = models.BooleanField(default=False)
    notification_sent_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        unique_together = ['student', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['student', 'date']),
            models.Index(fields=['date', 'status']),
        ]
    
    def __str__(self):
        return f"{self.student.full_name} - {self.date} - {self.status}"

class StudentParent(TimeStampedModel):
    """Parent-Student relationship mapping"""
    RELATIONSHIP_TYPES = [
        ('FATHER', 'Father'),
        ('MOTHER', 'Mother'),
        ('GUARDIAN', 'Guardian'),
        ('STEP_FATHER', 'Step Father'),
        ('STEP_MOTHER', 'Step Mother'),
        ('GRANDFATHER', 'Grandfather'),
        ('GRANDMOTHER', 'Grandmother'),
        ('UNCLE', 'Uncle'),
        ('AUNT', 'Aunt'),
        ('OTHER', 'Other'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='parent_relationships')
    parent_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='child_relationships')
    relationship_type = models.CharField(max_length=20, choices=RELATIONSHIP_TYPES)
    is_primary_contact = models.BooleanField(default=False)
    is_emergency_contact = models.BooleanField(default=False)
    can_pickup = models.BooleanField(default=True)
    receive_sms = models.BooleanField(default=True)
    receive_email = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['student', 'parent_user']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.parent_user.get_full_name()} ({self.relationship_type})"

# Create your models here.
