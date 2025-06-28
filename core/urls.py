from django.urls import path, include
from . import views

app_name = 'core'

urlpatterns = [
    # Main Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Authentication & User Management
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.user_profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('change-password/', views.change_password, name='change_password'),
    
    # School Configuration
    path('settings/', views.school_settings, name='school_settings'),
    path('settings/edit/', views.edit_school_settings, name='edit_school_settings'),
    path('system-config/', views.system_configuration, name='system_configuration'),
    
    # Academic Structure
    path('academics/', views.academics_dashboard, name='academics_dashboard'),
    path('academic-years/', views.academic_years, name='academic_years'),
    path('academic-years/add/', views.add_academic_year, name='add_academic_year'),
    path('academic-years/<int:year_id>/edit/', views.edit_academic_year, name='edit_academic_year'),
    
    path('subjects/', views.subjects, name='subjects'),
    path('subjects/add/', views.add_subject, name='add_subject'),
    path('subjects/<int:subject_id>/edit/', views.edit_subject, name='edit_subject'),
    path('subjects/<int:subject_id>/delete/', views.delete_subject, name='delete_subject'),
    
    path('grades/', views.grades, name='grades'),
    path('grades/add/', views.add_grade, name='add_grade'),
    path('grades/<int:grade_id>/edit/', views.edit_grade, name='edit_grade'),
    path('grades/<int:grade_id>/students/', views.grade_students, name='grade_students'),
    
    # Infrastructure Management
    path('infrastructure/', views.infrastructure_dashboard, name='infrastructure_dashboard'),
    path('campuses/', views.campuses, name='campuses'),
    path('campuses/add/', views.add_campus, name='add_campus'),
    path('campuses/<int:campus_id>/edit/', views.edit_campus, name='edit_campus'),
    
    path('departments/', views.departments, name='departments'),
    path('departments/add/', views.add_department, name='add_department'),
    path('departments/<int:dept_id>/edit/', views.edit_department, name='edit_department'),
    
    path('buildings/', views.buildings, name='buildings'),
    path('buildings/add/', views.add_building, name='add_building'),
    path('buildings/<int:building_id>/edit/', views.edit_building, name='edit_building'),
    
    path('rooms/', views.rooms, name='rooms'),
    path('rooms/add/', views.add_room, name='add_room'),
    path('rooms/<int:room_id>/edit/', views.edit_room, name='edit_room'),
    
    # Advanced Analytics & AI
    path('analytics/', views.ai_analytics_dashboard, name='ai_analytics_dashboard'),
    path('analytics/student-performance/', views.student_performance_analytics, name='student_performance_analytics'),
    path('analytics/attendance-prediction/', views.attendance_prediction, name='attendance_prediction'),
    path('analytics/behavioral-analysis/', views.behavioral_analysis, name='behavioral_analysis'),
    path('analytics/generate/', views.generate_ai_insights, name='generate_ai_insights'),
    
    # Communication System  
    path('communication/', views.communication_dashboard, name='communication_dashboard'),
    path('chat/', views.chat_rooms, name='chat_rooms'),
    path('chat/room/<uuid:room_id>/', views.chat_room, name='chat_room'),
    path('chat/create/', views.create_chat_room, name='create_chat_room'),
    path('notifications/', views.notifications, name='notifications'),
    path('announcements/', views.announcements, name='announcements'),
    path('announcements/add/', views.add_announcement, name='add_announcement'),
    
    # Parent Portal Integration
    path('parent-portal/', views.parent_portal_dashboard, name='parent_portal_dashboard'),
    path('parent-portal/settings/', views.parent_portal_settings, name='parent_portal_settings'),
    path('parent-portal/children/', views.parent_children, name='parent_children'),
    path('parent-portal/child/<int:student_id>/', views.parent_child_detail, name='parent_child_detail'),
    
    # Virtual Classrooms
    path('virtual-classrooms/', views.virtual_classrooms_list, name='virtual_classrooms_list'),
    path('virtual-classrooms/add/', views.virtual_classroom_add, name='virtual_classroom_add'),
    path('virtual-classrooms/<uuid:classroom_id>/', views.virtual_classroom_detail, name='virtual_classroom_detail'),
    path('virtual-classrooms/<uuid:classroom_id>/join/', views.virtual_classroom_join, name='virtual_classroom_join'),
    
    # Advanced Reporting
    path('reports/', views.reports_dashboard, name='reports_dashboard'),
    path('reports/advanced/', views.advanced_reports, name='advanced_reports'),
    path('reports/generate/<uuid:report_id>/', views.generate_report, name='generate_report'),
    path('reports/scheduled/', views.scheduled_reports, name='scheduled_reports'),
    path('reports/export/<str:format>/', views.export_report, name='export_report'),
    
    # Mobile App Management
    path('mobile/', views.mobile_app_dashboard, name='mobile_app_dashboard'),
    path('mobile/sessions/', views.mobile_sessions, name='mobile_sessions'),
    path('mobile/analytics/', views.mobile_usage_analytics, name='mobile_usage_analytics'),
    path('mobile/push-notifications/', views.push_notifications, name='push_notifications'),
    
    # Biometric System
    path('biometric/', views.biometric_dashboard, name='biometric_dashboard'),
    path('biometric/enrollment/', views.biometric_enrollment, name='biometric_enrollment'),
    path('biometric/attendance/', views.biometric_attendance, name='biometric_attendance'),
    path('biometric/devices/', views.biometric_devices, name='biometric_devices'),
    
    # System Administration
    path('system/', views.system_dashboard, name='system_dashboard'),
    path('system/audit-logs/', views.audit_logs, name='audit_logs'),
    path('system/backup/', views.system_backup, name='system_backup'),
    path('system/health/', views.system_health, name='system_health'),
    path('system/maintenance/', views.system_maintenance, name='system_maintenance'),
    
    # Import/Export Features
    path('import/', views.data_import, name='data_import'),
    path('export/', views.data_export, name='data_export'),
    path('bulk-operations/', views.bulk_operations, name='bulk_operations'),
    
    # API Endpoints
    path('api/', include([
        path('dashboard/stats/', views.api_dashboard_stats, name='api_dashboard_stats'),
        path('notifications/<uuid:notification_id>/read/', views.api_mark_notification_read, name='api_mark_notification_read'),
        path('chat/send-message/', views.api_send_chat_message, name='api_send_chat_message'),
        path('analytics/generate/', views.api_generate_analytics, name='api_generate_analytics'),
        path('search/', views.api_global_search, name='api_global_search'),
        path('system/health/', views.api_system_health, name='api_system_health'),
    ])),
    
    # HR Module (Enhanced)
    path('hr/', include('core.hr_urls')),
] 