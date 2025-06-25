#!/usr/bin/env python
"""
Advanced Data Population Script for School Management System
This script populates advanced features like AI Analytics, Chat Systems, 
Parent Portals, Mobile App Sessions, Advanced Reports, Smart Notifications,
Biometric Attendance, and Virtual Classrooms with realistic data.
"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone
import random
import uuid

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_modernized.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import (
    AIAnalytics, RealTimeChat, ChatMessage, ParentPortal, MobileAppSession,
    AdvancedReport, SmartNotification, BiometricAttendance, VirtualClassroom,
    VirtualClassroomParticipant, Student, Teacher, Grade
)

def populate_ai_analytics():
    """Populate AI Analytics with sample data"""
    print("Creating AI Analytics...")
    
    students = Student.objects.all()[:50]  # Get first 50 students
    grades = Grade.objects.all()[:10]      # Get first 10 grades
    
    analysis_types = [
        'STUDENT_PERFORMANCE', 'ATTENDANCE_PREDICTION', 'FEE_COLLECTION_FORECAST',
        'TEACHER_WORKLOAD', 'RESOURCE_OPTIMIZATION', 'BEHAVIORAL_ANALYSIS',
        'ACADEMIC_RISK', 'PARENT_ENGAGEMENT'
    ]
    
    analytics_data = []
    for i in range(100):
        analysis_type = random.choice(analysis_types)
        target_student = random.choice(students) if random.choice([True, False]) else None
        target_grade = random.choice(grades) if not target_student else None
        
        # Generate realistic analysis data
        if analysis_type == 'STUDENT_PERFORMANCE':
            analysis_data = {
                'subjects': ['Math', 'Science', 'English'],
                'scores': [random.randint(60, 100) for _ in range(3)],
                'trend': random.choice(['improving', 'declining', 'stable'])
            }
            insights = {
                'performance_level': random.choice(['excellent', 'good', 'average', 'needs_improvement']),
                'strongest_subject': random.choice(['Math', 'Science', 'English']),
                'weakest_subject': random.choice(['Math', 'Science', 'English'])
            }
            recommendations = [
                'Provide additional practice in weak areas',
                'Encourage participation in advanced classes',
                'Consider peer tutoring opportunities'
            ]
        elif analysis_type == 'ATTENDANCE_PREDICTION':
            analysis_data = {
                'historical_attendance': random.uniform(0.7, 0.98),
                'factors': ['weather', 'day_of_week', 'exam_schedule'],
                'predicted_rate': random.uniform(0.75, 0.95)
            }
            insights = {
                'risk_level': random.choice(['low', 'medium', 'high']),
                'key_factors': ['Monday mornings', 'After holidays']
            }
            recommendations = [
                'Send early morning reminders',
                'Implement attendance incentives',
                'Contact parents for chronic absenteeism'
            ]
        else:
            analysis_data = {'sample_metric': random.uniform(0.1, 1.0)}
            insights = {'key_insight': 'Generated insight'}
            recommendations = ['Take appropriate action']
        
        analytics_data.append(AIAnalytics(
            analysis_type=analysis_type,
            target_student=target_student,
            target_grade=target_grade,
            analysis_data=analysis_data,
            insights=insights,
            recommendations=recommendations,
            confidence_score=random.uniform(0.6, 0.95),
            is_automated=random.choice([True, False]),
            next_analysis_date=timezone.now() + timedelta(days=random.randint(1, 30))
        ))
    
    AIAnalytics.objects.bulk_create(analytics_data)
    print(f"Created {len(analytics_data)} AI Analytics records")


def populate_real_time_chat():
    """Populate Real-time Chat system"""
    print("Creating Real-time Chat system...")
    
    users = User.objects.all()
    teachers = Teacher.objects.all()
    
    # Create various chat rooms
    chat_rooms = []
    
    # Teacher-Parent chats
    for i in range(20):
        teacher = random.choice(teachers)
        chat_rooms.append(RealTimeChat(
            chat_type='TEACHER_PARENT',
            name=f"Parent Conference - {teacher.user.get_full_name()}",
            description=f"Discussion about student progress with {teacher.user.get_full_name()}",
            is_group=False,
            is_private=True,
            max_participants=5,
            allow_file_sharing=True,
            allow_voice_messages=True
        ))
    
    # Class group chats
    grades = Grade.objects.all()[:10]
    for grade in grades:
        chat_rooms.append(RealTimeChat(
            chat_type='CLASS_GROUP',
            name=f"{grade.name} - Class Discussion",
            description=f"General discussion for {grade.name} students and teachers",
            is_group=True,
            is_private=False,
            max_participants=50,
            allow_file_sharing=True,
            allow_voice_messages=False,
            is_moderated=True
        ))
    
    # Emergency chats
    chat_rooms.append(RealTimeChat(
        chat_type='EMERGENCY',
        name='Emergency Response Team',
        description='Emergency communication channel for staff',
        is_group=True,
        is_private=True,
        max_participants=20,
        allow_file_sharing=True,
        allow_voice_messages=True,
        is_moderated=True
    ))
    
    RealTimeChat.objects.bulk_create(chat_rooms)
    
    # Add participants to chat rooms
    created_chats = RealTimeChat.objects.all()
    for chat in created_chats:
        # Add random participants
        participants = random.sample(list(users), min(random.randint(2, 10), len(users)))
        chat.participants.set(participants)
        
        # Add admin users for moderated chats
        if chat.is_moderated:
            admin_users = random.sample(list(teachers.values_list('user', flat=True)), 
                                      min(2, len(teachers)))
            chat.admin_users.set(admin_users)
    
    print(f"Created {len(chat_rooms)} chat rooms")
    
    # Create sample messages
    messages = []
    for chat in created_chats[:10]:  # Only for first 10 chats to avoid too much data
        participants = list(chat.participants.all())
        if participants:
            for i in range(random.randint(5, 20)):
                sender = random.choice(participants)
                message_types = ['TEXT', 'IMAGE', 'FILE']
                message_type = random.choice(message_types)
                
                if message_type == 'TEXT':
                    content = random.choice([
                        "Hello everyone!",
                        "How is everyone doing?",
                        "Don't forget about tomorrow's assignment.",
                        "Great job on the recent test!",
                        "Any questions about the homework?",
                        "Looking forward to our next class.",
                        "Please review the study materials.",
                        "Happy to help if you need assistance."
                    ])
                else:
                    content = f"Shared a {message_type.lower()}"
                
                messages.append(ChatMessage(
                    chat_room=chat,
                    sender=sender,
                    message_type=message_type,
                    content=content,
                    reactions={
                        '👍': random.sample([p.id for p in participants], 
                                          random.randint(0, min(3, len(participants)))),
                        '❤️': random.sample([p.id for p in participants], 
                                          random.randint(0, min(2, len(participants))))
                    }
                ))
    
    ChatMessage.objects.bulk_create(messages)
    print(f"Created {len(messages)} chat messages")


def populate_parent_portals():
    """Populate Parent Portal data"""
    print("Creating Parent Portals...")
    
    # Get random users to be parents
    parent_users = User.objects.all()[:50]  # First 50 users as parents
    
    portals = []
    for parent in parent_users:
        portals.append(ParentPortal(
            parent_user=parent,
            dashboard_layout={
                'widgets': ['attendance', 'grades', 'fees', 'announcements'],
                'layout': 'grid',
                'theme': random.choice(['light', 'dark', 'auto'])
            },
            notification_preferences={
                'email': True,
                'sms': random.choice([True, False]),
                'push': True,
                'frequency': random.choice(['immediate', 'daily', 'weekly'])
            },
            privacy_settings={
                'share_progress': random.choice([True, False]),
                'allow_teacher_contact': True,
                'show_in_directory': random.choice([True, False])
            },
            device_tokens=[f"token_{uuid.uuid4().hex[:16]}" for _ in range(random.randint(1, 3))],
            app_version=random.choice(['1.0.0', '1.1.0', '1.2.0', '2.0.0']),
            last_app_login=timezone.now() - timedelta(days=random.randint(0, 30)),
            preferred_communication_method=random.choice(['EMAIL', 'SMS', 'PUSH', 'WHATSAPP']),
            emergency_contacts=[
                {
                    'name': 'Emergency Contact 1',
                    'phone': f'+91{random.randint(7000000000, 9999999999)}',
                    'relationship': 'Relative'
                }
            ],
            login_count=random.randint(10, 200),
            last_activity=timezone.now() - timedelta(hours=random.randint(1, 72)),
            feature_usage_stats={
                'attendance_views': random.randint(5, 50),
                'grade_views': random.randint(10, 100),
                'fee_payments': random.randint(1, 10),
                'message_sent': random.randint(0, 20)
            }
        ))
    
    ParentPortal.objects.bulk_create(portals)
    print(f"Created {len(portals)} Parent Portals")


def populate_mobile_app_sessions():
    """Populate Mobile App Session data"""
    print("Creating Mobile App Sessions...")
    
    users = User.objects.all()[:100]  # First 100 users
    app_types = ['PARENT', 'STUDENT', 'TEACHER', 'ADMIN']
    
    sessions = []
    for i in range(300):  # 300 sessions
        user = random.choice(users)
        app_type = random.choice(app_types)
        
        # Generate realistic device info
        devices = [
            {'model': 'iPhone 14', 'os': 'iOS 16.1', 'brand': 'Apple'},
            {'model': 'Samsung Galaxy S23', 'os': 'Android 13', 'brand': 'Samsung'},
            {'model': 'OnePlus 11', 'os': 'Android 13', 'brand': 'OnePlus'},
            {'model': 'iPhone 13', 'os': 'iOS 15.7', 'brand': 'Apple'},
            {'model': 'Pixel 7', 'os': 'Android 13', 'brand': 'Google'}
        ]
        device = random.choice(devices)
        
        session_start = timezone.now() - timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        is_active = random.choice([True, False])
        session_end = None if is_active else session_start + timedelta(
            minutes=random.randint(5, 120)
        )
        
        sessions.append(MobileAppSession(
            user=user,
            app_type=app_type,
            device_info=device,
            app_version=random.choice(['1.0.0', '1.1.0', '1.2.0', '2.0.0']),
            os_version=device['os'],
            device_token=f"device_token_{uuid.uuid4().hex}",
            session_start=session_start,
            session_end=session_end,
            is_active=is_active,
            last_latitude=random.uniform(12.0, 13.0) if random.choice([True, False]) else None,
            last_longitude=random.uniform(77.0, 78.0) if random.choice([True, False]) else None,
            location_updated_at=session_start + timedelta(minutes=random.randint(1, 30))
        ))
    
    MobileAppSession.objects.bulk_create(sessions)
    print(f"Created {len(sessions)} Mobile App Sessions")


def populate_advanced_reports():
    """Populate Advanced Reports"""
    print("Creating Advanced Reports...")
    
    users = User.objects.filter(is_staff=True)  # Staff users can create reports
    
    reports = []
    report_names = [
        'Monthly Academic Performance Report',
        'Attendance Analytics Dashboard',
        'Fee Collection Summary',
        'Teacher Performance Metrics',
        'Student Behavioral Analysis',
        'Parent Engagement Report',
        'Resource Utilization Report',
        'Predictive Analytics - At-Risk Students',
        'Financial Performance Analysis',
        'Campus Safety Report'
    ]
    
    for i, name in enumerate(report_names):
        category = random.choice(['ACADEMIC', 'FINANCIAL', 'ATTENDANCE', 'BEHAVIORAL', 'OPERATIONAL', 'PREDICTIVE'])
        format_type = random.choice(['PDF', 'EXCEL', 'CSV', 'DASHBOARD'])
        
        reports.append(AdvancedReport(
            name=name,
            description=f"Comprehensive {category.lower()} analysis and insights for school management",
            category=category,
            filters={
                'date_range': '30_days',
                'grade_levels': ['all'],
                'departments': ['all']
            },
            parameters={
                'include_charts': True,
                'detailed_breakdown': True,
                'comparison_period': 'previous_month'
            },
            data_sources=['students', 'attendance', 'grades', 'fees'],
            format=format_type,
            template=f"template_{category.lower()}",
            is_scheduled=random.choice([True, False]),
            schedule_expression='0 8 1 * *' if random.choice([True, False]) else None,  # Monthly at 8 AM
            next_run=timezone.now() + timedelta(days=random.randint(1, 30)),
            use_ai_insights=random.choice([True, False]),
            ai_analysis_level=random.choice(['BASIC', 'ADVANCED', 'PREDICTIVE']),
            last_generated=timezone.now() - timedelta(days=random.randint(1, 30)),
            generation_count=random.randint(1, 20),
            average_generation_time=random.uniform(30.0, 300.0)  # 30 seconds to 5 minutes
        ))
    
    AdvancedReport.objects.bulk_create(reports)
    
    # Add recipients to reports
    created_reports = AdvancedReport.objects.all()
    for report in created_reports:
        recipients = random.sample(list(users), min(random.randint(1, 5), len(users)))
        report.recipients.set(recipients)
    
    print(f"Created {len(reports)} Advanced Reports")


def populate_smart_notifications():
    """Populate Smart Notifications"""
    print("Creating Smart Notifications...")
    
    users = User.objects.all()[:100]  # First 100 users
    
    notifications = []
    for i in range(200):  # 200 notifications
        trigger_type = random.choice([
            'ACADEMIC_ALERT', 'ATTENDANCE_WARNING', 'FEE_REMINDER',
            'EXAM_PREPARATION', 'BEHAVIORAL_CONCERN', 'ACHIEVEMENT_RECOGNITION',
            'PARENT_MEETING', 'CUSTOM_TRIGGER'
        ])
        
        recipient = random.choice(users)
        
        # Generate content based on trigger type
        if trigger_type == 'ACADEMIC_ALERT':
            title = "Academic Performance Alert"
            message = f"Your child's performance in Mathematics needs attention. Current grade: {random.choice(['C', 'D', 'F'])}"
            action_items = ['Schedule parent-teacher meeting', 'Arrange tutoring', 'Review study habits']
        elif trigger_type == 'ATTENDANCE_WARNING':
            title = "Attendance Warning"
            message = f"Attendance rate has dropped to {random.randint(60, 75)}%. Immediate attention required."
            action_items = ['Contact parents', 'Review attendance policy', 'Schedule meeting']
        elif trigger_type == 'FEE_REMINDER':
            title = "Fee Payment Reminder"
            message = f"Monthly fee payment of ₹{random.randint(5000, 15000)} is due in 3 days."
            action_items = ['Make payment online', 'Contact accounts office', 'Set up auto-payment']
        elif trigger_type == 'ACHIEVEMENT_RECOGNITION':
            title = "Achievement Recognition"
            message = f"Congratulations! Excellent performance in {random.choice(['Science Fair', 'Math Olympiad', 'Sports Meet'])}."
            action_items = ['Share achievement', 'Apply for scholarships', 'Continue excellence']
        else:
            title = f"{trigger_type.replace('_', ' ').title()}"
            message = "Important notification requiring your attention."
            action_items = ['Take appropriate action']
        
        notifications.append(SmartNotification(
            trigger_type=trigger_type,
            recipient=recipient,
            title=title,
            message=message,
            action_items=action_items,
            priority_score=random.uniform(0.3, 1.0),
            preferred_channels=['EMAIL', 'SMS'] if random.choice([True, False]) else ['PUSH'],
            delivery_time_preference=random.choice(['IMMEDIATE', 'MORNING', 'AFTERNOON', 'EVENING']),
            personalization_data={
                'student_name': 'Sample Student',
                'parent_name': recipient.get_full_name(),
                'class': random.choice(['Class 1', 'Class 2', 'Class 3'])
            },
            language_preference='en',
            is_sent=random.choice([True, False]),
            sent_at=timezone.now() - timedelta(hours=random.randint(1, 72)) if random.choice([True, False]) else None,
            is_read=random.choice([True, False]),
            read_at=timezone.now() - timedelta(hours=random.randint(1, 48)) if random.choice([True, False]) else None,
            effectiveness_score=random.uniform(0.6, 1.0) if random.choice([True, False]) else None
        ))
    
    SmartNotification.objects.bulk_create(notifications)
    print(f"Created {len(notifications)} Smart Notifications")


def populate_biometric_attendance():
    """Populate Biometric Attendance data"""
    print("Creating Biometric Attendance data...")
    
    users = User.objects.all()[:100]  # First 100 users
    
    biometric_data = []
    for user in users:
        # Each user can have multiple biometric types
        biometric_types = random.sample(
            ['FINGERPRINT', 'FACE_RECOGNITION', 'IRIS_SCAN', 'PALM_PRINT'],
            random.randint(1, 2)
        )
        
        for i, bio_type in enumerate(biometric_types):
            biometric_data.append(BiometricAttendance(
                user=user,
                biometric_type=bio_type,
                biometric_template=b'encrypted_biometric_data_placeholder',  # Placeholder
                template_quality=random.uniform(0.7, 0.98),
                enrollment_device=random.choice([
                    'Biometric Scanner 1', 'Biometric Scanner 2', 'Mobile App',
                    'Tablet Scanner', 'Door Access System'
                ]),
                enrollment_location=random.choice([
                    'Main Office', 'Security Gate', 'Classroom Block A', 'Library'
                ]),
                is_active=True,
                is_primary=(i == 0),  # First biometric type is primary
                last_used=timezone.now() - timedelta(days=random.randint(0, 30)),
                usage_count=random.randint(10, 500),
                enrollment_verified_by=random.choice(User.objects.filter(is_staff=True))
            ))
    
    BiometricAttendance.objects.bulk_create(biometric_data)
    print(f"Created {len(biometric_data)} Biometric Attendance records")


def populate_virtual_classrooms():
    """Populate Virtual Classroom data"""
    print("Creating Virtual Classrooms...")
    
    teachers = Teacher.objects.all()
    students = User.objects.all()[:100]  # First 100 users as students
    
    classrooms = []
    for i in range(30):  # 30 virtual classrooms
        host = random.choice(teachers).user
        
        # Generate realistic class data
        class_types = ['LIVE_LECTURE', 'TUTORIAL', 'EXAM', 'PARENT_MEETING', 'WEBINAR']
        class_type = random.choice(class_types)
        
        platforms = ['ZOOM', 'GOOGLE_MEET', 'MICROSOFT_TEAMS', 'WEBEX']
        platform = random.choice(platforms)
        
        scheduled_start = timezone.now() + timedelta(
            days=random.randint(-30, 30),
            hours=random.randint(8, 18),
            minutes=random.choice([0, 30])
        )
        scheduled_end = scheduled_start + timedelta(hours=random.randint(1, 3))
        
        classroom = VirtualClassroom(
            title=f"{class_type.replace('_', ' ').title()} - {random.choice(['Mathematics', 'Science', 'English', 'History'])}",
            description=f"Interactive {class_type.lower().replace('_', ' ')} session",
            class_type=class_type,
            platform=platform,
            meeting_id=f"{random.randint(100000000, 999999999)}",
            meeting_password=f"pass{random.randint(1000, 9999)}" if random.choice([True, False]) else None,
            meeting_url=f"https://{platform.lower()}.com/j/{random.randint(100000000, 999999999)}",
            scheduled_start=scheduled_start,
            scheduled_end=scheduled_end,
            actual_start=scheduled_start + timedelta(minutes=random.randint(-5, 15)) if random.choice([True, False]) else None,
            actual_end=scheduled_end + timedelta(minutes=random.randint(-10, 20)) if random.choice([True, False]) else None,
            host=host,
            max_participants=random.randint(20, 100),
            is_recorded=random.choice([True, False]),
            recording_url=f"https://recordings.example.com/{uuid.uuid4()}" if random.choice([True, False]) else None,
            allow_chat=True,
            allow_screen_sharing=random.choice([True, False]),
            require_approval=random.choice([True, False]),
            is_active=True,
            is_recurring=random.choice([True, False]),
            recurrence_pattern={'frequency': 'weekly', 'day': 'monday'} if random.choice([True, False]) else {}
        )
        classrooms.append(classroom)
    
    VirtualClassroom.objects.bulk_create(classrooms)
    
    # Add participants to virtual classrooms
    created_classrooms = VirtualClassroom.objects.all()
    participants_data = []
    
    for classroom in created_classrooms:
        # Add random participants
        num_participants = min(random.randint(5, 25), len(students))
        participants = random.sample(list(students), num_participants)
        
        classroom.participants.set(participants)
        
        # Create participant records with detailed tracking
        for participant in participants:
            if classroom.actual_start:  # Only if class actually happened
                joined_at = classroom.actual_start + timedelta(minutes=random.randint(0, 10))
                left_at = joined_at + timedelta(minutes=random.randint(30, 120))
                total_duration = left_at - joined_at
                
                attendance_status = random.choice(['PRESENT', 'LATE', 'LEFT_EARLY']) if random.random() > 0.1 else 'ABSENT'
                
                participants_data.append(VirtualClassroomParticipant(
                    virtual_classroom=classroom,
                    user=participant,
                    role=random.choice(['PARTICIPANT', 'PRESENTER']) if random.random() > 0.9 else 'PARTICIPANT',
                    joined_at=joined_at if attendance_status != 'ABSENT' else None,
                    left_at=left_at if attendance_status != 'ABSENT' else None,
                    total_duration=total_duration if attendance_status != 'ABSENT' else None,
                    chat_messages_count=random.randint(0, 15),
                    questions_asked=random.randint(0, 5),
                    screen_share_duration=timedelta(minutes=random.randint(0, 10)) if random.choice([True, False]) else None,
                    attendance_status=attendance_status,
                    session_rating=random.randint(3, 5) if random.choice([True, False]) else None,
                    feedback=random.choice([
                        'Great session!', 'Very informative', 'Could use more interaction',
                        'Technical issues', 'Excellent presentation', None
                    ])
                ))
    
    VirtualClassroomParticipant.objects.bulk_create(participants_data)
    print(f"Created {len(classrooms)} Virtual Classrooms with {len(participants_data)} participant records")


def main():
    """Main function to populate all advanced data"""
    print("Starting Advanced Data Population...")
    print("=" * 50)
    
    try:
        populate_ai_analytics()
        populate_real_time_chat()
        populate_parent_portals()
        populate_mobile_app_sessions()
        populate_advanced_reports()
        populate_smart_notifications()
        populate_biometric_attendance()
        populate_virtual_classrooms()
        
        print("=" * 50)
        print("✅ Advanced Data Population Completed Successfully!")
        print("\nSummary of Advanced Features:")
        print(f"- AI Analytics: {AIAnalytics.objects.count()} records")
        print(f"- Real-time Chats: {RealTimeChat.objects.count()} chat rooms")
        print(f"- Chat Messages: {ChatMessage.objects.count()} messages")
        print(f"- Parent Portals: {ParentPortal.objects.count()} portals")
        print(f"- Mobile App Sessions: {MobileAppSession.objects.count()} sessions")
        print(f"- Advanced Reports: {AdvancedReport.objects.count()} reports")
        print(f"- Smart Notifications: {SmartNotification.objects.count()} notifications")
        print(f"- Biometric Records: {BiometricAttendance.objects.count()} records")
        print(f"- Virtual Classrooms: {VirtualClassroom.objects.count()} classrooms")
        print(f"- Virtual Participants: {VirtualClassroomParticipant.objects.count()} participants")
        
    except Exception as e:
        print(f"❌ Error during population: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main() 