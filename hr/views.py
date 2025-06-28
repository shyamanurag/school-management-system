from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Count, Avg, Sum, F
from django.utils import timezone
from datetime import datetime, timedelta, date
from core.models import (
    Employee, Department, LeaveApplication, LeaveType, 
    PerformanceReview, TrainingProgram, TrainingEnrollment,
    EmployeePayroll, HRAnalytics, PayrollStructure
)
from django.contrib.auth.models import User
import csv
from decimal import Decimal

# ===== HR DASHBOARD =====
@login_required
def hr_dashboard(request):
    """Enterprise HR Dashboard with Comprehensive Analytics"""
    today = timezone.now().date()
    current_month = today.month
    current_year = today.year
    
    # Core HR Statistics
    total_employees = Employee.objects.filter(employment_status='ACTIVE').count()
    new_hires_month = Employee.objects.filter(
        date_of_joining__month=current_month,
        date_of_joining__year=current_year
    ).count()
    
    # Payroll Statistics
    current_payroll = EmployeePayroll.objects.filter(
        pay_period_start__month=current_month,
        pay_period_start__year=current_year
    )
    total_payroll_cost = current_payroll.aggregate(total=Sum('net_salary'))['total'] or 0
    pending_payroll = current_payroll.filter(is_processed=False).count()
    
    # Leave Statistics
    pending_leave_requests = LeaveApplication.objects.filter(status='PENDING').count()
    approved_leaves_month = LeaveApplication.objects.filter(
        status='APPROVED',
        start_date__month=current_month,
        start_date__year=current_year
    ).count()
    
    # Training Statistics
    active_training_programs = TrainingProgram.objects.filter(is_active=True).count()
    employees_in_training = TrainingEnrollment.objects.filter(
        status__in=['REGISTERED', 'CONFIRMED', 'ATTENDED']
    ).values('employee').distinct().count()
    
    # Performance Reviews
    pending_reviews = PerformanceReview.objects.filter(
        status__in=['DRAFT', 'SELF_ASSESSMENT', 'MANAGER_REVIEW']
    ).count()
    
    # Department-wise Employee Distribution
    department_stats = Employee.objects.filter(
        employment_status='ACTIVE'
    ).values(
        'department__name'
    ).annotate(
        employee_count=Count('id'),
        avg_salary=Avg('basic_salary')
    ).order_by('-employee_count')
    
    # Recent Activities
    recent_hires = Employee.objects.filter(
        employment_status='ACTIVE'
    ).order_by('-date_of_joining')[:5]
    
    recent_leave_requests = LeaveApplication.objects.select_related(
        'employee', 'leave_type'
    ).order_by('-created_at')[:10]
    
    # Monthly Trends
    monthly_hires = Employee.objects.filter(
        date_of_joining__year=current_year
    ).extra(
        select={'month': "EXTRACT(month FROM date_of_joining)"}
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    context = {
        'page_title': 'HR Management Dashboard',
        'total_employees': total_employees,
        'new_hires_month': new_hires_month,
        'total_payroll_cost': total_payroll_cost,
        'pending_payroll': pending_payroll,
        'pending_leave_requests': pending_leave_requests,
        'approved_leaves_month': approved_leaves_month,
        'active_training_programs': active_training_programs,
        'employees_in_training': employees_in_training,
        'pending_reviews': pending_reviews,
        'department_stats': department_stats,
        'recent_hires': recent_hires,
        'recent_leave_requests': recent_leave_requests,
        'monthly_hires': list(monthly_hires),
    }
    
    return render(request, 'hr/dashboard.html', context)

# ===== EMPLOYEE MANAGEMENT =====
class EmployeeListView(LoginRequiredMixin, ListView):
    model = Employee
    template_name = 'hr/employee_list.html'
    context_object_name = 'employees'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = Employee.objects.select_related('department', 'user').filter(
            employment_status='ACTIVE'
        ).order_by('employee_id')
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(employee_id__icontains=search) |
                Q(designation__icontains=search)
            )
        
        # Department filter
        department = self.request.GET.get('department')
        if department:
            queryset = queryset.filter(department_id=department)
            
        # Employment type filter
        emp_type = self.request.GET.get('employment_type')
        if emp_type:
            queryset = queryset.filter(employment_type=emp_type)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Employee Management'
        context['departments'] = Department.objects.filter(is_active=True)
        context['employment_types'] = Employee.EMPLOYMENT_TYPES
        context['total_employees'] = Employee.objects.filter(employment_status='ACTIVE').count()
        return context

