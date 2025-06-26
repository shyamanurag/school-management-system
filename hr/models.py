from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericRelation
from core.models import TimeStampedModel, SchoolSettings, UUIDModel, AcademicYear, Attachment
from decimal import Decimal
import uuid

class Department(TimeStampedModel):
    """School departments"""
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='departments')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    
    # Hierarchy
    parent_department = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='sub_departments')
    
    # Management
    head_of_department = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='headed_departments')
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['school', 'code']
    
    def __str__(self):
        return f"{self.school.name} - {self.name}"

class Designation(TimeStampedModel):
    """Employee designations/positions"""
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='designations')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='designations')
    
    title = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    
    # Hierarchy
    level = models.IntegerField(default=1, help_text="Hierarchy level (1=highest)")
    reports_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates')
    
    # Salary configuration
    min_salary = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    max_salary = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    
    # Job requirements
    minimum_qualification = models.CharField(max_length=200, blank=True, null=True)
    experience_required_years = models.IntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['school', 'code']
    
    def __str__(self):
        return f"{self.school.name} - {self.title}"

class Employee(UUIDModel, TimeStampedModel):
    """Employee master - Teachers and Staff"""
    EMPLOYEE_TYPES = [
        ('TEACHING', 'Teaching Staff'),
        ('NON_TEACHING', 'Non-Teaching Staff'),
        ('ADMINISTRATIVE', 'Administrative Staff'),
        ('SUPPORT', 'Support Staff'),
        ('CONTRACTUAL', 'Contractual'),
        ('TEMPORARY', 'Temporary'),
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
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    MARITAL_STATUS = [
        ('SINGLE', 'Single'),
        ('MARRIED', 'Married'),
        ('DIVORCED', 'Divorced'),
        ('WIDOWED', 'Widowed'),
    ]
    
    # Basic Information
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='employees')
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='employee_profile')
    
    # Employee Identity
    employee_id = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    place_of_birth = models.CharField(max_length=200, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    blood_group = models.CharField(max_length=3, choices=[
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-'),
    ], blank=True, null=True)
    
    # Contact Information
    email = models.EmailField(unique=True)
    phone_number = PhoneNumberField()
    alternate_phone = PhoneNumberField(blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=200)
    emergency_contact_phone = PhoneNumberField()
    emergency_contact_relation = models.CharField(max_length=50)
    
    # Address
    current_address = models.TextField()
    permanent_address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=50, default='India')
    
    # Personal Details
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS, default='SINGLE')
    spouse_name = models.CharField(max_length=200, blank=True, null=True)
    number_of_children = models.IntegerField(default=0)
    religion = models.CharField(max_length=50, blank=True, null=True)
    caste = models.CharField(max_length=50, blank=True, null=True)
    nationality = models.CharField(max_length=50, default='Indian')
    mother_tongue = models.CharField(max_length=50, blank=True, null=True)
    
    # Government IDs
    aadhar_number = models.CharField(
        max_length=12, 
        blank=True, 
        null=True,
        validators=[RegexValidator(r'^\d{12}$', 'Aadhar number must be 12 digits')]
    )
    pan_number = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        validators=[RegexValidator(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', 'Invalid PAN format')]
    )
    passport_number = models.CharField(max_length=20, blank=True, null=True)
    driving_license = models.CharField(max_length=20, blank=True, null=True)
    voter_id = models.CharField(max_length=20, blank=True, null=True)
    
    # Employment Details
    employee_type = models.CharField(max_length=20, choices=EMPLOYEE_TYPES)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='employees')
    designation = models.ForeignKey(Designation, on_delete=models.CASCADE, related_name='employees')
    
    # Employment dates
    date_of_joining = models.DateField()
    probation_period_months = models.IntegerField(default=6)
    probation_end_date = models.DateField(blank=True, null=True)
    confirmation_date = models.DateField(blank=True, null=True)
    
    # Status
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS, default='ACTIVE')
    last_working_date = models.DateField(blank=True, null=True)
    reason_for_leaving = models.TextField(blank=True, null=True)
    
    # Reporting
    reporting_manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates')
    
    # Qualifications
    highest_qualification = models.CharField(max_length=100, blank=True, null=True)
    specialization = models.CharField(max_length=100, blank=True, null=True)
    total_experience_years = models.FloatField(default=0)
    teaching_experience_years = models.FloatField(default=0, blank=True, null=True)
    
    # Teaching specific (for teaching staff)
    subjects_taught = models.TextField(blank=True, null=True, help_text="Comma-separated list of subjects")
    classes_taught = models.TextField(blank=True, null=True, help_text="Comma-separated list of classes")
    
    # Files
    profile_photo = models.ImageField(upload_to='employee_photos/', blank=True, null=True)
    resume = models.FileField(upload_to='employee_resumes/', blank=True, null=True)
    attachments = GenericRelation(Attachment)
    
    # Timestamps
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['first_name', 'last_name']
        indexes = [
            models.Index(fields=['school', 'employee_id']),
            models.Index(fields=['department', 'designation']),
            models.Index(fields=['employment_status']),
            models.Index(fields=['aadhar_number']),
            models.Index(fields=['pan_number']),
        ]
    
    def __str__(self):
        return f"{self.employee_id} - {self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        names = [self.first_name, self.middle_name, self.last_name]
        return ' '.join(filter(None, names))
    
    @property
    def age(self):
        today = timezone.now().date()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))

