from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
from core.models import TimeStampedModel, SchoolSettings, UUIDModel, AcademicYear
from students.models import Student, SchoolClass, Section, Category
import uuid

class FeeCategory(TimeStampedModel):
    """Fee categories (Tuition, Transport, etc.) for Indian schools"""
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='fee_categories')
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    
    # Configuration
    is_mandatory = models.BooleanField(default=True)
    is_refundable = models.BooleanField(default=False)
    refund_percentage = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Accounting
    account_code = models.CharField(max_length=50, blank=True, null=True)
    tax_applicable = models.BooleanField(default=False)
    tax_percentage = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Indian education specific
    is_development_fee = models.BooleanField(default=False, help_text="One-time development fee")
    is_annual_fee = models.BooleanField(default=False)
    is_examination_fee = models.BooleanField(default=False)
    is_transport_fee = models.BooleanField(default=False)
    is_hostel_fee = models.BooleanField(default=False)
    is_library_fee = models.BooleanField(default=False)
    is_activity_fee = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['school', 'code']
        verbose_name_plural = 'Fee Categories'
    
    def __str__(self):
        return f"{self.school.name} - {self.name}"

class FeeStructure(TimeStampedModel):
    """Fee structure for different classes - Indian education system"""
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='fee_structures')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='fee_structures')
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='fee_structures')
    student_category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='fee_structures')
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    # Payment configuration
    is_installment_allowed = models.BooleanField(default=True)
    number_of_installments = models.IntegerField(default=4)
    installment_gap_days = models.IntegerField(default=90)  # Days between installments
    
    # Late fee configuration
    late_fee_applicable = models.BooleanField(default=True)
    late_fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    late_fee_percentage = models.FloatField(default=0)
    grace_period_days = models.IntegerField(default=7)
    
    # Discounts
    early_payment_discount = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    sibling_discount = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    staff_ward_discount = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Indian specific
    rte_fee_waiver = models.BooleanField(default=False, help_text="RTE students fee waiver")
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['school', 'academic_year', 'school_class', 'student_category']
    
    def __str__(self):
        return f"{self.school.name} - {self.name} - {self.academic_year.name}"

class FeeItem(TimeStampedModel):
    """Individual fee items within a structure"""
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE, related_name='fee_items')
    fee_category = models.ForeignKey(FeeCategory, on_delete=models.CASCADE, related_name='fee_items')
    
    name = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Payment schedule
    is_one_time = models.BooleanField(default=False)
    is_monthly = models.BooleanField(default=False)
    is_quarterly = models.BooleanField(default=False)
    is_annual = models.BooleanField(default=True)
    
    # Due dates (for non-installment items)
    due_date = models.DateField(blank=True, null=True)
    
    # Configuration
    is_optional = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['fee_structure', 'fee_category']
        ordering = ['fee_category__name']
    
    def __str__(self):
        return f"{self.fee_structure.name} - {self.name} - ₹{self.amount}"

class PaymentMethod(TimeStampedModel):
    """Payment methods supported by the school"""
    PAYMENT_TYPES = [
        ('CASH', 'Cash'),
        ('CHEQUE', 'Cheque'),
        ('DD', 'Demand Draft'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('UPI', 'UPI'),
        ('CARD', 'Credit/Debit Card'),
        ('NET_BANKING', 'Net Banking'),
        ('MOBILE_WALLET', 'Mobile Wallet'),
        ('RAZORPAY', 'Razorpay'),
        ('PAYU', 'PayU'),
        ('PAYTM', 'Paytm'),
        ('PHONEPE', 'PhonePe'),
        ('GPAY', 'Google Pay'),
    ]
    
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='payment_methods')
    name = models.CharField(max_length=100)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    
    # Configuration
    is_online = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    processing_fee_percentage = models.FloatField(default=0)
    processing_fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Gateway configuration
    gateway_name = models.CharField(max_length=100, blank=True, null=True)
    merchant_id = models.CharField(max_length=200, blank=True, null=True)
    api_key = models.CharField(max_length=500, blank=True, null=True)
    secret_key = models.CharField(max_length=500, blank=True, null=True)
    is_test_mode = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['school', 'name']
    
    def __str__(self):
        return f"{self.school.name} - {self.name}"

