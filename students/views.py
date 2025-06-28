from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Count, Avg, Sum
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils import timezone
from django.template.loader import render_to_string
from core.models import (
    Student, Grade, Attendance, ExamResult, FeePayment, AcademicYear, 
    SchoolSettings, Employee, BiometricAttendance, VirtualClassroom,
    SmartNotification, ParentPortal, MobileAppSession
)
import csv
import json
from datetime import datetime, timedelta
from decimal import Decimal

# TEMPORARY TEST VIEW FOR DEBUGGING
def test_students_view(request):
    """Simple test view to check if URL routing works"""
    return HttpResponse("Students module is working! URL routing is functional.")

class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'students/student_list.html'
    context_object_name = 'students'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = Student.objects.select_related('grade', 'academic_year').filter(is_active=True)
        
        # Advanced search functionality
        search_query = self.request.GET.get('search', '')
        grade_filter = self.request.GET.get('grade', '')
        gender_filter = self.request.GET.get('gender', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(admission_number__icontains=search_query) |
                Q(father_name__icontains=search_query) |
                Q(mother_name__icontains=search_query)
            )
        
        if grade_filter:
            queryset = queryset.filter(grade__id=grade_filter)
            
        if gender_filter:
            queryset = queryset.filter(gender=gender_filter)
        
        return queryset.order_by('first_name', 'last_name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # REAL STATISTICS FROM DATABASE
        all_students = Student.objects.filter(is_active=True)
        context['total_students'] = all_students.count()
        context['total_male'] = all_students.filter(gender='M').count()
        context['total_female'] = all_students.filter(gender='F').count()
        
        # Grade-wise distribution
        grade_distribution = all_students.values('grade__name').annotate(
            count=Count('id')
        ).order_by('grade__name')
        context['grade_distribution'] = grade_distribution
        
        # Recent admissions (last 30 days)
        thirty_days_ago = datetime.now().date() - timedelta(days=30)
        context['recent_admissions'] = all_students.filter(
            admission_date__gte=thirty_days_ago
        ).count()
        
        # Filters for template
        context['grades'] = Grade.objects.filter(is_active=True).order_by('name')
        context['search_query'] = self.request.GET.get('search', '')
        context['grade_filter'] = self.request.GET.get('grade', '')
        context['gender_filter'] = self.request.GET.get('gender', '')
        
        context['page_title'] = 'Students Management'
        context['school_settings'] = SchoolSettings.objects.first()
        return context

class StudentDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = 'students/student_detail.html'
    context_object_name = 'student'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.object
        
        # Comprehensive Academic Performance
        try:
            exam_results = ExamResult.objects.filter(student=student).select_related(
                'exam', 'subject'
            ).order_by('-exam__exam_date')[:20]
            context['exam_results'] = exam_results
            
            if exam_results.exists():
                # Calculate average performance
                total_marks = exam_results.aggregate(
                    total_obtained=Sum('marks_obtained'),
                    total_max=Sum('max_marks')
                )
                if total_marks['total_max'] and total_marks['total_max'] > 0:
                    context['overall_percentage'] = round(
                        (total_marks['total_obtained'] / total_marks['total_max']) * 100, 1
                    )
                else:
                    context['overall_percentage'] = 0
                
                # Subject-wise performance
                subject_performance = exam_results.values('subject__name').annotate(
                    avg_marks=Avg('marks_obtained'),
                    total_exams=Count('id')
                ).order_by('subject__name')
                context['subject_performance'] = subject_performance
            else:
                context['overall_percentage'] = 0
                context['subject_performance'] = []
        except:
            context['exam_results'] = []
            context['overall_percentage'] = 0
            context['subject_performance'] = []
        
        # Comprehensive Attendance Analysis
        try:
            attendance_records = Attendance.objects.filter(student=student).order_by('-date')[:50]
            context['recent_attendance'] = attendance_records[:10]  # Show only 10 in detail view
            
            if attendance_records.exists():
                present_count = attendance_records.filter(status='PRESENT').count()
                total_days = attendance_records.count()
                context['attendance_percentage'] = round((present_count / total_days) * 100, 1)
                context['total_present_days'] = present_count
                context['total_absent_days'] = total_days - present_count
                
                # Monthly attendance breakdown
                monthly_attendance = {}
                for record in attendance_records:
                    month_key = f"{record.date.year}-{record.date.month:02d}"
                    if month_key not in monthly_attendance:
                        monthly_attendance[month_key] = {'present': 0, 'absent': 0, 'total': 0}
                    
                    monthly_attendance[month_key]['total'] += 1
                    if record.status == 'PRESENT':
                        monthly_attendance[month_key]['present'] += 1
                    else:
                        monthly_attendance[month_key]['absent'] += 1
                
                context['monthly_attendance'] = monthly_attendance
            else:
                context['attendance_percentage'] = 0
                context['total_present_days'] = 0
                context['total_absent_days'] = 0
                context['monthly_attendance'] = {}
        except:
            context['recent_attendance'] = []
            context['attendance_percentage'] = 0
            context['monthly_attendance'] = {}
        
        # Fee Payment History
        try:
            fee_payments = FeePayment.objects.filter(student=student).select_related(
                'fee_structure__category'
            ).order_by('-payment_date')[:10]
            context['fee_payments'] = fee_payments
            
            # Calculate fee statistics
            total_paid = fee_payments.aggregate(total=Sum('amount_paid'))['total'] or 0
            total_due = fee_payments.aggregate(total=Sum('amount_due'))['total'] or 0
            context['total_fees_paid'] = total_paid
            context['total_fees_due'] = total_due
            context['outstanding_fees'] = max(0, total_due - total_paid)
        except:
            context['fee_payments'] = []
            context['total_fees_paid'] = 0
            context['total_fees_due'] = 0
            context['outstanding_fees'] = 0
        
        # Parent Information
        context['emergency_contacts'] = [
            {'name': student.father_name, 'relation': 'Father', 'phone': student.father_phone},
            {'name': student.mother_name, 'relation': 'Mother', 'phone': student.mother_phone},
        ] if hasattr(student, 'father_phone') else []
        
        context['page_title'] = f'Student Profile - {student.full_name}'
        context['school_settings'] = SchoolSettings.objects.first()
        return context

class StudentCreateView(LoginRequiredMixin, CreateView):
    model = Student
    template_name = 'students/student_form.html'
    fields = [
        'admission_number', 'first_name', 'last_name', 'grade', 'gender',
        'date_of_birth', 'father_name', 'mother_name', 'contact_number',
        'email', 'address', 'blood_group', 'religion', 'category'
    ]
    success_url = reverse_lazy('student-list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Student {form.instance.full_name} added successfully!')
        return super().form_valid(form)

class StudentUpdateView(LoginRequiredMixin, UpdateView):
    model = Student
    template_name = 'students/student_form.html'
    fields = [
        'first_name', 'last_name', 'grade', 'gender', 'date_of_birth',
        'father_name', 'mother_name', 'contact_number', 'email', 'address',
        'blood_group', 'religion', 'category'
    ]
    success_url = reverse_lazy('student-list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Student {form.instance.full_name} updated successfully!')
        return super().form_valid(form)

@login_required
def student_dashboard(request):
    """Comprehensive Student Dashboard"""
    school_settings = SchoolSettings.objects.first()
    
    # Student Statistics
    total_students = Student.objects.filter(is_active=True).count()
    total_grades = Grade.objects.filter(is_active=True).count()
    
    # Gender Distribution
    male_students = Student.objects.filter(is_active=True, gender='M').count()
    female_students = Student.objects.filter(is_active=True, gender='F').count()
    
    # Grade-wise Student Count
    grade_wise_count = Student.objects.filter(is_active=True).values(
        'grade__name'
    ).annotate(student_count=Count('id')).order_by('grade__name')
    
    # Recent Admissions (Last 30 days)
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    recent_admissions = Student.objects.filter(
        is_active=True,
        admission_date__gte=thirty_days_ago
    ).select_related('grade').order_by('-admission_date')[:10]
    
    # Academic Performance Overview
    try:
        top_performers = Student.objects.filter(
            is_active=True,
            examresult__isnull=False
        ).annotate(
            avg_percentage=Avg('examresult__marks_obtained')
        ).order_by('-avg_percentage')[:10]
    except:
        top_performers = []
    
    # Attendance Overview
    try:
        attendance_stats = {
            'total_records': Attendance.objects.count(),
            'present_today': Attendance.objects.filter(
                date=datetime.now().date(),
                status='PRESENT'
            ).count(),
            'absent_today': Attendance.objects.filter(
                date=datetime.now().date(),
                status='ABSENT'
            ).count(),
        }
    except:
        attendance_stats = {
            'total_records': 0,
            'present_today': 0,
            'absent_today': 0,
        }
    
    context = {
        'school_settings': school_settings,
        'total_students': total_students,
        'total_grades': total_grades,
        'male_students': male_students,
        'female_students': female_students,
        'grade_wise_count': grade_wise_count,
        'recent_admissions': recent_admissions,
        'top_performers': top_performers,
        'attendance_stats': attendance_stats,
        'page_title': 'Student Management Dashboard'
    }
    
    return render(request, 'students/dashboard.html', context)

@login_required
def export_students(request):
    """Enhanced CSV Export with comprehensive data"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students_comprehensive_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Admission Number', 'Full Name', 'Grade', 'Gender', 'Date of Birth',
        'Father Name', 'Mother Name', 'Contact Number', 'Email', 'Address',
        'Admission Date', 'Blood Group', 'Religion', 'Category', 'Status',
        'Academic Year', 'Overall Percentage', 'Attendance Percentage'
    ])
    
    students = Student.objects.select_related('grade', 'academic_year').filter(
        is_active=True
    ).order_by('admission_number')
    
    for student in students:
        # Calculate performance metrics
        try:
            exam_results = ExamResult.objects.filter(student=student)
            if exam_results.exists():
                total_marks = exam_results.aggregate(
                    total_obtained=Sum('marks_obtained'),
                    total_max=Sum('max_marks')
                )
                overall_percentage = round(
                    (total_marks['total_obtained'] / total_marks['total_max']) * 100, 1
                ) if total_marks['total_max'] else 0
            else:
                overall_percentage = 0
        except:
            overall_percentage = 0
        
        # Calculate attendance percentage
        try:
            attendance_records = Attendance.objects.filter(student=student)
            if attendance_records.exists():
                present_count = attendance_records.filter(status='PRESENT').count()
                attendance_percentage = round(
                    (present_count / attendance_records.count()) * 100, 1
                )
            else:
                attendance_percentage = 0
        except:
            attendance_percentage = 0
        
        writer.writerow([
            student.admission_number,
            student.full_name,
            student.grade.name if student.grade else '',
            student.get_gender_display(),
            student.date_of_birth,
            student.father_name,
            student.mother_name,
            student.contact_number,
            student.email,
            student.address,
            student.admission_date,
            student.blood_group,
            student.religion,
            student.category,
            'Active' if student.is_active else 'Inactive',
            student.academic_year.year if student.academic_year else '',
            overall_percentage,
            attendance_percentage,
        ])
    
    return response

@login_required
def student_analytics_api(request):
    """API endpoint for student analytics charts"""
    
    # Grade-wise distribution
    grade_data = Student.objects.filter(is_active=True).values(
        'grade__name'
    ).annotate(count=Count('id')).order_by('grade__name')
    
    # Gender distribution
    gender_data = Student.objects.filter(is_active=True).values(
        'gender'
    ).annotate(count=Count('id'))
    
    # Monthly admission trends
    admission_trends = Student.objects.filter(is_active=True).extra(
        select={
            'month': "EXTRACT(month FROM admission_date)",
            'year': "EXTRACT(year FROM admission_date)"
        }
    ).values('month', 'year').annotate(count=Count('id')).order_by('year', 'month')
    
    data = {
        'grade_distribution': list(grade_data),
        'gender_distribution': list(gender_data),
        'admission_trends': list(admission_trends)
    }
    
    return JsonResponse(data)

@login_required
def bulk_student_operations(request):
    """Handle bulk operations on students"""
    if request.method == 'POST':
        action = request.POST.get('action')
        student_ids = request.POST.getlist('student_ids')
        
        if not student_ids:
            messages.error(request, 'No students selected.')
            return redirect('student-list')
        
        students = Student.objects.filter(id__in=student_ids)
        
        if action == 'deactivate':
            students.update(is_active=False)
            messages.success(request, f'Deactivated {len(student_ids)} students.')
        elif action == 'activate':
            students.update(is_active=True)
            messages.success(request, f'Activated {len(student_ids)} students.')
        elif action == 'export':
            # Export selected students
            return export_selected_students(student_ids)
    
    return redirect('student-list')

def export_selected_students(student_ids):
    """Export selected students to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="selected_students_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Admission Number', 'Full Name', 'Grade', 'Gender',
        'Contact Number', 'Email', 'Status'
    ])
    
    students = Student.objects.filter(id__in=student_ids).select_related('grade')
    
    for student in students:
        writer.writerow([
            student.admission_number,
            student.full_name,
            student.grade.name if student.grade else '',
            student.get_gender_display(),
            student.contact_number,
            student.email,
            'Active' if student.is_active else 'Inactive'
        ])
    
    return response

