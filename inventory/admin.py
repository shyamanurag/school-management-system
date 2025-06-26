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

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'item_code', 'category', 'current_stock', 'unit_price']
    list_filter = ['category', 'supplier']
    search_fields = ['name', 'item_code']

@admin.register(StockIssue)
class StockIssueAdmin(admin.ModelAdmin):
    list_display = ['issue_number', 'issued_to_user', 'total_value', 'status']
    list_filter = ['status', 'issue_date']

# Register your models here.