class StudentFeeAssignment(TimeStampedModel):
    """Assign fee structure to students"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fee_assignments')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE, related_name='student_assignments')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='student_fee_assignments')
    
    # Custom adjustments
    discount_percentage = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_reason = models.CharField(max_length=200, blank=True, null=True)
    
    # Scholarship
    scholarship_name = models.CharField(max_length=200, blank=True, null=True)
    scholarship_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    scholarship_percentage = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    scholarship_reference = models.CharField(max_length=100, blank=True, null=True)
    
    # Government schemes
    is_pmcare_beneficiary = models.BooleanField(default=False, help_text="PM CARES scholarship")
    is_state_scholarship = models.BooleanField(default=False)
    state_scholarship_name = models.CharField(max_length=200, blank=True, null=True)
    state_scholarship_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        unique_together = ['student', 'academic_year']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.fee_structure.name}"

class FeeInstallment(TimeStampedModel):
    """Fee installment schedules"""
    INSTALLMENT_TYPES = [
        ('FIRST_TERM', 'First Term'),
        ('SECOND_TERM', 'Second Term'),
        ('THIRD_TERM', 'Third Term'),
        ('FOURTH_TERM', 'Fourth Term'),
        ('ANNUAL', 'Annual'),
        ('ADMISSION', 'Admission Fee'),
        ('DEVELOPMENT', 'Development Fee'),
        ('EXAMINATION', 'Examination Fee'),
        ('TRANSPORT', 'Transport Fee'),
        ('HOSTEL', 'Hostel Fee'),
    ]
    
    student_fee_assignment = models.ForeignKey(StudentFeeAssignment, on_delete=models.CASCADE, related_name='installments')
    installment_number = models.IntegerField()
    installment_type = models.CharField(max_length=20, choices=INSTALLMENT_TYPES)
    installment_name = models.CharField(max_length=100)  # "First Term", "Second Term", etc.
    
    # Amount breakdown
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Dates
    due_date = models.DateField()
    
    # Status
    is_paid = models.BooleanField(default=False)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Late fee
    late_fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    late_fee_waived = models.BooleanField(default=False)
    late_fee_waiver_reason = models.CharField(max_length=200, blank=True, null=True)
    
    class Meta:
        unique_together = ['student_fee_assignment', 'installment_number']
        ordering = ['installment_number']
    
    def __str__(self):
        return f"{self.student_fee_assignment.student.full_name} - {self.installment_name}"

class FeePayment(UUIDModel, TimeStampedModel):
    """Fee payment records - Indian payment gateway integration"""
    PAYMENT_STATUS = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
        ('REFUNDED', 'Refunded'),
        ('PARTIALLY_REFUNDED', 'Partially Refunded'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fee_payments')
    installment = models.ForeignKey(FeeInstallment, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, related_name='payments')
    
    # Payment details
    receipt_number = models.CharField(max_length=50, unique=True)
    payment_date = models.DateField()
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2)
    late_fee_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    processing_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Payment instrument details
    reference_number = models.CharField(max_length=100, blank=True, null=True)  # Cheque no, transaction ID, etc.
    bank_name = models.CharField(max_length=200, blank=True, null=True)
    branch_name = models.CharField(max_length=200, blank=True, null=True)
    
    # Online payment gateway details
    gateway_transaction_id = models.CharField(max_length=200, blank=True, null=True)
    gateway_payment_id = models.CharField(max_length=200, blank=True, null=True)
    gateway_order_id = models.CharField(max_length=200, blank=True, null=True)
    gateway_signature = models.CharField(max_length=500, blank=True, null=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    
    # UPI specific
    upi_id = models.CharField(max_length=100, blank=True, null=True)
    upi_reference = models.CharField(max_length=100, blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='PENDING')
    remarks = models.TextField(blank=True, null=True)
    failure_reason = models.TextField(blank=True, null=True)
    
    # Staff details
    collected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='collected_payments')
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_payments')
    verified_at = models.DateTimeField(blank=True, null=True)
    
    # Receipt printing
    receipt_printed = models.BooleanField(default=False)
    receipt_printed_at = models.DateTimeField(blank=True, null=True)
    receipt_printed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='printed_receipts')
    
    class Meta:
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"{self.student.full_name} - ₹{self.total_amount} - {self.receipt_number}"

class FeeRefund(UUIDModel, TimeStampedModel):
    """Fee refund management"""
    REFUND_TYPES = [
        ('WITHDRAWAL', 'Student Withdrawal'),
        ('OVERPAYMENT', 'Overpayment'),
        ('DUPLICATE', 'Duplicate Payment'),
        ('CANCELLED_ADMISSION', 'Cancelled Admission'),
        ('CLASS_CHANGE', 'Class Change'),
        ('TRANSFER', 'School Transfer'),
        ('SCHOLARSHIP_ADJUSTMENT', 'Scholarship Adjustment'),
        ('OTHER', 'Other'),
    ]
    
    REFUND_STATUS = [
        ('REQUESTED', 'Requested'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('PROCESSED', 'Processed'),
        ('COMPLETED', 'Completed'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fee_refunds')
    payment = models.ForeignKey(FeePayment, on_delete=models.CASCADE, related_name='refunds')
    
    # Refund details
    refund_type = models.CharField(max_length=25, choices=REFUND_TYPES)
    refund_amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.TextField()
    
    # Processing
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requested_refunds')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_refunds')
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_refunds')
    
    # Dates
    requested_date = models.DateField(auto_now_add=True)
    approved_date = models.DateField(blank=True, null=True)
    processed_date = models.DateField(blank=True, null=True)
    expected_refund_date = models.DateField(blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=REFUND_STATUS, default='REQUESTED')
    admin_remarks = models.TextField(blank=True, null=True)
    
    # Refund details
    refund_reference = models.CharField(max_length=100, blank=True, null=True)
    refund_mode = models.CharField(max_length=50, blank=True, null=True)
    refund_account_number = models.CharField(max_length=30, blank=True, null=True)
    refund_ifsc_code = models.CharField(max_length=11, blank=True, null=True)
    
    class Meta:
        ordering = ['-requested_date']
    
    def __str__(self):
        return f"{self.student.full_name} - Refund ₹{self.refund_amount}"

class FeeDiscount(TimeStampedModel):
    """Fee discount schemes for Indian schools"""
    DISCOUNT_TYPES = [
        ('PERCENTAGE', 'Percentage'),
        ('FIXED_AMOUNT', 'Fixed Amount'),
        ('WAIVER', 'Complete Waiver'),
    ]
    
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='fee_discounts')
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    
    # Discount configuration
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    discount_percentage = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Applicability
    applicable_categories = models.ManyToManyField(FeeCategory, blank=True, related_name='discounts')
    applicable_classes = models.ManyToManyField(SchoolClass, blank=True, related_name='fee_discounts')
    
    # Criteria
    minimum_marks_required = models.FloatField(blank=True, null=True)
    maximum_family_income = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    is_need_based = models.BooleanField(default=False)
    is_merit_based = models.BooleanField(default=False)
    is_sports_quota = models.BooleanField(default=False)
    is_staff_ward = models.BooleanField(default=False)
    is_sibling_discount = models.BooleanField(default=False)
    is_early_payment = models.BooleanField(default=False)
    
    # Government schemes
    is_rte_scheme = models.BooleanField(default=False)
    is_pmcare_scheme = models.BooleanField(default=False)
    is_state_scholarship = models.BooleanField(default=False)
    
    # Validity
    valid_from = models.DateField()
    valid_till = models.DateField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['school', 'code']
    
    def __str__(self):
        return f"{self.school.name} - {self.name}"

class FeeDefaulter(TimeStampedModel):
    """Track fee defaulters"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fee_defaults')
    installment = models.ForeignKey(FeeInstallment, on_delete=models.CASCADE, related_name='defaults')
    
    # Overdue details
    overdue_amount = models.DecimalField(max_digits=12, decimal_places=2)
    overdue_days = models.IntegerField()
    
    # Notices sent
    first_notice_sent = models.BooleanField(default=False)
    first_notice_date = models.DateField(blank=True, null=True)
    second_notice_sent = models.BooleanField(default=False)
    second_notice_date = models.DateField(blank=True, null=True)
    final_notice_sent = models.BooleanField(default=False)
    final_notice_date = models.DateField(blank=True, null=True)
    
    # Actions taken
    parent_meeting_scheduled = models.BooleanField(default=False)
    parent_meeting_date = models.DateField(blank=True, null=True)
    tc_hold = models.BooleanField(default=False, help_text="Transfer Certificate on hold")
    exam_debarred = models.BooleanField(default=False)
    
    # Resolution
    is_resolved = models.BooleanField(default=False)
    resolved_date = models.DateField(blank=True, null=True)
    resolution_remarks = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ['student', 'installment']
    
    def __str__(self):
        return f"{self.student.full_name} - Overdue ₹{self.overdue_amount}"