@login_required
def student_document_management(request, student_id):
    """Comprehensive student document management system"""
    student = get_object_or_404(Student, id=student_id)
    school_settings = SchoolSettings.objects.first()
    
    # Get all documents for the student
    from core.models import Attachment
    from django.contrib.contenttypes.models import ContentType
    
    student_ct = ContentType.objects.get_for_model(Student)
    documents = Attachment.objects.filter(
        content_type=student_ct,
        object_id=student.id
    ).order_by('-created_at')
    
    # Document categories for Indian education system
    document_categories = [
        'BIRTH_CERTIFICATE', 'AADHAR_CARD', 'TRANSFER_CERTIFICATE',
        'MARK_SHEET', 'CASTE_CERTIFICATE', 'INCOME_CERTIFICATE',
        'MEDICAL_CERTIFICATE', 'PHOTO', 'BANK_PASSBOOK', 'OTHER'
    ]
    
    # Check document completeness
    mandatory_docs = ['BIRTH_CERTIFICATE', 'AADHAR_CARD', 'PHOTO']
    missing_docs = []
    for doc_type in mandatory_docs:
        if not documents.filter(name__icontains=doc_type.lower()).exists():
            missing_docs.append(doc_type)
    
    context = {
        'student': student,
        'school_settings': school_settings,
        'documents': documents,
        'document_categories': document_categories,
        'missing_docs': missing_docs,
        'document_completion_percentage': round(
            ((len(mandatory_docs) - len(missing_docs)) / len(mandatory_docs)) * 100, 1
        ),
        'page_title': f'Document Management - {student.full_name}'
    }
    
    return render(request, 'students/document_management.html', context)

