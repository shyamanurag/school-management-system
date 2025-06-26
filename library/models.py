from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils import timezone
from datetime import timedelta
from core.models import TimeStampedModel, SchoolSettings, UUIDModel, AcademicYear
from students.models import Student, SchoolClass
from hr.models import Employee
from decimal import Decimal
import uuid

class LibrarySection(TimeStampedModel):
    """Library sections (Fiction, Non-Fiction, Reference, etc.)"""
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='library_sections')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    floor_location = models.CharField(max_length=50, blank=True, null=True)
    shelf_range = models.CharField(max_length=50, blank=True, null=True, help_text="A1-A50")
    
    # Access control
    is_reference_only = models.BooleanField(default=False)
    min_class_access = models.ForeignKey(SchoolClass, on_delete=models.SET_NULL, null=True, blank=True)
    staff_only_access = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['school', 'code']
    
    def __str__(self):
        return f"{self.school.name} - {self.name}"

class Author(TimeStampedModel):
    """Book authors"""
    name = models.CharField(max_length=200)
    biography = models.TextField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Publisher(TimeStampedModel):
    """Book publishers"""
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Subject(TimeStampedModel):
    """Book subjects/categories"""
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='library_subjects')
    name = models.CharField(max_length=100)
    dewey_decimal_code = models.CharField(max_length=10, blank=True, null=True)
    parent_subject = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='sub_subjects')
    
    class Meta:
        unique_together = ['school', 'name']
        ordering = ['name']
    
    def __str__(self):
        return f"{self.school.name} - {self.name}"

