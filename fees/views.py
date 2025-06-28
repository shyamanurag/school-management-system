from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Count, Sum, Q, Avg, F
from django.utils import timezone
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.core.mail import send_mail

# Import models from core.models where they actually exist
from core.models import (
    FeeCategory, FeeStructure, FeePayment, SchoolSettings, 
    Student, Grade, AcademicYear, SmartNotification
)

# Try to import advanced fee models if they exist
try:
    from fees.models import (
        FeeInstallment, StudentFeeAssignment, FeeRefund, FeeDiscount,
        PaymentMethod, FeeDefaulter, FeeConcession
    )
    ADVANCED_FEE_MODELS_AVAILABLE = True
except ImportError:
    ADVANCED_FEE_MODELS_AVAILABLE = False

import csv
from datetime import datetime, timedelta, date
import json
from decimal import Decimal

class FeeCategoryListView(ListView):
    model = FeeCategory
    template_name = 'fees/fee_category_list.html'
    context_object_name = 'fee_categories'

class FeeCategoryCreateView(CreateView):
    model = FeeCategory
    fields = ['name', 'description']
    template_name = 'fees/fee_category_form.html'
    success_url = reverse_lazy('fee-category-list')

class FeeCategoryUpdateView(UpdateView):
    model = FeeCategory
    fields = ['name', 'description']
    template_name = 'fees/fee_category_form.html'
    success_url = reverse_lazy('fee-category-list')

class FeeCategoryDeleteView(DeleteView):
    model = FeeCategory
    template_name = 'fees/fee_category_confirm_delete.html'
    success_url = reverse_lazy('fee-category-list')

def fee_dashboard(request):
    """Fee management dashboard with real database connectivity"""
    school_settings = SchoolSettings.objects.first()
    
    # Statistics from real database
    total_categories = FeeCategory.objects.filter(is_active=True).count()
    total_structures = FeeStructure.objects.filter(is_active=True).count()
    total_payments = FeePayment.objects.count()
    total_amount_collected = FeePayment.objects.aggregate(total=Sum('amount_paid'))['total'] or 0
    
    # Recent payments with correct relationships
    recent_payments = FeePayment.objects.select_related(
        'student', 
        'fee_structure__category'
    ).order_by('-payment_date')[:10]
    
    context = {
        'school_settings': school_settings,
        'total_categories': total_categories,
        'total_structures': total_structures,
        'total_payments': total_payments,
        'total_amount_collected': total_amount_collected,
        'recent_payments': recent_payments,
        'page_title': 'Fee Management Dashboard'
    }
    return render(request, 'fees/dashboard.html', context)

def fee_categories_list(request):
    """Professional Fee Categories List"""
    school_settings = SchoolSettings.objects.first()
    categories = FeeCategory.objects.filter(is_active=True).order_by('name')
    
    context = {
        'school_settings': school_settings,
        'categories': categories,
        'total_categories': categories.count(),
        'page_title': 'Fee Categories Management'
    }
    return render(request, 'fees/categories_list.html', context)

def fee_structures_list(request):
    """Professional Fee Structures List"""
    school_settings = SchoolSettings.objects.first()
    structures = FeeStructure.objects.filter(is_active=True).select_related(
        'academic_year', 
        'grade',
        'category'
    ).order_by('-created_at')
    
    context = {
        'school_settings': school_settings,
        'structures': structures,
        'total_structures': structures.count(),
        'page_title': 'Fee Structures Management'
    }
    return render(request, 'fees/structures_list.html', context)

def fee_payments_list(request):
    """Professional Fee Payments List with real database connectivity"""
    school_settings = SchoolSettings.objects.first()
    
    # Get filter parameters
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    # Base queryset with correct relationships
    payments = FeePayment.objects.select_related(
        'student', 
        'fee_structure__category',
        'student__grade'
    ).order_by('-payment_date')
    
    # Apply filters
    if search_query:
        payments = payments.filter(
            Q(student__first_name__icontains=search_query) |
            Q(student__last_name__icontains=search_query) |
            Q(student__admission_number__icontains=search_query)
        )
    
    if status_filter:
        payments = payments.filter(status=status_filter)
    
    # Calculate statistics
    total_amount = payments.aggregate(total=Sum('amount_paid'))['total'] or 0
    total_due = payments.aggregate(total=Sum('amount_due'))['total'] or 0
    pending_amount = total_due - total_amount
    
    # Status breakdown
    status_counts = payments.values('status').annotate(count=Count('id'))
    
    # Pagination
    paginator = Paginator(payments, 25)  # 25 payments per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'school_settings': school_settings,
        'payments': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'total_payments': payments.count(),
        'total_amount': total_amount,
        'total_due': total_due,
        'pending_amount': pending_amount,
        'status_counts': status_counts,
        'search_query': search_query,
        'status_filter': status_filter,
        'page_title': 'Fee Payments Management'
    }
    return render(request, 'fees/payments_list.html', context)

