from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count, Sum, Avg, F, Max, Min, StdDev, Case, When, Value, FloatField
from django.db.models.functions import Extract, TruncMonth, TruncWeek, TruncDay
from django.utils import timezone
from datetime import datetime, timedelta, date
import json
import csv
from decimal import Decimal

# Import all models for comprehensive analytics
from core.models import (
    Student, Teacher, AcademicYear, Campus, Department, Subject, Grade,
    FeeCategory, FeePayment, Exam, ExamResult, Attendance,
    SchoolSettings, SystemConfiguration
)
from admissions.models import AdmissionApplication
from finance.models import Expense, FeeStructure
from library.models import BookIssue
from transport.models import Vehicle, StudentTransport
from hr.models import EmployeeAttendance, LeaveRequest

# ===== MAIN ANALYTICS DASHBOARD =====
@login_required
def analytics_dashboard(request):
    """Advanced School Analytics Dashboard"""
    school_settings = SchoolSettings.objects.first()
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    
    # Overall School Statistics
    school_stats = {
        'total_students': Student.objects.filter(is_active=True).count(),
        'total_teachers': Teacher.objects.filter(is_active=True).count(),
        'total_grades': Grade.objects.count(),
        'total_subjects': Subject.objects.count(),
        'total_employees': Employee.objects.filter(status='active').count(),
        'active_vehicles': Vehicle.objects.filter(status='active').count(),
    }
    
    # Academic Performance Overview
    current_month = timezone.now().replace(day=1)
    academic_stats = {
        'total_exams_conducted': ExamResult.objects.filter(
            exam_date__gte=current_month
        ).values('exam').distinct().count(),
        'average_score': ExamResult.objects.filter(
            exam_date__gte=current_month
        ).aggregate(avg=Avg('marks_obtained'))['avg'] or 0,
        'top_performers': ExamResult.objects.filter(
            exam_date__gte=current_month,
            percentage__gte=90
        ).count(),
        'below_average': ExamResult.objects.filter(
            exam_date__gte=current_month,
            percentage__lt=40
        ).count(),
    }
    
    # Attendance Analytics
    today = timezone.now().date()
    attendance_stats = {
        'student_attendance_today': Attendance.objects.filter(
            date=today,
            is_present=True
        ).count(),
        'student_absence_today': Attendance.objects.filter(
            date=today,
            is_present=False
        ).count(),
        'employee_attendance_today': EmployeeAttendance.objects.filter(
            date=today,
            status='present'
        ).count(),
        'employee_leave_today': EmployeeAttendance.objects.filter(
            date=today,
            status='leave'
        ).count(),
    }
    
    # Financial Analytics
    financial_stats = {
        'monthly_revenue': FeePayment.objects.filter(
            payment_date__gte=current_month,
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0,
        'monthly_expenses': Expense.objects.filter(
            expense_date__gte=current_month,
            status='approved'
        ).aggregate(total=Sum('amount'))['total'] or 0,
        'pending_fees': FeePayment.objects.filter(
            status='pending'
        ).aggregate(total=Sum('amount'))['total'] or 0,
        'fee_collection_rate': 0,  # Calculate based on expected vs collected
    }
    
    # Calculate fee collection rate
    total_expected = FeeStructure.objects.filter(
        is_active=True
    ).aggregate(
        total=Sum(F('amount') * F('grade__student_count'))
    )['total'] or 0
    
    if total_expected > 0:
        financial_stats['fee_collection_rate'] = (
            financial_stats['monthly_revenue'] / total_expected * 100
        )
    
    # Admission Analytics
    admission_stats = {
        'total_applications': AdmissionApplication.objects.count(),
        'pending_applications': AdmissionApplication.objects.filter(
            status='pending'
        ).count(),
        'admission_rate': 0,
    }
    
    total_apps = admission_stats['total_applications']
    if total_apps > 0:
        approved_apps = AdmissionApplication.objects.filter(status='approved').count()
        admission_stats['admission_rate'] = (approved_apps / total_apps * 100)
    
    # Recent Trends (Last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    # Student enrollment trend
    enrollment_trend = []
    for i in range(30):
        date = (timezone.now() - timedelta(days=i)).date()
        new_students = Student.objects.filter(
            admission_date=date
        ).count()
        enrollment_trend.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': new_students
        })
    
    # Performance trends by grade
    grade_performance = Grade.objects.annotate(
        avg_performance=Avg('student__examresult__percentage',
                          filter=Q(student__examresult__exam_date__gte=thirty_days_ago)),
        student_count=Count('student', filter=Q(student__is_active=True))
    ).filter(avg_performance__isnull=False)
    
    # Top performing subjects
    subject_performance = Subject.objects.annotate(
        avg_score=Avg('examresult__percentage',
                     filter=Q(examresult__exam_date__gte=thirty_days_ago))
    ).filter(avg_score__isnull=False).order_by('-avg_score')[:10]
    
    # Library usage analytics
    library_stats = {
        'books_issued_today': BookIssue.objects.filter(
            issue_date=today
        ).count(),
        'books_returned_today': BookIssue.objects.filter(
            return_date=today
        ).count(),
        'overdue_books': BookIssue.objects.filter(
            due_date__lt=today,
            return_date__isnull=True
        ).count(),
    }
    
    # Transport analytics
    transport_stats = {
        'students_using_transport': StudentTransport.objects.filter(
            is_active=True
        ).count(),
        'vehicles_in_operation': Vehicle.objects.filter(
            status='active'
        ).count(),
        'transport_utilization': 0,
    }
    
    total_capacity = Vehicle.objects.filter(status='active').aggregate(
        total=Sum('capacity')
    )['total'] or 0
    
    if total_capacity > 0:
        transport_stats['transport_utilization'] = (
            transport_stats['students_using_transport'] / total_capacity * 100
        )
    
    context = {
        'page_title': 'School Analytics Dashboard',
        'school_settings': school_settings,
        'current_academic_year': current_academic_year,
        'school_stats': school_stats,
        'academic_stats': academic_stats,
        'attendance_stats': attendance_stats,
        'financial_stats': financial_stats,
        'admission_stats': admission_stats,
        'enrollment_trend': list(reversed(enrollment_trend))[:7],  # Last 7 days
        'grade_performance': grade_performance,
        'subject_performance': subject_performance,
        'library_stats': library_stats,
        'transport_stats': transport_stats,
    }
    
    return render(request, 'analytics/dashboard.html', context)

