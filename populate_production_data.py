"""
COMPREHENSIVE DATA POPULATION SCRIPT
Populates the production database with sample data for all modules
"""

import os
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_modernized.settings.production')
django.setup()

from django.contrib.auth.models import User, Group
from django.utils import timezone
from core.models import *
from students.models import Student
from academics.models import *
from fees.models import *
from examinations.models import *
from library.models import *
from transport.models import *
from hostel.models import *
from hr.models import *
from inventory.models import *

def create_sample_data():
    """Create comprehensive sample data for all modules"""
    print(" STARTING COMPREHENSIVE DATA POPULATION...")
    
    # 1. Create School Settings
    print(" Creating school settings...")
    school_settings, created = SchoolSettings.objects.get_or_create(
        defaults={
            'name': 'Modern International School',
            'address': '123 Education Avenue',
            'city': 'Knowledge City',
            'state': 'Education State',
            'postal_code': '12345',
            'phone': '+1-555-0123',
            'email': 'admin@modernschool.edu',
            'principal_name': 'Dr. Sarah Johnson',
            'principal_email': 'principal@modernschool.edu',
            'principal_phone': '+1-555-0124',
            'established_date': timezone.now().date() - timedelta(days=3650),
            'board_affiliation': 'CBSE'
        }
    )
    
    # 2. Create Academic Year
    print(" Creating academic year...")
    academic_year, created = AcademicYear.objects.get_or_create(
        name='2024-25',
        defaults={
            'start_date': datetime(2024, 4, 1).date(),
            'end_date': datetime(2025, 3, 31).date(),
            'is_current': True,
            'is_active': True
        }
    )
    
    # 3. Create Campus and Infrastructure
    print(" Creating campus infrastructure...")
    campus, created = Campus.objects.get_or_create(
        name='Main Campus',
        defaults={
            'address': '123 Education Avenue',
            'city': 'Knowledge City',
            'state': 'Education State',
            'postal_code': '12345',
            'phone': '+1-555-0123',
            'is_active': True
        }
    )
    
    # 4. Create Departments
    print(" Creating departments...")
    departments = [
        'Mathematics', 'Science', 'English', 'Social Studies', 'Physical Education',
        'Arts', 'Computer Science', 'Languages', 'Commerce', 'Administration'
    ]
    
    for dept_name in departments:
        Department.objects.get_or_create(
            name=dept_name,
            defaults={
                'campus': campus,
                'head_name': f'Dr. {dept_name} Head',
                'phone': f'+1-555-{random.randint(1000, 9999)}',
                'email': f'{dept_name.lower().replace(" ", "")}@modernschool.edu',
                'is_active': True
            }
        )
    
    # 5. Create Grades
    print(" Creating grades...")
    grades_data = [
        ('Nursery', 1, 'A'), ('LKG', 2, 'A'), ('UKG', 3, 'A'),
        ('Class 1', 4, 'A'), ('Class 1', 4, 'B'),
        ('Class 2', 5, 'A'), ('Class 2', 5, 'B'),
        ('Class 3', 6, 'A'), ('Class 3', 6, 'B'),
        ('Class 4', 7, 'A'), ('Class 4', 7, 'B'),
        ('Class 5', 8, 'A'), ('Class 5', 8, 'B'),
        ('Class 6', 9, 'A'), ('Class 6', 9, 'B'),
        ('Class 7', 10, 'A'), ('Class 7', 10, 'B'),
        ('Class 8', 11, 'A'), ('Class 8', 11, 'B'),
        ('Class 9', 12, 'A'), ('Class 9', 12, 'B'),
        ('Class 10', 13, 'A'), ('Class 10', 13, 'B'),
        ('Class 11 Science', 14, 'A'), ('Class 11 Science', 14, 'B'),
        ('Class 11 Commerce', 14, 'C'), ('Class 12 Science', 15, 'A'),
        ('Class 12 Science', 15, 'B'), ('Class 12 Commerce', 15, 'C')
    ]
    
    for grade_name, numeric_value, section in grades_data:
        Grade.objects.get_or_create(
            name=grade_name,
            section=section,
            academic_year=academic_year,
            defaults={
                'numeric_value': numeric_value,
                'capacity': random.randint(25, 40),
                'class_teacher': f'Teacher {grade_name} {section}',
                'is_active': True
            }
        )
    
    # 6. Create Subjects
    print(" Creating subjects...")
    subjects_data = [
        ('Mathematics', 'MATH', 'Mathematics'),
        ('Physics', 'PHY', 'Science'),
        ('Chemistry', 'CHEM', 'Science'),
        ('Biology', 'BIO', 'Science'),
        ('English', 'ENG', 'English'),
        ('Hindi', 'HIN', 'Languages'),
        ('History', 'HIST', 'Social Studies'),
        ('Geography', 'GEO', 'Social Studies'),
        ('Computer Science', 'CS', 'Computer Science'),
        ('Physical Education', 'PE', 'Physical Education'),
        ('Art', 'ART', 'Arts'),
        ('Economics', 'ECO', 'Commerce'),
        ('Accountancy', 'ACC', 'Commerce'),
        ('Business Studies', 'BS', 'Commerce')
    ]
    
    for subject_name, code, dept_name in subjects_data:
        department = Department.objects.get(name=dept_name)
        Subject.objects.get_or_create(
            name=subject_name,
            code=code,
            department=department,
            defaults={
                'credits': random.randint(2, 6),
                'theory_hours': random.randint(3, 5),
                'practical_hours': random.randint(0, 2),
                'description': f'{subject_name} curriculum for academic excellence',
                'is_active': True
            }
        )
    
    # 7. Create Teachers
    print(" Creating teachers...")
    teacher_names = [
        'John Smith', 'Mary Johnson', 'David Brown', 'Sarah Davis', 'Michael Wilson',
        'Emily Taylor', 'James Anderson', 'Lisa Garcia', 'Robert Martinez', 'Jennifer Rodriguez',
        'William Lopez', 'Amanda Gonzalez', 'Christopher Hernandez', 'Jessica Moore', 'Daniel Jackson'
    ]
    
    for i, name in enumerate(teacher_names, 1):
        first_name, last_name = name.split()
        username = f'teacher{i:02d}'
        
        # Create user account
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'email': f'{first_name.lower()}.{last_name.lower()}@modernschool.edu',
                'is_staff': False,
                'is_active': True
            }
        )
        if created:
            user.set_password('teacher123')
            user.save()
        
        # Create teacher profile
        Teacher.objects.get_or_create(
            user=user,
            defaults={
                'employee_id': f'TCH{i:03d}',
                'phone': f'+1-555-{random.randint(1000, 9999)}',
                'address': f'{random.randint(100, 999)} Teacher Street',
                'qualification': random.choice(['B.Ed', 'M.Ed', 'Ph.D']),
                'experience_years': random.randint(1, 20),
                'join_date': timezone.now().date() - timedelta(days=random.randint(30, 1000)),
                'is_active': True
            }
        )
    
    # 8. Create Students
    print(" Creating students...")
    grades = Grade.objects.all()
    
    for i in range(1, 1018):  # Create 1017 students
        grade = random.choice(grades)
        username = f'student{i:04d}'
        
        # Create user account
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'first_name': f'Student{i}',
                'last_name': f'Lastname{i}',
                'email': f'student{i}@modernschool.edu',
                'is_staff': False,
                'is_active': True
            }
        )
        if created:
            user.set_password('student123')
            user.save()
        
        # Create student profile
        Student.objects.get_or_create(
            user=user,
            defaults={
                'student_id': f'STU{i:04d}',
                'grade': grade,
                'phone': f'+1-555-{random.randint(1000, 9999)}',
                'address': f'{random.randint(100, 999)} Student Street',
                'parent_name': f'Parent {i}',
                'parent_phone': f'+1-555-{random.randint(1000, 9999)}',
                'parent_email': f'parent{i}@email.com',
                'admission_date': timezone.now().date() - timedelta(days=random.randint(30, 365)),
                'is_active': True
            }
        )
    
    # 9. Create Fee Categories and Payments
    print(" Creating fee structure...")
    fee_categories = [
        ('Tuition Fee', 5000), ('Library Fee', 500), ('Laboratory Fee', 1000),
        ('Sports Fee', 300), ('Transport Fee', 800), ('Exam Fee', 200)
    ]
    
    for category_name, amount in fee_categories:
        FeeCategory.objects.get_or_create(
            name=category_name,
            defaults={
                'description': f'{category_name} for academic year',
                'amount': Decimal(str(amount)),
                'is_active': True
            }
        )
    
    # Create fee payments
    students = Student.objects.all()[:100]  # Sample payments for first 100 students
    categories = FeeCategory.objects.all()
    
    for student in students:
        for category in categories:
            for month in range(1, 13):  # 12 months
                if random.choice([True, False, True]):  # 66% chance of payment
                    FeePayment.objects.get_or_create(
                        student=student,
                        fee_category=category,
                        academic_year=academic_year,
                        month=month,
                        defaults={
                            'amount_due': category.amount,
                            'amount_paid': category.amount,
                            'payment_date': timezone.now().date() - timedelta(days=random.randint(1, 300)),
                            'payment_method': random.choice(['CASH', 'CARD', 'ONLINE', 'CHEQUE']),
                            'status': 'PAID',
                            'receipt_number': f'RCP{random.randint(10000, 99999)}'
                        }
                    )
    
    # 10. Create Exam Results
    print(" Creating exam results...")
    exams_data = [
        'First Term', 'Second Term', 'Final Exam', 'Mid Term', 'Unit Test 1', 'Unit Test 2'
    ]
    
    for exam_name in exams_data:
        exam, created = Exam.objects.get_or_create(
            name=exam_name,
            academic_year=academic_year,
            defaults={
                'start_date': timezone.now().date() - timedelta(days=random.randint(30, 200)),
                'end_date': timezone.now().date() - timedelta(days=random.randint(20, 190)),
                'total_marks': 100,
                'passing_marks': 35,
                'is_active': True
            }
        )
        
        # Create exam results for students
        students_sample = Student.objects.all()[:200]  # Results for first 200 students
        subjects_sample = Subject.objects.all()[:5]  # 5 subjects per exam
        
        for student in students_sample:
            for subject in subjects_sample:
                ExamResult.objects.get_or_create(
                    exam=exam,
                    student=student,
                    subject=subject,
                    defaults={
                        'marks_obtained': random.randint(25, 95),
                        'total_marks': 100,
                        'grade': random.choice(['A+', 'A', 'B+', 'B', 'C+', 'C', 'D']),
                        'remarks': random.choice(['Excellent', 'Good', 'Average', 'Needs Improvement'])
                    }
                )
    
    # 11. Create Attendance Records
    print(" Creating attendance records...")
    students_sample = Student.objects.all()[:100]  # Attendance for first 100 students
    
    for student in students_sample:
        for i in range(200):  # 200 attendance records per student
            date = timezone.now().date() - timedelta(days=i)
            if date.weekday() < 5:  # Only weekdays
                Attendance.objects.get_or_create(
                    student=student,
                    date=date,
                    defaults={
                        'status': random.choice(['PRESENT', 'ABSENT', 'LATE']) if random.random() > 0.1 else 'PRESENT',
                        'remarks': random.choice(['', 'Sick', 'Family function', 'Late arrival']) if random.random() > 0.8 else ''
                    }
                )
    
    print(" DATA POPULATION COMPLETED!")
    
    # Print statistics
    print("\n FINAL DATABASE STATISTICS:")
    print(f"   Users: {User.objects.count()}")
    print(f"   Students: {Student.objects.count()}")
    print(f"   Teachers: {Teacher.objects.count()}")
    print(f"   Grades: {Grade.objects.count()}")
    print(f"   Subjects: {Subject.objects.count()}")
    print(f"   Fee Payments: {FeePayment.objects.count()}")
    print(f"   Exam Results: {ExamResult.objects.count()}")
    print(f"   Attendance Records: {Attendance.objects.count()}")
    print(f"   Departments: {Department.objects.count()}")
    print(f"   Campuses: {Campus.objects.count()}")

if __name__ == "__main__":
    try:
        create_sample_data()
        print("\n SUCCESS: Sample data created successfully!")
    except Exception as e:
        print(f"\n ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
