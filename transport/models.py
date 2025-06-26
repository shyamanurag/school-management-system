from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericRelation
from core.models import TimeStampedModel, SchoolSettings, UUIDModel, AcademicYear, Attachment
from students.models import Student
from hr.models import Employee
from decimal import Decimal
import uuid

class TransportVendor(TimeStampedModel):
    """Transport service vendors/contractors"""
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='transport_vendors')
    
    # Vendor details
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    contact_person = models.CharField(max_length=200)
    phone_number = PhoneNumberField()
    email = models.EmailField(blank=True, null=True)
    
    # Address
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    
    # Business details
    license_number = models.CharField(max_length=50, blank=True, null=True)
    license_expiry = models.DateField(blank=True, null=True)
    pan_number = models.CharField(max_length=10, blank=True, null=True)
    gst_number = models.CharField(max_length=15, blank=True, null=True)
    
    # Bank details
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    account_number = models.CharField(max_length=30, blank=True, null=True)
    ifsc_code = models.CharField(max_length=11, blank=True, null=True)
    
    # Contract details
    contract_start_date = models.DateField(blank=True, null=True)
    contract_end_date = models.DateField(blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['school', 'code']
    
    def __str__(self):
        return f"{self.school.name} - {self.name}"

class Vehicle(UUIDModel, TimeStampedModel):
    """School transport vehicles"""
    VEHICLE_TYPES = [
        ('BUS', 'School Bus'),
        ('VAN', 'Van'),
        ('CAR', 'Car'),
        ('AUTO', 'Auto Rickshaw'),
        ('TEMPO', 'Tempo Traveller'),
    ]
    
    FUEL_TYPES = [
        ('PETROL', 'Petrol'),
        ('DIESEL', 'Diesel'),
        ('CNG', 'CNG'),
        ('ELECTRIC', 'Electric'),
        ('HYBRID', 'Hybrid'),
    ]
    
    OWNERSHIP_TYPES = [
        ('OWNED', 'School Owned'),
        ('LEASED', 'Leased'),
        ('CONTRACTED', 'Contracted'),
    ]
    
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='vehicles')
    vendor = models.ForeignKey(TransportVendor, on_delete=models.SET_NULL, null=True, blank=True, related_name='vehicles')
    
    # Vehicle identification
    vehicle_number = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    ownership_type = models.CharField(max_length=20, choices=OWNERSHIP_TYPES)
    
    # Vehicle details
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year_of_manufacture = models.IntegerField()
    color = models.CharField(max_length=50)
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPES)
    seating_capacity = models.IntegerField()
    
    # Registration details
    registration_number = models.CharField(max_length=20)
    registration_date = models.DateField()
    registration_expiry = models.DateField()
    
    # Insurance details
    insurance_company = models.CharField(max_length=200, blank=True, null=True)
    insurance_policy_number = models.CharField(max_length=50, blank=True, null=True)
    insurance_expiry = models.DateField(blank=True, null=True)
    insurance_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    
    # Permits and licenses
    fitness_certificate_expiry = models.DateField(blank=True, null=True)
    permit_expiry = models.DateField(blank=True, null=True)
    pollution_certificate_expiry = models.DateField(blank=True, null=True)
    
    # GPS and safety
    gps_device_id = models.CharField(max_length=100, blank=True, null=True)
    gps_installed = models.BooleanField(default=False)
    cctv_installed = models.BooleanField(default=False)
    first_aid_kit = models.BooleanField(default=False)
    fire_extinguisher = models.BooleanField(default=False)
    speed_governor = models.BooleanField(default=False)
    
    # Financial
    purchase_date = models.DateField(blank=True, null=True)
    purchase_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    monthly_lease_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)
    current_mileage = models.IntegerField(default=0, help_text="Current odometer reading")
    
    # Photos and documents
    vehicle_photo = models.ImageField(upload_to='vehicle_photos/', blank=True, null=True)
    attachments = GenericRelation(Attachment)
    
    class Meta:
        ordering = ['vehicle_number']
        indexes = [
            models.Index(fields=['school', 'vehicle_number']),
            models.Index(fields=['gps_device_id']),
        ]
    
    def __str__(self):
        return f"{self.vehicle_number} - {self.make} {self.model}"