class FeeReport(UUIDModel, TimeStampedModel):
    """Fee collection reports for Indian schools"""
    REPORT_TYPES = [
        ('DAILY', 'Daily Collection'),
        ('WEEKLY', 'Weekly Collection'),
        ('MONTHLY', 'Monthly Collection'),
        ('CLASS_WISE', 'Class-wise Collection'),
        ('DEFAULTER', 'Fee Defaulters'),
        ('OUTSTANDING', 'Outstanding Fees'),
        ('PAYMENT_MODE', 'Payment Mode wise'),
        ('SCHOLARSHIP', 'Scholarship Report'),
        ('REFUND', 'Refund Report'),
        ('TAX', 'Tax Report'),
        ('RTE', 'RTE Student Report'),
        ('CATEGORY_WISE', 'Category-wise Collection'),
    ]
    
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='fee_reports')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_fee_reports')
    
    # Report parameters
    from_date = models.DateField()
    to_date = models.DateField()
    report_data = models.JSONField(default=dict)
    
    # Filters
    class_filter = models.ForeignKey(SchoolClass, on_delete=models.SET_NULL, null=True, blank=True)
    category_filter = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    payment_method_filter = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True)
    
    # File
    report_file = models.FileField(upload_to='fee_reports/', blank=True, null=True)
    
    # Summary
    total_collection = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_outstanding = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_refunds = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.school.name} - {self.report_type} - {self.from_date} to {self.to_date}"