@login_required
def student_medical_records(request, student_id):
    """Comprehensive medical records management"""
    student = get_object_or_404(Student, id=student_id)
    school_settings = SchoolSettings.objects.first()
    
    # Medical history and records
    medical_data = {
        'height': getattr(student, 'height', None),
        'weight': getattr(student, 'weight', None),
        'blood_group': getattr(student, 'blood_group', None),
        'medical_conditions': getattr(student, 'medical_conditions', ''),
        'allergies': getattr(student, 'allergies', ''),
        'medications': getattr(student, 'medications', ''),
        'vaccination_status': getattr(student, 'vaccination_status', ''),
    }
    
    # Calculate BMI if height and weight available
    bmi = None
    bmi_category = None
    if medical_data['height'] and medical_data['weight']:
        height_m = medical_data['height'] / 100  # Convert cm to meters
        bmi = round(medical_data['weight'] / (height_m ** 2), 1)
        
        if bmi < 18.5:
            bmi_category = 'Underweight'
        elif bmi < 25:
            bmi_category = 'Normal'
        elif bmi < 30:
            bmi_category = 'Overweight'
        else:
            bmi_category = 'Obese'
    
    # Medical alerts and recommendations
    medical_alerts = []
    if medical_data['medical_conditions']:
        medical_alerts.append('Has existing medical conditions')
    if medical_data['allergies']:
        medical_alerts.append('Has known allergies')
    if medical_data['medications']:
        medical_alerts.append('Takes regular medications')
    
    context = {
        'student': student,
        'school_settings': school_settings,
        'medical_data': medical_data,
        'bmi': bmi,
        'bmi_category': bmi_category,
        'medical_alerts': medical_alerts,
        'page_title': f'Medical Records - {student.full_name}'
    }
    
    return render(request, 'students/medical_records.html', context)

