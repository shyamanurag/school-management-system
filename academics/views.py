from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta, date
from core.models import (
    Student, Subject, Grade, Attendance, Teacher, AcademicYear
)
import csv

# ===== ACADEMICS DASHBOARD =====
@login_required
def academics_dashboard(request):
    """Professional Academics Dashboard with Real Database Statistics"""
    today = timezone.now().date()
    current_week_start = today - timedelta(days=today.weekday())
    
    # Core Statistics
    total_subjects = Subject.objects.filter(is_active=True).count()
    total_grades = Grade.objects.filter(is_active=True).count()
    total_attendance = Attendance.objects.count()
    
    # Today's Attendance
    todays_attendance = Attendance.objects.filter(date=today).count()
    present_today = Attendance.objects.filter(date=today, status='PRESENT').count()
    attendance_rate_today = (present_today / todays_attendance * 100) if todays_attendance > 0 else 0
    
    # This Week's Statistics
    week_attendance = Attendance.objects.filter(
        date__gte=current_week_start,
        date__lte=today
    ).aggregate(
        total=Count('id'),
        present=Count('id', filter=Q(status='PRESENT'))
    )
    
    weekly_rate = (week_attendance['present'] / week_attendance['total'] * 100) if week_attendance['total'] > 0 else 0
    
    # Subject-wise Attendance
    subject_attendance = Attendance.objects.filter(
        date__gte=current_week_start
    ).values(
        'student__grade__name'
    ).annotate(
        total=Count('id'),
        present=Count('id', filter=Q(status='PRESENT'))
    ).order_by('student__grade__numeric_value')
    
    # Recent Low Attendance Students
    low_attendance_students = Attendance.objects.filter(
        date__gte=current_week_start
    ).values(
        'student__first_name', 'student__last_name', 'student__admission_number'
    ).annotate(
        total_days=Count('id'),
        present_days=Count('id', filter=Q(status='PRESENT'))
    ).filter(total_days__gte=3).order_by('present_days')[:10]
    
    context = {
        'page_title': 'Academics Dashboard',
        'total_subjects': total_subjects,
        'total_grades': total_grades,
        'total_attendance': total_attendance,
        'todays_attendance': todays_attendance,
        'present_today': present_today,
        'attendance_rate_today': round(attendance_rate_today, 1),
        'weekly_rate': round(weekly_rate, 1),
        'subject_attendance': subject_attendance,
        'low_attendance_students': low_attendance_students,
    }
    
    return render(request, 'academics/dashboard.html', context)

# ===== ATTENDANCE MANAGEMENT =====
class AttendanceListView(LoginRequiredMixin, ListView):
    model = Attendance
    template_name = 'academics/attendance_list.html'
    context_object_name = 'attendance_records'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = Attendance.objects.select_related(
            'student', 'student__grade'
        ).order_by('-date', 'student__first_name')
        
        # Date filter
        date_filter = self.request.GET.get('date')
        if date_filter:
            queryset = queryset.filter(date=date_filter)
        else:
            # Default to today
            queryset = queryset.filter(date=timezone.now().date())
        
        # Grade filter
        grade_id = self.request.GET.get('grade')
        if grade_id:
            queryset = queryset.filter(student__grade_id=grade_id)
            
        # Status filter
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(student__first_name__icontains=search) |
                Q(student__last_name__icontains=search) |
                Q(student__admission_number__icontains=search)
            )
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Attendance Management'
        context['grades'] = Grade.objects.filter(is_active=True).order_by('numeric_value')
        context['attendance_choices'] = Attendance.ATTENDANCE_STATUS
        
        # Statistics for current filter
        queryset = self.get_queryset()
        if queryset.exists():
            total = queryset.count()
            present = queryset.filter(status='PRESENT').count()
            context['attendance_rate'] = round((present / total * 100), 1) if total > 0 else 0
            context['total_records'] = total
            context['present_count'] = present
        else:
            context['attendance_rate'] = 0
            context['total_records'] = 0
            context['present_count'] = 0
            
        return context

@login_required
def mark_attendance(request):
    """Mark attendance for a grade/class"""
    if request.method == 'POST':
        date_str = request.POST.get('date')
        grade_id = request.POST.get('grade')
        
        if not date_str or not grade_id:
            messages.error(request, 'Date and Grade are required')
            return redirect('academics:mark-attendance')
        
        attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        grade = get_object_or_404(Grade, id=grade_id)
        
        # Get all students in the grade
        students = Student.objects.filter(grade=grade, is_active=True)
        
        for student in students:
            status = request.POST.get(f'student_{student.id}', 'ABSENT')
            remarks = request.POST.get(f'remarks_{student.id}', '')
            
            # Create or update attendance
            attendance, created = Attendance.objects.get_or_create(
                student=student,
                date=attendance_date,
                defaults={
                    'status': status,
                    'remarks': remarks,
                    'marked_by': request.user
                }
            )
            
            if not created:
                attendance.status = status
                attendance.remarks = remarks
                attendance.marked_by = request.user
                attendance.save()
        
        messages.success(request, f'Attendance marked for {grade.name} on {attendance_date}')
        return redirect('academics:attendance-list')
    
    # GET request - show form
    grades = Grade.objects.filter(is_active=True).order_by('numeric_value')
    context = {
        'page_title': 'Mark Attendance',
        'grades': grades,
        'today': timezone.now().date(),
    }
    
    grade_id = request.GET.get('grade')
    date_str = request.GET.get('date', timezone.now().date().strftime('%Y-%m-%d'))
    
    if grade_id:
        grade = get_object_or_404(Grade, id=grade_id)
        students = Student.objects.filter(grade=grade, is_active=True).order_by('first_name')
        
        # Check if attendance already marked
        attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        existing_attendance = Attendance.objects.filter(
            student__in=students,
            date=attendance_date
        ).select_related('student')
        
        attendance_dict = {att.student.id: att for att in existing_attendance}
        
        context.update({
            'selected_grade': grade,
            'students': students,
            'selected_date': date_str,
            'existing_attendance': attendance_dict,
        })
    
    return render(request, 'academics/mark_attendance.html', context)