class EmployeeDocument(UUIDModel, TimeStampedModel):
    """Employee document management"""
    DOCUMENT_TYPES = [
        ('RESUME', 'Resume/CV'),
        ('AADHAR_CARD', 'Aadhar Card'),
        ('PAN_CARD', 'PAN Card'),
        ('PASSPORT', 'Passport'),
        ('DRIVING_LICENSE', 'Driving License'),
        ('VOTER_ID', 'Voter ID'),
        ('DEGREE_CERTIFICATE', 'Degree Certificate'),
        ('MARK_SHEET', 'Mark Sheet'),
        ('EXPERIENCE_CERTIFICATE', 'Experience Certificate'),
        ('SALARY_CERTIFICATE', 'Salary Certificate'),
        ('CASTE_CERTIFICATE', 'Caste Certificate'),
        ('MEDICAL_CERTIFICATE', 'Medical Certificate'),
        ('POLICE_VERIFICATION', 'Police Verification'),
        ('BANK_PASSBOOK', 'Bank Passbook'),
        ('APPOINTMENT_LETTER', 'Appointment Letter'),
        ('CONTRACT', 'Contract'),
        ('INCREMENT_LETTER', 'Increment Letter'),
        ('PROMOTION_LETTER', 'Promotion Letter'),
        ('WARNING_LETTER', 'Warning Letter'),
        ('APPRECIATION_LETTER', 'Appreciation Letter'),
        ('RESIGNATION_LETTER', 'Resignation Letter'),
        ('TERMINATION_LETTER', 'Termination Letter'),
        ('PHOTO', 'Photograph'),
        ('OTHER', 'Other'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES)
    document_name = models.CharField(max_length=200)
    file = models.FileField(upload_to='employee_documents/')
    file_size = models.BigIntegerField()
    
    # Verification
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_employee_documents')
    verified_at = models.DateTimeField(blank=True, null=True)
    
    # Document details
    expiry_date = models.DateField(blank=True, null=True)
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.document_name}"