# ===== STUDENT ANALYTICS =====
@login_required
def student_analytics(request):
    """Detailed student performance and demographic analytics"""
    
    # Performance trends over time
    performance_trends = ExamResult.objects.annotate(
        month=TruncMonth('exam__exam_date')
    ).values('month').annotate(
        avg_percentage=Avg('percentage'),
        total_exams=Count('id')
    ).order_by('month')
    
    # Top performing students
    top_performers = Student.objects.annotate(
        avg_performance=Avg('examresult__percentage')
    ).filter(
        avg_performance__isnull=False
    ).order_by('-avg_performance')[:10]
    
    # Grade-wise performance comparison
    grade_performance = Grade.objects.annotate(
        avg_marks=Avg('student__examresult__marks_obtained'),
        total_students=Count('student', filter=Q(student__is_active=True)),
        avg_attendance=Avg('student__attendancerecord__status')
    ).order_by('grade_level')
    
    # Subject popularity
    subject_enrollment = Subject.objects.annotate(
        student_count=Count('examresult__student', distinct=True)
    ).order_by('-student_count')[:15]
    
    context = {
        'page_title': 'Student Analytics',
        'performance_trends': list(performance_trends),
        'top_performers': top_performers,
        'grade_performance': grade_performance,
        'subject_enrollment': subject_enrollment,
    }
    
    return render(request, 'analytics/student_analytics.html', context)