class Book(UUIDModel, TimeStampedModel):
    """Books in library"""
    BOOK_TYPES = [
        ('TEXTBOOK', 'Textbook'),
        ('REFERENCE', 'Reference'),
        ('FICTION', 'Fiction'),
        ('NON_FICTION', 'Non-Fiction'),
        ('MAGAZINE', 'Magazine'),
        ('JOURNAL', 'Journal'),
        ('NEWSPAPER', 'Newspaper'),
        ('DIGITAL', 'Digital Book'),
        ('AUDIO', 'Audio Book'),
        ('DVD', 'DVD/CD'),
        ('OTHER', 'Other'),
    ]
    
    CONDITION_CHOICES = [
        ('NEW', 'New'),
        ('GOOD', 'Good'),
        ('FAIR', 'Fair'),
        ('POOR', 'Poor'),
        ('DAMAGED', 'Damaged'),
        ('LOST', 'Lost'),
    ]
    
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='library_books')
    
    # Book identification
    accession_number = models.CharField(max_length=50, unique=True)
    isbn = models.CharField(max_length=13, blank=True, null=True, validators=[
        RegexValidator(r'^\d{10}(\d{3})?$', 'ISBN must be 10 or 13 digits')
    ])
    barcode = models.CharField(max_length=50, blank=True, null=True)
    rfid_tag = models.CharField(max_length=50, blank=True, null=True, help_text="RFID tag number")
    
    # Book details
    title = models.CharField(max_length=500)
    subtitle = models.CharField(max_length=500, blank=True, null=True)
    authors = models.ManyToManyField(Author, related_name='books')
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, blank=True, related_name='books')
    publication_year = models.IntegerField(blank=True, null=True)
    edition = models.CharField(max_length=50, blank=True, null=True)
    pages = models.IntegerField(blank=True, null=True)
    language = models.CharField(max_length=50, default='English')
    
    # Classification
    book_type = models.CharField(max_length=20, choices=BOOK_TYPES)
    section = models.ForeignKey(LibrarySection, on_delete=models.CASCADE, related_name='books')
    subjects = models.ManyToManyField(Subject, related_name='books')
    
    # Physical details
    shelf_location = models.CharField(max_length=50, blank=True, null=True)
    rack_number = models.CharField(max_length=20, blank=True, null=True)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='NEW')
    
    # Purchase details
    purchase_date = models.DateField(blank=True, null=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    vendor = models.CharField(max_length=200, blank=True, null=True)
    bill_number = models.CharField(max_length=50, blank=True, null=True)
    
    # Digital content
    digital_file = models.FileField(upload_to='digital_books/', blank=True, null=True)
    digital_url = models.URLField(blank=True, null=True)
    
    # Access control
    is_reference_only = models.BooleanField(default=False)
    is_restricted = models.BooleanField(default=False)
    min_class_level = models.ForeignKey(SchoolClass, on_delete=models.SET_NULL, null=True, blank=True)
    staff_only = models.BooleanField(default=False)
    
    # Availability
    total_copies = models.IntegerField(default=1)
    available_copies = models.IntegerField(default=1)
    
    # Metadata
    summary = models.TextField(blank=True, null=True)
    keywords = models.TextField(blank=True, null=True, help_text="Comma-separated keywords")
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['title']
        indexes = [
            models.Index(fields=['school', 'accession_number']),
            models.Index(fields=['isbn']),
            models.Index(fields=['barcode']),
            models.Index(fields=['rfid_tag']),
            models.Index(fields=['title']),
            models.Index(fields=['book_type']),
        ]
    
    def __str__(self):
        return f"{self.accession_number} - {self.title}"
    
    @property
    def is_available(self):
        return self.available_copies > 0

class LibraryMember(TimeStampedModel):
    """Library membership for students and staff"""
    MEMBER_TYPES = [
        ('STUDENT', 'Student'),
        ('STAFF', 'Staff'),
        ('EXTERNAL', 'External Member'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('SUSPENDED', 'Suspended'),
        ('EXPIRED', 'Expired'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='library_members')
    member_id = models.CharField(max_length=50, unique=True)
    member_type = models.CharField(max_length=20, choices=MEMBER_TYPES)
    
    # Member references
    student = models.OneToOneField(Student, on_delete=models.CASCADE, null=True, blank=True, related_name='library_membership')
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, null=True, blank=True, related_name='library_membership')
    
    # External member details (if applicable)
    external_name = models.CharField(max_length=200, blank=True, null=True)
    external_phone = models.CharField(max_length=20, blank=True, null=True)
    external_email = models.EmailField(blank=True, null=True)
    external_address = models.TextField(blank=True, null=True)
    
    # Membership details
    membership_start_date = models.DateField()
    membership_end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    
    # Borrowing limits
    max_books_allowed = models.IntegerField(default=5)
    max_issue_days = models.IntegerField(default=14)
    
    # Security deposit (for external members)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deposit_paid = models.BooleanField(default=False)
    
    # Photo and ID
    photo = models.ImageField(upload_to='library_member_photos/', blank=True, null=True)
    id_card_printed = models.BooleanField(default=False)
    
    class Meta:
        indexes = [
            models.Index(fields=['school', 'member_id']),
            models.Index(fields=['member_type', 'status']),
        ]
    
    def __str__(self):
        if self.student:
            return f"{self.member_id} - {self.student.full_name}"
        elif self.employee:
            return f"{self.member_id} - {self.employee.full_name}"
        else:
            return f"{self.member_id} - {self.external_name}"
    
    @property
    def member_name(self):
        if self.student:
            return self.student.full_name
        elif self.employee:
            return self.employee.full_name
        else:
            return self.external_name
    
    @property
    def is_active(self):
        return self.status == 'ACTIVE' and self.membership_end_date >= timezone.now().date()

class BookIssue(UUIDModel, TimeStampedModel):
    """Book issue/checkout records"""
    ISSUE_STATUS = [
        ('ISSUED', 'Issued'),
        ('RETURNED', 'Returned'),
        ('OVERDUE', 'Overdue'),
        ('LOST', 'Lost'),
        ('DAMAGED', 'Damaged'),
        ('RENEWED', 'Renewed'),
    ]
    
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='book_issues')
    issue_number = models.CharField(max_length=50, unique=True)
    
    # Issue details
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='issues')
    member = models.ForeignKey(LibraryMember, on_delete=models.CASCADE, related_name='book_issues')
    
    # Dates
    issue_date = models.DateField()
    due_date = models.DateField()
    return_date = models.DateField(blank=True, null=True)
    
    # Staff
    issued_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='issued_books')
    returned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='returned_books')
    
    # Status
    status = models.CharField(max_length=20, choices=ISSUE_STATUS, default='ISSUED')
    
    # Renewal tracking
    renewal_count = models.IntegerField(default=0)
    max_renewals_allowed = models.IntegerField(default=2)
    
    # Return condition
    return_condition = models.CharField(max_length=20, choices=Book.CONDITION_CHOICES, blank=True, null=True)
    return_remarks = models.TextField(blank=True, null=True)
    
    # Fine details
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fine_paid = models.BooleanField(default=False)
    fine_waived = models.BooleanField(default=False)
    fine_waiver_reason = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-issue_date']
        indexes = [
            models.Index(fields=['school', 'issue_number']),
            models.Index(fields=['book', 'status']),
            models.Index(fields=['member', 'status']),
            models.Index(fields=['due_date', 'status']),
        ]
    
    def __str__(self):
        return f"{self.issue_number} - {self.book.title} - {self.member.member_name}"
    
    @property
    def is_overdue(self):
        if self.status == 'ISSUED' and self.due_date < timezone.now().date():
            return True
        return False
    
    @property
    def days_overdue(self):
        if self.is_overdue:
            return (timezone.now().date() - self.due_date).days
        return 0
    
    def calculate_fine(self):
        """Calculate fine based on overdue days"""
        if self.is_overdue:
            fine_per_day = Decimal('2.00')  # ₹2 per day
            return fine_per_day * self.days_overdue
        return Decimal('0.00')

