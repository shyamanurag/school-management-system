#!/usr/bin/env python
"""
Simplified Advanced Data Population Script
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

def populate_parent_portals():
    """Populate Parent Portal data"""
    print("Creating Parent Portals...")
    
    # Get first 20 users as parents
    parent_users = User.objects.all()[:20]
    
    portals = []
    for parent in parent_users:
        portals.append(ParentPortal(
            parent_user=parent,
            dashboard_layout={'widgets': ['attendance', 'grades']},
            notification_preferences={'email': True, 'sms': True},
            privacy_settings={'share_progress': True},
            preferred_communication_method='EMAIL',
            login_count=random.randint(10, 100),
            last_activity=timezone.now() - timedelta(days=random.randint(1, 30))
        ))
    
    ParentPortal.objects.bulk_create(portals)
    print(f"Created {len(portals)} Parent Portals")

def populate_virtual_classrooms():
    """Populate Virtual Classroom data"""
    print("Creating Virtual Classrooms...")
    
    teachers = Teacher.objects.all()[:5]  # First 5 teachers
    
    if not teachers:
        print("No teachers found, skipping virtual classrooms")
        return
    
    classrooms = []
    for i in range(10):  # 10 virtual classrooms
        host = random.choice(teachers).user
        
        scheduled_start = timezone.now() + timedelta(days=random.randint(1, 30))
        scheduled_end = scheduled_start + timedelta(hours=1)
        
        classroom = VirtualClassroom(
            title=f"Virtual Class {i+1}",
            description="Sample virtual classroom",
            class_type='LIVE_LECTURE',
            platform='ZOOM',
            meeting_id=f"{random.randint(100000000, 999999999)}",
            meeting_url=f"https://zoom.com/j/{random.randint(100000000, 999999999)}",
            scheduled_start=scheduled_start,
            scheduled_end=scheduled_end,
            host=host,
            max_participants=50,
            is_active=True
        )
        classrooms.append(classroom)
    
    VirtualClassroom.objects.bulk_create(classrooms)
    print(f"Created {len(classrooms)} Virtual Classrooms")

def main():
    """Main function"""
    print("Starting Simplified Advanced Data Population...")
    
    try:
        populate_parent_portals()
        populate_virtual_classrooms()
        
        print("✅ Simplified Population Completed!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main() 