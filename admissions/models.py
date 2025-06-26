from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericRelation
from core.models import TimeStampedModel, SchoolSettings, UUIDModel, AcademicYear, Attachment
from students.models import SchoolClass, Section
from hr.models import Employee
from decimal import Decimal
import uuid

class AcademicSession(TimeStampedModel):
    """Academic sessions for admissions"""
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='admissions_academic_sessions')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='admissions_academic_sessions')
    
    # Session details
    session_name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    # Application period
    application_start_date = models.DateField()
    application_end_date = models.DateField()
    late_application_end_date = models.DateField(blank=True, null=True)
    late_application_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Process dates
    entrance_test_date = models.DateField(blank=True, null=True)
    interview_start_date = models.DateField(blank=True, null=True)
    interview_end_date = models.DateField(blank=True, null=True)
    result_declaration_date = models.DateField(blank=True, null=True)
    admission_confirmation_deadline = models.DateField(blank=True, null=True)
    
    # Configuration
    is_online_application = models.BooleanField(default=True)
    is_entrance_test_required = models.BooleanField(default=False)
    is_interview_required = models.BooleanField(default=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_published = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-application_start_date']
    
    def __str__(self):
        return f"{self.school.name} - {self.session_name}"

class AdmissionCriteria(TimeStampedModel):
    """Admission criteria and eligibility"""
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, related_name='admission_criteria')
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='admission_criteria')
    
    # Eligibility criteria
    minimum_age_years = models.IntegerField(default=0)
    maximum_age_years = models.IntegerField(default=25)
    previous_class_required = models.CharField(max_length=100, blank=True, null=True)
    minimum_percentage = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Seat allocation
    total_seats = models.IntegerField()
    general_seats = models.IntegerField()
    reserved_seats = models.IntegerField(default=0)
    management_quota_seats = models.IntegerField(default=0)
    
    # Reservation categories
    sc_seats = models.IntegerField(default=0)
    st_seats = models.IntegerField(default=0)
    obc_seats = models.IntegerField(default=0)
    ews_seats = models.IntegerField(default=0)
    pwd_seats = models.IntegerField(default=0)
    
    # Fees
    application_fee = models.DecimalField(max_digits=10, decimal_places=2)
    admission_fee = models.DecimalField(max_digits=10, decimal_places=2)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Requirements
    required_documents = models.JSONField(default=list, help_text="List of required documents")
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['session', 'school_class']
    
    def __str__(self):
        return f"{self.session.session_name} - {self.school_class.name}"

