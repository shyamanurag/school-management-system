from rest_framework import serializers, viewsets, generics, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q, Count, Avg, Sum, Max, Min
from django.utils import timezone
from datetime import datetime, timedelta
from core.models import (
    Student, Grade, Attendance, ExamResult, FeePayment, AcademicYear
)
from .serializers import StudentSerializer, StudentCreateSerializer
import json

# ===== ADVANCED STUDENT ANALYTICS API =====

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def student_analytics_dashboard_api(request):
    """Comprehensive student analytics for dashboard"""
    
    # Basic Statistics
    total_students = Student.objects.filter(is_active=True).count()
    male_students = Student.objects.filter(is_active=True, gender='M').count()
    female_students = Student.objects.filter(is_active=True, gender='F').count()
    
    # Grade-wise distribution
    grade_distribution = Student.objects.filter(is_active=True).values(
        'grade__name', 'grade__numeric_value'
    ).annotate(
        student_count=Count('id'),
        male_count=Count('id', filter=Q(gender='M')),
        female_count=Count('id', filter=Q(gender='F'))
    ).order_by('grade__numeric_value')
    
    # Recent admissions (last 30 days)
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    recent_admissions = Student.objects.filter(
        is_active=True,
        admission_date__gte=thirty_days_ago
    ).count()
    
    # Performance statistics
    try:
        performance_stats = ExamResult.objects.aggregate(
            total_results=Count('id'),
            average_percentage=Avg('percentage'),
            highest_score=Max('total_marks_obtained'),
            lowest_score=Min('total_marks_obtained')
        )
        
        # Top performers (above 85%)
        top_performers = ExamResult.objects.filter(
            percentage__gte=85
        ).values(
            'student__id', 'student__first_name', 'student__last_name',
            'student__admission_number'
        ).annotate(
            avg_percentage=Avg('percentage'),
            total_exams=Count('id')
        ).order_by('-avg_percentage')[:10]
        
    except:
        performance_stats = {
            'total_results': 0,
            'average_percentage': 0,
            'highest_score': 0,
            'lowest_score': 0
        }
        top_performers = []
    
    # Attendance statistics
    try:
        today = timezone.now().date()
        attendance_today = Attendance.objects.filter(date=today)
        present_today = attendance_today.filter(status='PRESENT').count()
        total_today = attendance_today.count()
        attendance_rate = (present_today / total_today * 100) if total_today > 0 else 0
        
        # Weekly attendance trend
        week_start = today - timedelta(days=6)
        weekly_attendance = []
        for i in range(7):
            day = week_start + timedelta(days=i)
            day_attendance = Attendance.objects.filter(date=day)
            day_total = day_attendance.count()
            day_present = day_attendance.filter(status='PRESENT').count()
            day_rate = (day_present / day_total * 100) if day_total > 0 else 0
            
            weekly_attendance.append({
                'date': day.strftime('%Y-%m-%d'),
                'day': day.strftime('%a'),
                'attendance_rate': round(day_rate, 1),
                'present_count': day_present,
                'total_count': day_total
            })
            
    except:
        attendance_rate = 0
        weekly_attendance = []
    
    # Fee payment statistics
    try:
        fee_stats = FeePayment.objects.aggregate(
            total_payments=Count('id'),
            total_amount_paid=Sum('amount_paid'),
            total_amount_due=Sum('amount_due')
        )
        
        # Calculate outstanding fees
        outstanding_fees = fee_stats['total_amount_due'] - fee_stats['total_amount_paid']
        outstanding_fees = max(0, outstanding_fees) if outstanding_fees else 0
        
    except:
        fee_stats = {
            'total_payments': 0,
            'total_amount_paid': 0,
            'total_amount_due': 0
        }
        outstanding_fees = 0
    
    return Response({
        'student_statistics': {
            'total_students': total_students,
            'male_students': male_students,
            'female_students': female_students,
            'recent_admissions': recent_admissions
        },
        'grade_distribution': list(grade_distribution),
        'performance_overview': {
            'total_exam_results': performance_stats['total_results'],
            'average_percentage': round(performance_stats['average_percentage'] or 0, 2),
            'highest_score': performance_stats['highest_score'] or 0,
            'lowest_score': performance_stats['lowest_score'] or 0,
            'top_performers_count': len(top_performers)
        },
        'top_performers': list(top_performers),
        'attendance_overview': {
            'today_attendance_rate': round(attendance_rate, 1),
            'present_today': present_today if 'present_today' in locals() else 0,
            'total_today': total_today if 'total_today' in locals() else 0,
            'weekly_trend': weekly_attendance
        },
        'financial_overview': {
            'total_payments': fee_stats['total_payments'],
            'total_amount_paid': float(fee_stats['total_amount_paid'] or 0),
            'total_amount_due': float(fee_stats['total_amount_due'] or 0),
            'outstanding_fees': float(outstanding_fees)
        },
        'timestamp': timezone.now().isoformat()
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def student_performance_analytics_api(request, student_id):
    """Detailed performance analytics for individual student"""
    try:
        student = Student.objects.get(id=student_id, is_active=True)
    except Student.DoesNotExist:
        return Response({
            'error': 'Student not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Basic student info
    student_info = {
        'id': student.id,
        'full_name': student.full_name,
        'admission_number': student.admission_number,
        'grade': student.grade.name if student.grade else None,
        'gender': student.get_gender_display(),
        'admission_date': student.admission_date
    }
    
    # Academic performance
    try:
        exam_results = ExamResult.objects.filter(student=student).select_related('exam', 'subject')
        
        if exam_results.exists():
            performance_summary = exam_results.aggregate(
                total_exams=Count('id'),
                average_percentage=Avg('percentage'),
                highest_score=Max('percentage'),
                lowest_score=Min('percentage'),
                total_marks_obtained=Sum('total_marks_obtained'),
                total_max_marks=Sum('exam__total_marks')
            )
            
            # Subject-wise performance
            subject_performance = exam_results.values(
                'subject__name'
            ).annotate(
                exam_count=Count('id'),
                avg_percentage=Avg('percentage'),
                total_marks=Sum('total_marks_obtained'),
                max_marks=Sum('exam__total_marks')
            ).order_by('subject__name')
            
            # Recent exam results (last 10)
            recent_results = exam_results.order_by('-exam__start_date')[:10]
            recent_results_data = [{
                'exam_name': result.exam.name,
                'subject': result.subject.name if result.subject else 'N/A',
                'marks_obtained': result.total_marks_obtained,
                'total_marks': result.exam.total_marks,
                'percentage': result.percentage,
                'exam_date': result.exam.start_date,
                'is_passed': result.is_passed
            } for result in recent_results]
            
        else:
            performance_summary = {
                'total_exams': 0,
                'average_percentage': 0,
                'highest_score': 0,
                'lowest_score': 0
            }
            subject_performance = []
            recent_results_data = []
            
    except:
        performance_summary = {'total_exams': 0, 'average_percentage': 0, 'highest_score': 0, 'lowest_score': 0}
        subject_performance = []
        recent_results_data = []
    
    # Attendance analysis
    try:
        attendance_records = Attendance.objects.filter(student=student)
        
        if attendance_records.exists():
            total_days = attendance_records.count()
            present_days = attendance_records.filter(status='PRESENT').count()
            absent_days = attendance_records.filter(status='ABSENT').count()
            late_days = attendance_records.filter(status='LATE').count()
            
            attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
            
            # Monthly attendance trend (last 6 months)
            monthly_attendance = []
            for i in range(6):
                month_start = timezone.now().date().replace(day=1) - timedelta(days=30*i)
                month_end = month_start.replace(day=28) + timedelta(days=4)  # Last day of month
                month_end = month_end - timedelta(days=month_end.day)
                
                month_records = attendance_records.filter(
                    date__gte=month_start, date__lte=month_end
                )
                month_total = month_records.count()
                month_present = month_records.filter(status='PRESENT').count()
                month_rate = (month_present / month_total * 100) if month_total > 0 else 0
                
                monthly_attendance.append({
                    'month': month_start.strftime('%Y-%m'),
                    'month_name': month_start.strftime('%B %Y'),
                    'total_days': month_total,
                    'present_days': month_present,
                    'attendance_rate': round(month_rate, 1)
                })
            
            monthly_attendance.reverse()  # Oldest to newest
            
        else:
            total_days = present_days = absent_days = late_days = 0
            attendance_percentage = 0
            monthly_attendance = []
            
    except:
        total_days = present_days = absent_days = late_days = 0
        attendance_percentage = 0
        monthly_attendance = []
    
    # Fee payment history
    try:
        fee_payments = FeePayment.objects.filter(student=student).select_related('fee_structure')
        
        if fee_payments.exists():
            fee_summary = fee_payments.aggregate(
                total_payments=Count('id'),
                total_paid=Sum('amount_paid'),
                total_due=Sum('amount_due')
            )
            
            outstanding = fee_summary['total_due'] - fee_summary['total_paid']
            outstanding = max(0, outstanding) if outstanding else 0
            
            recent_payments = fee_payments.order_by('-payment_date')[:5]
            payment_history = [{
                'payment_date': payment.payment_date,
                'amount_paid': float(payment.amount_paid),
                'fee_category': payment.fee_structure.category.name if payment.fee_structure and payment.fee_structure.category else 'N/A',
                'payment_method': payment.payment_method
            } for payment in recent_payments]
            
        else:
            fee_summary = {'total_payments': 0, 'total_paid': 0, 'total_due': 0}
            outstanding = 0
            payment_history = []
            
    except:
        fee_summary = {'total_payments': 0, 'total_paid': 0, 'total_due': 0}
        outstanding = 0
        payment_history = []
    
    return Response({
        'student_info': student_info,
        'academic_performance': {
            'summary': performance_summary,
            'subject_wise': list(subject_performance),
            'recent_results': recent_results_data
        },
        'attendance_analysis': {
            'total_days': total_days,
            'present_days': present_days,
            'absent_days': absent_days,
            'late_days': late_days,
            'attendance_percentage': round(attendance_percentage, 1),
            'monthly_trend': monthly_attendance
        },
        'financial_status': {
            'fee_summary': fee_summary,
            'outstanding_amount': float(outstanding),
            'recent_payments': payment_history
        }
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def student_search_api(request):
    """Advanced student search with multiple filters"""
    query = request.GET.get('q', '')
    grade_id = request.GET.get('grade_id')
    gender = request.GET.get('gender')
    status = request.GET.get('status', 'active')
    
    students = Student.objects.select_related('grade')
    
    # Status filter
    if status == 'active':
        students = students.filter(is_active=True)
    elif status == 'inactive':
        students = students.filter(is_active=False)
    
    # Search query
    if query:
        students = students.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(admission_number__icontains=query) |
            Q(father_name__icontains=query) |
            Q(mother_name__icontains=query) |
            Q(email__icontains=query)
        )
    
    # Grade filter
    if grade_id:
        students = students.filter(grade_id=grade_id)
    
    # Gender filter
    if gender:
        students = students.filter(gender=gender)
    
    # Limit results
    students = students[:50]  # Limit to 50 results for performance
    
    student_data = []
    for student in students:
        # Get basic performance data
        try:
            latest_result = ExamResult.objects.filter(student=student).order_by('-exam__start_date').first()
            latest_percentage = latest_result.percentage if latest_result else None
        except:
            latest_percentage = None
        
        # Get attendance rate (last 30 days)
        try:
            thirty_days_ago = timezone.now().date() - timedelta(days=30)
            attendance_records = Attendance.objects.filter(student=student, date__gte=thirty_days_ago)
            if attendance_records.exists():
                present_count = attendance_records.filter(status='PRESENT').count()
                attendance_rate = (present_count / attendance_records.count() * 100)
            else:
                attendance_rate = None
        except:
            attendance_rate = None
        
        student_data.append({
            'id': student.id,
            'admission_number': student.admission_number,
            'full_name': student.full_name,
            'grade': student.grade.name if student.grade else None,
            'gender': student.get_gender_display(),
            'contact_number': student.contact_number,
            'email': student.email,
            'admission_date': student.admission_date,
            'is_active': student.is_active,
            'latest_percentage': round(latest_percentage, 1) if latest_percentage else None,
            'attendance_rate': round(attendance_rate, 1) if attendance_rate else None
        })
    
    return Response({
        'students': student_data,
        'total_found': len(student_data),
        'search_params': {
            'query': query,
            'grade_id': grade_id,
            'gender': gender,
            'status': status
        }
    })

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def bulk_student_operations_api(request):
    """API for bulk operations on students"""
    try:
        action = request.data.get('action')
        student_ids = request.data.get('student_ids', [])
        
        if not action or not student_ids:
            return Response({
                'error': 'Missing required fields: action, student_ids'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        students = Student.objects.filter(id__in=student_ids)
        
        if not students.exists():
            return Response({
                'error': 'No students found with provided IDs'
            }, status=status.HTTP_404_NOT_FOUND)
        
        results = {'processed': 0, 'message': ''}
        
        if action == 'activate':
            updated = students.update(is_active=True)
            results['processed'] = updated
            results['message'] = f'Activated {updated} students'
            
        elif action == 'deactivate':
            updated = students.update(is_active=False)
            results['processed'] = updated
            results['message'] = f'Deactivated {updated} students'
            
        elif action == 'export':
            # Return student data for export
            student_data = []
            for student in students:
                student_data.append({
                    'admission_number': student.admission_number,
                    'full_name': student.full_name,
                    'grade': student.grade.name if student.grade else '',
                    'gender': student.get_gender_display(),
                    'contact_number': student.contact_number,
                    'email': student.email,
                    'admission_date': student.admission_date.strftime('%Y-%m-%d'),
                    'status': 'Active' if student.is_active else 'Inactive'
                })
            
            return Response({
                'action': 'export',
                'students': student_data,
                'total_exported': len(student_data)
            })
            
        else:
            return Response({
                'error': f'Unknown action: {action}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'success': True,
            'action': action,
            'results': results
        })
        
    except Exception as e:
        return Response({
            'error': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ===== TRADITIONAL API VIEWS =====

class StudentListCreateAPI(generics.ListCreateAPIView):
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'admission_number', 'father_name', 'mother_name']
    ordering_fields = ['admission_date', 'first_name', 'last_name']
    ordering = ['-admission_date']
    
    def get_queryset(self):
        queryset = Student.objects.select_related('grade').filter(is_active=True)
        
        # Grade filter
        grade_id = self.request.query_params.get('grade_id')
        if grade_id:
            queryset = queryset.filter(grade_id=grade_id)
        
        # Gender filter
        gender = self.request.query_params.get('gender')
        if gender:
            queryset = queryset.filter(gender=gender)
            
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return StudentCreateSerializer
        return StudentSerializer

class StudentDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.filter(is_active=True)
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]