class BookReservation(UUIDModel, TimeStampedModel):
    """Book reservation system"""
    RESERVATION_STATUS = [
        ('ACTIVE', 'Active'),
        ('FULFILLED', 'Fulfilled'),
        ('CANCELLED', 'Cancelled'),
        ('EXPIRED', 'Expired'),
    ]
    
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='book_reservations')
    reservation_number = models.CharField(max_length=50, unique=True)
    
    # Reservation details
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reservations')
    member = models.ForeignKey(LibraryMember, on_delete=models.CASCADE, related_name='reservations')
    
    # Dates
    reservation_date = models.DateField(auto_now_add=True)
    expiry_date = models.DateField()
    fulfilled_date = models.DateField(blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=RESERVATION_STATUS, default='ACTIVE')
    priority = models.IntegerField(default=1, help_text="1=highest priority")
    
    # Notification
    notification_sent = models.BooleanField(default=False)
    notification_date = models.DateField(blank=True, null=True)
    
    class Meta:
        ordering = ['priority', 'reservation_date']
        unique_together = ['book', 'member', 'status']
    
    def __str__(self):
        return f"{self.reservation_number} - {self.book.title} - {self.member.member_name}"

class LibraryFine(UUIDModel, TimeStampedModel):
    """Library fines management"""
    FINE_TYPES = [
        ('OVERDUE', 'Overdue Fine'),
        ('DAMAGE', 'Damage Fine'),
        ('LOST_BOOK', 'Lost Book Fine'),
        ('LATE_RETURN', 'Late Return Fine'),
        ('OTHER', 'Other Fine'),
    ]
    
    PAYMENT_STATUS = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('WAIVED', 'Waived'),
        ('PARTIAL', 'Partially Paid'),
    ]
    
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='library_fines')
    fine_number = models.CharField(max_length=50, unique=True)
    
    # Fine details
    member = models.ForeignKey(LibraryMember, on_delete=models.CASCADE, related_name='fines')
    book_issue = models.ForeignKey(BookIssue, on_delete=models.CASCADE, null=True, blank=True, related_name='fines')
    
    fine_type = models.CharField(max_length=20, choices=FINE_TYPES)
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    
    # Payment details
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='PENDING')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_date = models.DateField(blank=True, null=True)
    payment_mode = models.CharField(max_length=20, choices=[
        ('CASH', 'Cash'),
        ('CARD', 'Card'),
        ('UPI', 'UPI'),
        ('ONLINE', 'Online'),
    ], blank=True, null=True)
    
    # Waiver details
    waiver_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    waiver_reason = models.TextField(blank=True, null=True)
    waived_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='waived_fines')
    
    # Staff
    imposed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='imposed_fines')
    collected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='collected_fines')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.fine_number} - {self.member.member_name} - ₹{self.fine_amount}"
    
    @property
    def balance_amount(self):
        return self.fine_amount - self.amount_paid - self.waiver_amount