class ApplicationForm(UUIDModel, TimeStampedModel):
    """Student admission applications"""
    APPLICATION_STATUS = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
        ('UNDER_REVIEW', 'Under Review'),
        ('DOCUMENT_VERIFICATION', 'Document Verification'),
        ('ENTRANCE_TEST_SCHEDULED', 'Entrance Test Scheduled'),
        ('ENTRANCE_TEST_COMPLETED', 'Entrance Test Completed'),
        ('INTERVIEW_SCHEDULED', 'Interview Scheduled'),
        ('INTERVIEW_COMPLETED', 'Interview Completed'),
        ('SELECTED', 'Selected'),
        ('WAITLISTED', 'Waitlisted'),
        ('REJECTED', 'Rejected'),
        ('ADMISSION_CONFIRMED', 'Admission Confirmed'),
        ('ADMISSION_CANCELLED', 'Admission Cancelled'),
    ]
    
    CATEGORY_CHOICES = [
        ('GENERAL', 'General'),
        ('SC', 'Scheduled Caste'),
        ('ST', 'Scheduled Tribe'),
        ('OBC', 'Other Backward Class'),
        ('EWS', 'Economically Weaker Section'),
        ('PWD', 'Person with Disability'),
    ]
    
    RELIGION_CHOICES = [
        ('HINDU', 'Hindu'),
        ('MUSLIM', 'Muslim'),
        ('CHRISTIAN', 'Christian'),
        ('SIKH', 'Sikh'),
        ('BUDDHIST', 'Buddhist'),
        ('JAIN', 'Jain'),
        ('PARSI', 'Parsi'),
        ('OTHER', 'Other'),
    ]
    
    # Application identification
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, related_name='applications')
    criteria = models.ForeignKey(AdmissionCriteria, on_delete=models.CASCADE, related_name='applications')
    application_number = models.CharField(max_length=50, unique=True)
    
    # Student details
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=[
        ('M', 'Male'), ('F', 'Female'), ('O', 'Other')
    ])
    blood_group = models.CharField(max_length=3, choices=[
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-'),
    ], blank=True, null=True)
    
    # Contact information
    email = models.EmailField()
    phone_number = PhoneNumberField()
    current_address = models.TextField()
    permanent_address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=50, default='India')
    
    # Personal details
    religion = models.CharField(max_length=20, choices=RELIGION_CHOICES, blank=True, null=True)
    caste = models.CharField(max_length=50, blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='GENERAL')
    nationality = models.CharField(max_length=50, default='Indian')
    mother_tongue = models.CharField(max_length=50, blank=True, null=True)
    
    # Government IDs
    aadhar_number = models.CharField(
        max_length=12, 
        blank=True, 
        null=True,
        validators=[RegexValidator(r'^\d{12}$', 'Aadhar number must be 12 digits')]
    )
    birth_certificate_number = models.CharField(max_length=50, blank=True, null=True)
    
    # Previous education
    previous_school_name = models.CharField(max_length=200, blank=True, null=True)
    previous_class = models.CharField(max_length=20, blank=True, null=True)
    previous_percentage = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    previous_board = models.CharField(max_length=100, blank=True, null=True)
    previous_year_passed = models.IntegerField(blank=True, null=True)
    transfer_certificate_number = models.CharField(max_length=50, blank=True, null=True)
    
    # Parent/Guardian 1 (Primary)
    parent1_name = models.CharField(max_length=200)
    parent1_relation = models.CharField(max_length=20, choices=[
        ('FATHER', 'Father'), ('MOTHER', 'Mother'), ('GUARDIAN', 'Guardian')
    ])
    parent1_occupation = models.CharField(max_length=100)
    parent1_income = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    parent1_phone = PhoneNumberField()
    parent1_email = models.EmailField(blank=True, null=True)
    parent1_qualification = models.CharField(max_length=100, blank=True, null=True)
    parent1_organization = models.CharField(max_length=200, blank=True, null=True)
    
    # Parent/Guardian 2 (Secondary)
    parent2_name = models.CharField(max_length=200, blank=True, null=True)
    parent2_relation = models.CharField(max_length=20, choices=[
        ('FATHER', 'Father'), ('MOTHER', 'Mother'), ('GUARDIAN', 'Guardian')
    ], blank=True, null=True)
    parent2_occupation = models.CharField(max_length=100, blank=True, null=True)
    parent2_income = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    parent2_phone = PhoneNumberField(blank=True, null=True)
    parent2_email = models.EmailField(blank=True, null=True)
    parent2_qualification = models.CharField(max_length=100, blank=True, null=True)
    parent2_organization = models.CharField(max_length=200, blank=True, null=True)
    
    # Emergency contact
    emergency_contact_name = models.CharField(max_length=200)
    emergency_contact_phone = PhoneNumberField()
    emergency_contact_relation = models.CharField(max_length=50)
    
    # Medical information
    medical_conditions = models.TextField(blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    medications = models.TextField(blank=True, null=True)
    special_needs = models.TextField(blank=True, null=True)
    
    # Preferences
    preferred_section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True)
    transport_required = models.BooleanField(default=False)
    hostel_required = models.BooleanField(default=False)
    
    # Application status
    status = models.CharField(max_length=30, choices=APPLICATION_STATUS, default='DRAFT')
    submitted_at = models.DateTimeField(blank=True, null=True)
    
    # Payment information
    application_fee_paid = models.BooleanField(default=False)
    payment_reference = models.CharField(max_length=100, blank=True, null=True)
    payment_date = models.DateField(blank=True, null=True)
    
    # Photo
    student_photo = models.ImageField(upload_to='admission_photos/', blank=True, null=True)
    
    # Documents
    attachments = GenericRelation(Attachment)
    
    # Processing
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_applications')
    review_notes = models.TextField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.application_number:
            # Generate application number
            year = self.session.academic_year.name[:4]
            count = ApplicationForm.objects.filter(session=self.session).count() + 1
            self.application_number = f"ADM{year}{count:06d}"
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['session', 'status']),
            models.Index(fields=['application_number']),
            models.Index(fields=['email']),
            models.Index(fields=['phone_number']),
        ]
    
    def __str__(self):
        return f"{self.application_number} - {self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        names = [self.first_name, self.middle_name, self.last_name]
        return ' '.join(filter(None, names))
    
    @property
    def age(self):
        today = timezone.now().date()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))