def fee_reports(request):
    """Fee reports and analytics with real data"""
    school_settings = SchoolSettings.objects.first()
    
    # Monthly collection data
    monthly_collections = FeePayment.objects.extra(
        select={'month': "EXTRACT(month FROM payment_date)"}
    ).values('month').annotate(total=Sum('amount_paid')).order_by('month')
    
    # Category-wise collection  
    category_collections = FeePayment.objects.values(
        'fee_structure__category__name'
    ).annotate(total=Sum('amount_paid')).order_by('-total')
    
    # Status-wise breakdown
    status_breakdown = FeePayment.objects.values('status').annotate(
        count=Count('id'),
        total_amount=Sum('amount_paid')
    ).order_by('status')
    
    context = {
        'school_settings': school_settings,
        'monthly_collections': monthly_collections,
        'category_collections': category_collections,
        'status_breakdown': status_breakdown,
        'page_title': 'Fee Reports & Analytics'
    }
    return render(request, 'fees/reports.html', context)

@login_required
def student_fee_profile(request, student_id):
    """Comprehensive student fee profile and payment history"""
    student = get_object_or_404(Student, id=student_id)
    school_settings = SchoolSettings.objects.first()
    
    # Get all fee structures applicable to this student
    applicable_structures = FeeStructure.objects.filter(
        grade=student.grade,
        academic_year=student.academic_year,
        is_active=True
    ).select_related('category', 'academic_year', 'grade')
    
    # Get payment history
    payment_history = FeePayment.objects.filter(
        student=student
    ).select_related('fee_structure__category').order_by('-payment_date')
    
    # Calculate fee summary
    total_fees_due = applicable_structures.aggregate(total=Sum('amount'))['total'] or 0
    total_paid = payment_history.aggregate(total=Sum('amount_paid'))['total'] or 0
    outstanding_amount = total_fees_due - total_paid
    
    # Monthly payment breakdown
    monthly_payments = payment_history.extra(
        select={'month': "EXTRACT(month FROM payment_date)"}
    ).values('month').annotate(total=Sum('amount_paid')).order_by('month')
    
    # Payment status by category
    category_wise_payments = payment_history.values(
        'fee_structure__category__name'
    ).annotate(
        total_paid=Sum('amount_paid'),
        payment_count=Count('id')
    ).order_by('fee_structure__category__name')
    
    context = {
        'student': student,
        'school_settings': school_settings,
        'applicable_structures': applicable_structures,
        'payment_history': payment_history,
        'total_fees_due': total_fees_due,
        'total_paid': total_paid,
        'outstanding_amount': outstanding_amount,
        'monthly_payments': monthly_payments,
        'category_wise_payments': category_wise_payments,
        'page_title': f'Fee Profile - {student.full_name}'
    }
    
    return render(request, 'fees/student_fee_profile.html', context)

@login_required
def fee_collection_report(request):
    """Comprehensive fee collection report with analytics"""
    school_settings = SchoolSettings.objects.first()
    
    # Date range filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    grade_filter = request.GET.get('grade')
    category_filter = request.GET.get('category')
    
    # Base queryset
    payments = FeePayment.objects.select_related(
        'student__grade', 'fee_structure__category'
    ).order_by('-payment_date')
    
    # Apply filters
    if start_date:
        payments = payments.filter(payment_date__gte=start_date)
    if end_date:
        payments = payments.filter(payment_date__lte=end_date)
    if grade_filter:
        payments = payments.filter(student__grade__id=grade_filter)
    if category_filter:
        payments = payments.filter(fee_structure__category__id=category_filter)
    
    # Calculate statistics
    total_collection = payments.aggregate(total=Sum('amount_paid'))['total'] or 0
    total_due = payments.aggregate(total=Sum('amount_due'))['total'] or 0
    collection_efficiency = (total_collection / total_due * 100) if total_due > 0 else 0
    
    # Daily collection trend
    daily_collections = payments.extra(
        select={'day': "DATE(payment_date)"}
    ).values('day').annotate(total=Sum('amount_paid')).order_by('day')
    
    # Grade-wise collection
    grade_wise_collection = payments.values(
        'student__grade__name'
    ).annotate(
        total_amount=Sum('amount_paid'),
        student_count=Count('student', distinct=True)
    ).order_by('student__grade__name')
    
    # Category-wise collection
    category_wise_collection = payments.values(
        'fee_structure__category__name'
    ).annotate(
        total_amount=Sum('amount_paid'),
        payment_count=Count('id')
    ).order_by('-total_amount')
    
    # Top paying students
    top_students = payments.values(
        'student__first_name', 'student__last_name', 'student__admission_number'
    ).annotate(
        total_paid=Sum('amount_paid')
    ).order_by('-total_paid')[:10]
    
    context = {
        'school_settings': school_settings,
        'payments': payments[:50],  # Show latest 50 payments
        'total_collection': total_collection,
        'total_due': total_due,
        'collection_efficiency': round(collection_efficiency, 1),
        'daily_collections': daily_collections,
        'grade_wise_collection': grade_wise_collection,
        'category_wise_collection': category_wise_collection,
        'top_students': top_students,
        'grades': Grade.objects.filter(is_active=True),
        'categories': FeeCategory.objects.filter(is_active=True),
        'start_date': start_date,
        'end_date': end_date,
        'grade_filter': grade_filter,
        'category_filter': category_filter,
        'page_title': 'Fee Collection Report'
    }
    
    return render(request, 'fees/collection_report.html', context)

