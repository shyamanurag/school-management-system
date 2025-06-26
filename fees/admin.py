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
    list_display = ['school', 'academic_year', 'school_class', 'name', 'is_active']
    list_filter = ['school', 'academic_year', 'is_active']
    
@admin.register(FeeItem)
class FeeItemAdmin(admin.ModelAdmin):
    list_display = ['fee_structure', 'fee_category', 'amount', 'due_date']
    list_filter = ['fee_category', 'due_date']

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'payment_type', 'school', 'is_active']
    list_filter = ['payment_type', 'school', 'is_active']

@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'student', 'amount_paid', 'payment_date', 'status']
    list_filter = ['status', 'payment_date', 'payment_method']
    search_fields = ['receipt_number', 'student__first_name', 'student__last_name']

@admin.register(FeeDiscount)
class FeeDiscountAdmin(admin.ModelAdmin):
    list_display = ['name', 'discount_type', 'school', 'is_active']
    list_filter = ['discount_type', 'school', 'is_active']

@admin.register(FeeInstallment)
class FeeInstallmentAdmin(admin.ModelAdmin):
    list_display = ['student_fee_assignment', 'installment_name', 'net_amount', 'due_date', 'is_paid']
    list_filter = ['installment_type', 'due_date', 'is_paid']
    search_fields = ['student_fee_assignment__student__first_name', 'installment_name']

@admin.register(FeeRefund)
class FeeRefundAdmin(admin.ModelAdmin):
    list_display = ['student', 'refund_type', 'refund_amount', 'status', 'requested_date']
    list_filter = ['refund_type', 'status', 'requested_date']
    search_fields = ['student__first_name', 'student__last_name']

@admin.register(FeeDefaulter)
class FeeDefaulterAdmin(admin.ModelAdmin):
    list_display = ['student', 'overdue_amount', 'overdue_days', 'first_notice_sent', 'is_resolved']
    list_filter = ['first_notice_sent', 'second_notice_sent', 'is_resolved']
    search_fields = ['student__first_name', 'student__last_name']

# Register your models here.