class DocumentSubmission(UUIDModel, TimeStampedModel):
    """Document submissions for applications"""
    DOCUMENT_TYPES = [
        ('BIRTH_CERTIFICATE', 'Birth Certificate'),
        ('AADHAR_CARD', 'Aadhar Card'),
        ('PREVIOUS_MARKSHEET', 'Previous Class Marksheet'),
        ('TRANSFER_CERTIFICATE', 'Transfer Certificate'),
        ('CHARACTER_CERTIFICATE', 'Character Certificate'),
        ('CASTE_CERTIFICATE', 'Caste Certificate'),
        ('INCOME_CERTIFICATE', 'Income Certificate'),
        ('DISABILITY_CERTIFICATE', 'Disability Certificate'),
        ('PASSPORT_PHOTO', 'Passport Size Photograph'),
        ('PARENT_ID_PROOF', 'Parent ID Proof'),
        ('ADDRESS_PROOF', 'Address Proof'),
        ('MEDICAL_CERTIFICATE', 'Medical Certificate'),
        ('VACCINATION_CARD', 'Vaccination Card'),
        ('BANK_PASSBOOK', 'Bank Passbook Copy'),
        ('OTHER', 'Other Document'),
    ]
    
    VERIFICATION_STATUS = [
        ('PENDING', 'Pending Verification'),
        ('VERIFIED', 'Verified'),
        ('REJECTED', 'Rejected'),
        ('RESUBMIT_REQUIRED', 'Resubmit Required'),
    ]
    
    application = models.ForeignKey(ApplicationForm, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES)
    document_name = models.CharField(max_length=200)
    file = models.FileField(upload_to='admission_documents/')
    file_size = models.BigIntegerField()
    
    # Verification
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='PENDING')
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_admission_documents')
    verified_at = models.DateTimeField(blank=True, null=True)
    verification_notes = models.TextField(blank=True, null=True)
    
    # Document details
    is_mandatory = models.BooleanField(default=True)
    expiry_date = models.DateField(blank=True, null=True)
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        unique_together = ['application', 'document_type']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.application.application_number} - {self.document_name}"

class EntranceTest(TimeStampedModel):
    """Entrance test configuration"""
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, related_name='entrance_tests')
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='entrance_tests')
    
    # Test details
    test_name = models.CharField(max_length=200)
    test_date = models.DateField()
    start_time = models.TimeField()
    duration_minutes = models.IntegerField()
    
    # Test configuration
    total_marks = models.IntegerField()
    passing_marks = models.IntegerField()
    
    # Subjects and weightage
    subjects = models.JSONField(default=list, help_text="List of subjects with marks distribution")
    
    # Instructions
    test_instructions = models.TextField()
    
    # Results
    results_declared = models.BooleanField(default=False)
    result_declaration_date = models.DateField(blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['session', 'school_class']
    
    def __str__(self):
        return f"{self.test_name} - {self.school_class.name}"

class EntranceTestResult(UUIDModel, TimeStampedModel):
    """Entrance test results"""
    application = models.OneToOneField(ApplicationForm, on_delete=models.CASCADE, related_name='entrance_test_result')
    entrance_test = models.ForeignKey(EntranceTest, on_delete=models.CASCADE, related_name='results')
    
    # Test attendance
    is_present = models.BooleanField(default=True)
    seat_number = models.CharField(max_length=20, blank=True, null=True)
    
    # Marks
    marks_obtained = models.FloatField(default=0)
    percentage = models.FloatField(default=0)
    
    # Subject-wise marks
    subject_wise_marks = models.JSONField(default=dict)
    
    # Ranking
    rank = models.IntegerField(blank=True, null=True)
    
    # Status
    is_qualified = models.BooleanField(default=False)
    
    # Answer sheet
    answer_sheet = models.FileField(upload_to='entrance_test_sheets/', blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if self.entrance_test.total_marks > 0:
            self.percentage = (self.marks_obtained / self.entrance_test.total_marks) * 100
        self.is_qualified = self.marks_obtained >= self.entrance_test.passing_marks
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-marks_obtained']
    
    def __str__(self):
        return f"{self.application.application_number} - {self.marks_obtained}/{self.entrance_test.total_marks}"

class Interview(TimeStampedModel):
    """Interview configuration and scheduling"""
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, related_name='interviews')
    
    # Interview details
    interview_name = models.CharField(max_length=200)
    interview_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    # Panel
    interview_panel = models.ManyToManyField(Employee, related_name='interview_panels')
    
    # Configuration
    duration_per_candidate_minutes = models.IntegerField(default=15)
    max_marks = models.IntegerField(default=100)
    passing_marks = models.IntegerField(default=60)
    
    # Evaluation criteria
    evaluation_criteria = models.JSONField(default=list, help_text="List of evaluation parameters")
    
    # Instructions
    instructions = models.TextField(blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.interview_name} - {self.interview_date}"

class InterviewSchedule(UUIDModel, TimeStampedModel):
    """Individual interview schedules"""
    application = models.OneToOneField(ApplicationForm, on_delete=models.CASCADE, related_name='interview_schedule')
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE, related_name='schedules')
    
    # Schedule details
    interview_time = models.TimeField()
    room_number = models.CharField(max_length=50, blank=True, null=True)
    
    # Status
    is_completed = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    cancellation_reason = models.TextField(blank=True, null=True)
    
    # Notification
    email_sent = models.BooleanField(default=False)
    sms_sent = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['interview_time']
    
    def __str__(self):
        return f"{self.application.application_number} - {self.interview.interview_name} - {self.interview_time}"