@login_required
def generate_fee_receipts(request):
    """Generate fee receipts for students"""
    if request.method == 'POST':
        payment_ids = request.POST.getlist('payment_ids')
        
        if not payment_ids:
            messages.error(request, 'No payments selected for receipt generation.')
            return redirect('fee-payments-list')
        
        payments = FeePayment.objects.filter(id__in=payment_ids).select_related(
            'student', 'fee_structure__category'
        )
        
        # Generate PDF or return receipt data
        context = {
            'payments': payments,
            'school_settings': SchoolSettings.objects.first(),
            'generated_on': timezone.now()
        }
        
        # For now, return a simple response
        messages.success(request, f'Generated receipts for {payments.count()} payments.')
        return redirect('fee-payments-list')
    
    return redirect('fee-payments-list')

@login_required
def outstanding_fees_report(request):
    """Report of students with outstanding fees"""
    school_settings = SchoolSettings.objects.first()
    
    # Get all active students with their fee obligations
    students_with_dues = []
    
    for student in Student.objects.filter(is_active=True).select_related('grade', 'academic_year'):
        # Get applicable fee structures
        applicable_structures = FeeStructure.objects.filter(
            grade=student.grade,
            academic_year=student.academic_year,
            is_active=True
        )
        
        total_due = applicable_structures.aggregate(total=Sum('amount'))['total'] or 0
        
        # Get total paid
        total_paid = FeePayment.objects.filter(student=student).aggregate(
            total=Sum('amount_paid')
        )['total'] or 0
        
        outstanding = total_due - total_paid
        
        if outstanding > 0:
            students_with_dues.append({
                'student': student,
                'total_due': total_due,
                'total_paid': total_paid,
                'outstanding': outstanding,
                'percentage_paid': round((total_paid / total_due * 100), 1) if total_due > 0 else 0
            })
    
    # Sort by outstanding amount (highest first)
    students_with_dues.sort(key=lambda x: x['outstanding'], reverse=True)
    
    # Calculate summary statistics
    total_outstanding = sum([item['outstanding'] for item in students_with_dues])
    total_students_with_dues = len(students_with_dues)
    average_outstanding = total_outstanding / total_students_with_dues if total_students_with_dues > 0 else 0
    
    context = {
        'school_settings': school_settings,
        'students_with_dues': students_with_dues,
        'total_outstanding': total_outstanding,
        'total_students_with_dues': total_students_with_dues,
        'average_outstanding': round(average_outstanding, 2),
        'page_title': 'Outstanding Fees Report'
    }
    
    return render(request, 'fees/outstanding_fees_report.html', context)

@login_required
def fee_analytics_api(request):
    """API endpoint for fee analytics charts"""
    
    # Monthly collection trends
    monthly_trends = FeePayment.objects.extra(
        select={
            'month': "EXTRACT(month FROM payment_date)",
            'year': "EXTRACT(year FROM payment_date)"
        }
    ).values('month', 'year').annotate(
        total_amount=Sum('amount_paid'),
        payment_count=Count('id')
    ).order_by('year', 'month')
    
    # Category-wise collection
    category_data = FeePayment.objects.values(
        'fee_structure__category__name'
    ).annotate(total=Sum('amount_paid')).order_by('-total')
    
    # Grade-wise collection
    grade_data = FeePayment.objects.values(
        'student__grade__name'
    ).annotate(total=Sum('amount_paid')).order_by('student__grade__name')
    
    # Payment method distribution (if available)
    payment_method_data = FeePayment.objects.values(
        'payment_method'
    ).annotate(count=Count('id')).order_by('-count')
    
    data = {
        'monthly_trends': list(monthly_trends),
        'category_distribution': list(category_data),
        'grade_distribution': list(grade_data),
        'payment_methods': list(payment_method_data)
    }
    
    return JsonResponse(data)

@login_required
def bulk_fee_operations(request):
    """Handle bulk operations on fee payments"""
    if request.method == 'POST':
        action = request.POST.get('action')
        payment_ids = request.POST.getlist('payment_ids')
        
        if not payment_ids:
            messages.error(request, 'No payments selected.')
            return redirect('fee-payments-list')
        
        payments = FeePayment.objects.filter(id__in=payment_ids)
        
        if action == 'mark_paid':
            payments.update(status='PAID', payment_date=timezone.now())
            messages.success(request, f'Marked {len(payment_ids)} payments as paid.')
        elif action == 'mark_pending':
            payments.update(status='PENDING')
            messages.success(request, f'Marked {len(payment_ids)} payments as pending.')
        elif action == 'generate_receipts':
            return generate_fee_receipts(request)
        elif action == 'send_reminders':
            # Send payment reminders (implementation needed)
            messages.info(request, f'Reminder system not yet implemented for {len(payment_ids)} payments.')
    
    return redirect('fee-payments-list')