class SalaryStructure(TimeStampedModel):
    """Salary structure templates"""
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='salary_structures')
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    
    # Applicability
    applicable_designations = models.ManyToManyField(Designation, blank=True, related_name='salary_structures')
    applicable_employee_types = models.JSONField(default=list, help_text="List of employee types")
    
    # Basic components
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)
    hra_percentage = models.FloatField(default=40.0, help_text="House Rent Allowance percentage")
    da_percentage = models.FloatField(default=0.0, help_text="Dearness Allowance percentage")
    
    # Allowances
    transport_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    medical_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    education_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    special_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Deductions
    pf_applicable = models.BooleanField(default=True, help_text="Provident Fund applicable")
    pf_percentage = models.FloatField(default=12.0)
    esi_applicable = models.BooleanField(default=False, help_text="ESI applicable")
    esi_percentage = models.FloatField(default=0.75)
    tds_applicable = models.BooleanField(default=True, help_text="TDS applicable")
    
    # Professional tax (state-wise)
    professional_tax_applicable = models.BooleanField(default=True)
    professional_tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=200)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['school', 'code']
    
    def __str__(self):
        return f"{self.school.name} - {self.name}"

class EmployeeSalary(UUIDModel, TimeStampedModel):
    """Individual employee salary configuration"""
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='salary_config')
    salary_structure = models.ForeignKey(SalaryStructure, on_delete=models.CASCADE, related_name='employee_salaries')
    
    # Override amounts (if different from structure)
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)
    hra_amount = models.DecimalField(max_digits=10, decimal_places=2)
    da_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Allowances
    transport_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    medical_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    education_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    special_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Calculated fields
    gross_salary = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    
    # Bank details
    bank_name = models.CharField(max_length=100)
    bank_branch = models.CharField(max_length=100)
    account_number = models.CharField(max_length=30)
    ifsc_code = models.CharField(max_length=11)
    account_holder_name = models.CharField(max_length=200)
    
    # Statutory details
    pf_number = models.CharField(max_length=50, blank=True, null=True)
    uan_number = models.CharField(max_length=12, blank=True, null=True, help_text="Universal Account Number")
    esi_number = models.CharField(max_length=20, blank=True, null=True)
    
    # Effective date
    effective_from = models.DateField()
    effective_to = models.DateField(blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        # Calculate gross salary
        self.gross_salary = (
            self.basic_salary + self.hra_amount + self.da_amount +
            self.transport_allowance + self.medical_allowance + 
            self.education_allowance + self.special_allowance + self.other_allowances
        )
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.employee.full_name} - ₹{self.gross_salary}"

class PayrollMonth(TimeStampedModel):
    """Payroll processing months"""
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='payroll_months')
    month = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    year = models.IntegerField()
    
    # Processing status
    is_processed = models.BooleanField(default=False)
    processed_date = models.DateField(blank=True, null=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_payrolls')
    
    # Lock status
    is_locked = models.BooleanField(default=False)
    locked_date = models.DateField(blank=True, null=True)
    locked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='locked_payrolls')
    
    # Summary
    total_employees = models.IntegerField(default=0)
    total_gross_salary = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_net_salary = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    class Meta:
        unique_together = ['school', 'month', 'year']
    
    def __str__(self):
        return f"{self.school.name} - {self.month:02d}/{self.year}"