# ===== SUBJECT MANAGEMENT =====
class SubjectListView(LoginRequiredMixin, ListView):
    model = Subject
    template_name = 'academics/subject_list.html'
    context_object_name = 'subjects'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = Subject.objects.select_related('department').filter(is_active=True).order_by('name')
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search) |
                Q(department__name__icontains=search)
            )
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Subject Management'
        context['total_subjects'] = Subject.objects.filter(is_active=True).count()
        return context

class SubjectDetailView(LoginRequiredMixin, DetailView):
    model = Subject
    template_name = 'academics/subject_detail.html'
    context_object_name = 'subject'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subject = self.object
        
        # Get teachers teaching this subject
        teachers = Teacher.objects.filter(subjects=subject, is_active=True)
        
        # Get recent exam results for this subject
        from core.models import ExamResult
        recent_results = ExamResult.objects.filter(
            subject=subject
        ).select_related('exam', 'student').order_by('-exam__start_date')[:20]
        
        context.update({
            'page_title': f'Subject - {subject.name}',
            'teachers': teachers,
            'recent_results': recent_results,
        })
        return context

# ===== GRADE MANAGEMENT =====
class GradeListView(LoginRequiredMixin, ListView):
    model = Grade
    template_name = 'academics/grade_list.html'
    context_object_name = 'grades'
    
    def get_queryset(self):
        return Grade.objects.select_related(
            'academic_year', 'class_teacher', 'room'
        ).filter(is_active=True).order_by('numeric_value', 'section')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Grade Management'
        
        # Add student counts for each grade
        grades_with_counts = []
        for grade in self.get_queryset():
            student_count = Student.objects.filter(grade=grade, is_active=True).count()
            grades_with_counts.append({
                'grade': grade,
                'student_count': student_count
            })
        
        context['grades_with_counts'] = grades_with_counts
        return context

class GradeDetailView(LoginRequiredMixin, DetailView):
    model = Grade
    template_name = 'academics/grade_detail.html'
    context_object_name = 'grade'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        grade = self.object
        
        # Get students in this grade
        students = Student.objects.filter(grade=grade, is_active=True).order_by('roll_number')
        
        # Recent attendance for this grade
        recent_attendance = Attendance.objects.filter(
            student__grade=grade,
            date__gte=timezone.now().date() - timedelta(days=7)
        ).values('date').annotate(
            total=Count('id'),
            present=Count('id', filter=Q(status='PRESENT'))
        ).order_by('-date')
        
        context.update({
            'page_title': f'Grade - {grade.name}-{grade.section}',
            'students': students,
            'student_count': students.count(),
            'recent_attendance': recent_attendance,
        })
        return context

# ===== REPORTS AND ANALYTICS =====
@login_required
def attendance_reports(request):
    """Comprehensive attendance reports"""
    # Date range filter
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)  # Last 30 days
    
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if date_from:
        start_date = datetime.strptime(date_from, '%Y-%m-%d').date()
    if date_to:
        end_date = datetime.strptime(date_to, '%Y-%m-%d').date()
    
    # Grade-wise attendance summary
    grade_summary = Attendance.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    ).values(
        'student__grade__name', 'student__grade__numeric_value'
    ).annotate(
        total_records=Count('id'),
        present_count=Count('id', filter=Q(status='PRESENT')),
        absent_count=Count('id', filter=Q(status='ABSENT')),
        late_count=Count('id', filter=Q(status='LATE'))
    ).order_by('student__grade__numeric_value')
    
    # Calculate attendance percentages
    for grade in grade_summary:
        if grade['total_records'] > 0:
            grade['attendance_rate'] = round(
                (grade['present_count'] / grade['total_records']) * 100, 1
            )
        else:
            grade['attendance_rate'] = 0
    
    # Daily attendance trend
    daily_trend = Attendance.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    ).values('date').annotate(
        total=Count('id'),
        present=Count('id', filter=Q(status='PRESENT'))
    ).order_by('date')
    
    context = {
        'page_title': 'Attendance Reports',
        'start_date': start_date,
        'end_date': end_date,
        'grade_summary': grade_summary,
        'daily_trend': daily_trend,
    }
    
    return render(request, 'academics/attendance_reports.html', context)

@login_required
def export_attendance(request):
    """Export attendance data to CSV"""
    # Get filter parameters
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    grade_id = request.GET.get('grade')
    
    queryset = Attendance.objects.select_related('student', 'student__grade')
    
    if date_from:
        queryset = queryset.filter(date__gte=date_from)
    if date_to:
        queryset = queryset.filter(date__lte=date_to)
    if grade_id:
        queryset = queryset.filter(student__grade_id=grade_id)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Date', 'Student ID', 'Student Name', 'Grade', 'Status', 'Remarks'
    ])
    
    for record in queryset.order_by('-date', 'student__first_name'):
        writer.writerow([
            record.date,
            record.student.admission_number,
            record.student.full_name,
            record.student.grade.name if record.student.grade else '',
            record.get_status_display(),
            record.remarks or ''
        ])
    
    return response
