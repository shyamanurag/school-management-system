from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Count, Sum, Avg, F, Case, When, Value, CharField, BooleanField, Max, Min
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from .models import (
    AdmissionApplication, AdmissionCriteria, EntranceTest, TestResult,
    AdmissionBatch, InterviewSchedule, AdmissionFee, DocumentSubmission,
    AdmissionStatus, AdmissionGrade, EnrollmentConfirmation
)
from core.models import SchoolSettings, Grade, Student, AcademicYear
import csv
import json

# ===== COMPREHENSIVE ADMISSIONS DASHBOARD =====
@login_required
def admissions_dashboard(request):
    """Advanced Admissions Management Dashboard"""
    school_settings = SchoolSettings.objects.first()
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    
    # Application Statistics
    application_stats = {
        'total_applications': AdmissionApplication.objects.count(),
        'pending_applications': AdmissionApplication.objects.filter(
            status='pending'
        ).count(),
        'approved_applications': AdmissionApplication.objects.filter(
            status='approved'
        ).count(),
        'rejected_applications': AdmissionApplication.objects.filter(
            status='rejected'
        ).count(),
        'waitlisted_applications': AdmissionApplication.objects.filter(
            status='waitlisted'
        ).count(),
    }
    
    # Current Month Statistics
    current_month = timezone.now().replace(day=1)
    monthly_stats = {
        'new_applications': AdmissionApplication.objects.filter(
            application_date__gte=current_month
        ).count(),
        'interviews_scheduled': InterviewSchedule.objects.filter(
            interview_date__gte=current_month.date()
        ).count(),
        'tests_conducted': EntranceTest.objects.filter(
            test_date__gte=current_month.date()
        ).count(),
        'enrollments_confirmed': EnrollmentConfirmation.objects.filter(
            confirmation_date__gte=current_month.date()
        ).count(),
    }
    
    # Grade-wise Application Distribution
    grade_distribution = AdmissionApplication.objects.values(
        'applying_for_grade__name'
    ).annotate(
        application_count=Count('id'),
        approved_count=Count('id', filter=Q(status='approved')),
        pending_count=Count('id', filter=Q(status='pending'))
    ).order_by('applying_for_grade__name')
    
    # Recent Applications
    recent_applications = AdmissionApplication.objects.select_related(
        'applying_for_grade'
    ).order_by('-application_date')[:15]
    
    # Upcoming Interviews
    upcoming_interviews = InterviewSchedule.objects.filter(
        interview_date__gte=timezone.now().date()
    ).select_related('application', 'application__applying_for_grade').order_by('interview_date')[:10]
    
    # Upcoming Tests
    upcoming_tests = EntranceTest.objects.filter(
        test_date__gte=timezone.now().date()
    ).order_by('test_date')[:10]
    
    # Fee Collection Statistics
    fee_stats = {
        'total_admission_fees': AdmissionFee.objects.filter(
            payment_status='paid'
        ).aggregate(total=Sum('amount'))['total'] or 0,
        'pending_fees': AdmissionFee.objects.filter(
            payment_status='pending'
        ).aggregate(total=Sum('amount'))['total'] or 0,
        'fee_defaulters': AdmissionFee.objects.filter(
            payment_status='overdue'
        ).count(),
    }
    
    # Document Submission Status
    document_stats = {
        'complete_documents': DocumentSubmission.objects.filter(
            is_complete=True
        ).count(),
        'incomplete_documents': DocumentSubmission.objects.filter(
            is_complete=False
        ).count(),
        'pending_verification': DocumentSubmission.objects.filter(
            verification_status='pending'
        ).count(),
    }
    
    # Application Trend (Last 6 months)
    application_trends = []
    for i in range(6):
        month_start = (timezone.now().replace(day=1) - timedelta(days=i*30)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        applications = AdmissionApplication.objects.filter(
            application_date__range=[month_start, month_end]
        ).count()
        
        admissions = AdmissionApplication.objects.filter(
            application_date__range=[month_start, month_end],
            status='approved'
        ).count()
        
        application_trends.append({
            'month': month_start.strftime('%b %Y'),
            'applications': applications,
            'admissions': admissions
        })
    
    # Priority Applications (based on criteria)
    priority_applications = AdmissionApplication.objects.filter(
        is_priority=True,
        status='pending'
    ).select_related('applying_for_grade')[:10]
    
    context = {
        'page_title': 'Admissions Management Dashboard',
        'school_settings': school_settings,
        'current_academic_year': current_academic_year,
        'application_stats': application_stats,
        'monthly_stats': monthly_stats,
        'grade_distribution': grade_distribution,
        'recent_applications': recent_applications,
        'upcoming_interviews': upcoming_interviews,
        'upcoming_tests': upcoming_tests,
        'fee_stats': fee_stats,
        'document_stats': document_stats,
        'application_trends': list(reversed(application_trends)),
        'priority_applications': priority_applications,
    }
    
    return render(request, 'admissions/dashboard.html', context)

# ===== APPLICATION MANAGEMENT =====
class AdmissionApplicationListView(LoginRequiredMixin, ListView):
    model = AdmissionApplication
    template_name = 'admissions/application_list.html'
    context_object_name = 'applications'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = AdmissionApplication.objects.select_related(
            'applying_for_grade', 'academic_year'
        ).annotate(
            test_score=Avg('testresult__score'),
            interview_score=Avg('interviewschedule__score')
        )
        
        # Filtering
        status_filter = self.request.GET.get('status', '')
        grade_filter = self.request.GET.get('grade', '')
        academic_year_filter = self.request.GET.get('academic_year', '')
        search_query = self.request.GET.get('search', '')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if grade_filter:
            queryset = queryset.filter(applying_for_grade_id=grade_filter)
        if academic_year_filter:
            queryset = queryset.filter(academic_year_id=academic_year_filter)
        if search_query:
            queryset = queryset.filter(
                Q(student_name__icontains=search_query) |
                Q(father_name__icontains=search_query) |
                Q(mother_name__icontains=search_query) |
                Q(contact_phone__icontains=search_query) |
                Q(application_number__icontains=search_query)
            )
        
        return queryset.order_by('-application_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Admission Applications'
        context['grades'] = Grade.objects.all()
        context['academic_years'] = AcademicYear.objects.all()
        context['status_choices'] = AdmissionApplication.STATUS_CHOICES
        return context

class AdmissionApplicationDetailView(LoginRequiredMixin, DetailView):
    model = AdmissionApplication
    template_name = 'admissions/application_detail.html'
    context_object_name = 'application'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        application = self.get_object()
        
        # Test Results
        context['test_results'] = TestResult.objects.filter(
            application=application
        ).select_related('entrance_test')
        
        # Interview Schedules
        context['interviews'] = InterviewSchedule.objects.filter(
            application=application
        ).order_by('-interview_date')
        
        # Document Submissions
        context['documents'] = DocumentSubmission.objects.filter(
            application=application
        )
        
        # Fee Information
        context['fees'] = AdmissionFee.objects.filter(
            application=application
        )
        
        # Status History
        context['status_history'] = AdmissionStatus.objects.filter(
            application=application
        ).order_by('-status_date')
        
        # Eligibility Check
        context['meets_criteria'] = self.check_eligibility(application)
        
        context['page_title'] = f'Application: {application.application_number}'
        return context
    
    def check_eligibility(self, application):
        """Check if application meets admission criteria"""
        criteria = AdmissionCriteria.objects.filter(
            grade=application.applying_for_grade,
            academic_year=application.academic_year
        ).first()
        
        if not criteria:
            return True
        
        # Check age criteria
        if criteria.minimum_age or criteria.maximum_age:
            age = (timezone.now().date() - application.date_of_birth).days // 365
            if criteria.minimum_age and age < criteria.minimum_age:
                return False
            if criteria.maximum_age and age > criteria.maximum_age:
                return False
        
        # Check test score
        if criteria.minimum_test_score:
            avg_score = TestResult.objects.filter(
                application=application
            ).aggregate(avg=Avg('score'))['avg']
            if avg_score and avg_score < criteria.minimum_test_score:
                return False
        
        return True

# ===== APPLICATION PROCESSING =====
@login_required
def process_application(request, pk):
    """Process admission application (approve/reject/waitlist)"""
    application = get_object_or_404(AdmissionApplication, pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        remarks = request.POST.get('remarks', '')
        
        if action == 'approve':
            application.status = 'approved'
            application.approval_date = timezone.now().date()
            application.approved_by = request.user
            application.remarks = remarks
            
            # Create admission status record
            AdmissionStatus.objects.create(
                application=application,
                status='approved',
                status_date=timezone.now().date(),
                remarks=remarks,
                updated_by=request.user
            )
            
            # Generate student record if not exists
            student, created = Student.objects.get_or_create(
                first_name=application.student_name.split()[0],
                last_name=' '.join(application.student_name.split()[1:]) if len(application.student_name.split()) > 1 else '',
                defaults={
                    'grade': application.applying_for_grade,
                    'date_of_birth': application.date_of_birth,
                    'gender': application.gender,
                    'father_name': application.father_name,
                    'mother_name': application.mother_name,
                    'contact_phone': application.contact_phone,
                    'email': application.email,
                    'address': application.address,
                    'is_active': True,
                    'admission_date': timezone.now().date(),
                }
            )
            
            if created:
                # Generate student ID
                student.student_id = f"{application.applying_for_grade.grade_code}{timezone.now().year}{student.id:04d}"
                student.save()
                
                messages.success(request, f'Application approved and student record created: {student.student_id}')
            else:
                messages.success(request, 'Application approved successfully')
            
        elif action == 'reject':
            application.status = 'rejected'
            application.rejection_date = timezone.now().date()
            application.rejected_by = request.user
            application.rejection_reason = remarks
            
            # Create admission status record
            AdmissionStatus.objects.create(
                application=application,
                status='rejected',
                status_date=timezone.now().date(),
                remarks=remarks,
                updated_by=request.user
            )
            
            messages.success(request, 'Application rejected')
            
        elif action == 'waitlist':
            application.status = 'waitlisted'
            application.waitlist_date = timezone.now().date()
            application.remarks = remarks
            
            # Create admission status record
            AdmissionStatus.objects.create(
                application=application,
                status='waitlisted',
                status_date=timezone.now().date(),
                remarks=remarks,
                updated_by=request.user
            )
            
            messages.success(request, 'Application moved to waitlist')
        
        application.save()
        return redirect('admissions:application_detail', pk=application.pk)
    
    context = {
        'application': application,
        'page_title': f'Process Application: {application.application_number}'
    }
    
    return render(request, 'admissions/process_application.html', context)

# ===== ENTRANCE TEST MANAGEMENT =====
class EntranceTestListView(LoginRequiredMixin, ListView):
    model = EntranceTest
    template_name = 'admissions/entrance_test_list.html'
    context_object_name = 'tests'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = EntranceTest.objects.annotate(
            registered_count=Count('testresult__application', distinct=True),
            appeared_count=Count('testresult', filter=Q(testresult__appeared=True)),
            average_score=Avg('testresult__score')
        )
        
        grade_filter = self.request.GET.get('grade', '')
        status_filter = self.request.GET.get('status', '')
        
        if grade_filter:
            queryset = queryset.filter(grade_id=grade_filter)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-test_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Entrance Tests'
        context['grades'] = Grade.objects.all()
        context['status_choices'] = EntranceTest.STATUS_CHOICES
        return context

@login_required
def test_results_entry(request, test_id):
    """Enter test results for students"""
    test = get_object_or_404(EntranceTest, id=test_id)
    
    if request.method == 'POST':
        # Bulk result entry
        application_ids = request.POST.getlist('application_ids[]')
        scores = request.POST.getlist('scores[]')
        appeared_flags = request.POST.getlist('appeared[]')
        remarks_list = request.POST.getlist('remarks[]')
        
        updated_count = 0
        
        for i, app_id in enumerate(application_ids):
            if app_id and i < len(scores):
                try:
                    application = AdmissionApplication.objects.get(id=app_id)
                    score = float(scores[i]) if scores[i] else 0
                    appeared = str(appeared_flags[i]).lower() == 'true' if i < len(appeared_flags) else False
                    remarks = remarks_list[i] if i < len(remarks_list) else ''
                    
                    result, created = TestResult.objects.get_or_create(
                        entrance_test=test,
                        application=application,
                        defaults={
                            'score': score,
                            'appeared': appeared,
                            'remarks': remarks,
                            'result_date': timezone.now().date()
                        }
                    )
                    
                    if not created:
                        result.score = score
                        result.appeared = appeared
                        result.remarks = remarks
                        result.save()
                    
                    updated_count += 1
                    
                except (AdmissionApplication.DoesNotExist, ValueError):
                    continue
        
        messages.success(request, f'Test results updated for {updated_count} students')
        return redirect('admissions:entrance_test_detail', pk=test.pk)
    
    # GET request
    # Get applications for this test's grade
    applications = AdmissionApplication.objects.filter(
        applying_for_grade=test.grade,
        status__in=['pending', 'approved']
    ).select_related('applying_for_grade')
    
    # Get existing results
    existing_results = TestResult.objects.filter(
        entrance_test=test
    ).select_related('application')
    
    context = {
        'test': test,
        'applications': applications,
        'existing_results': existing_results,
        'page_title': f'Test Results: {test.test_name}'
    }
    
    return render(request, 'admissions/test_results_entry.html', context)

# ===== INTERVIEW MANAGEMENT =====
@login_required
def interview_scheduling(request):
    """Schedule interviews for approved applications"""
    if request.method == 'POST':
        application_id = request.POST.get('application_id')
        interview_date = request.POST.get('interview_date')
        interview_time = request.POST.get('interview_time')
        interviewer = request.POST.get('interviewer')
        venue = request.POST.get('venue', '')
        remarks = request.POST.get('remarks', '')
        
        try:
            application = AdmissionApplication.objects.get(id=application_id)
            
            # Check if interview already scheduled
            existing_interview = InterviewSchedule.objects.filter(
                application=application,
                status='scheduled'
            ).first()
            
            if existing_interview:
                messages.warning(request, f'Interview already scheduled for {application.student_name}')
                return redirect('admissions:interview_scheduling')
            
            # Create interview schedule
            InterviewSchedule.objects.create(
                application=application,
                interview_date=interview_date,
                interview_time=interview_time,
                interviewer=interviewer,
                venue=venue,
                remarks=remarks,
                status='scheduled',
                scheduled_by=request.user
            )
            
            messages.success(request, f'Interview scheduled for {application.student_name}')
            return redirect('admissions:interview_scheduling')
            
        except AdmissionApplication.DoesNotExist:
            messages.error(request, 'Application not found')
    
    # GET request
    # Applications eligible for interview
    eligible_applications = AdmissionApplication.objects.filter(
        status__in=['approved', 'pending']
    ).exclude(
        id__in=InterviewSchedule.objects.filter(
            status='scheduled'
        ).values_list('application_id', flat=True)
    ).select_related('applying_for_grade')
    
    # Scheduled interviews
    scheduled_interviews = InterviewSchedule.objects.filter(
        status='scheduled'
    ).select_related('application').order_by('interview_date')
    
    context = {
        'page_title': 'Interview Scheduling',
        'eligible_applications': eligible_applications,
        'scheduled_interviews': scheduled_interviews,
    }
    
    return render(request, 'admissions/interview_scheduling.html', context)

# ===== FEE MANAGEMENT =====
@login_required
def admission_fee_management(request):
    """Manage admission fees"""
    fees = AdmissionFee.objects.select_related(
        'application', 'application__applying_for_grade'
    ).order_by('-payment_date')
    
    # Filtering
    status_filter = request.GET.get('status', '')
    grade_filter = request.GET.get('grade', '')
    
    if status_filter:
        fees = fees.filter(payment_status=status_filter)
    if grade_filter:
        fees = fees.filter(application__applying_for_grade_id=grade_filter)
    
    # Fee statistics
    fee_stats = {
        'total_collected': fees.filter(payment_status='paid').aggregate(
            total=Sum('amount')
        )['total'] or 0,
        'pending_amount': fees.filter(payment_status='pending').aggregate(
            total=Sum('amount')
        )['total'] or 0,
        'overdue_amount': fees.filter(payment_status='overdue').aggregate(
            total=Sum('amount')
        )['total'] or 0,
    }
    
    context = {
        'page_title': 'Admission Fee Management',
        'fees': fees[:50],
        'fee_stats': fee_stats,
        'grades': Grade.objects.all(),
        'status_choices': AdmissionFee.STATUS_CHOICES,
        'selected_status': status_filter,
        'selected_grade': grade_filter,
    }
    
    return render(request, 'admissions/fee_management.html', context)

# ===== DOCUMENT VERIFICATION =====
@login_required
def document_verification(request):
    """Document verification for applications"""
    documents = DocumentSubmission.objects.select_related(
        'application'
    ).order_by('-submission_date')
    
    # Filtering
    verification_status = request.GET.get('verification_status', '')
    complete_status = request.GET.get('complete_status', '')
    
    if verification_status:
        documents = documents.filter(verification_status=verification_status)
    if complete_status == 'complete':
        documents = documents.filter(is_complete=True)
    elif complete_status == 'incomplete':
        documents = documents.filter(is_complete=False)
    
    # Document statistics
    doc_stats = {
        'total_submissions': documents.count(),
        'verified': documents.filter(verification_status='verified').count(),
        'pending_verification': documents.filter(verification_status='pending').count(),
        'rejected': documents.filter(verification_status='rejected').count(),
        'complete_documents': documents.filter(is_complete=True).count(),
    }
    
    context = {
        'page_title': 'Document Verification',
        'documents': documents[:50],
        'doc_stats': doc_stats,
        'verification_choices': DocumentSubmission.VERIFICATION_CHOICES,
        'selected_verification': verification_status,
        'selected_complete': complete_status,
    }
    
    return render(request, 'admissions/document_verification.html', context)

# ===== REPORTS AND ANALYTICS =====
@login_required
def admissions_reports(request):
    """Admissions Reports and Analytics"""
    # Date range filtering
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    report_type = request.GET.get('report_type', 'summary')
    
    if not start_date:
        start_date = (timezone.now() - timedelta(days=30)).date()
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    if not end_date:
        end_date = timezone.now().date()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Application Analysis
    applications = AdmissionApplication.objects.filter(
        application_date__range=[start_date, end_date]
    )
    
    application_summary = {
        'total_applications': applications.count(),
        'approved': applications.filter(status='approved').count(),
        'rejected': applications.filter(status='rejected').count(),
        'pending': applications.filter(status='pending').count(),
        'waitlisted': applications.filter(status='waitlisted').count(),
    }
    
    # Grade-wise Analysis
    grade_analysis = applications.values(
        'applying_for_grade__name'
    ).annotate(
        total=Count('id'),
        approved=Count('id', filter=Q(status='approved')),
        rejection_rate=Count('id', filter=Q(status='rejected')) * 100.0 / Count('id')
    ).order_by('applying_for_grade__name')
    
    # Test Performance Analysis
    test_performance = TestResult.objects.filter(
        result_date__range=[start_date, end_date]
    ).aggregate(
        average_score=Avg('score'),
        highest_score=Max('score'),
        lowest_score=Min('score'),
        total_appeared=Count('id', filter=Q(appeared=True))
    )
    
    # Fee Collection Analysis
    fee_collection = AdmissionFee.objects.filter(
        payment_date__range=[start_date, end_date]
    ).aggregate(
        total_collected=Sum('amount', filter=Q(payment_status='paid')),
        pending_amount=Sum('amount', filter=Q(payment_status='pending'))
    )
    
    context = {
        'page_title': 'Admissions Reports & Analytics',
        'start_date': start_date,
        'end_date': end_date,
        'report_type': report_type,
        'application_summary': application_summary,
        'grade_analysis': grade_analysis,
        'test_performance': test_performance,
        'fee_collection': fee_collection,
    }
    
    return render(request, 'admissions/admissions_reports.html', context)

# ===== API ENDPOINTS =====
@login_required
def admissions_analytics_api(request):
    """API endpoint for admissions analytics data"""
    # Monthly application trends
    monthly_data = []
    for i in range(12):
        month_start = (timezone.now().replace(day=1) - timedelta(days=i*30)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        applications = AdmissionApplication.objects.filter(
            application_date__range=[month_start, month_end]
        ).count()
        
        admissions = AdmissionApplication.objects.filter(
            application_date__range=[month_start, month_end],
            status='approved'
        ).count()
        
        monthly_data.append({
            'month': month_start.strftime('%b %Y'),
            'applications': applications,
            'admissions': admissions
        })
    
    # Status distribution
    status_distribution = AdmissionApplication.objects.values('status').annotate(
        count=Count('id')
    )
    
    # Grade-wise applications
    grade_distribution = AdmissionApplication.objects.values(
        'applying_for_grade__name'
    ).annotate(count=Count('id'))
    
    return JsonResponse({
        'monthly_trends': list(reversed(monthly_data)),
        'status_distribution': list(status_distribution),
        'grade_distribution': list(grade_distribution),
        'status': 'success'
    })

# ===== DATA EXPORT FUNCTIONS =====
@login_required
def export_admissions_csv(request):
    """Export admissions data to CSV"""
    export_type = request.GET.get('type', 'applications')
    
    response = HttpResponse(content_type='text/csv')
    
    if export_type == 'applications':
        response['Content-Disposition'] = 'attachment; filename="admission_applications.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'Application Number', 'Student Name', 'Father Name', 'Mother Name',
            'Applying For Grade', 'Application Date', 'Status', 'Contact Phone',
            'Email', 'Date of Birth', 'Gender', 'Address'
        ])
        
        applications = AdmissionApplication.objects.select_related('applying_for_grade')
        
        for app in applications:
            writer.writerow([
                app.application_number,
                app.student_name,
                app.father_name,
                app.mother_name,
                app.applying_for_grade.name if app.applying_for_grade else '',
                app.application_date,
                app.get_status_display(),
                app.contact_phone,
                app.email,
                app.date_of_birth,
                app.get_gender_display(),
                app.address
            ])
    
    elif export_type == 'test_results':
        response['Content-Disposition'] = 'attachment; filename="test_results.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'Test Name', 'Student Name', 'Application Number', 'Score',
            'Appeared', 'Result Date', 'Grade', 'Remarks'
        ])
        
        results = TestResult.objects.select_related(
            'entrance_test', 'application', 'application__applying_for_grade'
        )
        
        for result in results:
            writer.writerow([
                result.entrance_test.test_name,
                result.application.student_name,
                result.application.application_number,
                result.score,
                'Yes' if result.appeared else 'No',
                result.result_date,
                result.application.applying_for_grade.name if result.application.applying_for_grade else '',
                result.remarks
            ])
    
    return response 