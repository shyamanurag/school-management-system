from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericRelation
from core.models import TimeStampedModel, SchoolSettings, UUIDModel, AcademicYear, Attachment
from hr.models import Employee
from decimal import Decimal
import uuid

class InventoryCategory(TimeStampedModel):
    """Inventory item categories"""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='inventory_categories')
    
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    
    # Hierarchy
    parent_category = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='sub_categories')
    
    # Asset classification
    is_fixed_asset = models.BooleanField(default=False)
    is_consumable = models.BooleanField(default=False)
    depreciation_rate = models.FloatField(default=0, help_text="Annual depreciation rate in percentage")
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['school', 'code']
        verbose_name_plural = 'Inventory Categories'
    
    def __str__(self):
        return f"{self.school.name} - {self.name}"

class Supplier(TimeStampedModel):
    """Suppliers/Vendors for inventory items"""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='suppliers')
    
    # Supplier details
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    contact_person = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    
    # Address
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=50, default='India')
    
    # Business details
    gst_number = models.CharField(max_length=15, blank=True, null=True)
    pan_number = models.CharField(max_length=10, blank=True, null=True)
    license_number = models.CharField(max_length=50, blank=True, null=True)
    
    # Bank details
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    account_number = models.CharField(max_length=30, blank=True, null=True)
    ifsc_code = models.CharField(max_length=11, blank=True, null=True)
    
    # Rating and performance
    rating = models.FloatField(default=5.0, validators=[MinValueValidator(1.0), MaxValueValidator(5.0)])
    total_orders = models.IntegerField(default=0)
    on_time_delivery_percentage = models.FloatField(default=100.0)
    
    # Payment terms
    payment_terms_days = models.IntegerField(default=30)
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['school', 'code']
    
    def __str__(self):
        return f"{self.school.name} - {self.name}"

