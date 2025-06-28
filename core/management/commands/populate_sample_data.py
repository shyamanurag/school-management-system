from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
import random
from decimal import Decimal

from core.models import *
from students.models import Student
from academics.models import *
from fees.models import *

class Command(BaseCommand):
    help = 'Populate database with sample data for school ERP'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(' Starting sample data population...'))
        
        # Create basic data
        self.create_school_settings()
        self.create_academic_year()
        self.create_infrastructure()
        self.create_academic_structure()
        self.create_users_and_profiles()
        self.create_fee_data()
        
        self.stdout.write(self.style.SUCCESS(' Sample data population completed!'))
        self.print_statistics()
    
    def create_school_settings(self):
        self.stdout.write(' Creating school settings...')
        SchoolSettings.objects.get_or_create(
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
    
    def create_academic_year(self):
        self.stdout.write(' Creating academic year...')
        AcademicYear.objects.get_or_create(
            name='2024-25',
            defaults={
                'start_date': datetime(2024, 4, 1).date(),
                'end_date': datetime(2025, 3, 31).date(),
                'is_current': True,
                'is_active': True
            }
        )
    
    def create_infrastructure(self):
        self.stdout.write(' Creating infrastructure...')
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
        
        # Create departments
        departments = [
            'Mathematics', 'Science', 'English', 'Social Studies',
            'Physical Education', 'Arts', 'Computer Science'
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
    
    def create_academic_structure(self):
        self.stdout.write(' Creating academic structure...')
        academic_year = AcademicYear.objects.get(name='2024-25')
        
        # Create grades
        grades_data = [
            ('Class 1', 1, 'A'), ('Class 1', 1, 'B'),
            ('Class 2', 2, 'A'), ('Class 2', 2, 'B'),
            ('Class 3', 3, 'A'), ('Class 3', 3, 'B'),
            ('Class 4', 4, 'A'), ('Class 4', 4, 'B'),
            ('Class 5', 5, 'A'), ('Class 5', 5, 'B'),
            ('Class 6', 6, 'A'), ('Class 6', 6, 'B'),
            ('Class 7', 7, 'A'), ('Class 7', 7, 'B'),
            ('Class 8', 8, 'A'), ('Class 8', 8, 'B'),
            ('Class 9', 9, 'A'), ('Class 9', 9, 'B'),
            ('Class 10', 10, 'A'), ('Class 10', 10, 'B'),
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
        
        # Create subjects
        subjects_data = [
            ('Mathematics', 'MATH', 'Mathematics'),
            ('English', 'ENG', 'English'),
            ('Science', 'SCI', 'Science'),
            ('Social Studies', 'SS', 'Social Studies'),
            ('Physical Education', 'PE', 'Physical Education'),
        ]
        
        for subject_name, code, dept_name in subjects_data:
            try:
                department = Department.objects.get(name=dept_name)
                Subject.objects.get_or_create(
                    name=subject_name,
                    code=code,
                    department=department,
                    defaults={
                        'credits': random.randint(2, 6),
                        'theory_hours': random.randint(3, 5),
                        'practical_hours': random.randint(0, 2),
                        'description': f'{subject_name} curriculum',
                        'is_active': True
                    }
                )
            except Department.DoesNotExist:
                continue
    
    def create_users_and_profiles(self):
        self.stdout.write(' Creating users and profiles...')
        
        # Create teachers
        for i in range(1, 16):
            username = f'teacher{i:02d}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': f'Teacher{i}',
                    'last_name': f'Lastname{i}',
                    'email': f'teacher{i}@modernschool.edu',
                    'is_staff': False,
                    'is_active': True
                }
            )
            if created:
                user.set_password('teacher123')
                user.save()
            
            Teacher.objects.get_or_create(
                user=user,
                defaults={
                    'employee_id': f'TCH{i:03d}',
                    'phone': f'+1-555-{random.randint(1000, 9999)}',
                    'address': f'{random.randint(100, 999)} Teacher Street',
                    'qualification': random.choice(['B.Ed', 'M.Ed']),
                    'experience_years': random.randint(1, 20),
                    'join_date': timezone.now().date() - timedelta(days=random.randint(30, 1000)),
                    'is_active': True
                }
            )
        
        # Create students
        grades = Grade.objects.all()
        for i in range(1, 1018):
            username = f'student{i:04d}'
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
            
            if grades:
                grade = random.choice(grades)
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
    
    def create_fee_data(self):
        self.stdout.write(' Creating fee data...')
        # Create fee categories
        fee_categories = [
            ('Tuition Fee', 5000),
            ('Library Fee', 500),
            ('Sports Fee', 300),
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
        
        # Create some fee payments
        academic_year = AcademicYear.objects.get(name='2024-25')
        students = Student.objects.all()[:100]
        categories = FeeCategory.objects.all()
        
        for student in students:
            for category in categories[:2]:  # First 2 categories only
                if random.choice([True, False]):
                    FeePayment.objects.get_or_create(
                        student=student,
                        fee_category=category,
                        academic_year=academic_year,
                        month=random.randint(1, 12),
                        defaults={
                            'amount_due': category.amount,
                            'amount_paid': category.amount,
                            'payment_date': timezone.now().date() - timedelta(days=random.randint(1, 100)),
                            'payment_method': random.choice(['CASH', 'CARD', 'ONLINE']),
                            'status': 'PAID',
                            'receipt_number': f'RCP{random.randint(10000, 99999)}'
                        }
                    )
    
    def print_statistics(self):
        self.stdout.write('\n DATABASE STATISTICS:')
        self.stdout.write(f'   Total Users: {User.objects.count()}')
        self.stdout.write(f'   Students: {Student.objects.count()}')
        self.stdout.write(f'   Teachers: {Teacher.objects.count()}')
        self.stdout.write(f'   Grades: {Grade.objects.count()}')
        self.stdout.write(f'   Subjects: {Subject.objects.count()}')
        self.stdout.write(f'   Fee Payments: {FeePayment.objects.count()}')
        self.stdout.write(f'   Departments: {Department.objects.count()}')
        self.stdout.write(f'   Campuses: {Campus.objects.count()}')