# ===== FINANCIAL ANALYTICS =====
@login_required
def financial_analytics(request):
    """Financial Analytics and Revenue Insights"""
    current_year = timezone.now().year
    current_month = timezone.now().replace(day=1)
    
    # Revenue analytics
    revenue_stats = {
        'monthly_revenue': FeePayment.objects.filter(
            payment_date__gte=current_month,
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0,
        'yearly_revenue': FeePayment.objects.filter(
            payment_date__year=current_year,
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0,
        'pending_fees': FeePayment.objects.filter(
            status='pending'
        ).aggregate(total=Sum('amount'))['total'] or 0,
        'overdue_fees': FeePayment.objects.filter(
            status='overdue'
        ).aggregate(total=Sum('amount'))['total'] or 0,
    }
    
    # Expense analytics
    expense_stats = {
        'monthly_expenses': Expense.objects.filter(
            expense_date__gte=current_month,
            status='approved'
        ).aggregate(total=Sum('amount'))['total'] or 0,
        'yearly_expenses': Expense.objects.filter(
            expense_date__year=current_year,
            status='approved'
        ).aggregate(total=Sum('amount'))['total'] or 0,
        'pending_approvals': Expense.objects.filter(
            status='pending'
        ).count(),
    }
    
    # Monthly financial trends
    financial_trends = []
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
        
        profit = revenue - expenses
        
        financial_trends.append({
            'month': month_start.strftime('%b %Y'),
            'revenue': float(revenue),
            'expenses': float(expenses),
            'profit': float(profit)
        })
    
    # Grade-wise fee collection
    grade_collection = Grade.objects.annotate(
        total_students=Count('student', filter=Q(student__is_active=True)),
        fees_collected=Sum('student__feepayment__amount',
                         filter=Q(student__feepayment__status='completed')),
        pending_fees=Sum('student__feepayment__amount',
                        filter=Q(student__feepayment__status='pending'))
    ).filter(total_students__gt=0)
    
    # Fee defaulters analysis
    defaulters = Student.objects.annotate(
        pending_amount=Sum('feepayment__amount',
                         filter=Q(feepayment__status='pending')),
        overdue_amount=Sum('feepayment__amount',
                         filter=Q(feepayment__status='overdue'))
    ).filter(Q(pending_amount__gt=0) | Q(overdue_amount__gt=0))
    
    context = {
        'page_title': 'Financial Analytics',
        'revenue_stats': revenue_stats,
        'expense_stats': expense_stats,
        'financial_trends': list(reversed(financial_trends)),
        'grade_collection': grade_collection,
        'defaulters': defaulters[:20],
        'net_profit': revenue_stats['monthly_revenue'] - expense_stats['monthly_expenses'],
    }
    
    return render(request, 'analytics/financial_analytics.html', context)

# ===== ATTENDANCE ANALYTICS =====
@login_required
def attendance_analytics(request):
    """Attendance Analytics and Insights"""
    # Overall attendance statistics
    total_students = Student.objects.filter(is_active=True).count()
    today = timezone.now().date()
    current_month = timezone.now().replace(day=1).date()
    
    # Daily attendance summary
    daily_attendance = {
        'present_today': Attendance.objects.filter(date=today, is_present=True).count(),
        'absent_today': Attendance.objects.filter(date=today, is_present=False).count(),
        'attendance_rate_today': 0,
    }
    
    if total_students > 0:
        daily_attendance['attendance_rate_today'] = (
            daily_attendance['present_today'] / total_students * 100
        )
    
    # Monthly attendance trends
    monthly_attendance = []
    for i in range(30):
        date = (timezone.now() - timedelta(days=i)).date()
        present_count = Attendance.objects.filter(date=date, is_present=True).count()
        total_marked = Attendance.objects.filter(date=date).count()
        
        rate = (present_count / total_marked * 100) if total_marked > 0 else 0
        
        monthly_attendance.append({
            'date': date.strftime('%Y-%m-%d'),
            'attendance_rate': round(rate, 2),
            'present_count': present_count,
            'total_count': total_marked
        })
    
    # Grade-wise attendance
    grade_attendance = Grade.objects.annotate(
        total_students=Count('student', filter=Q(student__is_active=True)),
        present_today=Count('student__attendance', 
                          filter=Q(student__attendance__date=today,
                                  student__attendance__is_present=True)),
        monthly_avg_attendance=Avg('student__attendance__is_present',
                                 filter=Q(student__attendance__date__gte=current_month))
    ).filter(total_students__gt=0)
    
    # Chronic absentees (students with <75% attendance)
    chronic_absentees = Student.objects.annotate(
        attendance_rate=Avg('attendance__is_present',
                          filter=Q(attendance__date__gte=current_month)) * 100
    ).filter(attendance_rate__lt=75, attendance_rate__isnull=False)
    
    # Perfect attendance students
    perfect_attendance = Student.objects.annotate(
        attendance_rate=Avg('attendance__is_present',
                          filter=Q(attendance__date__gte=current_month)) * 100
    ).filter(attendance_rate=100)
    
    # Teacher attendance
    teacher_attendance = {
        'present_today': EmployeeAttendance.objects.filter(
            date=today, status='present'
        ).count(),
        'on_leave_today': EmployeeAttendance.objects.filter(
            date=today, status='leave'
        ).count(),
        'absent_today': EmployeeAttendance.objects.filter(
            date=today, status='absent'
        ).count(),
    }
    
    context = {
        'page_title': 'Attendance Analytics',
        'daily_attendance': daily_attendance,
        'monthly_attendance': list(reversed(monthly_attendance))[:30],
        'grade_attendance': grade_attendance,
        'chronic_absentees': chronic_absentees[:20],
        'perfect_attendance': perfect_attendance[:20],
        'teacher_attendance': teacher_attendance,
    }
    
    return render(request, 'analytics/attendance_analytics.html', context)

# ===== PERFORMANCE ANALYTICS =====
@login_required
def performance_analytics(request):
    """Academic performance analysis and predictions"""
    
    # Subject-wise performance analysis
    subject_analysis = Subject.objects.annotate(
        avg_marks=Avg('examresult__marks_obtained'),
        max_marks=Max('examresult__marks_obtained'),
        min_marks=Min('examresult__marks_obtained'),
        std_deviation=StdDev('examresult__marks_obtained'),
        total_exams=Count('examresult'),
        pass_rate=Count('examresult', filter=Q(examresult__percentage__gte=35)) * 100.0 / Count('examresult')
    ).filter(total_exams__gt=0).order_by('-avg_marks')
    
    # Grade-wise performance comparison
    grade_comparison = Grade.objects.annotate(
        avg_percentage=Avg('student__examresult__percentage'),
        total_students=Count('student', filter=Q(student__is_active=True)),
        total_exams=Count('student__examresult'),
        distinction_count=Count('student__examresult', filter=Q(student__examresult__percentage__gte=75)),
        first_class_count=Count('student__examresult', filter=Q(
            student__examresult__percentage__gte=60,
            student__examresult__percentage__lt=75
        )),
        pass_count=Count('student__examresult', filter=Q(
            student__examresult__percentage__gte=35,
            student__examresult__percentage__lt=60
        )),
        fail_count=Count('student__examresult', filter=Q(student__examresult__percentage__lt=35))
    ).filter(total_exams__gt=0).order_by('grade_level')
    
    # Performance trends over time
    performance_trends = ExamResult.objects.annotate(
        month=TruncMonth('exam__exam_date')
    ).values('month').annotate(
        avg_percentage=Avg('percentage'),
        total_students=Count('student', distinct=True),
        total_exams=Count('id')
    ).order_by('month')
    
    # Top and bottom performers
    top_performers = Student.objects.annotate(
        avg_percentage=Avg('examresult__percentage'),
        total_exams=Count('examresult')
    ).filter(
        total_exams__gte=3,  # At least 3 exams
        avg_percentage__isnull=False
    ).order_by('-avg_percentage')[:10]
    
    bottom_performers = Student.objects.annotate(
        avg_percentage=Avg('examresult__percentage'),
        total_exams=Count('examresult')
    ).filter(
        total_exams__gte=3,
        avg_percentage__isnull=False,
        avg_percentage__lt=50  # Below 50%
    ).order_by('avg_percentage')[:10]
    
    # Exam-wise analysis
    recent_exams = Exam.objects.annotate(
        avg_marks=Avg('examresult__marks_obtained'),
        total_students=Count('examresult__student', distinct=True),
        pass_rate=Count('examresult', filter=Q(examresult__percentage__gte=35)) * 100.0 / Count('examresult')
    ).filter(total_students__gt=0).order_by('-exam_date')[:10]
    
    context = {
        'page_title': 'Performance Analytics',
        'subject_analysis': subject_analysis,
        'grade_comparison': grade_comparison,
        'performance_trends': list(performance_trends),
        'top_performers': top_performers,
        'bottom_performers': bottom_performers,
        'recent_exams': recent_exams,
    }
    
    return render(request, 'analytics/performance_analytics.html', context)

# ===== PREDICTIVE ANALYTICS =====
@login_required
def predictive_analytics(request):
    """Predictive Analytics and Forecasting"""
    # Student performance prediction
    students_at_risk = Student.objects.annotate(
        avg_score=Avg('examresult__percentage'),
        attendance_rate=Avg('attendance__is_present') * 100,
        recent_performance=Avg('examresult__percentage',
                             filter=Q(examresult__exam_date__gte=timezone.now() - timedelta(days=30)))
    ).filter(
        Q(avg_score__lt=40) | Q(attendance_rate__lt=75) | Q(recent_performance__lt=35)
    ).exclude(avg_score__isnull=True)
    
    # Fee collection prediction
    current_month = timezone.now().replace(day=1)
    monthly_collection = FeePayment.objects.filter(
        payment_date__gte=current_month,
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Calculate average monthly collection for prediction
    avg_monthly_collection = FeePayment.objects.filter(
        payment_date__gte=timezone.now() - timedelta(days=365),
        status='completed'
    ).extra(
        select={'month': "DATE_FORMAT(payment_date, '%%Y-%%m')"}
    ).values('month').annotate(
        total=Sum('amount')
    ).aggregate(avg=Avg('total'))['avg'] or 0
    
    # Enrollment prediction based on trends
    enrollment_trend = Student.objects.filter(
        admission_date__gte=timezone.now() - timedelta(days=365)
    ).extra(
        select={'month': "DATE_FORMAT(admission_date, '%%Y-%%m')"}
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    # Resource utilization prediction
    resource_utilization = {
        'library_capacity': library_stats.get('books_issued_this_month', 0) / 1000 * 100,  # Assuming 1000 book capacity
        'transport_capacity': transport_stats.get('students_using_transport', 0) / 
                            (Vehicle.objects.filter(status='active').aggregate(
                                total=Sum('capacity'))['total'] or 1) * 100,
        'classroom_utilization': Grade.objects.aggregate(
            total_students=Sum('student_count')
        )['total_students'] or 0 / 1500 * 100,  # Assuming 1500 total capacity
    }
    
    context = {
        'page_title': 'Predictive Analytics',
        'students_at_risk': students_at_risk[:20],
        'monthly_collection': monthly_collection,
        'predicted_collection': avg_monthly_collection,
        'enrollment_trend': list(enrollment_trend),
        'resource_utilization': resource_utilization,
    }
    
    return render(request, 'analytics/predictive_analytics.html', context)

# ===== EXPORT FUNCTIONS =====
@login_required
def export_analytics_data(request):
    """Export analytics data to CSV"""
    export_type = request.GET.get('type', 'overview')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="analytics_{export_type}.csv"'
    
    writer = csv.writer(response)
    
    if export_type == 'performance':
        writer.writerow(['Grade', 'Total Students', 'Average Performance', 'Pass Rate'])
        
        grade_data = Grade.objects.annotate(
            total_students=Count('student', filter=Q(student__is_active=True)),
            avg_performance=Avg('student__examresult__percentage'),
            pass_rate=Count('student__examresult',
                          filter=Q(student__examresult__percentage__gte=40)) * 100.0 /
                     Count('student__examresult')
        ).filter(total_students__gt=0)
        
        for grade in grade_data:
            writer.writerow([
                grade.name,
                grade.total_students,
                round(grade.avg_performance or 0, 2),
                round(grade.pass_rate or 0, 2)
            ])
    
    elif export_type == 'financial':
        writer.writerow(['Month', 'Revenue', 'Expenses', 'Profit'])
        
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
            
            writer.writerow([
                month_start.strftime('%b %Y'),
                revenue,
                expenses,
                revenue - expenses
            ])
    
    return response

# ===== API ENDPOINTS FOR CHARTS =====
@login_required
def analytics_api(request):
    """API endpoint for analytics data for charts"""
    chart_type = request.GET.get('type', 'overview')
    
    if chart_type == 'overview':
        # Overall school statistics for dashboard
        data = {
            'students': Student.objects.filter(is_active=True).count(),
            'teachers': Teacher.objects.filter(is_active=True).count(),
            'revenue': FeePayment.objects.filter(
                payment_date__gte=timezone.now().replace(day=1),
                status='completed'
            ).aggregate(total=Sum('amount'))['total'] or 0,
            'attendance_rate': Attendance.objects.filter(
                date=timezone.now().date()
            ).aggregate(
                rate=Count('id', filter=Q(is_present=True)) * 100.0 / Count('id')
            )['rate'] or 0,
        }
    
    elif chart_type == 'performance':
        # Grade-wise performance data
        data = list(Grade.objects.annotate(
            avg_performance=Avg('student__examresult__percentage')
        ).values('name', 'avg_performance'))
    
    elif chart_type == 'attendance':
        # Monthly attendance trends
        data = []
        for i in range(12):
            month_start = (timezone.now().replace(day=1) - timedelta(days=i*30)).replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            attendance_rate = Attendance.objects.filter(
                date__range=[month_start.date(), month_end.date()]
            ).aggregate(
                rate=Count('id', filter=Q(is_present=True)) * 100.0 / Count('id')
            )['rate'] or 0
            
            data.append({
                'month': month_start.strftime('%b %Y'),
                'attendance_rate': round(attendance_rate, 2)
            })
    
    elif chart_type == 'financial':
        # Financial trends
        data = []
        for i in range(6):
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
            
            data.append({
                'month': month_start.strftime('%b %Y'),
                'revenue': float(revenue),
                'expenses': float(expenses),
                'profit': float(revenue - expenses)
            })
    
    return JsonResponse({
        'data': data,
        'status': 'success'
    })

# ===== CUSTOM REPORTS =====
@login_required
def custom_reports(request):
    """Custom Report Builder"""
    if request.method == 'POST':
        report_type = request.POST.get('report_type')
        date_from = request.POST.get('date_from')
        date_to = request.POST.get('date_to')
        filters = request.POST.get('filters', '{}')
        
        # Process custom report based on parameters
        # This would be expanded based on specific requirements
        
        context = {
            'page_title': 'Custom Report Results',
            'report_type': report_type,
            'date_from': date_from,
            'date_to': date_to,
        }
        
        return render(request, 'analytics/custom_report_results.html', context)
    
    context = {
        'page_title': 'Custom Report Builder',
        'grades': Grade.objects.all(),
        'subjects': Subject.objects.all(),
    }
    
    return render(request, 'analytics/custom_reports.html', context)