class Brand(TimeStampedModel):
    """Product brands"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class InventoryItem(UUIDModel, TimeStampedModel):
    """Inventory items/products"""
    ITEM_TYPES = [
        ('ASSET', 'Fixed Asset'),
        ('CONSUMABLE', 'Consumable'),
        ('STATIONERY', 'Stationery'),
        ('FURNITURE', 'Furniture'),
        ('EQUIPMENT', 'Equipment'),
        ('BOOK', 'Book/Educational Material'),
        ('UNIFORM', 'Uniform'),
        ('SPORTS', 'Sports Equipment'),
        ('LAB_EQUIPMENT', 'Laboratory Equipment'),
        ('IT_EQUIPMENT', 'IT Equipment'),
        ('MAINTENANCE', 'Maintenance Supplies'),
        ('FOOD', 'Food Items'),
        ('MEDICAL', 'Medical Supplies'),
        ('CLEANING', 'Cleaning Supplies'),
        ('OTHER', 'Other'),
    ]
    
    UNIT_TYPES = [
        ('PCS', 'Pieces'),
        ('KG', 'Kilograms'),
        ('LITER', 'Liters'),
        ('METER', 'Meters'),
        ('BOX', 'Box'),
        ('PACKET', 'Packet'),
        ('BOTTLE', 'Bottle'),
        ('SET', 'Set'),
        ('DOZEN', 'Dozen'),
        ('BUNDLE', 'Bundle'),
        ('ROLL', 'Roll'),
        ('PAIR', 'Pair'),
    ]
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='inventory_items')
    category = models.ForeignKey(InventoryCategory, on_delete=models.CASCADE, related_name='items')
    
    # Item identification
    item_code = models.CharField(max_length=50, unique=True)
    barcode = models.CharField(max_length=50, blank=True, null=True)
    
    # Item details
    name = models.CharField(max_length=200)
    description = models.TextField()
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='items')
    model_number = models.CharField(max_length=100, blank=True, null=True)
    
    # Physical properties
    unit = models.CharField(max_length=20, choices=UNIT_TYPES, default='PCS')
    weight_kg = models.FloatField(blank=True, null=True)
    dimensions = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    
    # Stock information
    current_stock = models.FloatField(default=0)
    minimum_stock_level = models.FloatField(default=0)
    maximum_stock_level = models.FloatField(default=0)
    reorder_level = models.FloatField(default=0)
    
    # Location
    storage_location = models.CharField(max_length=200, blank=True, null=True)
    rack_number = models.CharField(max_length=50, blank=True, null=True)
    shelf_number = models.CharField(max_length=50, blank=True, null=True)
    
    # Pricing
    standard_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    average_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    last_purchase_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Preferred supplier
    preferred_supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='preferred_items')
    
    # Asset specific (for fixed assets)
    asset_tag_number = models.CharField(max_length=50, blank=True, null=True)
    purchase_date = models.DateField(blank=True, null=True)
    warranty_expiry = models.DateField(blank=True, null=True)
    depreciation_rate = models.FloatField(default=0)
    useful_life_years = models.IntegerField(blank=True, null=True)
    
    # Images and documents
    item_image = models.ImageField(upload_to='inventory_images/', blank=True, null=True)
    attachments = GenericRelation(Attachment)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_tracked = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['school', 'item_code']),
            models.Index(fields=['category', 'item_type']),
            models.Index(fields=['barcode']),
            models.Index(fields=['current_stock']),
        ]
    
    def __str__(self):
        return f"{self.item_code} - {self.name}"
    
    @property
    def is_low_stock(self):
        return self.current_stock <= self.reorder_level
    
    @property
    def stock_value(self):
        return self.current_stock * self.average_cost

class PurchaseOrder(UUIDModel, TimeStampedModel):
    """Purchase orders for inventory procurement"""
    ORDER_STATUS = [
        ('DRAFT', 'Draft'),
        ('PENDING_APPROVAL', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('SENT_TO_SUPPLIER', 'Sent to Supplier'),
        ('CONFIRMED', 'Confirmed by Supplier'),
        ('PARTIALLY_RECEIVED', 'Partially Received'),
        ('RECEIVED', 'Fully Received'),
        ('CANCELLED', 'Cancelled'),
        ('REJECTED', 'Rejected'),
    ]
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='purchase_orders')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchase_orders')
    
    # Order identification
    po_number = models.CharField(max_length=50, unique=True)
    po_date = models.DateField()
    
    # Order details
    required_by_date = models.DateField()
    delivery_address = models.TextField()
    
    # Financial
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_charges = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Status
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='DRAFT')
    
    # Approval workflow
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requested_purchase_orders')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_purchase_orders')
    approval_date = models.DateField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    # Terms and conditions
    terms_and_conditions = models.TextField(blank=True, null=True)
    special_instructions = models.TextField(blank=True, null=True)
    
    # Payment terms
    payment_terms = models.CharField(max_length=100, blank=True, null=True)
    advance_payment_percentage = models.FloatField(default=0)
    
    # Files
    po_document = models.FileField(upload_to='purchase_orders/', blank=True, null=True)
    
    class Meta:
        ordering = ['-po_date']
    
    def __str__(self):
        return f"{self.po_number} - {self.supplier.name}"

class PurchaseOrderItem(UUIDModel, TimeStampedModel):
    """Items in purchase orders"""
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='po_items')
    
    # Quantity and pricing
    quantity_ordered = models.FloatField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_percentage = models.FloatField(default=0)
    line_total = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Delivery tracking
    quantity_received = models.FloatField(default=0)
    quantity_pending = models.FloatField(default=0)
    
    # Item specifications
    specifications = models.TextField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        # Calculate line total
        discount_amount = (self.unit_price * self.quantity_ordered * self.discount_percentage) / 100
        self.line_total = (self.unit_price * self.quantity_ordered) - discount_amount
        self.quantity_pending = self.quantity_ordered - self.quantity_received
        super().save(*args, **kwargs)
    
    class Meta:
        unique_together = ['purchase_order', 'inventory_item']
    
    def __str__(self):
        return f"{self.purchase_order.po_number} - {self.inventory_item.name}"

class GoodsReceipt(UUIDModel, TimeStampedModel):
    """Goods receipt/delivery records"""
    RECEIPT_STATUS = [
        ('DRAFT', 'Draft'),
        ('RECEIVED', 'Received'),
        ('QUALITY_CHECK', 'Quality Check'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('RETURNED', 'Returned'),
    ]
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='goods_receipts')
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='receipts')
    
    # Receipt details
    receipt_number = models.CharField(max_length=50, unique=True)
    receipt_date = models.DateField()
    delivery_date = models.DateField()
    
    # Delivery details
    delivery_challan_number = models.CharField(max_length=50, blank=True, null=True)
    transporter_name = models.CharField(max_length=200, blank=True, null=True)
    vehicle_number = models.CharField(max_length=20, blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=RECEIPT_STATUS, default='DRAFT')
    
    # Quality check
    quality_check_done = models.BooleanField(default=False)
    quality_check_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='quality_checked_receipts')
    quality_check_date = models.DateField(blank=True, null=True)
    quality_remarks = models.TextField(blank=True, null=True)
    
    # Received by
    received_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_goods')
    
    # Documents
    delivery_challan = models.FileField(upload_to='delivery_challans/', blank=True, null=True)
    invoice = models.FileField(upload_to='supplier_invoices/', blank=True, null=True)
    
    class Meta:
        ordering = ['-receipt_date']
    
    def __str__(self):
        return f"{self.receipt_number} - {self.purchase_order.po_number}"

class GoodsReceiptItem(UUIDModel, TimeStampedModel):
    """Items in goods receipt"""
    ITEM_STATUS = [
        ('RECEIVED', 'Received'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('DAMAGED', 'Damaged'),
        ('SHORT_RECEIVED', 'Short Received'),
    ]
    
    goods_receipt = models.ForeignKey(GoodsReceipt, on_delete=models.CASCADE, related_name='items')
    po_item = models.ForeignKey(PurchaseOrderItem, on_delete=models.CASCADE, related_name='receipt_items')
    
    # Quantities
    quantity_ordered = models.FloatField()
    quantity_received = models.FloatField()
    quantity_accepted = models.FloatField(default=0)
    quantity_rejected = models.FloatField(default=0)
    
    # Status
    status = models.CharField(max_length=20, choices=ITEM_STATUS, default='RECEIVED')
    rejection_reason = models.TextField(blank=True, null=True)
    
    # Pricing
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    
    class Meta:
        unique_together = ['goods_receipt', 'po_item']
    
    def __str__(self):
        return f"{self.goods_receipt.receipt_number} - {self.po_item.inventory_item.name}"

class StockTransaction(UUIDModel, TimeStampedModel):
    """Stock movement transactions"""
    TRANSACTION_TYPES = [
        ('PURCHASE', 'Purchase Receipt'),
        ('ISSUE', 'Stock Issue'),
        ('RETURN', 'Stock Return'),
        ('TRANSFER', 'Stock Transfer'),
        ('ADJUSTMENT', 'Stock Adjustment'),
        ('DAMAGE', 'Damage/Loss'),
        ('AUDIT', 'Stock Audit'),
        ('OPENING', 'Opening Stock'),
    ]
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='stock_transactions')
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='transactions')
    
    # Transaction details
    transaction_number = models.CharField(max_length=50, unique=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    transaction_date = models.DateField()
    
    # Quantities
    quantity = models.FloatField()
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Stock levels after transaction
    stock_before = models.FloatField()
    stock_after = models.FloatField()
    
    # References
    reference_document = models.CharField(max_length=100, blank=True, null=True)
    goods_receipt = models.ForeignKey(GoodsReceipt, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    
    # Department/Location
    from_location = models.CharField(max_length=200, blank=True, null=True)
    to_location = models.CharField(max_length=200, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    
    # Staff
    transaction_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stock_transactions')
    authorized_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='authorized_transactions')
    
    # Additional info
    remarks = models.TextField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        self.total_value = self.quantity * self.unit_cost
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-transaction_date']
        indexes = [
            models.Index(fields=['inventory_item', 'transaction_date']),
            models.Index(fields=['transaction_type']),
        ]
    
    def __str__(self):
        return f"{self.transaction_number} - {self.inventory_item.name} - {self.transaction_type}"

class StockIssue(UUIDModel, TimeStampedModel):
    """Stock issue to departments/staff"""
    ISSUE_STATUS = [
        ('REQUESTED', 'Requested'),
        ('APPROVED', 'Approved'),
        ('ISSUED', 'Issued'),
        ('PARTIALLY_ISSUED', 'Partially Issued'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='stock_issues')
    
    # Issue details
    issue_number = models.CharField(max_length=50, unique=True)
    issue_date = models.DateField()
    
    # Requestor details
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requested_stock_issues')
    department = models.CharField(max_length=100)
    purpose = models.TextField()
    
    # Issue to
    issued_to_employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_stock_issues')
    issued_to_department = models.CharField(max_length=100, blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=ISSUE_STATUS, default='REQUESTED')
    
    # Approval
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_stock_issues')
    approval_date = models.DateField(blank=True, null=True)
    
    # Issue processing
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='issued_stocks')
    
    # Return details
    expected_return_date = models.DateField(blank=True, null=True)
    is_returnable = models.BooleanField(default=False)
    
    # Remarks
    remarks = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-issue_date']
    
    def __str__(self):
        return f"{self.issue_number} - {self.department}"

class StockIssueItem(UUIDModel, TimeStampedModel):
    """Items in stock issue"""
    stock_issue = models.ForeignKey(StockIssue, on_delete=models.CASCADE, related_name='items')
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='issue_items')
    
    # Quantities
    quantity_requested = models.FloatField()
    quantity_approved = models.FloatField(default=0)
    quantity_issued = models.FloatField(default=0)
    
    # Pricing
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Return tracking
    quantity_returned = models.FloatField(default=0)
    quantity_pending_return = models.FloatField(default=0)
    
    def save(self, *args, **kwargs):
        self.total_cost = self.quantity_issued * self.unit_cost
        if self.stock_issue.is_returnable:
            self.quantity_pending_return = self.quantity_issued - self.quantity_returned
        super().save(*args, **kwargs)
    
    class Meta:
        unique_together = ['stock_issue', 'inventory_item']
    
    def __str__(self):
        return f"{self.stock_issue.issue_number} - {self.inventory_item.name}"

class InventoryAudit(UUIDModel, TimeStampedModel):
    """Inventory audit/stock taking"""
    AUDIT_STATUS = [
        ('PLANNED', 'Planned'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('APPROVED', 'Approved'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='inventory_audits')
    
    # Audit details
    audit_number = models.CharField(max_length=50, unique=True)
    audit_date = models.DateField()
    audit_type = models.CharField(max_length=20, choices=[
        ('FULL', 'Full Inventory Audit'),
        ('CYCLE', 'Cycle Count'),
        ('CATEGORY', 'Category Audit'),
        ('LOCATION', 'Location Audit'),
        ('RANDOM', 'Random Audit'),
    ])
    
    # Scope
    categories = models.ManyToManyField(InventoryCategory, blank=True, related_name='audits')
    locations = models.JSONField(default=list, help_text="List of locations to audit")
    
    # Team
    audit_team = models.ManyToManyField(User, related_name='inventory_audits')
    audit_supervisor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='supervised_audits')
    
    # Status
    status = models.CharField(max_length=20, choices=AUDIT_STATUS, default='PLANNED')
    
    # Results
    total_items_audited = models.IntegerField(default=0)
    discrepancies_found = models.IntegerField(default=0)
    total_variance_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Approval
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_audits')
    approval_date = models.DateField(blank=True, null=True)
    
    # Reports
    audit_report = models.FileField(upload_to='audit_reports/', blank=True, null=True)
    
    class Meta:
        ordering = ['-audit_date']
    
    def __str__(self):
        return f"{self.audit_number} - {self.audit_date}"

class InventoryAuditItem(UUIDModel, TimeStampedModel):
    """Individual item audit records"""
    audit = models.ForeignKey(InventoryAudit, on_delete=models.CASCADE, related_name='audit_items')
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='audit_records')
    
    # Stock levels
    system_stock = models.FloatField()
    physical_stock = models.FloatField()
    variance = models.FloatField()
    variance_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Audit details
    audited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audited_items')
    audit_date = models.DateField()
    
    # Discrepancy details
    has_discrepancy = models.BooleanField(default=False)
    discrepancy_reason = models.TextField(blank=True, null=True)
    action_taken = models.TextField(blank=True, null=True)
    
    # Photos for evidence
    audit_photo = models.ImageField(upload_to='audit_photos/', blank=True, null=True)
    
    def save(self, *args, **kwargs):
        self.variance = self.physical_stock - self.system_stock
        self.variance_value = self.variance * self.inventory_item.average_cost
        self.has_discrepancy = abs(self.variance) > 0.01  # Tolerance for rounding
        super().save(*args, **kwargs)
    
    class Meta:
        unique_together = ['audit', 'inventory_item']
    
    def __str__(self):
        return f"{self.audit.audit_number} - {self.inventory_item.name}"

class InventoryReport(UUIDModel, TimeStampedModel):
    """Inventory reports and analytics"""
    REPORT_TYPES = [
        ('STOCK_SUMMARY', 'Stock Summary'),
        ('LOW_STOCK', 'Low Stock Report'),
        ('DEAD_STOCK', 'Dead Stock Report'),
        ('FAST_MOVING', 'Fast Moving Items'),
        ('SLOW_MOVING', 'Slow Moving Items'),
        ('STOCK_VALUATION', 'Stock Valuation'),
        ('CONSUMPTION_ANALYSIS', 'Consumption Analysis'),
        ('SUPPLIER_PERFORMANCE', 'Supplier Performance'),
        ('PURCHASE_ANALYSIS', 'Purchase Analysis'),
        ('AUDIT_SUMMARY', 'Audit Summary'),
        ('ABC_ANALYSIS', 'ABC Analysis'),
        ('ASSET_REGISTER', 'Asset Register'),
    ]
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='inventory_reports')
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_inventory_reports')
    
    # Report parameters
    from_date = models.DateField(blank=True, null=True)
    to_date = models.DateField(blank=True, null=True)
    report_data = models.JSONField(default=dict)
    
    # Filters
    category_filter = models.ForeignKey(InventoryCategory, on_delete=models.SET_NULL, null=True, blank=True)
    supplier_filter = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    location_filter = models.CharField(max_length=200, blank=True, null=True)
    
    # File
    report_file = models.FileField(upload_to='inventory_reports/', blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.school.name} - {self.report_type} - {self.created_at.date()}"