class EmployeeDetailView(LoginRequiredMixin, DetailView):
    model = Employee
    template_name = 'hr/employee_detail.html'
    context_object_name = 'employee'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = self.object
        
        # Payroll History
        payroll_history = EmployeePayroll.objects.filter(
            employee=employee
        ).order_by('-pay_period_start')[:12]
        
        # Leave History
        leave_history = LeaveApplication.objects.filter(
            employee=employee
        ).select_related('leave_type').order_by('-start_date')[:10]
        
        # Performance Reviews
        performance_reviews = PerformanceReview.objects.filter(
            employee=employee
        ).order_by('-review_period_start')[:5]
        
        # Training History
        training_history = TrainingEnrollment.objects.filter(
            employee=employee
        ).select_related('training_program').order_by('-enrollment_date')[:10]
        
        # Calculate metrics
        total_leave_days = leave_history.filter(status='APPROVED').aggregate(
            total=Sum('total_days')
        )['total'] or 0
        
        avg_performance = performance_reviews.aggregate(
            avg=Avg('overall_rating')
        )['avg'] or 0
        
        context.update({
            'page_title': f'Employee - {employee.full_name}',
            'payroll_history': payroll_history,
            'leave_history': leave_history,
            'performance_reviews': performance_reviews,
            'training_history': training_history,
            'total_leave_days': total_leave_days,
            'avg_performance': round(avg_performance, 1),
        })
        return context

