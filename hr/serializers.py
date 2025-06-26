from rest_framework import serializers
from .models import (
    Department, Designation, Employee, EmployeeDocument, SalaryStructure,
    EmployeeSalary, PayrollMonth, Payslip, LeaveType, EmployeeLeaveBalance,
    LeaveApplication
)

class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for Department model"""
    total_employees = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_total_employees(self, obj):
        return obj.employees.filter(employment_status='ACTIVE').count()

class DesignationSerializer(serializers.ModelSerializer):
    """Serializer for Designation model"""
    department_name = serializers.CharField(source='department.name', read_only=True)
    total_employees = serializers.SerializerMethodField()
    
    class Meta:
        model = Designation
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_total_employees(self, obj):
        return obj.employees.filter(employment_status='ACTIVE').count()

class EmployeeSerializer(serializers.ModelSerializer):
    """Serializer for Employee model"""
    department_name = serializers.CharField(source='department.name', read_only=True)
    designation_title = serializers.CharField(source='designation.title', read_only=True)
    reporting_manager_name = serializers.CharField(source='reporting_manager.full_name', read_only=True)
    age = serializers.ReadOnlyField()
    service_years = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'age']
        extra_kwargs = {
            'password': {'write_only': True},
            'aadhar_number': {'write_only': True},
            'pan_number': {'write_only': True},
        }
    
    def get_service_years(self, obj):
        from django.utils import timezone
        return round((timezone.now().date() - obj.date_of_joining).days / 365.25, 1)

class EmployeeDocumentSerializer(serializers.ModelSerializer):
    """Serializer for Employee Document model"""
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    verified_by_name = serializers.CharField(source='verified_by.get_full_name', read_only=True)
    
    class Meta:
        model = EmployeeDocument
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'file_size', 'is_verified', 'verified_by', 'verified_at']

class SalaryStructureSerializer(serializers.ModelSerializer):
    """Serializer for Salary Structure model"""
    calculated_gross_salary = serializers.SerializerMethodField()
    applicable_designation_names = serializers.SerializerMethodField()
    
    class Meta:
        model = SalaryStructure
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_calculated_gross_salary(self, obj):
        hra = (obj.basic_salary * obj.hra_percentage) / 100
        da = (obj.basic_salary * obj.da_percentage) / 100
        return float(
            obj.basic_salary + hra + da + 
            obj.transport_allowance + obj.medical_allowance + 
            obj.education_allowance + obj.special_allowance + obj.other_allowances
        )
    
    def get_applicable_designation_names(self, obj):
        return list(obj.applicable_designations.values_list('title', flat=True))

class EmployeeSalarySerializer(serializers.ModelSerializer):
    """Serializer for Employee Salary model"""
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    salary_structure_name = serializers.CharField(source='salary_structure.name', read_only=True)
    
    class Meta:
        model = EmployeeSalary
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'gross_salary']

class PayrollMonthSerializer(serializers.ModelSerializer):
    """Serializer for Payroll Month model"""
    processed_by_name = serializers.CharField(source='processed_by.get_full_name', read_only=True)
    locked_by_name = serializers.CharField(source='locked_by.get_full_name', read_only=True)
    month_name = serializers.SerializerMethodField()
    
    class Meta:
        model = PayrollMonth
        fields = '__all__'
        read_only_fields = [
            'created_at', 'updated_at', 'is_processed', 'processed_date', 
            'processed_by', 'total_employees', 'total_gross_salary', 
            'total_deductions', 'total_net_salary'
        ]
    
    def get_month_name(self, obj):
        months = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        return f"{months[obj.month - 1]} {obj.year}"

class PayslipSerializer(serializers.ModelSerializer):
    """Serializer for Payslip model"""
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    department_name = serializers.CharField(source='employee.department.name', read_only=True)
    designation_title = serializers.CharField(source='employee.designation.title', read_only=True)
    payroll_month_name = serializers.CharField(source='payroll_month.__str__', read_only=True)
    
    class Meta:
        model = Payslip
        fields = '__all__'
        read_only_fields = [
            'created_at', 'updated_at', 'gross_earnings', 
            'total_deductions', 'net_salary'
        ]

class LeaveTypeSerializer(serializers.ModelSerializer):
    """Serializer for Leave Type model"""
    total_applications = serializers.SerializerMethodField()
    
    class Meta:
        model = LeaveType
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_total_applications(self, obj):
        return obj.applications.count()

class EmployeeLeaveBalanceSerializer(serializers.ModelSerializer):
    """Serializer for Employee Leave Balance model"""
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    
    class Meta:
        model = EmployeeLeaveBalance
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'available_days']

class LeaveApplicationSerializer(serializers.ModelSerializer):
    """Serializer for Leave Application model"""
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    work_handover_to_name = serializers.CharField(source='work_handover_to.full_name', read_only=True)
    
    class Meta:
        model = LeaveApplication
        fields = '__all__'
        read_only_fields = [
            'created_at', 'updated_at', 'total_days', 'applied_date',
            'approved_by', 'approved_date'
        ] 