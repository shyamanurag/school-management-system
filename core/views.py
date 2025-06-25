from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from django.db import models
from .models import (
    SchoolSettings, AcademicYear, Campus, Department, Building, Room,
    SystemConfiguration, Subject, Grade, Teacher, Student, FeeCategory,
    FeeStructure, FeePayment, Attendance, Exam, ExamResult, AuditLog,
    Attachment, NotificationTemplate, AdmissionSession, AIAnalytics,
    RealTimeChat, ChatMessage, ParentPortal, MobileAppSession, AdvancedReport,
    SmartNotification, BiometricAttendance, VirtualClassroom, VirtualClassroomParticipant
)

# Create your views here.

def dashboard(request):
    """Main dashboard view with comprehensive statistics"""
    # Basic statistics
    total_students = Student.objects.count()
    total_teachers = Teacher.objects.count()
    total_grades = Grade.objects.count()
    total_subjects = Subject.objects.count()
    
    # Academic statistics
    total_exams = Exam.objects.count()
    total_exam_results = ExamResult.objects.count()
    
    # Fee statistics
    total_fee_categories = FeeCategory.objects.count()
    total_fee_payments = FeePayment.objects.count()
    total_fee_amount = FeePayment.objects.aggregate(
        total=models.Sum('amount_paid')
    )['total'] or 0
    
    # Attendance statistics
    total_attendance_records = Attendance.objects.count()
    today_attendance = Attendance.objects.filter(date=timezone.now().date()).count()
    
    # Infrastructure statistics
    total_campuses = Campus.objects.count()
    total_buildings = Building.objects.count()
    total_rooms = Room.objects.count()
    total_departments = Department.objects.count()
    
    # Advanced Features Statistics
    try:
        # AI & Analytics
        total_ai_analytics = AIAnalytics.objects.count()
        active_ai_insights = AIAnalytics.objects.filter(
            confidence_score__gte=0.8
        ).count()
        
        # Communication & Chat
        total_chat_rooms = RealTimeChat.objects.count()
        active_chat_rooms = RealTimeChat.objects.filter(
            is_archived=False
        ).count()
        total_chat_messages = ChatMessage.objects.count()
        
        # Parent Portal
        total_parent_portals = ParentPortal.objects.count()
        active_parent_users = ParentPortal.objects.filter(
            last_activity__gte=timezone.now() - timedelta(days=30)
        ).count()
        
        # Mobile App Usage
        total_mobile_sessions = MobileAppSession.objects.count()
        active_mobile_sessions = MobileAppSession.objects.filter(
            is_active=True
        ).count()
        
        # Advanced Reports
        total_reports = AdvancedReport.objects.count()
        scheduled_reports = AdvancedReport.objects.filter(
            is_scheduled=True
        ).count()
        
        # Smart Notifications
        total_notifications = SmartNotification.objects.count()
        unread_notifications = SmartNotification.objects.filter(
            is_read=False
        ).count()
        
        # Biometric & Security
        total_biometric_users = BiometricAttendance.objects.values('user').distinct().count()
        active_biometric_devices = BiometricAttendance.objects.filter(
            is_active=True
        ).count()
        
        # Virtual Classrooms
        total_virtual_classes = VirtualClassroom.objects.count()
        upcoming_virtual_classes = VirtualClassroom.objects.filter(
            scheduled_start__gte=timezone.now(),
            is_active=True
        ).count()
        total_virtual_participants = VirtualClassroomParticipant.objects.count()
        
    except Exception:
        # Fallback if advanced models aren't available
        total_ai_analytics = active_ai_insights = 0
        total_chat_rooms = active_chat_rooms = total_chat_messages = 0
        total_parent_portals = active_parent_users = 0
        total_mobile_sessions = active_mobile_sessions = 0
        total_reports = scheduled_reports = 0
        total_notifications = unread_notifications = 0
        total_biometric_users = active_biometric_devices = 0
        total_virtual_classes = upcoming_virtual_classes = total_virtual_participants = 0
    
    # Recent activity (last 7 days)
    week_ago = timezone.now() - timedelta(days=7)
    recent_students = Student.objects.filter(created_at__gte=week_ago).count()
    recent_payments = FeePayment.objects.filter(payment_date__gte=week_ago).count()
    recent_exams = Exam.objects.filter(created_at__gte=week_ago).count()
    
    # Calculate percentages for progress bars
    def safe_percentage(part, total):
        return round((part / total * 100), 1) if total > 0 else 0
    
    context = {
        # Basic Stats
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_grades': total_grades,
        'total_subjects': total_subjects,
        
        # Academic Stats
        'total_exams': total_exams,
        'total_exam_results': total_exam_results,
        'exam_completion_rate': safe_percentage(total_exam_results, total_students * total_exams),
        
        # Financial Stats
        'total_fee_categories': total_fee_categories,
        'total_fee_payments': total_fee_payments,
        'total_fee_amount': total_fee_amount,
        'fee_collection_rate': safe_percentage(total_fee_payments, total_students),
        
        # Attendance Stats
        'total_attendance_records': total_attendance_records,
        'today_attendance': today_attendance,
        'attendance_rate': safe_percentage(today_attendance, total_students),
        
        # Infrastructure Stats
        'total_campuses': total_campuses,
        'total_buildings': total_buildings,
        'total_rooms': total_rooms,
        'total_departments': total_departments,
        
        # Advanced Features Stats
        'total_ai_analytics': total_ai_analytics,
        'active_ai_insights': active_ai_insights,
        'ai_confidence_rate': safe_percentage(active_ai_insights, total_ai_analytics),
        
        'total_chat_rooms': total_chat_rooms,
        'active_chat_rooms': active_chat_rooms,
        'total_chat_messages': total_chat_messages,
        'chat_activity_rate': safe_percentage(active_chat_rooms, total_chat_rooms),
        
        'total_parent_portals': total_parent_portals,
        'active_parent_users': active_parent_users,
        'parent_engagement_rate': safe_percentage(active_parent_users, total_parent_portals),
        
        'total_mobile_sessions': total_mobile_sessions,
        'active_mobile_sessions': active_mobile_sessions,
        'mobile_usage_rate': safe_percentage(active_mobile_sessions, total_mobile_sessions),
        
        'total_reports': total_reports,
        'scheduled_reports': scheduled_reports,
        'report_automation_rate': safe_percentage(scheduled_reports, total_reports),
        
        'total_notifications': total_notifications,
        'unread_notifications': unread_notifications,
        'notification_read_rate': safe_percentage(total_notifications - unread_notifications, total_notifications),
        
        'total_biometric_users': total_biometric_users,
        'active_biometric_devices': active_biometric_devices,
        'biometric_adoption_rate': safe_percentage(total_biometric_users, total_students + total_teachers),
        
        'total_virtual_classes': total_virtual_classes,
        'upcoming_virtual_classes': upcoming_virtual_classes,
        'total_virtual_participants': total_virtual_participants,
        'virtual_class_utilization': safe_percentage(total_virtual_participants, total_virtual_classes * 25),  # Assuming avg 25 per class
        
        # Recent Activity
        'recent_students': recent_students,
        'recent_payments': recent_payments,
        'recent_exams': recent_exams,
        
        # System Health
        'system_health': 'Excellent' if total_students > 0 and total_teachers > 0 else 'Good',
        'last_updated': timezone.now(),
    }
    
    return render(request, 'core/dashboard.html', context)