class InterviewEvaluation(UUIDModel, TimeStampedModel):
    """Interview evaluation and scoring"""
    interview_schedule = models.OneToOneField(InterviewSchedule, on_delete=models.CASCADE, related_name='evaluation')
    evaluated_by = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='interview_evaluations')
    
    # Scores
    communication_score = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(25)])
    confidence_score = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(25)])
    knowledge_score = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(25)])
    overall_impression = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(25)])
    
    # Total
    total_score = models.IntegerField(default=0, editable=False)
    percentage = models.FloatField(default=0, editable=False)
    
    # Feedback
    strengths = models.TextField(blank=True, null=True)
    areas_for_improvement = models.TextField(blank=True, null=True)
    recommendation = models.CharField(max_length=25, choices=[
        ('STRONGLY_RECOMMEND', 'Strongly Recommend'),
        ('RECOMMEND', 'Recommend'),
        ('NEUTRAL', 'Neutral'),
        ('NOT_RECOMMEND', 'Not Recommend'),
        ('STRONGLY_NOT_RECOMMEND', 'Strongly Not Recommend'),
    ])
    
    # Overall comments
    comments = models.TextField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        self.total_score = (
            self.communication_score + self.confidence_score + 
            self.knowledge_score + self.overall_impression
        )
        self.percentage = (self.total_score / 100) * 100
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.interview_schedule.application.application_number} - {self.total_score}/100"

class AdmissionResult(UUIDModel, TimeStampedModel):
    """Final admission results"""
    RESULT_STATUS = [
        ('SELECTED', 'Selected'),
        ('WAITLISTED', 'Waitlisted'),
        ('REJECTED', 'Rejected'),
    ]
    
    application = models.OneToOneField(ApplicationForm, on_delete=models.CASCADE, related_name='admission_result')
    
    # Result details
    result_status = models.CharField(max_length=20, choices=RESULT_STATUS)
    merit_rank = models.IntegerField(blank=True, null=True)
    waitlist_number = models.IntegerField(blank=True, null=True)
    
    # Allocation
    allocated_class = models.ForeignKey(SchoolClass, on_delete=models.SET_NULL, null=True, blank=True)
    allocated_section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Scores summary
    entrance_test_score = models.FloatField(blank=True, null=True)
    interview_score = models.FloatField(blank=True, null=True)
    total_score = models.FloatField(default=0)
    
    # Result processing
    declared_date = models.DateField()
    declared_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='declared_admission_results')
    
    # Admission confirmation
    admission_confirmed = models.BooleanField(default=False)
    confirmation_date = models.DateField(blank=True, null=True)
    confirmation_deadline = models.DateField()
    
    # Fee payment
    admission_fee_paid = models.BooleanField(default=False)
    fee_payment_deadline = models.DateField()
    
    # Comments
    remarks = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['merit_rank']
    
    def __str__(self):
        return f"{self.application.application_number} - {self.result_status}"

class AdmissionReport(UUIDModel, TimeStampedModel):
    """Admission process reports and analytics"""
    REPORT_TYPES = [
        ('APPLICATION_SUMMARY', 'Application Summary'),
        ('CLASS_WISE_APPLICATIONS', 'Class-wise Applications'),
        ('CATEGORY_WISE_ANALYSIS', 'Category-wise Analysis'),
        ('ENTRANCE_TEST_ANALYSIS', 'Entrance Test Analysis'),
        ('INTERVIEW_ANALYSIS', 'Interview Analysis'),
        ('ADMISSION_STATISTICS', 'Admission Statistics'),
        ('REJECTION_ANALYSIS', 'Rejection Analysis'),
        ('WAITLIST_ANALYSIS', 'Waitlist Analysis'),
        ('REVENUE_ANALYSIS', 'Revenue Analysis'),
        ('DEMOGRAPHIC_ANALYSIS', 'Demographic Analysis'),
    ]
    
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, related_name='reports')
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_admission_reports')
    
    # Report data
    report_data = models.JSONField(default=dict)
    
    # Filters
    class_filter = models.ForeignKey(SchoolClass, on_delete=models.SET_NULL, null=True, blank=True)
    
    # File
    report_file = models.FileField(upload_to='admission_reports/', blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.session.session_name} - {self.report_type}" 