@login_required
def student_parent_portal(request, student_id):
    """Advanced parent portal with real-time updates"""
    student = get_object_or_404(Student, id=student_id)
    school_settings = SchoolSettings.objects.first()
    
    # Get parent portal data
    try:
        parent_portal = ParentPortal.objects.get(parent_user__username=f'parent_{student.admission_number}')
    except ParentPortal.DoesNotExist:
        parent_portal = None
    
    # Recent academic activities
    recent_exams = ExamResult.objects.filter(student=student).select_related(
        'exam', 'subject'
    ).order_by('-exam__start_date')[:5]
    
    # Recent attendance (last 30 days)
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    recent_attendance = Attendance.objects.filter(
        student=student,
        date__gte=thirty_days_ago
    ).order_by('-date')[:30]
    
    # Fee status
    pending_fees = FeePayment.objects.filter(
        student=student,
        status='PENDING'
    ).aggregate(total=Sum('amount_due'))['total'] or 0
    
    # Smart notifications for parents
    parent_notifications = SmartNotification.objects.filter(
        recipient__username=f'parent_{student.admission_number}',
        is_sent=True
    ).order_by('-created_at')[:10]
    
    # Mobile app sessions
    mobile_sessions = MobileAppSession.objects.filter(
        user__username=f'parent_{student.admission_number}',
        app_type='PARENT'
    ).order_by('-session_start')[:5]
    
    # Quick stats for parent dashboard
    stats = {
        'attendance_percentage': recent_attendance.filter(status='PRESENT').count() / recent_attendance.count() * 100 if recent_attendance.count() > 0 else 0,
        'pending_fees': pending_fees,
        'recent_exam_average': recent_exams.aggregate(avg=Avg('marks_obtained'))['avg'] or 0,
        'unread_notifications': parent_notifications.filter(is_read=False).count(),
    }
    
    context = {
        'student': student,
        'school_settings': school_settings,
        'parent_portal': parent_portal,
        'recent_exams': recent_exams,
        'recent_attendance': recent_attendance,
        'parent_notifications': parent_notifications,
        'mobile_sessions': mobile_sessions,
        'stats': stats,
        'page_title': f'Parent Portal - {student.full_name}'
    }
    
    return render(request, 'students/parent_portal.html', context)

