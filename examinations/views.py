from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Count, Avg, Sum, Max, Min
from django.utils import timezone
from datetime import datetime, timedelta
from core.models import (
    Exam, ExamResult, Student, Subject, Grade, AcademicYear, Teacher
)
import csv
import json

# ===== EXAMINATIONS DASHBOARD =====
@login_required
def examinations_dashboard(request):
    """Professional Examinations Dashboard with Real Database Statistics"""
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    
    # Core Statistics
    total_exams = Exam.objects.filter(is_active=True).count()
    total_results = ExamResult.objects.count()
    active_exams = Exam.objects.filter(
        is_active=True,
        start_date__lte=timezone.now().date(),
        end_date__gte=timezone.now().date()
    ).count()
    
    # Performance Analytics
    if total_results > 0:
        avg_percentage = ExamResult.objects.aggregate(
            avg=Avg('marks_obtained') * 100 / Avg('total_marks')
        )['avg'] or 0
        
        pass_rate = ExamResult.objects.filter(
            marks_obtained__gte=35  # Assuming 35% is passing
        ).count() / total_results * 100
    else:
        avg_percentage = 0
        pass_rate = 0
    
    # Recent Exams
    recent_exams = Exam.objects.filter(is_active=True).order_by('-start_date')[:5]
    
    # Top Performing Students
    top_students = ExamResult.objects.values(
        'student__first_name', 'student__last_name', 'student__admission_number'
    ).annotate(
        avg_marks=Avg('marks_obtained'),
        total_exams=Count('id')
    ).filter(total_exams__gte=3).order_by('-avg_marks')[:10]
    
    # Subject-wise Performance
    subject_performance = ExamResult.objects.values(
        'subject__name'
    ).annotate(
        avg_marks=Avg('marks_obtained'),
        total_students=Count('student', distinct=True),
        total_exams=Count('exam', distinct=True)
    ).order_by('-avg_marks')[:10]
    
    # Grade-wise Distribution
    grade_distribution = ExamResult.objects.values(
        'student__grade__name'
    ).annotate(
        avg_marks=Avg('marks_obtained'),
        student_count=Count('student', distinct=True)
    ).order_by('student__grade__numeric_value')
    
    context = {
        'page_title': 'Examinations Dashboard',
        'total_exams': total_exams,
        'total_results': total_results,
        'active_exams': active_exams,
        'avg_percentage': round(avg_percentage, 2),
        'pass_rate': round(pass_rate, 2),
        'recent_exams': recent_exams,
        'top_students': top_students,
        'subject_performance': subject_performance,
        'grade_distribution': grade_distribution,
        'current_academic_year': current_academic_year,
    }
    
    return render(request, 'examinations/dashboard.html', context)

# ===== EXAM MANAGEMENT =====
class ExamListView(LoginRequiredMixin, ListView):
    model = Exam
    template_name = 'examinations/exam_list.html'
    context_object_name = 'exams'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = Exam.objects.filter(is_active=True).order_by('-start_date')
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(exam_type__icontains=search)
            )
        
        # Exam type filter
        exam_type = self.request.GET.get('exam_type')
        if exam_type:
            queryset = queryset.filter(exam_type=exam_type)
            
        # Academic year filter
        academic_year = self.request.GET.get('academic_year')
        if academic_year:
            queryset = queryset.filter(academic_year_id=academic_year)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Exam Management'
        context['exam_types'] = Exam.EXAM_TYPES
        context['academic_years'] = AcademicYear.objects.filter(is_active=True)
        context['total_exams'] = Exam.objects.filter(is_active=True).count()
        return context

