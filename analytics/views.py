from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
import csv

# Import available models only
from core.models import Student, Teacher, Grade, Subject, SchoolSettings
from fees.models import FeePayment
from examinations.models import ExamResult
from academics.models import Attendance
from hr.models import Employee

@login_required
def analytics_dashboard(request):
    """Main Analytics Dashboard"""
    school_settings = SchoolSettings.objects.first()
    
    # Basic Statistics
    stats = {
        'total_students': Student.objects.filter(is_active=True).count(),
        'total_teachers': Teacher.objects.filter(is_active=True).count(),
        'total_grades': Grade.objects.count(),
        'total_subjects': Subject.objects.count(),
        'total_employees': Employee.objects.filter(employment_status='ACTIVE').count(),
    }
    
    # Financial Stats
    current_month = timezone.now().replace(day=1)
    financial_stats = {
        'monthly_revenue': FeePayment.objects.filter(
            payment_date__gte=current_month,
            status='COMPLETED'
        ).aggregate(total=Sum('amount'))['total'] or 0,
        'pending_fees': FeePayment.objects.filter(
            status='PENDING'
        ).aggregate(total=Sum('amount'))['total'] or 0,
    }
    
    # Attendance Stats
    today = timezone.now().date()
    attendance_stats = {
        'present_today': Attendance.objects.filter(
            date=today, is_present=True
        ).count(),
        'absent_today': Attendance.objects.filter(
            date=today, is_present=False
        ).count(),
    }
    
    # Academic Stats
    academic_stats = {
        'total_exams': ExamResult.objects.count(),
        'average_score': ExamResult.objects.aggregate(
            avg=Avg('percentage')
        )['avg'] or 0,
    }
    
    context = {
        'page_title': 'Analytics Dashboard',
        'school_settings': school_settings,
        'stats': stats,
        'financial_stats': financial_stats,
        'attendance_stats': attendance_stats,
        'academic_stats': academic_stats,
    }
    
    return render(request, 'analytics/analytics_dashboard.html', context)

@login_required
def student_analytics(request):
    """Student Analytics"""
    context = {
        'page_title': 'Student Analytics',
        'message': 'Student analytics module is working.'
    }
    return render(request, 'analytics/student_analytics.html', context)

@login_required
def financial_analytics(request):
    """Financial Analytics"""
    context = {
        'page_title': 'Financial Analytics',
        'message': 'Financial analytics module is working.'
    }
    return render(request, 'analytics/financial_analytics.html', context)

@login_required
def attendance_analytics(request):
    """Attendance Analytics"""
    context = {
        'page_title': 'Attendance Analytics',
        'message': 'Attendance analytics module is working.'
    }
    return render(request, 'analytics/attendance_analytics.html', context)

@login_required
def performance_analytics(request):
    """Performance Analytics"""
    context = {
        'page_title': 'Performance Analytics',
        'message': 'Performance analytics module is working.'
    }
    return render(request, 'analytics/performance_analytics.html', context)

@login_required
def analytics_api(request):
    """Analytics API"""
    data = {
        'students': Student.objects.filter(is_active=True).count(),
        'teachers': Teacher.objects.filter(is_active=True).count(),
        'status': 'success'
    }
    return JsonResponse(data)

@login_required
def export_analytics_data(request):
    """Export Analytics Data"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="analytics.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Metric', 'Value'])
    writer.writerow(['Students', Student.objects.filter(is_active=True).count()])
    writer.writerow(['Teachers', Teacher.objects.filter(is_active=True).count()])
    
    return response