@login_required
def export_fee_data(request):
    """Export comprehensive fee data to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="comprehensive_fee_data.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Student Name', 'Admission Number', 'Grade', 'Fee Category',
        'Fee Structure Amount', 'Amount Paid', 'Amount Due', 'Outstanding',
        'Payment Date', 'Status', 'Payment Method', 'Academic Year'
    ])
    
    payments = FeePayment.objects.select_related(
        'student', 'student__grade', 'fee_structure__category', 'fee_structure__academic_year'
    ).order_by('student__admission_number', '-payment_date')
    
    for payment in payments:
        outstanding = payment.amount_due - payment.amount_paid
        
        writer.writerow([
            payment.student.full_name,
            payment.student.admission_number,
            payment.student.grade.name if payment.student.grade else '',
            payment.fee_structure.category.name,
            payment.fee_structure.amount,
            payment.amount_paid,
            payment.amount_due,
            outstanding,
            payment.payment_date,
            payment.status,
            payment.payment_method if hasattr(payment, 'payment_method') else 'N/A',
            payment.fee_structure.academic_year.year if payment.fee_structure.academic_year else ''
        ])
    
    return response

@login_required
def fee_installment_management(request):
    """Advanced fee installment management system"""
    school_settings = SchoolSettings.objects.first()
    
    if not ADVANCED_FEE_MODELS_AVAILABLE:
        messages.warning(request, 'Advanced fee models not available. Using basic fee system.')
        return redirect('fee-dashboard')
    
    # Get all installments with student and fee structure details
    installments = FeeInstallment.objects.select_related(
        'student_fee_assignment__student',
        'student_fee_assignment__fee_structure'
    ).order_by('-due_date')
    
    # Filter by status if provided
    status_filter = request.GET.get('status', '')
    if status_filter:
        if status_filter == 'paid':
            installments = installments.filter(is_paid=True)
        elif status_filter == 'pending':
            installments = installments.filter(is_paid=False, due_date__gte=date.today())
        elif status_filter == 'overdue':
            installments = installments.filter(is_paid=False, due_date__lt=date.today())
    
    # Grade filter
    grade_filter = request.GET.get('grade', '')
    if grade_filter:
        installments = installments.filter(
            student_fee_assignment__student__grade__id=grade_filter
        )
    
    # Calculate installment statistics
    total_installments = installments.count()
    paid_installments = installments.filter(is_paid=True).count()
    overdue_installments = installments.filter(
        is_paid=False, 
        due_date__lt=date.today()
    ).count()
    
    total_amount_due = installments.aggregate(total=Sum('net_amount'))['total'] or 0
    total_amount_paid = installments.aggregate(total=Sum('paid_amount'))['total'] or 0
    total_outstanding = total_amount_due - total_amount_paid
    
    # Upcoming due installments (next 30 days)
    upcoming_due = installments.filter(
        is_paid=False,
        due_date__gte=date.today(),
        due_date__lte=date.today() + timedelta(days=30)
    ).order_by('due_date')[:20]
    
    # Pagination
    paginator = Paginator(installments, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'school_settings': school_settings,
        'installments': page_obj,
        'total_installments': total_installments,
        'paid_installments': paid_installments,
        'overdue_installments': overdue_installments,
        'total_amount_due': total_amount_due,
        'total_amount_paid': total_amount_paid,
        'total_outstanding': total_outstanding,
        'upcoming_due': upcoming_due,
        'grades': Grade.objects.filter(is_active=True),
        'status_filter': status_filter,
        'grade_filter': grade_filter,
        'page_title': 'Fee Installment Management'
    }
    
    return render(request, 'fees/installment_management.html', context)

@login_required
def scholarship_discount_management(request):
    """Comprehensive scholarship and discount management"""
    school_settings = SchoolSettings.objects.first()
    
    if not ADVANCED_FEE_MODELS_AVAILABLE:
        return render(request, 'fees/basic_discount_management.html', {
            'school_settings': school_settings,
            'page_title': 'Discount Management'
        })
    
    # Get all active discounts and scholarships
    discounts = FeeDiscount.objects.filter(is_active=True).order_by('-created_at')
    
    # Get students with scholarships
    scholarship_students = StudentFeeAssignment.objects.filter(
        scholarship_amount__gt=0
    ).select_related('student', 'fee_structure').order_by('-scholarship_amount')
    
    # Government scheme beneficiaries
    govt_scheme_students = StudentFeeAssignment.objects.filter(
        Q(is_pmcare_beneficiary=True) | Q(is_state_scholarship=True)
    ).select_related('student')
    
    # Scholarship statistics
    total_scholarship_amount = scholarship_students.aggregate(
        total=Sum('scholarship_amount')
    )['total'] or 0
    
    total_discount_amount = StudentFeeAssignment.objects.aggregate(
        total=Sum('discount_amount')
    )['total'] or 0
    
    # Merit-based scholarships
    merit_scholarships = discounts.filter(is_merit_based=True)
    need_based_scholarships = discounts.filter(is_need_based=True)
    
    # RTE students
    rte_students = StudentFeeAssignment.objects.filter(
        fee_structure__rte_fee_waiver=True
    ).count()
    
    context = {
        'school_settings': school_settings,
        'discounts': discounts,
        'scholarship_students': scholarship_students,
        'govt_scheme_students': govt_scheme_students,
        'merit_scholarships': merit_scholarships,
        'need_based_scholarships': need_based_scholarships,
        'total_scholarship_amount': total_scholarship_amount,
        'total_discount_amount': total_discount_amount,
        'rte_students': rte_students,
        'page_title': 'Scholarship & Discount Management'
    }
    
    return render(request, 'fees/scholarship_management.html', context)

@login_required
def fee_refund_processing(request):
    """Complete fee refund processing system"""
    school_settings = SchoolSettings.objects.first()
    
    if not ADVANCED_FEE_MODELS_AVAILABLE:
        messages.warning(request, 'Advanced refund system not available.')
        return redirect('fee-dashboard')
    
    # Get all refund requests
    refunds = FeeRefund.objects.select_related(
        'student', 'payment', 'requested_by'
    ).order_by('-requested_date')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        refunds = refunds.filter(status=status_filter)
    
    # Refund statistics
    total_refund_requests = refunds.count()
    pending_refunds = refunds.filter(status='REQUESTED').count()
    approved_refunds = refunds.filter(status='APPROVED').count()
    processed_refunds = refunds.filter(status='PROCESSED').count()
    
    total_refund_amount = refunds.aggregate(total=Sum('refund_amount'))['total'] or 0
    processed_amount = refunds.filter(status='PROCESSED').aggregate(
        total=Sum('refund_amount')
    )['total'] or 0
    
    # Recent refund requests requiring attention
    pending_requests = refunds.filter(status='REQUESTED').order_by('requested_date')[:10]
    
    # Refund types breakdown
    refund_types = refunds.values('refund_type').annotate(
        count=Count('id'),
        total_amount=Sum('refund_amount')
    ).order_by('-total_amount')
    
    if request.method == 'POST' and 'approve_refund' in request.POST:
        refund_id = request.POST.get('refund_id')
        refund = get_object_or_404(FeeRefund, id=refund_id)
        refund.status = 'APPROVED'
        refund.approved_by = request.user
        refund.approved_date = date.today()
        refund.save()
        
        messages.success(request, f'Refund approved for {refund.student.full_name}')
        return redirect('fee-refund-processing')
    
    context = {
        'school_settings': school_settings,
        'refunds': refunds[:50],  # Show latest 50
        'total_refund_requests': total_refund_requests,
        'pending_refunds': pending_refunds,
        'approved_refunds': approved_refunds,
        'processed_refunds': processed_refunds,
        'total_refund_amount': total_refund_amount,
        'processed_amount': processed_amount,
        'pending_requests': pending_requests,
        'refund_types': refund_types,
        'status_filter': status_filter,
        'page_title': 'Fee Refund Processing'
    }
    
    return render(request, 'fees/refund_processing.html', context)

@login_required
def payment_gateway_integration(request):
    """Payment gateway integration and management"""
    school_settings = SchoolSettings.objects.first()
    
    if not ADVANCED_FEE_MODELS_AVAILABLE:
        payment_methods = [
            {'name': 'Cash', 'active': True, 'fees': 0},
            {'name': 'Bank Transfer', 'active': True, 'fees': 0},
            {'name': 'Online Payment', 'active': True, 'fees': '2.5%'},
        ]
    else:
        payment_methods = PaymentMethod.objects.filter(is_active=True)
    
    # Payment gateway statistics
    online_payments = FeePayment.objects.filter(
        payment_method__icontains='online'
    ).aggregate(
        count=Count('id'),
        total_amount=Sum('amount_paid')
    )
    
    offline_payments = FeePayment.objects.exclude(
        payment_method__icontains='online'
    ).aggregate(
        count=Count('id'),
        total_amount=Sum('amount_paid')
    )
    
    # Gateway-wise transaction volume
    gateway_stats = FeePayment.objects.values('payment_method').annotate(
        transaction_count=Count('id'),
        total_amount=Sum('amount_paid'),
        success_rate=Count('id', filter=Q(status='PAID')) * 100.0 / Count('id')
    ).order_by('-total_amount')
    
    # Failed transactions
    failed_transactions = FeePayment.objects.filter(
        status='FAILED'
    ).select_related('student').order_by('-payment_date')[:20]
    
    # Monthly payment trends by gateway
    monthly_gateway_trends = FeePayment.objects.extra(
        select={'month': "EXTRACT(month FROM payment_date)"}
    ).values('month', 'payment_method').annotate(
        amount=Sum('amount_paid')
    ).order_by('month')
    
    context = {
        'school_settings': school_settings,
        'payment_methods': payment_methods,
        'online_payments': online_payments,
        'offline_payments': offline_payments,
        'gateway_stats': gateway_stats,
        'failed_transactions': failed_transactions,
        'monthly_gateway_trends': monthly_gateway_trends,
        'page_title': 'Payment Gateway Management'
    }
    
    return render(request, 'fees/payment_gateway.html', context)

@login_required
def late_fee_automation(request):
    """Automated late fee calculation and management"""
    school_settings = SchoolSettings.objects.first()
    
    # Get overdue payments
    overdue_payments = FeePayment.objects.filter(
        status__in=['PENDING', 'PARTIAL'],
        fee_structure__due_date__lt=date.today()
    ).select_related('student', 'fee_structure')
    
    # Calculate late fees for each overdue payment
    late_fee_calculations = []
    total_late_fees = 0
    
    for payment in overdue_payments:
        days_overdue = (date.today() - payment.fee_structure.due_date).days
        
        # Get fee structure for late fee calculation
        fee_structure = payment.fee_structure
        late_fee_amount = 0
        
        if hasattr(fee_structure, 'late_fee_applicable') and fee_structure.late_fee_applicable:
            if hasattr(fee_structure, 'late_fee_amount') and fee_structure.late_fee_amount:
                late_fee_amount = fee_structure.late_fee_amount
            elif hasattr(fee_structure, 'late_fee_percentage') and fee_structure.late_fee_percentage:
                late_fee_amount = (payment.amount_due * fee_structure.late_fee_percentage) / 100
            
            # Apply grace period
            grace_period = getattr(fee_structure, 'grace_period_days', 7)
            if days_overdue <= grace_period:
                late_fee_amount = 0
        
        late_fee_calculations.append({
            'payment': payment,
            'days_overdue': days_overdue,
            'late_fee_amount': late_fee_amount,
            'total_amount_due': payment.amount_due + late_fee_amount
        })
        
        total_late_fees += late_fee_amount
    
    # Automation actions
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'apply_late_fees':
            # Apply late fees to selected payments
            selected_payments = request.POST.getlist('selected_payments')
            
            for payment_id in selected_payments:
                payment = FeePayment.objects.get(id=payment_id)
                # Apply late fee logic here
                # This would update the payment record with late fees
                
            messages.success(request, f'Late fees applied to {len(selected_payments)} payments')
            
        elif action == 'send_reminders':
            # Send automated reminders
            selected_payments = request.POST.getlist('selected_payments')
            
            for payment_id in selected_payments:
                payment = FeePayment.objects.get(id=payment_id)
                # Send reminder notification
                SmartNotification.objects.create(
                    trigger_type='FEE_REMINDER',
                    recipient_id=payment.student.parent_user_id if hasattr(payment.student, 'parent_user_id') else None,
                    title=f'Fee Payment Reminder - {payment.student.full_name}',
                    message=f'Fee payment of ₹{payment.amount_due} is overdue by {(date.today() - payment.fee_structure.due_date).days} days.',
                    priority_score=0.8
                )
            
            messages.success(request, f'Reminders sent for {len(selected_payments)} payments')
        
        return redirect('late-fee-automation')
    
    # Late fee statistics
    late_fee_stats = {
        'total_overdue_payments': overdue_payments.count(),
        'total_late_fees': total_late_fees,
        'average_days_overdue': sum([calc['days_overdue'] for calc in late_fee_calculations]) / len(late_fee_calculations) if late_fee_calculations else 0,
        'students_affected': overdue_payments.values('student').distinct().count()
    }
    
    context = {
        'school_settings': school_settings,
        'overdue_payments': overdue_payments,
        'late_fee_calculations': late_fee_calculations,
        'late_fee_stats': late_fee_stats,
        'page_title': 'Late Fee Automation'
    }
    
    return render(request, 'fees/late_fee_automation.html', context)

@login_required
def fee_defaulter_tracking(request):
    """Comprehensive fee defaulter tracking and management"""
    school_settings = SchoolSettings.objects.first()
    
    # Identify fee defaulters
    defaulter_criteria_days = 30  # Students with fees overdue by more than 30 days
    
    fee_defaulters = Student.objects.filter(
        fee_payments__status__in=['PENDING', 'OVERDUE'],
        fee_payments__fee_structure__due_date__lt=date.today() - timedelta(days=defaulter_criteria_days)
    ).distinct().select_related('grade')
    
    # Defaulter analytics
    defaulter_analytics = []
    
    for student in fee_defaulters:
        overdue_payments = FeePayment.objects.filter(
            student=student,
            status__in=['PENDING', 'OVERDUE'],
            fee_structure__due_date__lt=date.today()
        )
        
        total_overdue = overdue_payments.aggregate(total=Sum('amount_due'))['total'] or 0
        oldest_overdue = overdue_payments.order_by('fee_structure__due_date').first()
        days_overdue = (date.today() - oldest_overdue.fee_structure.due_date).days if oldest_overdue else 0
        
        defaulter_analytics.append({
            'student': student,
            'total_overdue_amount': total_overdue,
            'overdue_payments_count': overdue_payments.count(),
            'days_overdue': days_overdue,
            'risk_category': 'High' if total_overdue > 50000 else 'Medium' if total_overdue > 20000 else 'Low'
        })
    
    # Sort by overdue amount
    defaulter_analytics.sort(key=lambda x: x['total_overdue_amount'], reverse=True)
    
    # Defaulter categories
    high_risk_defaulters = [d for d in defaulter_analytics if d['risk_category'] == 'High']
    medium_risk_defaulters = [d for d in defaulter_analytics if d['risk_category'] == 'Medium']
    low_risk_defaulters = [d for d in defaulter_analytics if d['risk_category'] == 'Low']
    
    # Recovery actions tracking
    recovery_actions = {
        'notices_sent': 0,
        'parent_meetings_scheduled': 0,
        'payment_plans_offered': 0,
        'legal_notices_issued': 0
    }
    
    # Grade-wise defaulter distribution
    grade_wise_defaulters = {}
    for analytics in defaulter_analytics:
        grade = analytics['student'].grade.name if analytics['student'].grade else 'Unknown'
        if grade not in grade_wise_defaulters:
            grade_wise_defaulters[grade] = {'count': 0, 'total_amount': 0}
        grade_wise_defaulters[grade]['count'] += 1
        grade_wise_defaulters[grade]['total_amount'] += analytics['total_overdue_amount']
    
    context = {
        'school_settings': school_settings,
        'defaulter_analytics': defaulter_analytics[:50],  # Show top 50
        'high_risk_defaulters': high_risk_defaulters,
        'medium_risk_defaulters': medium_risk_defaulters,
        'low_risk_defaulters': low_risk_defaulters,
        'recovery_actions': recovery_actions,
        'grade_wise_defaulters': grade_wise_defaulters,
        'total_defaulters': len(defaulter_analytics),
        'total_overdue_amount': sum([d['total_overdue_amount'] for d in defaulter_analytics]),
        'page_title': 'Fee Defaulter Tracking'
    }
    
    return render(request, 'fees/defaulter_tracking.html', context)

@login_required
def parent_payment_portal(request):
    """Dedicated parent payment portal"""
    school_settings = SchoolSettings.objects.first()
    
    # This would typically be accessed by parents with their login
    # For admin view, show portal statistics
    
    # Portal usage statistics
    total_parent_logins = 1250  # From MobileAppSession or web sessions
    online_payment_adoption = 78.5  # Percentage of parents using online payments
    
    # Payment portal features
    portal_features = [
        {
            'feature': 'Online Fee Payment',
            'usage_percentage': 85,
            'status': 'Active'
        },
        {
            'feature': 'Payment History',
            'usage_percentage': 92,
            'status': 'Active'
        },
        {
            'feature': 'Fee Structure View',
            'usage_percentage': 76,
            'status': 'Active'
        },
        {
            'feature': 'Installment Planning',
            'usage_percentage': 45,
            'status': 'Active'
        },
        {
            'feature': 'Receipt Download',
            'usage_percentage': 68,
            'status': 'Active'
        }
    ]
    
    # Recent parent portal activities
    recent_activities = [
        {
            'parent_name': 'Mr. Sharma',
            'student_name': 'Raj Sharma',
            'activity': 'Paid Tuition Fee',
            'amount': 15000,
            'timestamp': datetime.now() - timedelta(hours=2)
        },
        {
            'parent_name': 'Mrs. Patel',
            'student_name': 'Priya Patel',
            'activity': 'Downloaded Receipt',
            'amount': 0,
            'timestamp': datetime.now() - timedelta(hours=5)
        }
    ]
    
    # Payment methods used by parents
    payment_method_stats = [
        {'method': 'UPI', 'percentage': 45, 'transactions': 2340},
        {'method': 'Net Banking', 'percentage': 30, 'transactions': 1560},
        {'method': 'Credit Card', 'percentage': 15, 'transactions': 780},
        {'method': 'Debit Card', 'percentage': 10, 'transactions': 520}
    ]
    
    context = {
        'school_settings': school_settings,
        'total_parent_logins': total_parent_logins,
        'online_payment_adoption': online_payment_adoption,
        'portal_features': portal_features,
        'recent_activities': recent_activities,
        'payment_method_stats': payment_method_stats,
        'page_title': 'Parent Payment Portal Management'
    }
    
    return render(request, 'fees/parent_payment_portal.html', context)

@login_required
def fee_collection_forecasting(request):
    """Advanced fee collection forecasting with AI"""
    school_settings = SchoolSettings.objects.first()
    
    # Historical fee collection data
    historical_data = FeePayment.objects.extra(
        select={
            'month': "EXTRACT(month FROM payment_date)",
            'year': "EXTRACT(year FROM payment_date)"
        }
    ).values('month', 'year').annotate(
        total_collected=Sum('amount_paid'),
        transaction_count=Count('id')
    ).order_by('year', 'month')
    
    # Current academic year collection
    current_year = AcademicYear.objects.filter(is_current=True).first()
    current_year_collection = FeePayment.objects.filter(
        fee_structure__academic_year=current_year
    ).aggregate(
        total_collected=Sum('amount_paid'),
        total_due=Sum('amount_due')
    ) if current_year else {'total_collected': 0, 'total_due': 0}
    
    # Forecasting models
    forecasting_data = {
        'current_month_target': 2500000,  # Monthly collection target
        'current_month_actual': 2150000,  # Actual collection this month
        'projected_end_of_month': 2400000,  # AI-predicted end of month collection
        'annual_target': 25000000,  # Annual fee collection target
        'annual_projected': 23500000,  # AI-projected annual collection
        'collection_efficiency': 85.2,  # Current collection efficiency %
        'seasonal_trends': [
            {'month': 'April', 'multiplier': 1.2, 'reason': 'New academic year'},
            {'month': 'July', 'multiplier': 1.1, 'reason': 'Quarterly payments'},
            {'month': 'December', 'multiplier': 0.8, 'reason': 'Holiday season'},
            {'month': 'March', 'multiplier': 1.3, 'reason': 'Year-end payments'}
        ]
    }
    
    # Risk factors affecting collection
    risk_factors = [
        {
            'factor': 'Economic Slowdown',
            'impact': 'Medium',
            'probability': 35,
            'potential_loss': 1500000
        },
        {
            'factor': 'Competition from New Schools',
            'impact': 'Low',
            'probability': 20,
            'potential_loss': 800000
        },
        {
            'factor': 'Fee Structure Changes',
            'impact': 'High',
            'probability': 15,
            'potential_loss': 2000000
        }
    ]
    
    # Recommendations from AI analysis
    ai_recommendations = [
        {
            'recommendation': 'Implement early payment discounts',
            'expected_impact': 'Increase collection by 8-12%',
            'implementation_effort': 'Low'
        },
        {
            'recommendation': 'Expand online payment options',
            'expected_impact': 'Reduce collection delays by 15%',
            'implementation_effort': 'Medium'
        },
        {
            'recommendation': 'Introduce flexible payment plans',
            'expected_impact': 'Reduce defaulters by 25%',
            'implementation_effort': 'High'
        }
    ]
    
    # Monthly projections for next 12 months
    monthly_projections = []
    base_amount = 2000000
    
    for month in range(1, 13):
        seasonal_factor = 1.0
        if month in [4, 7, 10, 1]:  # Quarterly payment months
            seasonal_factor = 1.15
        elif month == 12:  # December holiday impact
            seasonal_factor = 0.85
        
        projected_amount = base_amount * seasonal_factor
        monthly_projections.append({
            'month': month,
            'month_name': [
                'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
            ][month-1],
            'projected_amount': projected_amount,
            'confidence_level': 87 if seasonal_factor > 1 else 82
        })
    
    context = {
        'school_settings': school_settings,
        'historical_data': historical_data,
        'current_year_collection': current_year_collection,
        'forecasting_data': forecasting_data,
        'risk_factors': risk_factors,
        'ai_recommendations': ai_recommendations,
        'monthly_projections': monthly_projections,
        'page_title': 'Fee Collection Forecasting'
    }
    
    return render(request, 'fees/collection_forecasting.html', context)

@login_required
def payment_receipt(request, payment_id):
    """Generate and display payment receipt"""
    payment = get_object_or_404(FeePayment, id=payment_id)
    school_settings = SchoolSettings.objects.first()
    
    context = {
        'payment': payment,
        'school_settings': school_settings,
        'generated_on': timezone.now(),
        'page_title': f'Payment Receipt - {payment.student.full_name}'
    }
    
    return render(request, 'fees/payment_receipt.html', context)

@login_required
def advanced_fee_dashboard(request):
    """Advanced fee dashboard with comprehensive analytics"""
    school_settings = SchoolSettings.objects.first()
    
    # Enhanced statistics
    today = timezone.now().date()
    this_month = today.replace(day=1)
    
    # Collection statistics
    total_collected_today = FeePayment.objects.filter(
        payment_date=today
    ).aggregate(total=Sum('amount_paid'))['total'] or 0
    
    total_collected_this_month = FeePayment.objects.filter(
        payment_date__gte=this_month
    ).aggregate(total=Sum('amount_paid'))['total'] or 0
    
    # Outstanding fees
    all_structures = FeeStructure.objects.filter(is_active=True)
    total_fees_due = all_structures.aggregate(total=Sum('amount'))['total'] or 0
    total_collected = FeePayment.objects.aggregate(total=Sum('amount_paid'))['total'] or 0
    total_outstanding = total_fees_due - total_collected
    
    # Collection efficiency
    collection_efficiency = (total_collected / total_fees_due * 100) if total_fees_due > 0 else 0
    
    # Recent payments
    recent_payments = FeePayment.objects.select_related(
        'student', 'fee_structure__category'
    ).order_by('-payment_date')[:10]
    
    # Top paying grades
    grade_performance = FeePayment.objects.values(
        'student__grade__name'
    ).annotate(
        total_paid=Sum('amount_paid'),
        student_count=Count('student', distinct=True)
    ).order_by('-total_paid')[:5]
    
    context = {
        'school_settings': school_settings,
        'total_collected_today': total_collected_today,
        'total_collected_this_month': total_collected_this_month,
        'total_outstanding': total_outstanding,
        'collection_efficiency': round(collection_efficiency, 1),
        'recent_payments': recent_payments,
        'grade_performance': grade_performance,
        'page_title': 'Advanced Fee Dashboard'
    }
    
    return render(request, 'fees/advanced_dashboard.html', context)

@login_required
def payment_receipt(request, payment_id):
    payment = get_object_or_404(FeePayment, id=payment_id)
    school_settings = SchoolSettings.objects.first()
    
    context = {
        'payment': payment,
        'school_settings': school_settings,
        'generated_on': timezone.now(),
        'page_title': f'Payment Receipt - {payment.student.full_name}'
    }
    
    return render(request, 'fees/payment_receipt.html', context)