class FeeConcession(TimeStampedModel):
    """Fee concessions for students"""
    CONCESSION_TYPES = [
        ('MERIT', 'Merit Based'),
        ('NEED', 'Need Based'),
        ('SPORTS', 'Sports Quota'),
        ('STAFF_WARD', 'Staff Ward'),
        ('SIBLING', 'Sibling Discount'),
        ('HANDICAPPED', 'Handicapped'),
        ('MINORITY', 'Minority'),
        ('BPL', 'Below Poverty Line'),
        ('GOVERNMENT', 'Government Scholarship'),
        ('OTHER', 'Other'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fee_concessions')
    concession_type = models.CharField(max_length=20, choices=CONCESSION_TYPES)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='fee_concessions')
    
    # Concession details
    concession_name = models.CharField(max_length=200)
    concession_percentage = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    concession_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Applicable fees
    applicable_categories = models.ManyToManyField(FeeCategory, related_name='concessions')
    
    # Approval
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='approved_concessions')
    approval_date = models.DateField()
    approval_remarks = models.TextField(blank=True, null=True)
    
    # Documents
    supporting_documents = models.TextField(blank=True, null=True, help_text="List of supporting documents")
    
    # Validity
    valid_from = models.DateField()
    valid_till = models.DateField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['student', 'concession_type', 'academic_year']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.concession_name}"

# Create your models here.