class EmployeeCreateView(LoginRequiredMixin, CreateView):
    model = Employee
    template_name = 'hr/employee_form.html'
    fields = [
        'user', 'employee_id', 'date_of_birth', 'gender', 'marital_status',
        'phone', 'current_address', 'emergency_contact_name', 'emergency_contact_phone',
        'employment_type', 'date_of_joining', 'department', 'designation',
        'qualification', 'basic_salary', 'gross_salary'
    ]
    
    def get_success_url(self):
        return reverse_lazy('hr:employee-detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Add New Employee'
        return context

class EmployeeUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Employee
    template_name = 'hr/employee_form.html'
    fields = [
        'employment_status', 'employment_type', 'department', 'designation',
        'phone', 'current_address', 'emergency_contact_name',
        'emergency_contact_phone', 'basic_salary', 'gross_salary'
    ]
    permission_required = 'core.change_employee'
    
    def get_success_url(self):
        return reverse_lazy('hr:employee-detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Edit Employee - {self.object.full_name}'
        return context

@login_required
def export_employees(request):
    """Export employee data to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="employees_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Employee ID', 'Name', 'Department', 'Designation', 'Employment Type',
        'Date of Joining', 'Basic Salary', 'Phone', 'Email'
    ])
    
    employees = Employee.objects.select_related('user', 'department').filter(
        employment_status='ACTIVE'
    ).order_by('employee_id')
    
    for emp in employees:
        writer.writerow([
            emp.employee_id,
            emp.full_name,
            emp.department.name if emp.department else '',
            emp.designation,
            emp.get_employment_type_display(),
            emp.date_of_joining,
            emp.basic_salary,
            emp.phone,
            emp.user.email if emp.user else '',
        ])
    
    return response

# ===== LEAVE MANAGEMENT =====
class LeaveApplicationListView(LoginRequiredMixin, ListView):
    model = LeaveApplication
    template_name = 'hr/leave_list.html'
    context_object_name = 'leave_applications'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = LeaveApplication.objects.select_related(
            'employee', 'employee__user', 'leave_type'
        ).order_by('-start_date')
        
        # Status filter
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Leave Management'
        context['leave_statuses'] = LeaveApplication.LEAVE_STATUS
        context['pending_count'] = LeaveApplication.objects.filter(status='PENDING').count()
        return context

@login_required
def approve_leave(request, leave_id):
    """Approve leave application"""
    leave_app = get_object_or_404(LeaveApplication, id=leave_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        remarks = request.POST.get('remarks')
        
        if action == 'approve':
            leave_app.status = 'APPROVED'
            leave_app.approved_by = request.user
            leave_app.approval_date = timezone.now()
            leave_app.approval_remarks = remarks
            messages.success(request, 'Leave application approved successfully')
        elif action == 'reject':
            leave_app.status = 'REJECTED'
            leave_app.approved_by = request.user
            leave_app.approval_date = timezone.now()
            leave_app.approval_remarks = remarks
            messages.success(request, 'Leave application rejected')
        
        leave_app.save()
        return redirect('hr:leave-list')
    
    context = {
        'page_title': 'Review Leave Application',
        'leave_application': leave_app,
    }
    return render(request, 'hr/approve_leave.html', context)

# ===== PERFORMANCE MANAGEMENT =====
class PerformanceReviewListView(LoginRequiredMixin, ListView):
    model = PerformanceReview
    template_name = 'hr/performance_list.html'
    context_object_name = 'reviews'
    paginate_by = 25
    
    def get_queryset(self):
        return PerformanceReview.objects.select_related(
            'employee', 'employee__user', 'reviewer'
        ).order_by('-review_period_start')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Performance Reviews'
        context['pending_count'] = PerformanceReview.objects.filter(
            status__in=['DRAFT', 'SELF_ASSESSMENT', 'MANAGER_REVIEW']
        ).count()
        return context

# ===== TRAINING MANAGEMENT =====
class TrainingProgramListView(LoginRequiredMixin, ListView):
    model = TrainingProgram
    template_name = 'hr/training_list.html'
    context_object_name = 'training_programs'
    paginate_by = 25
    
    def get_queryset(self):
        return TrainingProgram.objects.filter(is_active=True).order_by('-start_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Training Programs'
        context['active_programs'] = TrainingProgram.objects.filter(is_active=True).count()
        return context

# ===== PAYROLL MANAGEMENT =====
class PayrollListView(LoginRequiredMixin, ListView):
    model = EmployeePayroll
    template_name = 'hr/payroll_list.html'
    context_object_name = 'payrolls'
    paginate_by = 25
    
    def get_queryset(self):
        return EmployeePayroll.objects.select_related(
            'employee', 'employee__user', 'employee__department'
        ).order_by('-pay_period_start')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Payroll Statistics
        current_month_payroll = EmployeePayroll.objects.filter(
            pay_period_start__month=timezone.now().month,
            pay_period_start__year=timezone.now().year
        )
        
        context.update({
            'page_title': 'Payroll Management',
            'total_payroll': current_month_payroll.aggregate(total=Sum('net_salary'))['total'] or 0,
            'processed_count': current_month_payroll.filter(is_processed=True).count(),
            'pending_count': current_month_payroll.filter(is_processed=False).count(),
        })
        return context

@login_required
def generate_payroll(request):
    """Generate monthly payroll for all employees"""
    if request.method == 'POST':
        month = int(request.POST.get('month'))
        year = int(request.POST.get('year'))
        
        # Get period dates
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        # Generate payroll for active employees
        active_employees = Employee.objects.filter(employment_status='ACTIVE')
        created_count = 0
        
        for employee in active_employees:
            # Check if payroll already exists
            existing = EmployeePayroll.objects.filter(
                employee=employee,
                pay_period_start=start_date,
                pay_period_end=end_date
            ).exists()
            
            if not existing:
                # Calculate attendance
                working_days = 30  # Standard working days
                present_days = 30  # Default full attendance
                
                # Calculate basic components
                basic_salary = employee.basic_salary
                gross_salary = employee.gross_salary
                
                # Basic deductions (simplified)
                pf_deduction = basic_salary * Decimal('0.12')  # 12% PF
                tax_deduction = gross_salary * Decimal('0.10')  # 10% tax (simplified)
                total_deductions = pf_deduction + tax_deduction
                
                # Net salary
                net_salary = gross_salary - total_deductions
                
                EmployeePayroll.objects.create(
                    employee=employee,
                    pay_period_start=start_date,
                    pay_period_end=end_date,
                    basic_salary=basic_salary,
                    deductions={'pf': float(pf_deduction), 'tax': float(tax_deduction)},
                    gross_salary=gross_salary,
                    total_deductions=total_deductions,
                    net_salary=net_salary,
                    working_days=working_days,
                    present_days=present_days,
                    is_processed=True
                )
                created_count += 1
        
        messages.success(request, f'Payroll generated for {created_count} employees')
        return redirect('hr:payroll-list')
    
    context = {
        'page_title': 'Generate Payroll',
        'current_month': timezone.now().month,
        'current_year': timezone.now().year,
    }
    return render(request, 'hr/generate_payroll.html', context)

# ===== HR ANALYTICS =====
@login_required
def hr_analytics(request):
    """Advanced HR Analytics Dashboard"""
    current_year = timezone.now().year
    
    # Employee Analytics
    total_employees = Employee.objects.filter(employment_status='ACTIVE').count()
    turnover_rate = 0  # Calculate based on terminations
    
    # Department-wise Analytics
    dept_analytics = Employee.objects.filter(
        employment_status='ACTIVE'
    ).values(
        'department__name'
    ).annotate(
        count=Count('id'),
        avg_salary=Avg('basic_salary'),
        avg_experience=Avg('experience_before_joining')
    ).order_by('-count')
    
    # Training Analytics
    training_completion_rate = TrainingEnrollment.objects.filter(
        status='COMPLETED'
    ).count() / max(TrainingEnrollment.objects.count(), 1) * 100
    
    # Leave Analytics
    leave_analytics = LeaveApplication.objects.filter(
        start_date__year=current_year,
        status='APPROVED'
    ).values(
        'leave_type__name'
    ).annotate(
        count=Count('id'),
        total_days=Sum('total_days')
    ).order_by('-total_days')
    
    context = {
        'page_title': 'HR Analytics',
        'total_employees': total_employees,
        'turnover_rate': turnover_rate,
        'dept_analytics': dept_analytics,
        'training_completion_rate': round(training_completion_rate, 1),
        'leave_analytics': leave_analytics,
    }
    
    return render(request, 'hr/analytics.html', context)

# ===== REPORTS =====
@login_required
def payroll_report(request):
    """Monthly payroll report"""
    month = request.GET.get('month', timezone.now().month)
    year = request.GET.get('year', timezone.now().year)
    
    payrolls = EmployeePayroll.objects.filter(
        pay_period_start__month=month,
        pay_period_start__year=year
    ).select_related('employee', 'employee__user', 'employee__department')
    
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="payroll_{year}_{month}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Employee ID', 'Name', 'Department', 'Basic Salary',
            'Gross Salary', 'Deductions', 'Net Salary', 'Status'
        ])
        
        for payroll in payrolls:
            writer.writerow([
                payroll.employee.employee_id,
                payroll.employee.full_name,
                payroll.employee.department.name if payroll.employee.department else '',
                payroll.basic_salary,
                payroll.gross_salary,
                payroll.total_deductions,
                payroll.net_salary,
                'Processed' if payroll.is_processed else 'Pending',
            ])
        
        return response
    
    context = {
        'page_title': 'Payroll Report',
        'payrolls': payrolls,
        'month': int(month),
        'year': int(year),
        'total_gross': payrolls.aggregate(total=Sum('gross_salary'))['total'] or 0,
        'total_net': payrolls.aggregate(total=Sum('net_salary'))['total'] or 0,
    }
    
    return render(request, 'hr/payroll_report.html', context) 