# Placeholder views for all the URL patterns
def school_settings(request):
    return render(request, 'modules/coming_soon.html', {'module': 'School Settings'})

def academics_dashboard(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Academics Dashboard'})

def academic_years(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Academic Years'})

def subjects(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Subjects'})

def grades(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Grades'})

def students_list(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Students List'})

def student_add(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Add Student'})

def student_detail(request, student_id):
    return render(request, 'modules/coming_soon.html', {'module': 'Student Detail'})

def student_edit(request, student_id):
    return render(request, 'modules/coming_soon.html', {'module': 'Edit Student'})

def student_attendance(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Student Attendance'})

def teachers_list(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Teachers List'})

def teacher_add(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Add Teacher'})

def teacher_detail(request, teacher_id):
    return render(request, 'modules/coming_soon.html', {'module': 'Teacher Detail'})

def teacher_edit(request, teacher_id):
    return render(request, 'modules/coming_soon.html', {'module': 'Edit Teacher'})

def fees_dashboard(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Fees Dashboard'})

def fee_categories(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Fee Categories'})

def fee_structures(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Fee Structures'})

def fee_payments(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Fee Payments'})

def fee_reports(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Fee Reports'})

def exams_dashboard(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Exams Dashboard'})

def exams_list(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Exams List'})

def exam_add(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Add Exam'})

def exam_detail(request, exam_id):
    return render(request, 'modules/coming_soon.html', {'module': 'Exam Detail'})

def exam_results(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Exam Results'})

def infrastructure_dashboard(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Infrastructure Dashboard'})

def campuses(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Campuses'})

def buildings(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Buildings'})

def rooms(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Rooms'})

def departments(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Departments'})

def ai_analytics_dashboard(request):
    return render(request, 'modules/coming_soon.html', {'module': 'AI Analytics Dashboard'})

def student_performance_analytics(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Student Performance Analytics'})

def attendance_prediction(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Attendance Prediction'})

def behavioral_analysis(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Behavioral Analysis'})

def communication_dashboard(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Communication Dashboard'})

def chat_rooms(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Chat Rooms'})

def chat_room(request, room_id):
    return render(request, 'modules/coming_soon.html', {'module': 'Chat Room'})

def notifications(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Notifications'})

def announcements(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Announcements'})

def parent_portal_dashboard(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Parent Portal Dashboard'})

def parent_portal_settings(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Parent Portal Settings'})

def parent_children(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Parent Children'})

def parent_child_detail(request, student_id):
    return render(request, 'modules/coming_soon.html', {'module': 'Parent Child Detail'})

def virtual_classrooms_list(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Virtual Classrooms List'})

def virtual_classroom_add(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Add Virtual Classroom'})

def virtual_classroom_detail(request, classroom_id):
    return render(request, 'modules/coming_soon.html', {'module': 'Virtual Classroom Detail'})

def virtual_classroom_join(request, classroom_id):
    return render(request, 'modules/coming_soon.html', {'module': 'Join Virtual Classroom'})

def reports_dashboard(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Reports Dashboard'})

def advanced_reports(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Advanced Reports'})

def generate_report(request, report_id):
    return render(request, 'modules/coming_soon.html', {'module': 'Generate Report'})

def scheduled_reports(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Scheduled Reports'})

def mobile_app_dashboard(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Mobile App Dashboard'})

def mobile_sessions(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Mobile Sessions'})

def mobile_usage_analytics(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Mobile Usage Analytics'})

def biometric_dashboard(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Biometric Dashboard'})

def biometric_enrollment(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Biometric Enrollment'})

def biometric_attendance(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Biometric Attendance'})

def system_dashboard(request):
    return render(request, 'modules/coming_soon.html', {'module': 'System Dashboard'})

def system_configuration(request):
    return render(request, 'modules/coming_soon.html', {'module': 'System Configuration'})

def audit_logs(request):
    return render(request, 'modules/coming_soon.html', {'module': 'Audit Logs'})

def system_backup(request):
    return render(request, 'modules/coming_soon.html', {'module': 'System Backup'})

# API Views
from django.http import JsonResponse

def api_dashboard_stats(request):
    return JsonResponse({'status': 'success', 'message': 'API endpoint coming soon'})

def api_mark_notification_read(request, notification_id):
    return JsonResponse({'status': 'success', 'message': 'API endpoint coming soon'})

def api_send_chat_message(request):
    return JsonResponse({'status': 'success', 'message': 'API endpoint coming soon'})