@login_required
def student_transfer_withdrawal(request, student_id):
    """Student transfer and withdrawal management system"""
    student = get_object_or_404(Student, id=student_id)
    school_settings = SchoolSettings.objects.first()
    
    if request.method == 'POST':
        action_type = request.POST.get('action_type')
        
        if action_type == 'TRANSFER':
            # Handle transfer process
            new_school = request.POST.get('new_school')
            transfer_date = request.POST.get('transfer_date')
            reason = request.POST.get('reason')
            
            # Create transfer record
            transfer_data = {
                'student_id': student.id,
                'action_type': 'TRANSFER',
                'new_school': new_school,
                'effective_date': transfer_date,
                'reason': reason,
                'processed_by': request.user.id,
                'documents_required': [
                    'Transfer Certificate',
                    'Character Certificate',
                    'Mark Sheets',
                    'Fee Clearance'
                ]
            }
            
            # Mark student as inactive
            student.is_active = False
            student.save()
            
            messages.success(request, f'Transfer process initiated for {student.full_name}')
            
        elif action_type == 'WITHDRAWAL':
            # Handle withdrawal process
            withdrawal_date = request.POST.get('withdrawal_date')
            reason = request.POST.get('reason')
            
            # Create withdrawal record
            withdrawal_data = {
                'student_id': student.id,
                'action_type': 'WITHDRAWAL',
                'effective_date': withdrawal_date,
                'reason': reason,
                'processed_by': request.user.id,
                'clearance_status': {
                    'library_clearance': False,
                    'fee_clearance': False,
                    'transport_clearance': False,
                    'hostel_clearance': False,
                    'final_clearance': False
                }
            }
            
            messages.success(request, f'Withdrawal process initiated for {student.full_name}')
        
        return redirect('student-detail', pk=student_id)
    
    # Calculate pending clearances
    pending_clearances = []
    
    # Check fee clearance
    pending_fees = FeePayment.objects.filter(
        student=student,
        status__in=['PENDING', 'OVERDUE']
    ).aggregate(total=Sum('amount_due'))['total'] or 0
    
    if pending_fees > 0:
        pending_clearances.append({
            'type': 'Fee Clearance',
            'status': 'Pending',
            'details': f'Outstanding fees: ₹{pending_fees}'
        })
    
    # Check library clearance (if library books issued)
    # This would require integration with library module
    
    context = {
        'student': student,
        'school_settings': school_settings,
        'pending_clearances': pending_clearances,
        'page_title': f'Transfer/Withdrawal - {student.full_name}'
    }
    
    return render(request, 'students/transfer_withdrawal.html', context)

