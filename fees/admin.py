from django.contrib import admin
from .models import (
    FeeCategory, 
    FeeStructure, 
    FeeItem, 
    PaymentMethod, 
    StudentFeeAssignment, 
    FeeInstallment, 
    FeePayment, 
    FeeRefund, 
    FeeDiscount, 
    FeeDefaulter, 
    FeeReport, 
    FeeConcession
)

@admin.register(FeeCategory)
class FeeCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'school', 'is_active']
    list_filter = ['school', 'is_active']
    search_fields = ['name', 'code']

@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ['school', 'academic_year', 'school_class', 'total_annual_fee', 'is_active']
    list_filter = ['school', 'academic_year', 'is_active']
    
@admin.register(FeeItem)
class FeeItemAdmin(admin.ModelAdmin):
    list_display = ['fee_structure', 'category', 'amount', 'due_date']
    list_filter = ['category', 'due_date']

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'payment_type', 'school', 'is_active']
    list_filter = ['payment_type', 'school', 'is_active']

@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_number', 'student', 'amount_paid', 'payment_date', 'status']
    list_filter = ['status', 'payment_date', 'payment_method']
    search_fields = ['payment_number', 'student__first_name', 'student__last_name']

@admin.register(FeeDiscount)
class FeeDiscountAdmin(admin.ModelAdmin):
    list_display = ['name', 'discount_type', 'school', 'is_active']
    list_filter = ['discount_type', 'school', 'is_active']

# Register your models here.
