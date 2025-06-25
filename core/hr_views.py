from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import (
    Employee, HRAnalytics, Department, LeaveApplication, 
    PerformanceReview, TrainingEnrollment, EmployeePayroll
)
import json


def is_hr_staff(user):
    """Check if user has HR permissions"""
    return user.is_staff or user.groups.filter(name='HR').exists()


@login_required
@user_passes_test(is_hr_staff)
def hr_dashboard(request):
    """HR Dashboard with key metrics"""
    # Get current period data
    today = timezone.now().date()
    current_month_start = today.replace(day=1)
    last_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
    
    # Employee metrics
    total_employees = Employee.objects.filter(employment_status='ACTIVE').count()
    new_hires_this_month = Employee.objects.filter(
        date_of_joining__gte=current_month_start,
        employment_status='ACTIVE'
    ).count()
    
    # Leave metrics
    pending_leaves = LeaveApplication.objects.filter(status='PENDING').count()
    approved_leaves_today = LeaveApplication.objects.filter(
        status='APPROVED',
        start_date__lte=today,
        end_date__gte=today
    ).count()
    
    # Performance metrics
    pending_reviews = PerformanceReview.objects.filter(
        status__in=['DRAFT', 'SELF_ASSESSMENT', 'MANAGER_REVIEW']
    ).count()
    
    # Training metrics
    active_trainings = TrainingEnrollment.objects.filter(
        status__in=['REGISTERED', 'CONFIRMED'],
        training_program__start_date__gte=today
    ).count()
    
    # Payroll metrics
    pending_payrolls = EmployeePayroll.objects.filter(
        is_processed=False,
        pay_period_end__lt=today
    ).count()
    
    # Recent HR analytics
    recent_analytics = HRAnalytics.objects.order_by('-created_at')[:5]
    
    # Department-wise employee distribution
    dept_distribution = Employee.objects.filter(
        employment_status='ACTIVE'
    ).values('department__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    context = {
        'total_employees': total_employees,
        'new_hires_this_month': new_hires_this_month,
        'pending_leaves': pending_leaves,
        'approved_leaves_today': approved_leaves_today,
        'pending_reviews': pending_reviews,
        'active_trainings': active_trainings,
        'pending_payrolls': pending_payrolls,
        'recent_analytics': recent_analytics,
        'dept_distribution': dept_distribution,
    }
    
    return render(request, 'hr/dashboard.html', context)


@login_required
@user_passes_test(is_hr_staff)
def hr_analytics_list(request):
    """List all HR analytics reports"""
    analytics_type = request.GET.get('type')
    department_id = request.GET.get('department')
    
    analytics_qs = HRAnalytics.objects.all().order_by('-created_at')
    
    if analytics_type:
        analytics_qs = analytics_qs.filter(analytics_type=analytics_type)
    
    if department_id:
        analytics_qs = analytics_qs.filter(department_id=department_id)
    
    # Get filter options
    analytics_types = HRAnalytics.ANALYTICS_TYPES
    departments = Department.objects.filter(is_active=True)
    
    context = {
        'analytics': analytics_qs,
        'analytics_types': analytics_types,
        'departments': departments,
        'selected_type': analytics_type,
        'selected_department': department_id,
    }
    
    return render(request, 'hr/analytics_list.html', context)


@login_required
@user_passes_test(is_hr_staff)
def hr_analytics_detail(request, analytics_id):
    """Detailed view of HR analytics report"""
    analytics = get_object_or_404(HRAnalytics, id=analytics_id)
    
    context = {
        'analytics': analytics,
    }
    
    return render(request, 'hr/analytics_detail.html', context)