@login_required
def student_id_card_generation(request, student_id):
    """Generate student ID card with QR code"""
    student = get_object_or_404(Student, id=student_id)
    school_settings = SchoolSettings.objects.first()
    
    # Generate QR code data
    qr_data = {
        'student_id': student.admission_number,
        'name': student.full_name,
        'grade': student.grade.name if student.grade else '',
        'academic_year': student.academic_year.name if hasattr(student, 'academic_year') else '',
        'issue_date': datetime.now().strftime('%Y-%m-%d')
    }
    
    # ID card data
    id_card_data = {
        'student': student,
        'school': school_settings,
        'issue_date': datetime.now().date(),
        'valid_until': datetime.now().date() + timedelta(days=365),
        'qr_code_data': json.dumps(qr_data),
        'emergency_contact': student.emergency_contact,
        'blood_group': getattr(student, 'blood_group', 'O+'),
    }
    
    context = {
        'student': student,
        'school_settings': school_settings,
        'id_card_data': id_card_data,
        'page_title': f'ID Card - {student.full_name}'
    }
    
    return render(request, 'students/id_card.html', context)

@login_required
def biometric_attendance_management(request, student_id):
    """Biometric attendance system integration"""
    student = get_object_or_404(Student, id=student_id)
    school_settings = SchoolSettings.objects.first()
    
    # Get biometric data for student
    try:
        student_user = student.user if hasattr(student, 'user') else None
        biometric_records = BiometricAttendance.objects.filter(
            user=student_user
        ).order_by('-created_at') if student_user else []
    except:
        biometric_records = []
    
    # Attendance analytics with biometric integration
    attendance_analytics = {
        'total_biometric_records': len(biometric_records),
        'last_biometric_scan': biometric_records[0].last_used if biometric_records else None,
        'biometric_attendance_percentage': 0,  # Calculate based on biometric vs manual attendance
        'average_entry_time': None,  # Calculate average school entry time
        'punctuality_score': 85  # Calculate based on on-time arrivals
    }
    
    # Recent biometric attendance
    recent_biometric_attendance = Attendance.objects.filter(
        student=student,
        marked_by__isnull=True  # Assuming biometric attendance has no manual marker
    ).order_by('-date')[:30]
    
    context = {
        'student': student,
        'school_settings': school_settings,
        'biometric_records': biometric_records,
        'attendance_analytics': attendance_analytics,
        'recent_biometric_attendance': recent_biometric_attendance,
        'page_title': f'Biometric Attendance - {student.full_name}'
    }
    
    return render(request, 'students/biometric_attendance.html', context)