class DigitalResource(UUIDModel, TimeStampedModel):
    """Digital library resources"""
    RESOURCE_TYPES = [
        ('EBOOK', 'E-Book'),
        ('AUDIO', 'Audio Book'),
        ('VIDEO', 'Video'),
        ('ARTICLE', 'Article'),
        ('RESEARCH_PAPER', 'Research Paper'),
        ('MAGAZINE', 'Digital Magazine'),
        ('NEWSPAPER', 'Digital Newspaper'),
        ('DATABASE', 'Database Access'),
        ('SOFTWARE', 'Educational Software'),
        ('WEBSITE', 'Educational Website'),
    ]
    
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='digital_resources')
    
    # Resource details
    title = models.CharField(max_length=500)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    authors = models.ManyToManyField(Author, blank=True, related_name='digital_resources')
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, blank=True, related_name='digital_resources')
    
    # Content
    description = models.TextField()
    subjects = models.ManyToManyField(Subject, related_name='digital_resources')
    keywords = models.TextField(blank=True, null=True)
    
    # Access
    url = models.URLField(blank=True, null=True)
    file = models.FileField(upload_to='digital_resources/', blank=True, null=True)
    access_credentials = models.JSONField(default=dict, blank=True)
    
    # Licensing
    license_type = models.CharField(max_length=100, blank=True, null=True)
    license_expiry = models.DateField(blank=True, null=True)
    subscription_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Access control
    is_free = models.BooleanField(default=True)
    requires_login = models.BooleanField(default=False)
    min_class_level = models.ForeignKey(SchoolClass, on_delete=models.SET_NULL, null=True, blank=True)
    staff_only = models.BooleanField(default=False)
    
    # Statistics
    access_count = models.IntegerField(default=0)
    download_count = models.IntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['title']
    
    def __str__(self):
        return f"{self.title} ({self.resource_type})"

class LibraryEvent(UUIDModel, TimeStampedModel):
    """Library events and activities"""
    EVENT_TYPES = [
        ('BOOK_FAIR', 'Book Fair'),
        ('AUTHOR_VISIT', 'Author Visit'),
        ('READING_COMPETITION', 'Reading Competition'),
        ('STORYTELLING', 'Storytelling Session'),
        ('WORKSHOP', 'Workshop'),
        ('EXHIBITION', 'Exhibition'),
        ('BOOK_CLUB', 'Book Club Meeting'),
        ('LIBRARY_ORIENTATION', 'Library Orientation'),
        ('OTHER', 'Other'),
    ]
    
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='library_events')
    
    # Event details
    title = models.CharField(max_length=200)
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    description = models.TextField()
    
    # Schedule
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    venue = models.CharField(max_length=200)
    
    # Participants
    target_classes = models.ManyToManyField(SchoolClass, blank=True, related_name='library_events')
    max_participants = models.IntegerField(blank=True, null=True)
    registration_required = models.BooleanField(default=False)
    registration_deadline = models.DateField(blank=True, null=True)
    
    # Organizer
    organized_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_library_events')
    external_speaker = models.CharField(max_length=200, blank=True, null=True)
    
    # Resources
    budget = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    resources_required = models.TextField(blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_completed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.title} - {self.start_date}"

class LibraryReport(UUIDModel, TimeStampedModel):
    """Library reports and analytics"""
    REPORT_TYPES = [
        ('CIRCULATION', 'Circulation Report'),
        ('OVERDUE', 'Overdue Books Report'),
        ('POPULAR_BOOKS', 'Popular Books Report'),
        ('MEMBER_ACTIVITY', 'Member Activity Report'),
        ('COLLECTION_ANALYSIS', 'Collection Analysis'),
        ('FINE_COLLECTION', 'Fine Collection Report'),
        ('INVENTORY', 'Inventory Report'),
        ('DIGITAL_USAGE', 'Digital Resource Usage'),
        ('MONTHLY_SUMMARY', 'Monthly Summary'),
        ('ANNUAL_REPORT', 'Annual Report'),
    ]
    
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='library_reports')
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_library_reports')
    
    # Report parameters
    from_date = models.DateField()
    to_date = models.DateField()
    report_data = models.JSONField(default=dict)
    
    # Filters
    section_filter = models.ForeignKey(LibrarySection, on_delete=models.SET_NULL, null=True, blank=True)
    member_type_filter = models.CharField(max_length=20, blank=True, null=True)
    
    # File
    report_file = models.FileField(upload_to='library_reports/', blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.school.name} - {self.report_type} - {self.from_date} to {self.to_date}"
