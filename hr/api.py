from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Avg, Sum, Max, Min
from django.utils import timezone
from datetime import timedelta, datetime
from .models import (
    Department, Designation, Employee, EmployeeDocument, SalaryStructure,
    EmployeeSalary, PayrollMonth, Payslip, LeaveType, EmployeeLeaveBalance,
    LeaveApplication
)
from .serializers import (
    DepartmentSerializer, DesignationSerializer, EmployeeSerializer,
    EmployeeDocumentSerializer, SalaryStructureSerializer, EmployeeSalarySerializer,
    PayrollMonthSerializer, PayslipSerializer, LeaveTypeSerializer,
    EmployeeLeaveBalanceSerializer, LeaveApplicationSerializer
)

class DepartmentViewSet(viewsets.ModelViewSet):
    """API endpoints for Department management"""
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Department.objects.filter(school=self.request.user.profile.school)
    
    @action(detail=True, methods=['get'])
    def employees(self, request, pk=None):
        """Get all employees in this department"""
        department = self.get_object()
        employees = department.employees.filter(employment_status='ACTIVE')
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get department analytics"""
        department = self.get_object()
        employees = department.employees.filter(employment_status='ACTIVE')
        
        analytics = {
            'total_employees': employees.count(),
            'employee_types': employees.values('employee_type').annotate(count=Count('id')),
            'average_experience': employees.aggregate(avg=Avg('total_experience_years'))['avg'] or 0,
            'gender_distribution': employees.values('gender').annotate(count=Count('id')),
            'designations': employees.values('designation__title').annotate(count=Count('id'))
        }
        return Response(analytics)

class DesignationViewSet(viewsets.ModelViewSet):
    """API endpoints for Designation management"""
    serializer_class = DesignationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Designation.objects.filter(school=self.request.user.profile.school)
    
    @action(detail=True, methods=['get'])
    def employees(self, request, pk=None):
        """Get all employees with this designation"""
        designation = self.get_object()
        employees = designation.employees.filter(employment_status='ACTIVE')
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data)

class EmployeeViewSet(viewsets.ModelViewSet):
    """API endpoints for Employee management"""
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Employee.objects.filter(school=self.request.user.profile.school)
    
    @action(detail=True, methods=['get'])
    def profile_summary(self, request, pk=None):
        """Get comprehensive employee profile summary"""
        employee = self.get_object()
        
        # Leave balance
        current_year = timezone.now().year
        leave_balances = employee.leave_balances.filter(
            academic_year__name__contains=str(current_year)
        )
        
        # Recent payslips
        recent_payslips = employee.payslips.order_by('-payroll_month__year', '-payroll_month__month')[:3]
        
        # Documents status
        document_stats = {
            'total_documents': employee.documents.count(),
            'verified_documents': employee.documents.filter(is_verified=True).count(),
            'pending_verification': employee.documents.filter(is_verified=False).count()
        }
        
        summary = {
            'employee_details': EmployeeSerializer(employee).data,
            'leave_balances': EmployeeLeaveBalanceSerializer(leave_balances, many=True).data,
            'recent_payslips': PayslipSerializer(recent_payslips, many=True).data,
            'document_status': document_stats,
            'service_years': round((timezone.now().date() - employee.date_of_joining).days / 365.25, 1)
        }
        return Response(summary)
    
    @action(detail=True, methods=['get'])
    def attendance_summary(self, request, pk=None):
        """Get employee attendance summary"""
        employee = self.get_object()
        from_date = request.query_params.get('from_date', (timezone.now().date() - timedelta(days=30)).isoformat())
        to_date = request.query_params.get('to_date', timezone.now().date().isoformat())
        
        # This would integrate with attendance system
        summary = {
            'period': f"{from_date} to {to_date}",
            'working_days': 22,  # Sample data
            'present_days': 20,
            'absent_days': 2,
            'late_arrivals': 1,
            'early_departures': 0,
            'attendance_percentage': 90.9
        }
        return Response(summary)
    
    @action(detail=True, methods=['post'])
    def update_employment_status(self, request, pk=None):
        """Update employee employment status"""
        employee = self.get_object()
        new_status = request.data.get('status')
        reason = request.data.get('reason', '')
        
        if new_status in dict(Employee.EMPLOYMENT_STATUS):
            employee.employment_status = new_status
            if new_status in ['TERMINATED', 'RESIGNED', 'RETIRED']:
                employee.last_working_date = timezone.now().date()
                employee.reason_for_leaving = reason
            employee.save()
            
            return Response({'status': 'Employment status updated successfully'})
        
        return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

class EmployeeDocumentViewSet(viewsets.ModelViewSet):
    """API endpoints for Employee Document management"""
    serializer_class = EmployeeDocumentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return EmployeeDocument.objects.filter(employee__school=self.request.user.profile.school)
    
    @action(detail=True, methods=['post'])
    def verify_document(self, request, pk=None):
        """Verify an employee document"""
        document = self.get_object()
        document.is_verified = True
        document.verified_by = request.user
        document.verified_at = timezone.now()
        document.verification_notes = request.data.get('notes', '')
        document.save()
        
        return Response({'status': 'Document verified successfully'})

class SalaryStructureViewSet(viewsets.ModelViewSet):
    """API endpoints for Salary Structure management"""
    serializer_class = SalaryStructureSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SalaryStructure.objects.filter(school=self.request.user.profile.school)
    
    @action(detail=True, methods=['get'])
    def salary_breakdown(self, request, pk=None):
        """Get detailed salary breakdown"""
        structure = self.get_object()
        
        # Calculate components
        basic = structure.basic_salary
        hra = (basic * structure.hra_percentage) / 100
        da = (basic * structure.da_percentage) / 100
        
        gross_salary = (
            basic + hra + da + 
            structure.transport_allowance + structure.medical_allowance + 
            structure.education_allowance + structure.special_allowance + 
            structure.other_allowances
        )
        
        # Calculate deductions
        pf_employee = (basic * structure.pf_percentage) / 100 if structure.pf_applicable else 0
        esi_employee = (gross_salary * structure.esi_percentage) / 100 if structure.esi_applicable else 0
        
        total_deductions = (
            pf_employee + esi_employee + structure.professional_tax_amount
        )
        
        net_salary = gross_salary - total_deductions
        
        breakdown = {
            'basic_salary': float(basic),
            'hra': float(hra),
            'da': float(da),
            'transport_allowance': float(structure.transport_allowance),
            'medical_allowance': float(structure.medical_allowance),
            'education_allowance': float(structure.education_allowance),
            'special_allowance': float(structure.special_allowance),
            'other_allowances': float(structure.other_allowances),
            'gross_salary': float(gross_salary),
            'pf_employee': float(pf_employee),
            'esi_employee': float(esi_employee),
            'professional_tax': float(structure.professional_tax_amount),
            'total_deductions': float(total_deductions),
            'net_salary': float(net_salary)
        }
        
        return Response(breakdown)

class PayrollMonthViewSet(viewsets.ModelViewSet):
    """API endpoints for Payroll Month management"""
    serializer_class = PayrollMonthSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PayrollMonth.objects.filter(school=self.request.user.profile.school)
    
    @action(detail=True, methods=['post'])
    def process_payroll(self, request, pk=None):
        """Process payroll for the month"""
        payroll_month = self.get_object()
        
        if payroll_month.is_processed:
            return Response({'error': 'Payroll already processed'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get all active employees
        employees = Employee.objects.filter(
            school=payroll_month.school,
            employment_status='ACTIVE'
        )
        
        total_gross = 0
        total_deductions = 0
        total_net = 0
        
        for employee in employees:
            if hasattr(employee, 'salary_config'):
                # Create payslip logic would go here
                # This is a simplified version
                payslip_data = self._calculate_payslip(employee, payroll_month)
                total_gross += payslip_data['gross_earnings']
                total_deductions += payslip_data['total_deductions']
                total_net += payslip_data['net_salary']
        
        # Update payroll month
        payroll_month.is_processed = True
        payroll_month.processed_date = timezone.now().date()
        payroll_month.processed_by = request.user
        payroll_month.total_employees = employees.count()
        payroll_month.total_gross_salary = total_gross
        payroll_month.total_deductions = total_deductions
        payroll_month.total_net_salary = total_net
        payroll_month.save()
        
        return Response({'status': 'Payroll processed successfully'})
    
    def _calculate_payslip(self, employee, payroll_month):
        """Helper method to calculate payslip"""
        # Simplified calculation - in reality this would be more complex
        salary_config = employee.salary_config
        
        gross_earnings = salary_config.gross_salary
        total_deductions = gross_earnings * 0.15  # Simplified 15% deductions
        net_salary = gross_earnings - total_deductions
        
        return {
            'gross_earnings': gross_earnings,
            'total_deductions': total_deductions,
            'net_salary': net_salary
        }
    
    @action(detail=True, methods=['get'])
    def payroll_summary(self, request, pk=None):
        """Get payroll summary for the month"""
        payroll_month = self.get_object()
        
        payslips = payroll_month.payslips.all()
        
        summary = {
            'total_employees': payslips.count(),
            'total_gross_salary': sum(p.gross_earnings for p in payslips),
            'total_deductions': sum(p.total_deductions for p in payslips),
            'total_net_salary': sum(p.net_salary for p in payslips),
            'payment_status': {
                'paid': payslips.filter(is_paid=True).count(),
                'pending': payslips.filter(is_paid=False).count()
            },
            'department_wise_summary': self._get_department_wise_summary(payslips)
        }
        
        return Response(summary)
    
    def _get_department_wise_summary(self, payslips):
        """Get department-wise payroll summary"""
        dept_summary = {}
        for payslip in payslips:
            dept = payslip.employee.department.name
            if dept not in dept_summary:
                dept_summary[dept] = {
                    'employees': 0,
                    'gross_salary': 0,
                    'net_salary': 0
                }
            dept_summary[dept]['employees'] += 1
            dept_summary[dept]['gross_salary'] += float(payslip.gross_earnings)
            dept_summary[dept]['net_salary'] += float(payslip.net_salary)
        
        return dept_summary

class PayslipViewSet(viewsets.ModelViewSet):
    """API endpoints for Payslip management"""
    serializer_class = PayslipSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'employee_profile'):
            # Employee can only see their own payslips
            return Payslip.objects.filter(employee=user.employee_profile)
        else:
            # Admin/HR can see all payslips
            return Payslip.objects.filter(employee__school=user.profile.school)
    
    @action(detail=True, methods=['post'])
    def mark_as_paid(self, request, pk=None):
        """Mark payslip as paid"""
        payslip = self.get_object()
        payslip.is_paid = True
        payslip.payment_date = timezone.now().date()
        payslip.payment_reference = request.data.get('payment_reference', '')
        payslip.save()
        
        return Response({'status': 'Payslip marked as paid'})

class LeaveTypeViewSet(viewsets.ModelViewSet):
    """API endpoints for Leave Type management"""
    serializer_class = LeaveTypeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return LeaveType.objects.filter(school=self.request.user.profile.school)

class LeaveApplicationViewSet(viewsets.ModelViewSet):
    """API endpoints for Leave Application management"""
    serializer_class = LeaveApplicationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'employee_profile'):
            # Employee can see their own applications and those they need to approve
            return LeaveApplication.objects.filter(
                Q(employee=user.employee_profile) |
                Q(employee__reporting_manager=user.employee_profile)
            )
        else:
            # Admin/HR can see all applications
            return LeaveApplication.objects.filter(employee__school=user.profile.school)
    
    @action(detail=True, methods=['post'])
    def approve_leave(self, request, pk=None):
        """Approve leave application"""
        leave_application = self.get_object()
        
        if leave_application.status != 'SUBMITTED':
            return Response({'error': 'Only submitted applications can be approved'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        leave_application.status = 'APPROVED'
        leave_application.approved_by = request.user
        leave_application.approved_date = timezone.now().date()
        leave_application.save()
        
        # Update leave balance
        self._update_leave_balance(leave_application)
        
        return Response({'status': 'Leave application approved'})
    
    @action(detail=True, methods=['post'])
    def reject_leave(self, request, pk=None):
        """Reject leave application"""
        leave_application = self.get_object()
        
        if leave_application.status != 'SUBMITTED':
            return Response({'error': 'Only submitted applications can be rejected'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        leave_application.status = 'REJECTED'
        leave_application.approved_by = request.user
        leave_application.approved_date = timezone.now().date()
        leave_application.rejection_reason = request.data.get('reason', '')
        leave_application.save()
        
        return Response({'status': 'Leave application rejected'})
    
    def _update_leave_balance(self, leave_application):
        """Update employee leave balance after approval"""
        try:
            balance = EmployeeLeaveBalance.objects.get(
                employee=leave_application.employee,
                leave_type=leave_application.leave_type,
                academic_year__name__contains=str(timezone.now().year)
            )
            balance.used_days += leave_application.total_days
            balance.save()
        except EmployeeLeaveBalance.DoesNotExist:
            pass
    
    @action(detail=False, methods=['get'])
    def leave_calendar(self, request):
        """Get leave calendar for the month"""
        month = int(request.query_params.get('month', timezone.now().month))
        year = int(request.query_params.get('year', timezone.now().year))
        
        # Get approved leaves for the month
        leaves = self.get_queryset().filter(
            status='APPROVED',
            from_date__month=month,
            from_date__year=year
        )
        
        calendar_data = []
        for leave in leaves:
            calendar_data.append({
                'employee_name': leave.employee.full_name,
                'leave_type': leave.leave_type.name,
                'from_date': leave.from_date,
                'to_date': leave.to_date,
                'total_days': leave.total_days,
                'reason': leave.reason
            })
        
        return Response(calendar_data)

class EmployeeLeaveBalanceViewSet(viewsets.ModelViewSet):
    """API endpoints for Employee Leave Balance management"""
    serializer_class = EmployeeLeaveBalanceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'employee_profile'):
            return EmployeeLeaveBalance.objects.filter(employee=user.employee_profile)
        else:
            return EmployeeLeaveBalance.objects.filter(employee__school=user.profile.school)
    
    @action(detail=False, methods=['get'])
    def my_leave_balance(self, request):
        """Get current user's leave balance"""
        if not hasattr(request.user, 'employee_profile'):
            return Response({'error': 'User is not an employee'}, status=status.HTTP_400_BAD_REQUEST)
        
        current_year = timezone.now().year
        balances = self.get_queryset().filter(
            academic_year__name__contains=str(current_year)
        )
        
        serializer = self.get_serializer(balances, many=True)
        return Response(serializer.data) 