class Driver(UUIDModel, TimeStampedModel):
    """Vehicle drivers"""
    EMPLOYMENT_TYPES = [
        ('PERMANENT', 'Permanent'),
        ('CONTRACTUAL', 'Contractual'),
        ('TEMPORARY', 'Temporary'),
        ('VENDOR', 'Vendor Driver'),
    ]
    
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='drivers')
    vendor = models.ForeignKey(TransportVendor, on_delete=models.SET_NULL, null=True, blank=True, related_name='drivers')
    employee = models.OneToOneField(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='driver_profile')
    
    # Personal details
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    phone_number = PhoneNumberField()
    emergency_contact = PhoneNumberField()
    
    # Address
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    
    # Employment
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPES)
    joining_date = models.DateField()
    salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # License details
    license_number = models.CharField(max_length=20)
    license_type = models.CharField(max_length=50)  # Light Motor Vehicle, Heavy Motor Vehicle, etc.
    license_issue_date = models.DateField()
    license_expiry = models.DateField()
    
    # Experience and verification
    total_experience_years = models.IntegerField(default=0)
    police_verification_done = models.BooleanField(default=False)
    police_verification_date = models.DateField(blank=True, null=True)
    medical_certificate_date = models.DateField(blank=True, null=True)
    
    # Performance
    rating = models.FloatField(default=5.0, validators=[MinValueValidator(1.0), MaxValueValidator(5.0)])
    total_violations = models.IntegerField(default=0)
    
    # Bank details (for salary)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    account_number = models.CharField(max_length=30, blank=True, null=True)
    ifsc_code = models.CharField(max_length=11, blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)
    
    # Photos and documents
    photo = models.ImageField(upload_to='driver_photos/', blank=True, null=True)
    attachments = GenericRelation(Attachment)
    
    class Meta:
        ordering = ['first_name', 'last_name']
        indexes = [
            models.Index(fields=['school', 'license_number']),
            models.Index(fields=['phone_number']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.license_number}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class TransportRoute(UUIDModel, TimeStampedModel):
    """Transport routes"""
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='transport_routes')
    
    # Route details
    route_name = models.CharField(max_length=200)
    route_code = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    
    # Route information
    start_location = models.CharField(max_length=200)
    end_location = models.CharField(max_length=200)
    total_distance_km = models.FloatField()
    estimated_duration_minutes = models.IntegerField()
    
    # GPS coordinates
    start_latitude = models.FloatField(blank=True, null=True)
    start_longitude = models.FloatField(blank=True, null=True)
    end_latitude = models.FloatField(blank=True, null=True)
    end_longitude = models.FloatField(blank=True, null=True)
    
    # Route optimization
    route_polyline = models.TextField(blank=True, null=True, help_text="Encoded polyline for Google Maps")
    optimized_stops = models.JSONField(default=list, help_text="Optimized stop sequence")
    
    # Operational details
    morning_start_time = models.TimeField()
    morning_end_time = models.TimeField()
    evening_start_time = models.TimeField()
    evening_end_time = models.TimeField()
    
    # Pricing
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2)
    quarterly_fee = models.DecimalField(max_digits=10, decimal_places=2)
    annual_fee = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Capacity and status
    total_seats = models.IntegerField()
    occupied_seats = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['school', 'route_code']
        ordering = ['route_name']
    
    def __str__(self):
        return f"{self.school.name} - {self.route_name}"
    
    @property
    def available_seats(self):
        return self.total_seats - self.occupied_seats
    
    @property
    def occupancy_percentage(self):
        if self.total_seats > 0:
            return (self.occupied_seats / self.total_seats) * 100
        return 0

class BusStop(UUIDModel, TimeStampedModel):
    """Bus stops along routes"""
    route = models.ForeignKey(TransportRoute, on_delete=models.CASCADE, related_name='bus_stops')
    
    # Stop details
    stop_name = models.CharField(max_length=200)
    landmark = models.CharField(max_length=200, blank=True, null=True)
    address = models.TextField()
    
    # GPS coordinates
    latitude = models.FloatField()
    longitude = models.FloatField()
    
    # Timing
    morning_arrival_time = models.TimeField()
    morning_departure_time = models.TimeField()
    evening_arrival_time = models.TimeField()
    evening_departure_time = models.TimeField()
    
    # Sequence and distance
    stop_sequence = models.IntegerField()  # Order in route
    distance_from_school_km = models.FloatField()
    
    # Operational
    is_pickup_point = models.BooleanField(default=True)
    is_drop_point = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    
    # Safety features
    has_shelter = models.BooleanField(default=False)
    has_seating = models.BooleanField(default=False)
    has_lighting = models.BooleanField(default=False)
    is_safe_location = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['route', 'stop_sequence']
        unique_together = ['route', 'stop_sequence']
    
    def __str__(self):
        return f"{self.route.route_name} - {self.stop_name}"

