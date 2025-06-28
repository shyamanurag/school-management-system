from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Count, Sum, Avg, F
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from .models import (
    FeeCategory, FeeStructure, FeePayment, Expense, ExpenseCategory,
    Voucher, Invoice, FinancialTransaction, ScholarshipRecord
)
from core.models import Student, Grade, SchoolSettings, AcademicYear
import csv
import json

# ===== COMPREHENSIVE FINANCE DASHBOARD =====
@login_required
def finance_dashboard(request):
    """Advanced Financial Management Dashboard"""
    school_settings = SchoolSettings.objects.first()
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    
    # Current Month Statistics
    current_month = timezone.now().replace(day=1)
    next_month = (current_month + timedelta(days=32)).replace(day=1)
    
    # Fee Collection Statistics
    fee_stats = {
        'total_fee_collected': FeePayment.objects.filter(
            payment_date__gte=current_month,
            payment_date__lt=next_month,
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0,
        
        'pending_fees': FeePayment.objects.filter(
            status='pending'
        ).aggregate(total=Sum('amount'))['total'] or 0,
        
        'overdue_fees': FeePayment.objects.filter(
            status='overdue',
            due_date__lt=timezone.now().date()
        ).aggregate(total=Sum('amount'))['total'] or 0,
        
        'total_scholarships': ScholarshipRecord.objects.filter(
            is_active=True
        ).aggregate(total=Sum('scholarship_amount'))['total'] or 0,
    }
    
    # Expense Statistics
    expense_stats = {
        'monthly_expenses': Expense.objects.filter(
            expense_date__gte=current_month,
            expense_date__lt=next_month
        ).aggregate(total=Sum('amount'))['total'] or 0,
        
        'pending_approvals': Expense.objects.filter(
            status='pending'
        ).count(),
        
        'total_yearly_expenses': Expense.objects.filter(
            expense_date__year=timezone.now().year
        ).aggregate(total=Sum('amount'))['total'] or 0,
    }
    
    # Revenue vs Expense Analysis
    monthly_revenue = fee_stats['total_fee_collected']
    monthly_expense = expense_stats['monthly_expenses']
    net_income = monthly_revenue - monthly_expense
    
    # Recent Transactions
    recent_payments = FeePayment.objects.select_related(
        'student', 'fee_structure'
    ).order_by('-payment_date')[:10]
    
    recent_expenses = Expense.objects.select_related(
        'category', 'approved_by'
    ).order_by('-expense_date')[:10]
    
    # Outstanding Fees by Grade
    outstanding_by_grade = Grade.objects.annotate(
        pending_amount=Sum('student__feepayment__amount', 
                          filter=Q(student__feepayment__status='pending'))
    ).filter(pending_amount__gt=0)
    
    # Monthly Trends (Last 6 months)
    monthly_trends = []
    for i in range(6):
        month_start = (timezone.now().replace(day=1) - timedelta(days=i*30))
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        revenue = FeePayment.objects.filter(
            payment_date__range=[month_start, month_end],
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        expenses = Expense.objects.filter(
            expense_date__range=[month_start, month_end]
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        monthly_trends.append({
            'month': month_start.strftime('%b %Y'),
            'revenue': float(revenue),
            'expenses': float(expenses),
            'profit': float(revenue - expenses)
        })
    
    # Expense Category Breakdown
    expense_categories = ExpenseCategory.objects.annotate(
        total_amount=Sum('expense__amount', 
                        filter=Q(expense__expense_date__gte=current_month))
    ).filter(total_amount__gt=0).order_by('-total_amount')
    
    context = {
        'page_title': 'Financial Management Dashboard',
        'school_settings': school_settings,
        'current_academic_year': current_academic_year,
        'fee_stats': fee_stats,
        'expense_stats': expense_stats,
        'net_income': net_income,
        'recent_payments': recent_payments,
        'recent_expenses': recent_expenses,
        'outstanding_by_grade': outstanding_by_grade,
        'monthly_trends': list(reversed(monthly_trends)),
        'expense_categories': expense_categories,
    }
    
    return render(request, 'finance/dashboard.html', context)

# ===== FEE MANAGEMENT =====
class FeeStructureListView(LoginRequiredMixin, ListView):
    model = FeeStructure
    template_name = 'finance/fee_structure_list.html'
    context_object_name = 'fee_structures'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = FeeStructure.objects.select_related(
            'grade', 'category', 'academic_year'
        ).annotate(
            total_collected=Sum('feepayment__amount', 
                              filter=Q(feepayment__status='completed')),
            pending_amount=Sum('feepayment__amount', 
                             filter=Q(feepayment__status='pending'))
        )
        
        grade_filter = self.request.GET.get('grade', '')
        category_filter = self.request.GET.get('category', '')
        academic_year_filter = self.request.GET.get('academic_year', '')
        
        if grade_filter:
            queryset = queryset.filter(grade_id=grade_filter)
        if category_filter:
            queryset = queryset.filter(category_id=category_filter)
        if academic_year_filter:
            queryset = queryset.filter(academic_year_id=academic_year_filter)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Fee Structure Management'
        context['grades'] = Grade.objects.all()
        context['categories'] = FeeCategory.objects.all()
        context['academic_years'] = AcademicYear.objects.all()
        return context

@login_required
def fee_collection(request):
    """Fee Collection Interface"""
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        fee_structure_id = request.POST.get('fee_structure_id')
        amount = Decimal(request.POST.get('amount', '0'))
        payment_method = request.POST.get('payment_method', 'cash')
        transaction_id = request.POST.get('transaction_id', '')
        remarks = request.POST.get('remarks', '')
        
        try:
            student = Student.objects.get(id=student_id)
            fee_structure = FeeStructure.objects.get(id=fee_structure_id)
            
            # Check if partial payment is allowed
            if amount < fee_structure.amount and not fee_structure.allow_partial_payment:
                messages.error(request, 'Partial payment is not allowed for this fee structure.')
                return redirect('finance:fee_collection')
            
            # Create fee payment record
            fee_payment = FeePayment.objects.create(
                student=student,
                fee_structure=fee_structure,
                amount=amount,
                payment_date=timezone.now().date(),
                payment_method=payment_method,
                transaction_id=transaction_id,
                remarks=remarks,
                status='completed',
                collected_by=request.user
            )
            
            # Create financial transaction
            FinancialTransaction.objects.create(
                transaction_type='income',
                amount=amount,
                description=f'Fee payment from {student.first_name} {student.last_name}',
                reference_id=str(fee_payment.id),
                created_by=request.user
            )
            
            messages.success(request, f'Fee payment of Rs. {amount} collected successfully from {student.first_name} {student.last_name}')
            return redirect('finance:fee_payment_receipt', pk=fee_payment.pk)
            
        except Student.DoesNotExist:
            messages.error(request, 'Student not found')
        except FeeStructure.DoesNotExist:
            messages.error(request, 'Fee structure not found')
        except Exception as e:
            messages.error(request, f'Error processing payment: {str(e)}')
    
    # GET request - show collection form
    students = Student.objects.filter(is_active=True).select_related('grade')
    fee_structures = FeeStructure.objects.select_related('grade', 'category').filter(is_active=True)
    
    context = {
        'page_title': 'Fee Collection',
        'students': students,
        'fee_structures': fee_structures,
    }
    
    return render(request, 'finance/fee_collection.html', context)

@login_required
def fee_payment_receipt(request, pk):
    """Generate fee payment receipt"""
    payment = get_object_or_404(FeePayment, pk=pk)
    school_settings = SchoolSettings.objects.first()
    
    context = {
        'payment': payment,
        'school_settings': school_settings,
        'page_title': f'Fee Receipt - {payment.student.first_name} {payment.student.last_name}'
    }
    
    return render(request, 'finance/fee_receipt.html', context)

@login_required
def outstanding_fees_report(request):
    """Outstanding Fees Report"""
    grade_filter = request.GET.get('grade', '')
    category_filter = request.GET.get('category', '')
    
    # Base queryset for outstanding fees
    outstanding_payments = FeePayment.objects.filter(
        status__in=['pending', 'overdue']
    ).select_related('student', 'fee_structure', 'student__grade')
    
    if grade_filter:
        outstanding_payments = outstanding_payments.filter(student__grade_id=grade_filter)
    if category_filter:
        outstanding_payments = outstanding_payments.filter(fee_structure__category_id=category_filter)
    
    # Summary statistics
    total_outstanding = outstanding_payments.aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    overdue_amount = outstanding_payments.filter(
        status='overdue'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Grade-wise breakdown
    grade_breakdown = outstanding_payments.values(
        'student__grade__name'
    ).annotate(
        total_amount=Sum('amount'),
        student_count=Count('student', distinct=True)
    ).order_by('student__grade__name')
    
    context = {
        'page_title': 'Outstanding Fees Report',
        'outstanding_payments': outstanding_payments.order_by('due_date'),
        'total_outstanding': total_outstanding,
        'overdue_amount': overdue_amount,
        'grade_breakdown': grade_breakdown,
        'grades': Grade.objects.all(),
        'categories': FeeCategory.objects.all(),
        'selected_grade': grade_filter,
        'selected_category': category_filter,
    }
    
    return render(request, 'finance/outstanding_fees_report.html', context)

# ===== EXPENSE MANAGEMENT =====
class ExpenseListView(LoginRequiredMixin, ListView):
    model = Expense
    template_name = 'finance/expense_list.html'
    context_object_name = 'expenses'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Expense.objects.select_related(
            'category', 'approved_by', 'created_by'
        )
        
        category_filter = self.request.GET.get('category', '')
        status_filter = self.request.GET.get('status', '')
        date_from = self.request.GET.get('date_from', '')
        date_to = self.request.GET.get('date_to', '')
        
        if category_filter:
            queryset = queryset.filter(category_id=category_filter)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if date_from:
            queryset = queryset.filter(expense_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(expense_date__lte=date_to)
        
        return queryset.order_by('-expense_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Expense Management'
        context['categories'] = ExpenseCategory.objects.all()
        context['total_expenses'] = self.get_queryset().aggregate(
            total=Sum('amount')
        )['total'] or 0
        return context

@login_required
def expense_approval(request, pk):
    """Approve or reject expense"""
    expense = get_object_or_404(Expense, pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        remarks = request.POST.get('remarks', '')
        
        if action == 'approve':
            expense.status = 'approved'
            expense.approved_by = request.user
            expense.approval_date = timezone.now()
            expense.approval_remarks = remarks
            
            # Create financial transaction
            FinancialTransaction.objects.create(
                transaction_type='expense',
                amount=expense.amount,
                description=f'{expense.description} - {expense.category.name}',
                reference_id=str(expense.id),
                created_by=request.user
            )
            
            messages.success(request, f'Expense of Rs. {expense.amount} approved successfully')
            
        elif action == 'reject':
            expense.status = 'rejected'
            expense.approved_by = request.user
            expense.approval_date = timezone.now()
            expense.approval_remarks = remarks
            
            messages.warning(request, f'Expense of Rs. {expense.amount} rejected')
        
        expense.save()
        return redirect('finance:expense_list')
    
    context = {
        'expense': expense,
        'page_title': f'Expense Approval - {expense.description}'
    }
    
    return render(request, 'finance/expense_approval.html', context)

# ===== FINANCIAL REPORTS =====
@login_required
def financial_reports(request):
    """Comprehensive Financial Reports"""
    # Date range filtering
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    report_type = request.GET.get('report_type', 'summary')
    
    if not start_date:
        start_date = timezone.now().replace(day=1).date()
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    if not end_date:
        end_date = timezone.now().date()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Income Analysis
    fee_income = FeePayment.objects.filter(
        payment_date__range=[start_date, end_date],
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Expense Analysis
    total_expenses = Expense.objects.filter(
        expense_date__range=[start_date, end_date],
        status='approved'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Category-wise Income
    income_by_category = FeeCategory.objects.annotate(
        total_income=Sum('feestructure__feepayment__amount',
                        filter=Q(
                            feestructure__feepayment__payment_date__range=[start_date, end_date],
                            feestructure__feepayment__status='completed'
                        ))
    ).filter(total_income__gt=0).order_by('-total_income')
    
    # Category-wise Expenses
    expenses_by_category = ExpenseCategory.objects.annotate(
        total_expense=Sum('expense__amount',
                         filter=Q(
                             expense__expense_date__range=[start_date, end_date],
                             expense__status='approved'
                         ))
    ).filter(total_expense__gt=0).order_by('-total_expense')
    
    # Monthly comparison if range is large enough
    monthly_data = []
    if (end_date - start_date).days > 60:  # More than 2 months
        current_date = start_date.replace(day=1)
        while current_date <= end_date:
            next_month = (current_date + timedelta(days=32)).replace(day=1)
            month_end = min(next_month - timedelta(days=1), end_date)
            
            month_income = FeePayment.objects.filter(
                payment_date__range=[current_date, month_end],
                status='completed'
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            month_expense = Expense.objects.filter(
                expense_date__range=[current_date, month_end],
                status='approved'
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            monthly_data.append({
                'month': current_date.strftime('%b %Y'),
                'income': float(month_income),
                'expense': float(month_expense),
                'profit': float(month_income - month_expense)
            })
            
            current_date = next_month
    
    # Grade-wise fee collection
    grade_collection = Grade.objects.annotate(
        collected_amount=Sum('student__feepayment__amount',
                           filter=Q(
                               student__feepayment__payment_date__range=[start_date, end_date],
                               student__feepayment__status='completed'
                           ))
    ).filter(collected_amount__gt=0).order_by('-collected_amount')
    
    context = {
        'page_title': 'Financial Reports & Analytics',
        'start_date': start_date,
        'end_date': end_date,
        'report_type': report_type,
        'fee_income': fee_income,
        'total_expenses': total_expenses,
        'net_profit': fee_income - total_expenses,
        'income_by_category': income_by_category,
        'expenses_by_category': expenses_by_category,
        'monthly_data': monthly_data,
        'grade_collection': grade_collection,
    }
    
    return render(request, 'finance/financial_reports.html', context)

# ===== SCHOLARSHIP MANAGEMENT =====
@login_required
def scholarship_management(request):
    """Scholarship Management System"""
    active_scholarships = ScholarshipRecord.objects.filter(
        is_active=True
    ).select_related('student', 'student__grade')
    
    # Statistics
    total_scholarship_amount = active_scholarships.aggregate(
        total=Sum('scholarship_amount')
    )['total'] or 0
    
    scholarship_count = active_scholarships.count()
    
    # Grade-wise distribution
    grade_distribution = active_scholarships.values(
        'student__grade__name'
    ).annotate(
        student_count=Count('student'),
        total_amount=Sum('scholarship_amount')
    ).order_by('student__grade__name')
    
    context = {
        'page_title': 'Scholarship Management',
        'active_scholarships': active_scholarships,
        'total_scholarship_amount': total_scholarship_amount,
        'scholarship_count': scholarship_count,
        'grade_distribution': grade_distribution,
    }
    
    return render(request, 'finance/scholarship_management.html', context)

# ===== API ENDPOINTS =====
@login_required
def finance_analytics_api(request):
    """API endpoint for financial analytics data"""
    # Monthly revenue and expense trends
    monthly_data = []
    for i in range(12):
        month_start = (timezone.now().replace(day=1) - timedelta(days=i*30)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        revenue = FeePayment.objects.filter(
            payment_date__range=[month_start, month_end],
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        expenses = Expense.objects.filter(
            expense_date__range=[month_start, month_end],
            status='approved'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        monthly_data.append({
            'month': month_start.strftime('%b %Y'),
            'revenue': float(revenue),
            'expenses': float(expenses),
            'profit': float(revenue - expenses)
        })
    
    # Fee collection by category
    category_data = FeeCategory.objects.annotate(
        total_collected=Sum('feestructure__feepayment__amount',
                          filter=Q(feestructure__feepayment__status='completed'))
    ).values('name', 'total_collected')
    
    # Outstanding fees summary
    outstanding_summary = {
        'pending': FeePayment.objects.filter(status='pending').aggregate(
            total=Sum('amount')
        )['total'] or 0,
        'overdue': FeePayment.objects.filter(status='overdue').aggregate(
            total=Sum('amount')
        )['total'] or 0,
    }
    
    return JsonResponse({
        'monthly_trends': list(reversed(monthly_data)),
        'category_collection': list(category_data),
        'outstanding_summary': outstanding_summary,
        'status': 'success'
    })

# ===== DATA EXPORT FUNCTIONS =====
@login_required
def export_fee_collection_csv(request):
    """Export fee collection data to CSV"""
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="fee_collection_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Student Name', 'Grade', 'Fee Category', 'Amount', 'Payment Date',
        'Payment Method', 'Transaction ID', 'Status', 'Collected By'
    ])
    
    payments = FeePayment.objects.select_related(
        'student', 'student__grade', 'fee_structure__category', 'collected_by'
    )
    
    if start_date:
        payments = payments.filter(payment_date__gte=start_date)
    if end_date:
        payments = payments.filter(payment_date__lte=end_date)
    
    for payment in payments:
        writer.writerow([
            f"{payment.student.first_name} {payment.student.last_name}",
            payment.student.grade.name if payment.student.grade else '',
            payment.fee_structure.category.name,
            payment.amount,
            payment.payment_date,
            payment.payment_method,
            payment.transaction_id,
            payment.status,
            payment.collected_by.username if payment.collected_by else ''
        ])
    
    return response

@login_required
def export_expenses_csv(request):
    """Export expenses data to CSV"""
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expenses_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Date', 'Category', 'Description', 'Amount', 'Status',
        'Created By', 'Approved By', 'Approval Date'
    ])
    
    expenses = Expense.objects.select_related(
        'category', 'created_by', 'approved_by'
    )
    
    if start_date:
        expenses = expenses.filter(expense_date__gte=start_date)
    if end_date:
        expenses = expenses.filter(expense_date__lte=end_date)
    
    for expense in expenses:
        writer.writerow([
            expense.expense_date,
            expense.category.name,
            expense.description,
            expense.amount,
            expense.status,
            expense.created_by.username,
            expense.approved_by.username if expense.approved_by else '',
            expense.approval_date.date() if expense.approval_date else ''
        ])
    
    return response 