from django.contrib import admin
from .models import (
    InventoryCategory,
    Supplier,
    Brand,
    InventoryItem,
    PurchaseOrder,
    StockTransaction,
    StockIssue,
    InventoryAudit
)

@admin.register(InventoryCategory)
class InventoryCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'school', 'is_active']
    list_filter = ['school', 'is_active']
    search_fields = ['name', 'code']

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'school', 'contact_person', 'is_active']
    list_filter = ['school', 'is_active']

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'item_code', 'category', 'current_stock', 'standard_cost']
    list_filter = ['category', 'preferred_supplier', 'item_type']
    search_fields = ['name', 'item_code']

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['po_number', 'supplier', 'po_date', 'total_amount', 'status']
    list_filter = ['status', 'po_date', 'supplier']
    search_fields = ['po_number', 'supplier__name']

@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_number', 'inventory_item', 'transaction_type', 'quantity', 'transaction_date']
    list_filter = ['transaction_type', 'transaction_date']
    search_fields = ['transaction_number', 'inventory_item__name']

@admin.register(StockIssue)
class StockIssueAdmin(admin.ModelAdmin):
    list_display = ['issue_number', 'issued_to_employee', 'department', 'status', 'issue_date']
    list_filter = ['status', 'issue_date', 'department']
    search_fields = ['issue_number', 'issued_to_employee__user__first_name']

@admin.register(InventoryAudit)
class InventoryAuditAdmin(admin.ModelAdmin):
    list_display = ['audit_number', 'audit_date', 'audit_type', 'status', 'total_items_audited']
    list_filter = ['audit_type', 'status', 'audit_date']
    search_fields = ['audit_number']

# Register your models here.