class VehicleRouteAssignment(TimeStampedModel):
    """Assign vehicles to routes with drivers"""
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='route_assignments')
    route = models.ForeignKey(TransportRoute, on_delete=models.CASCADE, related_name='vehicle_assignments')
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='route_assignments')
    conductor = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name='conducted_routes')
    
    # Assignment period
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    
    # Shift details
    shift_type = models.CharField(max_length=20, choices=[
        ('MORNING', 'Morning Shift'),
        ('EVENING', 'Evening Shift'),
        ('BOTH', 'Both Shifts'),
        ('FULL_DAY', 'Full Day'),
    ], default='BOTH')
    
    # Status
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['vehicle', 'route', 'start_date']
    
    def __str__(self):
        return f"{self.vehicle.vehicle_number} - {self.route.route_name} - {self.driver.full_name}"

class StudentTransport(UUIDModel, TimeStampedModel):
    """Student transport subscriptions"""
    SUBSCRIPTION_TYPES = [
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
        ('HALF_YEARLY', 'Half Yearly'),
        ('ANNUAL', 'Annual'),
    ]
    
    TRANSPORT_TYPES = [
        ('PICKUP_ONLY', 'Pickup Only'),
        ('DROP_ONLY', 'Drop Only'),
        ('BOTH_WAYS', 'Both Ways'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='transport_subscriptions')
    route = models.ForeignKey(TransportRoute, on_delete=models.CASCADE, related_name='student_subscriptions')
    pickup_stop = models.ForeignKey(BusStop, on_delete=models.CASCADE, related_name='pickup_students')
    drop_stop = models.ForeignKey(BusStop, on_delete=models.CASCADE, related_name='drop_students')
    
    # Subscription details
    subscription_type = models.CharField(max_length=20, choices=SUBSCRIPTION_TYPES)
    transport_type = models.CharField(max_length=20, choices=TRANSPORT_TYPES, default='BOTH_WAYS')
    
    # Period
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Fees
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2)
    total_fee = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_fee = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payment status
    is_paid = models.BooleanField(default=False)
    payment_date = models.DateField(blank=True, null=True)
    
    # Emergency contacts
    emergency_contact_1 = PhoneNumberField()
    emergency_contact_2 = PhoneNumberField(blank=True, null=True)
    
    # Special requirements
    special_requirements = models.TextField(blank=True, null=True)
    medical_conditions = models.TextField(blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        self.net_fee = self.total_fee - self.discount_amount
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['student__first_name', 'student__last_name']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.route.route_name}"

class VehicleTracking(UUIDModel, TimeStampedModel):
    """Real-time vehicle tracking data"""
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='tracking_data')
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='tracking_data')
    
    # Location data
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude = models.FloatField(blank=True, null=True)
    accuracy = models.FloatField(blank=True, null=True)
    
    # Speed and direction
    speed_kmph = models.FloatField(default=0)
    direction = models.FloatField(blank=True, null=True)  # Bearing in degrees
    
    # Engine and vehicle status
    engine_status = models.BooleanField(default=False)
    door_status = models.BooleanField(default=False)  # Open/Closed
    fuel_level = models.FloatField(blank=True, null=True)
    
    # Emergency
    panic_button_pressed = models.BooleanField(default=False)
    emergency_alert = models.BooleanField(default=False)
    
    # Geofencing
    is_on_route = models.BooleanField(default=True)
    current_stop = models.ForeignKey(BusStop, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Timestamps
    gps_timestamp = models.DateTimeField()
    server_timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-gps_timestamp']
        indexes = [
            models.Index(fields=['vehicle', 'gps_timestamp']),
            models.Index(fields=['gps_timestamp']),
        ]
    
    def __str__(self):
        return f"{self.vehicle.vehicle_number} - {self.gps_timestamp}"

class TransportAlert(UUIDModel, TimeStampedModel):
    """Transport alerts and notifications"""
    ALERT_TYPES = [
        ('SPEED_VIOLATION', 'Speed Violation'),
        ('ROUTE_DEVIATION', 'Route Deviation'),
        ('PANIC_BUTTON', 'Panic Button Pressed'),
        ('BREAKDOWN', 'Vehicle Breakdown'),
        ('ACCIDENT', 'Accident'),
        ('LATE_ARRIVAL', 'Late Arrival'),
        ('EARLY_DEPARTURE', 'Early Departure'),
        ('NO_GPS_SIGNAL', 'No GPS Signal'),
        ('UNAUTHORIZED_STOP', 'Unauthorized Stop'),
        ('ENGINE_MALFUNCTION', 'Engine Malfunction'),
        ('OVERSPEEDING', 'Overspeeding'),
        ('HARSH_BRAKING', 'Harsh Braking'),
        ('HARSH_ACCELERATION', 'Harsh Acceleration'),
        ('OTHER', 'Other'),
    ]
    
    SEVERITY_LEVELS = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    ALERT_STATUS = [
        ('OPEN', 'Open'),
        ('ACKNOWLEDGED', 'Acknowledged'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    ]
    
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='alerts')
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='alerts')
    route = models.ForeignKey(TransportRoute, on_delete=models.SET_NULL, null=True, blank=True, related_name='alerts')
    
    # Alert details
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Location
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    location_address = models.CharField(max_length=500, blank=True, null=True)
    
    # Alert data
    speed_at_alert = models.FloatField(blank=True, null=True)
    alert_data = models.JSONField(default=dict)  # Additional alert specific data
    
    # Status and resolution
    status = models.CharField(max_length=20, choices=ALERT_STATUS, default='OPEN')
    acknowledged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='acknowledged_alerts')
    acknowledged_at = models.DateTimeField(blank=True, null=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_alerts')
    resolved_at = models.DateTimeField(blank=True, null=True)
    resolution_notes = models.TextField(blank=True, null=True)
    
    # Notifications sent
    parents_notified = models.BooleanField(default=False)
    admin_notified = models.BooleanField(default=False)
    driver_notified = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['vehicle', 'status']),
            models.Index(fields=['alert_type', 'severity']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.vehicle.vehicle_number} - {self.alert_type} - {self.severity}"