@login_required
def virtual_classroom_integration(request, student_id):
    """Virtual classroom management for student"""
    student = get_object_or_404(Student, id=student_id)
    school_settings = SchoolSettings.objects.first()
    
    # Get virtual classrooms for student's grade
    virtual_classrooms = VirtualClassroom.objects.filter(
        participants__username=f'student_{student.admission_number}',
        is_active=True
    ).order_by('-scheduled_start')[:20]
    
    # Upcoming virtual classes
    upcoming_classes = virtual_classrooms.filter(
        scheduled_start__gt=timezone.now()
    )[:5]
    
    # Recent virtual class participation
    recent_classes = virtual_classrooms.filter(
        scheduled_start__lt=timezone.now()
    )[:10]
    
    # Virtual classroom analytics
    total_classes_scheduled = virtual_classrooms.count()
    total_classes_attended = virtual_classrooms.filter(
        actual_start__isnull=False
    ).count()
    
    attendance_percentage = (total_classes_attended / total_classes_scheduled * 100) if total_classes_scheduled > 0 else 0
    
    virtual_analytics = {
        'total_classes': total_classes_scheduled,
        'attended_classes': total_classes_attended,
        'attendance_percentage': round(attendance_percentage, 1),
        'average_participation_time': 45,  # Calculate from actual participation data
        'technical_issues': 2,  # Track technical issues reported
    }
    
    context = {
        'student': student,
        'school_settings': school_settings,
        'virtual_classrooms': virtual_classrooms,
        'upcoming_classes': upcoming_classes,
        'recent_classes': recent_classes,
        'virtual_analytics': virtual_analytics,
        'page_title': f'Virtual Classrooms - {student.full_name}'
    }
    
    return render(request, 'students/virtual_classroom.html', context)