class ExamDetailView(LoginRequiredMixin, DetailView):
    model = Exam
    template_name = 'examinations/exam_detail.html'
    context_object_name = 'exam'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exam = self.object
        
        # Exam Results Statistics
        exam_results = ExamResult.objects.filter(exam=exam)
        total_students = exam_results.count()
        
        if total_students > 0:
            avg_marks = exam_results.aggregate(avg=Avg('marks_obtained'))['avg'] or 0
            max_marks = exam_results.aggregate(max=Max('marks_obtained'))['max'] or 0
            min_marks = exam_results.aggregate(min=Min('marks_obtained'))['min'] or 0
            pass_count = exam_results.filter(marks_obtained__gte=35).count()
            pass_rate = (pass_count / total_students) * 100 if total_students > 0 else 0
        else:
            avg_marks = max_marks = min_marks = pass_rate = 0
        
        # Subject-wise Results
        subject_results = exam_results.values(
            'subject__name'
        ).annotate(
            avg_marks=Avg('marks_obtained'),
            student_count=Count('student'),
            pass_count=Count('student', filter=Q(marks_obtained__gte=35))
        ).order_by('subject__name')
        
        # Grade-wise Results
        grade_results = exam_results.values(
            'student__grade__name'
        ).annotate(
            avg_marks=Avg('marks_obtained'),
            student_count=Count('student'),
            pass_count=Count('student', filter=Q(marks_obtained__gte=35))
        ).order_by('student__grade__numeric_value')
        
        # Top Performers
        top_performers = exam_results.select_related('student', 'subject').order_by(
            '-marks_obtained'
        )[:10]
        
        context.update({
            'page_title': f'Exam - {exam.name}',
            'total_students': total_students,
            'avg_marks': round(avg_marks, 2),
            'max_marks': max_marks,
            'min_marks': min_marks,
            'pass_rate': round(pass_rate, 2),
            'subject_results': subject_results,
            'grade_results': grade_results,
            'top_performers': top_performers,
        })
        return context

class ExamCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Exam
    template_name = 'examinations/exam_form.html'
    fields = [
        'name', 'exam_type', 'academic_year', 'start_date', 'end_date',
        'total_marks', 'passing_marks'
    ]
    permission_required = 'core.add_exam'
    success_url = reverse_lazy('examinations:exam-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Create New Exam'
        return context

class ExamUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Exam
    template_name = 'examinations/exam_form.html'
    fields = [
        'name', 'exam_type', 'start_date', 'end_date',
        'total_marks', 'passing_marks', 'is_active'
    ]
    permission_required = 'core.change_exam'
    
    def get_success_url(self):
        return reverse_lazy('examinations:exam-detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Edit Exam - {self.object.name}'
        return context

# ===== EXAM RESULTS MANAGEMENT =====
class ExamResultListView(LoginRequiredMixin, ListView):
    model = ExamResult
    template_name = 'examinations/result_list.html'
    context_object_name = 'results'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = ExamResult.objects.select_related(
            'student', 'exam', 'subject'
        ).order_by('-exam__start_date', 'student__first_name')
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(student__first_name__icontains=search) |
                Q(student__last_name__icontains=search) |
                Q(student__admission_number__icontains=search) |
                Q(exam__name__icontains=search) |
                Q(subject__name__icontains=search)
            )
        
        # Exam filter
        exam_id = self.request.GET.get('exam')
        if exam_id:
            queryset = queryset.filter(exam_id=exam_id)
            
        # Subject filter
        subject_id = self.request.GET.get('subject')
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
            
        # Grade filter
        grade_id = self.request.GET.get('grade')
        if grade_id:
            queryset = queryset.filter(student__grade_id=grade_id)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Exam Results'
        context['exams'] = Exam.objects.filter(is_active=True).order_by('-start_date')
        context['subjects'] = Subject.objects.filter(is_active=True).order_by('name')
        context['grades'] = Grade.objects.filter(is_active=True).order_by('numeric_value')
        context['total_results'] = ExamResult.objects.count()
        return context

class ExamResultDetailView(LoginRequiredMixin, DetailView):
    model = ExamResult
    template_name = 'examinations/result_detail.html'
    context_object_name = 'result'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        result = self.object
        
        # Student's other results for comparison
        student_results = ExamResult.objects.filter(
            student=result.student
        ).select_related('exam', 'subject').order_by('-exam__start_date')[:10]
        
        # Subject average for comparison
        subject_avg = ExamResult.objects.filter(
            subject=result.subject,
            exam=result.exam
        ).aggregate(avg=Avg('marks_obtained'))['avg'] or 0
        
        context.update({
            'page_title': f'Result - {result.student.full_name}',
            'student_results': student_results,
            'subject_avg': round(subject_avg, 2),
            'percentage': result.percentage,
        })
        return context

# ===== ANALYTICS AND REPORTS =====
@login_required
def exam_analytics(request):
    """Comprehensive Exam Analytics"""
    # Performance Trends
    performance_trends = ExamResult.objects.values(
        'exam__academic_year__name', 'exam__exam_type'
    ).annotate(
        avg_marks=Avg('marks_obtained'),
        total_students=Count('student'),
        pass_rate=Count('student', filter=Q(marks_obtained__gte=35)) * 100.0 / Count('student')
    ).order_by('exam__academic_year__start_date', 'exam__exam_type')
    
    # Subject Performance Comparison
    subject_comparison = ExamResult.objects.values(
        'subject__name'
    ).annotate(
        avg_marks=Avg('marks_obtained'),
        total_attempts=Count('id'),
        pass_rate=Count('id', filter=Q(marks_obtained__gte=35)) * 100.0 / Count('id'),
        top_score=Max('marks_obtained')
    ).order_by('-avg_marks')
    
    # Grade-wise Performance
    grade_performance = ExamResult.objects.values(
        'student__grade__name', 'student__grade__numeric_value'
    ).annotate(
        avg_marks=Avg('marks_obtained'),
        student_count=Count('student', distinct=True),
        exam_count=Count('exam', distinct=True)
    ).order_by('student__grade__numeric_value')
    
    context = {
        'page_title': 'Exam Analytics',
        'performance_trends': performance_trends,
        'subject_comparison': subject_comparison,
        'grade_performance': grade_performance,
    }
    
    return render(request, 'examinations/analytics.html', context)

@login_required
def exam_reports(request):
    """Exam Reports Dashboard"""
    context = {
        'page_title': 'Exam Reports',
    }
    return render(request, 'examinations/reports.html', context)

# ===== DATA EXPORT =====
@login_required
def export_exam_results(request):
    """Export exam results to CSV"""
    exam_id = request.GET.get('exam')
    subject_id = request.GET.get('subject')
    grade_id = request.GET.get('grade')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="exam_results_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Student ID', 'Student Name', 'Grade', 'Exam', 'Subject',
        'Marks Obtained', 'Total Marks', 'Percentage', 'Grade'
    ])
    
    results = ExamResult.objects.select_related(
        'student', 'exam', 'subject', 'student__grade'
    )
    
    if exam_id:
        results = results.filter(exam_id=exam_id)
    if subject_id:
        results = results.filter(subject_id=subject_id)
    if grade_id:
        results = results.filter(student__grade_id=grade_id)
    
    for result in results:
        writer.writerow([
            result.student.admission_number,
            result.student.full_name,
            result.student.grade.name if result.student.grade else '',
            result.exam.name,
            result.subject.name,
            result.marks_obtained,
            result.total_marks,
            f"{result.percentage:.2f}%",
            result.grade or ''
        ])
    
    return response

# ===== STUDENT PERFORMANCE =====
@login_required
def student_performance(request, student_id):
    """Individual Student Performance Analysis"""
    student = get_object_or_404(Student, pk=student_id)
    
    # Student's all exam results
    exam_results = ExamResult.objects.filter(
        student=student
    ).select_related('exam', 'subject').order_by('-exam__start_date')
    
    # Performance summary
    if exam_results.exists():
        avg_percentage = exam_results.aggregate(
            avg=Avg('marks_obtained') * 100 / Avg('total_marks')
        )['avg'] or 0
        
        best_subject = exam_results.values('subject__name').annotate(
            avg_marks=Avg('marks_obtained')
        ).order_by('-avg_marks').first()
        
        total_exams = exam_results.count()
        passed_exams = exam_results.filter(marks_obtained__gte=35).count()
    else:
        avg_percentage = 0
        best_subject = None
        total_exams = passed_exams = 0
    
    context = {
        'page_title': f'Performance - {student.full_name}',
        'student': student,
        'exam_results': exam_results,
        'avg_percentage': round(avg_percentage, 2),
        'best_subject': best_subject,
        'total_exams': total_exams,
        'passed_exams': passed_exams,
    }
    
    return render(request, 'examinations/student_performance.html', context) 