class VehicleMaintenance(UUIDModel, TimeStampedModel):
    """Vehicle maintenance records"""
    MAINTENANCE_TYPES = [
        ('ROUTINE', 'Routine Maintenance'),
        ('PREVENTIVE', 'Preventive Maintenance'),
        ('CORRECTIVE', 'Corrective Maintenance'),
        ('BREAKDOWN', 'Breakdown Repair'),
        ('ACCIDENT_REPAIR', 'Accident Repair'),
        ('INSPECTION', 'Inspection'),
        ('MODIFICATION', 'Modification'),
    ]
    
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('OVERDUE', 'Overdue'),
    ]
    
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='maintenance_records')
    
    # Maintenance details
    maintenance_type = models.CharField(max_length=30, choices=MAINTENANCE_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Scheduling
    scheduled_date = models.DateField()
    completed_date = models.DateField(blank=True, null=True)
    next_due_date = models.DateField(blank=True, null=True)
    next_due_mileage = models.IntegerField(blank=True, null=True)
    
    # Service provider
    service_provider = models.CharField(max_length=200)
    service_contact = models.CharField(max_length=100, blank=True, null=True)
    
    # Cost
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Parts and labor
    parts_replaced = models.TextField(blank=True, null=True)
    labor_hours = models.FloatField(blank=True, null=True)
    
    # Mileage
    mileage_at_maintenance = models.IntegerField(blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    
    # Staff
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requested_maintenance')
    completed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='completed_maintenance')
    
    # Documents
    attachments = GenericRelation(Attachment)
    
    class Meta:
        ordering = ['-scheduled_date']
    
    def __str__(self):
        return f"{self.vehicle.vehicle_number} - {self.title} - {self.scheduled_date}"

class TransportReport(UUIDModel, TimeStampedModel):
    """Transport reports and analytics"""
    REPORT_TYPES = [
        ('DAILY_TRIP', 'Daily Trip Report'),
        ('WEEKLY_SUMMARY', 'Weekly Summary'),
        ('MONTHLY_SUMMARY', 'Monthly Summary'),
        ('ROUTE_UTILIZATION', 'Route Utilization'),
        ('VEHICLE_PERFORMANCE', 'Vehicle Performance'),
        ('DRIVER_PERFORMANCE', 'Driver Performance'),
        ('FUEL_CONSUMPTION', 'Fuel Consumption'),
        ('MAINTENANCE_SUMMARY', 'Maintenance Summary'),
        ('ALERT_SUMMARY', 'Alert Summary'),
        ('REVENUE_REPORT', 'Revenue Report'),
        ('PARENT_FEEDBACK', 'Parent Feedback'),
        ('SAFETY_REPORT', 'Safety Report'),
    ]
    
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='transport_reports')
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_transport_reports')
    
    # Report parameters
    from_date = models.DateField()
    to_date = models.DateField()
    report_data = models.JSONField(default=dict)
    
    # Filters
    route_filter = models.ForeignKey(TransportRoute, on_delete=models.SET_NULL, null=True, blank=True)
    vehicle_filter = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)
    driver_filter = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True)
    
    # File
    report_file = models.FileField(upload_to='transport_reports/', blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.school.name} - {self.report_type} - {self.from_date} to {self.to_date}"