@login_required
@user_passes_test(is_hr_staff)
def employee_analytics_api(request):
    """API endpoint for employee analytics data"""
    period = request.GET.get('period', '12')  # months
    department_id = request.GET.get('department')
    
    try:
        period_months = int(period)
    except ValueError:
        period_months = 12
    
    # Calculate date range
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=period_months * 30)
    
    # Base queryset
    employees_qs = Employee.objects.all()
    if department_id:
        employees_qs = employees_qs.filter(department_id=department_id)
    
    # Employee status distribution
    status_distribution = employees_qs.values('employment_status').annotate(
        count=Count('id')
    )
    
    # Monthly hiring trend
    monthly_hires = []
    for i in range(period_months):
        month_start = end_date.replace(day=1) - timedelta(days=i*30)
        month_end = month_start + timedelta(days=30)
        hires = employees_qs.filter(
            date_of_joining__range=[month_start, month_end]
        ).count()
        monthly_hires.append({
            'month': month_start.strftime('%Y-%m'),
            'hires': hires
        })
    
    # Department distribution
    dept_distribution = employees_qs.filter(
        employment_status='ACTIVE'
    ).values('department__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Age distribution
    age_ranges = {
        '20-30': employees_qs.filter(
            date_of_birth__gte=end_date - timedelta(days=30*365),
            date_of_birth__lt=end_date - timedelta(days=20*365)
        ).count(),
        '31-40': employees_qs.filter(
            date_of_birth__gte=end_date - timedelta(days=40*365),
            date_of_birth__lt=end_date - timedelta(days=30*365)
        ).count(),
        '41-50': employees_qs.filter(
            date_of_birth__gte=end_date - timedelta(days=50*365),
            date_of_birth__lt=end_date - timedelta(days=40*365)
        ).count(),
        '50+': employees_qs.filter(
            date_of_birth__lt=end_date - timedelta(days=50*365)
        ).count(),
    }
    
    data = {
        'status_distribution': list(status_distribution),
        'monthly_hires': monthly_hires,
        'department_distribution': list(dept_distribution),
        'age_distribution': age_ranges,
        'total_employees': employees_qs.count(),
        'active_employees': employees_qs.filter(employment_status='ACTIVE').count(),
    }
    
    return JsonResponse(data)


@login_required
@user_passes_test(is_hr_staff)
def leave_analytics_api(request):
    """API endpoint for leave analytics data"""
    period = request.GET.get('period', '12')  # months
    department_id = request.GET.get('department')
    
    try:
        period_months = int(period)
    except ValueError:
        period_months = 12
    
    # Calculate date range
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=period_months * 30)
    
    # Base queryset
    leaves_qs = LeaveApplication.objects.filter(
        start_date__gte=start_date,
        start_date__lte=end_date
    )
    
    if department_id:
        leaves_qs = leaves_qs.filter(employee__department_id=department_id)
    
    # Leave type distribution
    leave_type_distribution = leaves_qs.values(
        'leave_type__name'
    ).annotate(
        count=Count('id'),
        total_days=Count('total_days')
    ).order_by('-count')
    
    # Leave status distribution
    status_distribution = leaves_qs.values('status').annotate(
        count=Count('id')
    )
    
    # Monthly leave trend
    monthly_leaves = []
    for i in range(period_months):
        month_start = end_date.replace(day=1) - timedelta(days=i*30)
        month_end = month_start + timedelta(days=30)
        leaves = leaves_qs.filter(
            start_date__range=[month_start, month_end]
        ).count()
        monthly_leaves.append({
            'month': month_start.strftime('%Y-%m'),
            'leaves': leaves
        })
    
    # Department-wise leave statistics
    dept_leaves = leaves_qs.values(
        'employee__department__name'
    ).annotate(
        count=Count('id'),
        avg_days=Avg('total_days')
    ).order_by('-count')
    
    data = {
        'leave_type_distribution': list(leave_type_distribution),
        'status_distribution': list(status_distribution),
        'monthly_leaves': monthly_leaves,
        'department_leaves': list(dept_leaves),
        'total_applications': leaves_qs.count(),
        'approved_applications': leaves_qs.filter(status='APPROVED').count(),
        'pending_applications': leaves_qs.filter(status='PENDING').count(),
    }
    
    return JsonResponse(data)


@login_required
@user_passes_test(is_hr_staff)
def performance_analytics_api(request):
    """API endpoint for performance analytics data"""
    period = request.GET.get('period', '12')  # months
    department_id = request.GET.get('department')
    
    try:
        period_months = int(period)
    except ValueError:
        period_months = 12
    
    # Calculate date range
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=period_months * 30)
    
    # Base queryset
    reviews_qs = PerformanceReview.objects.filter(
        review_period_start__gte=start_date,
        review_period_end__lte=end_date,
        status='COMPLETED'
    )
    
    if department_id:
        reviews_qs = reviews_qs.filter(employee__department_id=department_id)
    
    # Performance rating distribution
    rating_ranges = {
        'Excellent (4.5-5.0)': reviews_qs.filter(overall_rating__gte=4.5).count(),
        'Good (3.5-4.4)': reviews_qs.filter(
            overall_rating__gte=3.5, overall_rating__lt=4.5
        ).count(),
        'Average (2.5-3.4)': reviews_qs.filter(
            overall_rating__gte=2.5, overall_rating__lt=3.5
        ).count(),
        'Below Average (<2.5)': reviews_qs.filter(overall_rating__lt=2.5).count(),
    }
    
    # Department-wise performance
    dept_performance = reviews_qs.values(
        'employee__department__name'
    ).annotate(
        count=Count('id'),
        avg_rating=Avg('overall_rating')
    ).order_by('-avg_rating')
    
    # Review type distribution
    review_type_distribution = reviews_qs.values('review_type').annotate(
        count=Count('id'),
        avg_rating=Avg('overall_rating')
    )
    
    # Performance trend over time
    performance_trend = []
    for i in range(min(period_months, 12)):  # Max 12 months for trend
        month_start = end_date.replace(day=1) - timedelta(days=i*30)
        month_end = month_start + timedelta(days=30)
        month_reviews = reviews_qs.filter(
            review_period_start__range=[month_start, month_end]
        )
        avg_rating = month_reviews.aggregate(avg=Avg('overall_rating'))['avg'] or 0
        performance_trend.append({
            'month': month_start.strftime('%Y-%m'),
            'avg_rating': round(avg_rating, 2),
            'review_count': month_reviews.count()
        })
    
    data = {
        'rating_distribution': rating_ranges,
        'department_performance': list(dept_performance),
        'review_type_distribution': list(review_type_distribution),
        'performance_trend': performance_trend,
        'total_reviews': reviews_qs.count(),
        'avg_overall_rating': reviews_qs.aggregate(avg=Avg('overall_rating'))['avg'] or 0,
    }
    
    return JsonResponse(data) 