class Payslip(UUIDModel, TimeStampedModel):
    """Employee payslips"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payslips')
    payroll_month = models.ForeignKey(PayrollMonth, on_delete=models.CASCADE, related_name='payslips')
    
    # Salary components (for the month)
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)
    hra_amount = models.DecimalField(max_digits=10, decimal_places=2)
    da_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transport_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    medical_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    education_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    special_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Additional earnings (for the month)
    overtime_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bonus_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    incentive_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    arrears_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Attendance
    working_days = models.IntegerField()
    present_days = models.IntegerField()
    paid_leaves = models.IntegerField(default=0)
    unpaid_leaves = models.IntegerField(default=0)
    
    # Gross salary
    gross_earnings = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    
    # Statutory deductions
    pf_employee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pf_employer = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    esi_employee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    esi_employer = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tds_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    professional_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Other deductions
    loan_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    advance_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Total deductions
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    
    # Net salary
    net_salary = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    
    # Payment details
    payment_date = models.DateField(blank=True, null=True)
    payment_mode = models.CharField(max_length=20, choices=[
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('CASH', 'Cash'),
        ('CHEQUE', 'Cheque'),
    ], default='BANK_TRANSFER')
    payment_reference = models.CharField(max_length=100, blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    
    # Generated files
    payslip_pdf = models.FileField(upload_to='payslips/', blank=True, null=True)
    
    def save(self, *args, **kwargs):
        # Calculate totals
        self.gross_earnings = (
            self.basic_salary + self.hra_amount + self.da_amount +
            self.transport_allowance + self.medical_allowance + 
            self.education_allowance + self.special_allowance + self.other_allowances +
            self.overtime_amount + self.bonus_amount + self.incentive_amount + self.arrears_amount
        )
        
        self.total_deductions = (
            self.pf_employee + self.esi_employee + self.tds_amount + self.professional_tax +
            self.loan_deduction + self.advance_deduction + self.other_deductions
        )
        
        self.net_salary = self.gross_earnings - self.total_deductions
        
        super().save(*args, **kwargs)
    
    class Meta:
        unique_together = ['employee', 'payroll_month']
        ordering = ['-payroll_month__year', '-payroll_month__month']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.payroll_month}"

class LeaveType(TimeStampedModel):
    """Leave types configuration"""
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='leave_types')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    
    # Leave configuration
    is_paid = models.BooleanField(default=True)
    annual_allocation = models.IntegerField(help_text="Days allocated per year")
    max_consecutive_days = models.IntegerField(blank=True, null=True)
    min_advance_notice_days = models.IntegerField(default=1)
    
    # Carry forward
    can_carry_forward = models.BooleanField(default=False)
    max_carry_forward_days = models.IntegerField(default=0)
    
    # Applicable to
    applicable_to_teaching = models.BooleanField(default=True)
    applicable_to_non_teaching = models.BooleanField(default=True)
    
    # Documentation required
    medical_certificate_required = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['school', 'code']
    
    def __str__(self):
        return f"{self.school.name} - {self.name}"

class EmployeeLeaveBalance(TimeStampedModel):
    """Employee leave balance tracking"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_balances')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, related_name='employee_balances')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='leave_balances')
    
    # Balance
    allocated_days = models.IntegerField()
    used_days = models.IntegerField(default=0)
    carried_forward_days = models.IntegerField(default=0)
    available_days = models.IntegerField(editable=False)
    
    def save(self, *args, **kwargs):
        self.available_days = self.allocated_days + self.carried_forward_days - self.used_days
        super().save(*args, **kwargs)
    
    class Meta:
        unique_together = ['employee', 'leave_type', 'academic_year']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.leave_type.name} - {self.available_days} days"

class LeaveApplication(UUIDModel, TimeStampedModel):
    """Leave applications"""
    APPLICATION_STATUS = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_applications')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, related_name='applications')
    
    # Leave details
    from_date = models.DateField()
    to_date = models.DateField()
    total_days = models.IntegerField(editable=False)
    reason = models.TextField()
    
    # Contact during leave
    contact_number = PhoneNumberField(blank=True, null=True)
    emergency_contact = models.CharField(max_length=200, blank=True, null=True)
    
    # Work arrangement
    work_handover_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='covering_leaves')
    handover_notes = models.TextField(blank=True, null=True)
    
    # Application process
    status = models.CharField(max_length=20, choices=APPLICATION_STATUS, default='DRAFT')
    applied_date = models.DateField(auto_now_add=True)
    
    # Approval process
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='hr_approved_leaves')
    approved_date = models.DateField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    # Medical certificate (if required)
    medical_certificate = models.FileField(upload_to='medical_certificates/', blank=True, null=True)
    
    def save(self, *args, **kwargs):
        # Calculate total days
        if self.from_date and self.to_date:
            self.total_days = (self.to_date - self.from_date).days + 1
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-applied_date']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.leave_type.name} - {self.from_date} to {self.to_date}" 