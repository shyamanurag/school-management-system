from django.contrib import admin
from .models import *

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'school', 'head_of_department', 'is_active']
    list_filter = ['school', 'is_active']
    search_fields = ['name', 'code']

@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ['title', 'code', 'department', 'level', 'is_active']
    list_filter = ['department', 'level', 'is_active']
    search_fields = ['title', 'code']

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'full_name', 'department', 'designation', 'employment_status']
    list_filter = ['department', 'designation', 'employee_type', 'employment_status']
    search_fields = ['employee_id', 'first_name', 'last_name', 'email']
    readonly_fields = ['employee_id']

@admin.register(SalaryStructure)
class SalaryStructureAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'school', 'basic_salary', 'is_active']
    list_filter = ['school', 'is_active']
    search_fields = ['name', 'code']

@admin.register(EmployeeSalary)
class EmployeeSalaryAdmin(admin.ModelAdmin):
    list_display = ['employee', 'salary_structure', 'basic_salary', 'gross_salary', 'effective_from']
    list_filter = ['salary_structure', 'effective_from']
    search_fields = ['employee__employee_id', 'employee__first_name', 'employee__last_name']

@admin.register(Payslip)
class PayslipAdmin(admin.ModelAdmin):
    list_display = ['employee', 'payroll_month', 'gross_earnings', 'total_deductions', 'net_salary', 'is_paid']
    list_filter = ['payroll_month', 'is_paid']
    search_fields = ['employee__employee_id', 'employee__first_name', 'employee__last_name']

@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'school', 'annual_allocation', 'is_paid', 'is_active']
    list_filter = ['school', 'is_paid', 'is_active']
    search_fields = ['name', 'code']

@admin.register(LeaveApplication)
class LeaveApplicationAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'from_date', 'to_date', 'total_days', 'status']
    list_filter = ['leave_type', 'status', 'applied_date']
    search_fields = ['employee__employee_id', 'employee__first_name', 'employee__last_name'] 