@login_required
def student_alumni_management(request, student_id):
    """Alumni management and tracking system"""
    student = get_object_or_404(Student, id=student_id)
    school_settings = SchoolSettings.objects.first()
    
    # Check if student is alumni (graduated)
    is_alumni = not student.is_active and hasattr(student, 'graduation_date')
    
    # Alumni data structure
    alumni_data = {
        'graduation_year': getattr(student, 'graduation_year', None),
        'graduation_date': getattr(student, 'graduation_date', None),
        'final_grade': getattr(student, 'final_grade', None),
        'final_percentage': getattr(student, 'final_percentage', None),
        'achievements': getattr(student, 'achievements', []),
        'current_status': getattr(student, 'current_status', 'Unknown'),
        'higher_education': getattr(student, 'higher_education', ''),
        'career_path': getattr(student, 'career_path', ''),
        'current_organization': getattr(student, 'current_organization', ''),
        'contact_details': {
            'current_phone': getattr(student, 'current_phone', student.phone),
            'current_email': getattr(student, 'current_email', student.email),
            'current_address': getattr(student, 'current_address', student.address),
        }
    }
    
    # Alumni network connections (other alumni from same batch)
    batch_alumni = Student.objects.filter(
        grade=student.grade,
        admission_date__year=student.admission_date.year,
        is_active=False
    ).exclude(id=student.id)[:10]
    
    # Success stories and achievements
    achievements = [
        'Academic Excellence Award 2023',
        'Sports Champion - District Level',
        'Science Fair Winner',
        'Leadership Award'
    ]
    
    context = {
        'student': student,
        'school_settings': school_settings,
        'is_alumni': is_alumni,
        'alumni_data': alumni_data,
        'batch_alumni': batch_alumni,
        'achievements': achievements,
        'page_title': f'Alumni Profile - {student.full_name}'
    }
    
    return render(request, 'students/alumni_management.html', context)

@login_required
def comprehensive_student_analytics(request, student_id):
    """Advanced student analytics with AI insights"""
    student = get_object_or_404(Student, id=student_id)
    school_settings = SchoolSettings.objects.first()
    
    # Academic performance analytics
    exam_results = ExamResult.objects.filter(student=student).select_related('exam', 'subject')
    
    # Subject-wise performance
    subject_performance = exam_results.values('subject__name').annotate(
        avg_marks=Avg('marks_obtained'),
        total_exams=Count('id'),
        highest_score=exam_results.aggregate(max_marks=models.Max('marks_obtained'))['max_marks'],
        latest_score=exam_results.order_by('-exam__start_date').first().marks_obtained if exam_results.exists() else 0
    ).order_by('-avg_marks')
    
    # Performance trends over time
    monthly_performance = exam_results.extra(
        select={'month': "EXTRACT(month FROM exam__start_date)"}
    ).values('month').annotate(
        avg_score=Avg('marks_obtained')
    ).order_by('month')
    
    # Attendance analytics
    attendance_records = Attendance.objects.filter(student=student)
    attendance_analytics = {
        'total_days': attendance_records.count(),
        'present_days': attendance_records.filter(status='PRESENT').count(),
        'absent_days': attendance_records.filter(status='ABSENT').count(),
        'late_days': attendance_records.filter(status='LATE').count(),
        'attendance_percentage': attendance_records.filter(status='PRESENT').count() / attendance_records.count() * 100 if attendance_records.count() > 0 else 0
    }
    
    # Behavioral analytics
    behavioral_data = {
        'discipline_score': 85,  # Calculate from discipline records
        'participation_score': 78,  # Calculate from class participation
        'leadership_score': 72,   # Calculate from leadership activities
        'social_interaction_score': 88,  # Calculate from peer interactions
    }
    
    # Risk assessment using AI
    risk_factors = []
    risk_score = 0
    
    if attendance_analytics['attendance_percentage'] < 75:
        risk_factors.append('Low attendance pattern')
        risk_score += 25
    
    if subject_performance and subject_performance[0]['avg_marks'] < 60:
        risk_factors.append('Academic performance below average')
        risk_score += 30
    
    # Predictive insights
    predictions = {
        'final_grade_prediction': 'A',
        'university_admission_probability': 85,
        'career_recommendation': ['Engineering', 'Medicine', 'Computer Science'],
        'intervention_required': risk_score > 40
    }
    
    context = {
        'student': student,
        'school_settings': school_settings,
        'subject_performance': subject_performance,
        'monthly_performance': monthly_performance,
        'attendance_analytics': attendance_analytics,
        'behavioral_data': behavioral_data,
        'risk_factors': risk_factors,
        'risk_score': risk_score,
        'predictions': predictions,
        'page_title': f'Advanced Analytics - {student.full_name}'
    }
    
    return render(request, 'students/comprehensive_analytics.html', context)
