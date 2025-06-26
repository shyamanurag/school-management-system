#!/usr/bin/env python
"""
School Management System Data Population Script
This script creates comprehensive mock data for demonstration purposes.
"""

import os
import sys
import django
from datetime import date, datetime, timedelta
from decimal import Decimal
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_modernized.settings.production')
django.setup()

from django.contrib.auth.models import User
from core.models import *

# Global counter for unique admission numbers
admission_counter = 1

def clear_existing_data():
    """Clear existing data (except superuser)"""
    print("Clearing existing data...")
    
    # Clear in reverse dependency order
    ExamResult.objects.all().delete()
    Attendance.objects.all().delete()
    FeePayment.objects.all().delete()
    FeeStructure.objects.all().delete()
    Student.objects.all().delete()
    Teacher.objects.all().delete()
    Subject.objects.all().delete()
    Grade.objects.all().delete()
    Exam.objects.all().delete()
    FeeCategory.objects.all().delete()
    Room.objects.all().delete()
    Building.objects.all().delete()
    Campus.objects.all().delete()
    Department.objects.all().delete()
    AcademicYear.objects.all().delete()
    SystemConfiguration.objects.all().delete()
    SchoolSettings.objects.all().delete()
    
    # Keep superuser, delete other users
    User.objects.filter(is_superuser=False).delete()
    
    print("✓ Existing data cleared")

def create_school_settings():
    """Create school settings"""
    print("Creating school settings...")
    
    school = SchoolSettings.objects.create(
        name="Greenwood International School",
        address="123 Education Lane, Knowledge Park",
        city="Mumbai",
        state="Maharashtra",
        postal_code="400001",
        country="India",
        phone="+91-22-12345678",
        email="info@greenwoodschool.edu.in",
        website="https://www.greenwoodschool.edu.in",
        principal_name="Dr. Rajesh Kumar",
        principal_email="principal@greenwoodschool.edu.in",
        principal_phone="+91-22-12345679",
        established_date=date(1995, 6, 15),
        board_affiliation="CBSE",
        academic_year_start_month=4
    )
    
    print(f"✓ Created school: {school.name}")
    return school

def create_academic_years():
    """Create academic years"""
    print("Creating academic years...")
    
    years = []
    current_year = datetime.now().year
    
    for i in range(-2, 3):  # Create 5 years: 2 past, current, 2 future
        start_year = current_year + i
        end_year = start_year + 1
        
        year = AcademicYear.objects.create(
            name=f"{start_year}-{str(end_year)[2:]}",
            start_date=date(start_year, 4, 1),
            end_date=date(end_year, 3, 31),
            is_current=(i == 0),
            is_active=True
        )
        years.append(year)
    
    print(f"✓ Created {len(years)} academic years")
    return years

def create_campuses():
    """Create campuses"""
    print("Creating campuses...")
    
    campuses = [
        {
            'name': 'Main Campus',
            'code': 'MAIN',
            'address': '123 Education Lane, Knowledge Park',
            'city': 'Mumbai',
            'principal_name': 'Dr. Rajesh Kumar',
            'is_main_campus': True
        },
        {
            'name': 'Junior Campus',
            'code': 'JR',
            'address': '456 Learning Street, Study Zone',
            'city': 'Mumbai',
            'principal_name': 'Mrs. Priya Sharma',
            'is_main_campus': False
        }
    ]
    
    created_campuses = []
    for campus_data in campuses:
        campus = Campus.objects.create(
            name=campus_data['name'],
            code=campus_data['code'],
            address=campus_data['address'],
            city=campus_data['city'],
            phone=f"+91-22-{random.randint(10000000, 99999999)}",
            email=f"{campus_data['code'].lower()}@greenwoodschool.edu.in",
            principal_name=campus_data['principal_name'],
            is_main_campus=campus_data['is_main_campus'],
            is_active=True
        )
        created_campuses.append(campus)
    
    print(f"✓ Created {len(created_campuses)} campuses")
    return created_campuses

def create_departments():
    """Create academic departments"""
    print("Creating departments...")
    
    departments_data = [
        {'name': 'Mathematics', 'code': 'MATH'},
        {'name': 'Science', 'code': 'SCI'},
        {'name': 'English', 'code': 'ENG'},
        {'name': 'Social Studies', 'code': 'SS'},
        {'name': 'Hindi', 'code': 'HIN'},
        {'name': 'Computer Science', 'code': 'CS'},
        {'name': 'Physical Education', 'code': 'PE'},
        {'name': 'Arts & Crafts', 'code': 'ART'},
        {'name': 'Music', 'code': 'MUS'},
        {'name': 'Administration', 'code': 'ADM'}
    ]
    
    departments = []
    for dept_data in departments_data:
        dept = Department.objects.create(
            name=dept_data['name'],
            code=dept_data['code'],
            description=f"Department of {dept_data['name']}",
            budget_allocation=Decimal(random.randint(50000, 200000)),
            is_active=True
        )
        departments.append(dept)
    
    print(f"✓ Created {len(departments)} departments")
    return departments

def create_buildings_and_rooms(campuses):
    """Create buildings and rooms"""
    print("Creating buildings and rooms...")
    
    buildings = []
    rooms = []
    
    for campus in campuses:
        # Create 2-3 buildings per campus
        building_count = 3 if campus.is_main_campus else 2
        
        for i in range(building_count):
            building = Building.objects.create(
                campus=campus,
                name=f"Block {chr(65+i)}",  # Block A, Block B, etc.
                code=f"BLK{chr(65+i)}",
                floors=random.randint(2, 4),
                description=f"Academic Block {chr(65+i)} - {campus.name}",
                is_active=True
            )
            buildings.append(building)
            
            # Create rooms in each building
            rooms_per_floor = 8
            for floor in range(1, building.floors + 1):
                for room_num in range(1, rooms_per_floor + 1):
                    room_number = f"{floor}{room_num:02d}"
                    
                    # Assign room types based on room number
                    if room_num <= 6:
                        room_type = 'CLASSROOM'
                        name = f"Classroom {room_number}"
                    elif room_num == 7:
                        room_type = 'LAB'
                        name = f"Laboratory {room_number}"
                    else:
                        room_type = 'OFFICE'
                        name = f"Staff Room {room_number}"
                    
                    room = Room.objects.create(
                        building=building,
                        room_number=room_number,
                        name=name,
                        room_type=room_type,
                        floor=floor,
                        capacity=random.randint(25, 45) if room_type == 'CLASSROOM' else random.randint(15, 30),
                        area_sqft=random.randint(400, 800),
                        has_projector=random.choice([True, False]),
                        has_smartboard=random.choice([True, False]),
                        has_ac=random.choice([True, False]),
                        is_active=True
                    )
                    rooms.append(room)
    
    print(f"✓ Created {len(buildings)} buildings and {len(rooms)} rooms")
    return buildings, rooms

def create_subjects(departments):
    """Create subjects"""
    print("Creating subjects...")
    
    subjects_data = {
        'Mathematics': [
            {'name': 'Algebra', 'code': 'MATH101', 'credits': 4},
            {'name': 'Geometry', 'code': 'MATH102', 'credits': 4},
            {'name': 'Calculus', 'code': 'MATH201', 'credits': 5},
            {'name': 'Statistics', 'code': 'MATH202', 'credits': 3}
        ],
        'Science': [
            {'name': 'Physics', 'code': 'SCI101', 'credits': 4, 'practical': True},
            {'name': 'Chemistry', 'code': 'SCI102', 'credits': 4, 'practical': True},
            {'name': 'Biology', 'code': 'SCI103', 'credits': 4, 'practical': True},
            {'name': 'Environmental Science', 'code': 'SCI201', 'credits': 3}
        ],
        'English': [
            {'name': 'English Literature', 'code': 'ENG101', 'credits': 4},
            {'name': 'English Grammar', 'code': 'ENG102', 'credits': 3},
            {'name': 'Creative Writing', 'code': 'ENG201', 'credits': 3}
        ],
        'Social Studies': [
            {'name': 'History', 'code': 'SS101', 'credits': 3},
            {'name': 'Geography', 'code': 'SS102', 'credits': 3},
            {'name': 'Civics', 'code': 'SS103', 'credits': 2},
            {'name': 'Economics', 'code': 'SS201', 'credits': 4}
        ],
        'Hindi': [
            {'name': 'Hindi Literature', 'code': 'HIN101', 'credits': 3},
            {'name': 'Hindi Grammar', 'code': 'HIN102', 'credits': 2}
        ],
        'Computer Science': [
            {'name': 'Programming Basics', 'code': 'CS101', 'credits': 4, 'practical': True},
            {'name': 'Web Development', 'code': 'CS201', 'credits': 5, 'practical': True},
            {'name': 'Database Management', 'code': 'CS202', 'credits': 4, 'practical': True}
        ],
        'Physical Education': [
            {'name': 'Physical Training', 'code': 'PE101', 'credits': 2, 'practical': True},
            {'name': 'Sports', 'code': 'PE102', 'credits': 2, 'practical': True}
        ],
        'Arts & Crafts': [
            {'name': 'Drawing', 'code': 'ART101', 'credits': 2, 'practical': True},
            {'name': 'Painting', 'code': 'ART102', 'credits': 2, 'practical': True}
        ],
        'Music': [
            {'name': 'Vocal Music', 'code': 'MUS101', 'credits': 2, 'practical': True},
            {'name': 'Instrumental Music', 'code': 'MUS102', 'credits': 2, 'practical': True}
        ]
    }
    
    subjects = []
    dept_dict = {dept.name: dept for dept in departments}
    
    for dept_name, subject_list in subjects_data.items():
        if dept_name in dept_dict:
            for subject_data in subject_list:
                subject = Subject.objects.create(
                    name=subject_data['name'],
                    code=subject_data['code'],
                    department=dept_dict[dept_name],
                    description=f"{subject_data['name']} - {dept_name} Department",
                    credit_hours=subject_data['credits'],
                    is_practical=subject_data.get('practical', False),
                    is_active=True
                )
                subjects.append(subject)
    
    print(f"✓ Created {len(subjects)} subjects")
    return subjects

def create_users_and_teachers(departments, subjects):
    """Create teacher users and profiles"""
    print("Creating teachers...")
    
    teacher_names = [
        ('Mr.', 'Amit', 'Sharma', 'Mathematics'),
        ('Mrs.', 'Priya', 'Patel', 'Science'),
        ('Ms.', 'Sunita', 'Singh', 'English'),
        ('Mr.', 'Rajesh', 'Kumar', 'Social Studies'),
        ('Mrs.', 'Meera', 'Gupta', 'Hindi'),
        ('Mr.', 'Vikash', 'Jain', 'Computer Science'),
        ('Mr.', 'Suresh', 'Yadav', 'Physical Education'),
        ('Ms.', 'Kavita', 'Mishra', 'Arts & Crafts'),
        ('Mrs.', 'Geeta', 'Verma', 'Music'),
        ('Mr.', 'Anil', 'Agarwal', 'Mathematics'),
        ('Ms.', 'Pooja', 'Sinha', 'Science'),
        ('Mr.', 'Manoj', 'Tiwari', 'English'),
        ('Mrs.', 'Sushma', 'Pandey', 'Social Studies'),
        ('Mr.', 'Deepak', 'Joshi', 'Computer Science'),
        ('Ms.', 'Rekha', 'Saxena', 'Hindi')
    ]
    
    teachers = []
    dept_dict = {dept.name: dept for dept in departments}
    
    for i, (title, first_name, last_name, dept_name) in enumerate(teacher_names):
        # Create user
        username = f"teacher{i+1:02d}"
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=f"{username}@greenwoodschool.edu.in",
            password="teacher123"
        )
        
        # Create teacher profile
        teacher = Teacher.objects.create(
            user=user,
            employee_id=f"EMP{2024000 + i + 1}",
            phone=f"+91-{random.randint(7000000000, 9999999999)}",
            address=f"{random.randint(1, 999)} Teacher Colony, Mumbai",
            date_of_birth=date(random.randint(1975, 1990), random.randint(1, 12), random.randint(1, 28)),
            date_of_joining=date(random.randint(2015, 2023), random.randint(1, 12), random.randint(1, 28)),
            qualification=random.choice(['B.Ed, M.A.', 'M.Ed, M.Sc.', 'B.Ed, B.A.', 'M.Ed, M.A.']),
            experience_years=random.randint(2, 15),
            department=dept_dict.get(dept_name),
            salary=Decimal(random.randint(35000, 80000)),
            is_active=True
        )
        
        # Assign subjects to teacher
        dept_subjects = [s for s in subjects if s.department.name == dept_name]
        if dept_subjects:
            # Assign 1-3 subjects per teacher
            assigned_subjects = random.sample(dept_subjects, min(len(dept_subjects), random.randint(1, 3)))
            teacher.subjects.set(assigned_subjects)
        
        teachers.append(teacher)
    
    print(f"✓ Created {len(teachers)} teachers")
    return teachers

def create_grades_and_students(academic_years, rooms, teachers):
    """Create grades and students"""
    print("Creating grades and students...")
    
    global admission_counter
    current_year = [year for year in academic_years if year.is_current][0]
    
    # Create grades (classes)
    grades_data = [
        {'name': 'Nursery', 'numeric': 0},
        {'name': 'LKG', 'numeric': 1},
        {'name': 'UKG', 'numeric': 2},
        {'name': 'Class I', 'numeric': 3},
        {'name': 'Class II', 'numeric': 4},
        {'name': 'Class III', 'numeric': 5},
        {'name': 'Class IV', 'numeric': 6},
        {'name': 'Class V', 'numeric': 7},
        {'name': 'Class VI', 'numeric': 8},
        {'name': 'Class VII', 'numeric': 9},
        {'name': 'Class VIII', 'numeric': 10},
        {'name': 'Class IX', 'numeric': 11},
        {'name': 'Class X', 'numeric': 12}
    ]
    
    grades = []
    students = []
    
    # Get classroom rooms
    classroom_rooms = [room for room in rooms if room.room_type == 'CLASSROOM']
    
    for grade_data in grades_data:
        # Create 2-3 sections per grade
        sections = ['A', 'B', 'C'] if grade_data['numeric'] >= 8 else ['A', 'B']
        
        for section in sections:
            # Assign a room and class teacher
            room = random.choice(classroom_rooms) if classroom_rooms else None
            class_teacher = random.choice(teachers).user if teachers else None
            
            grade = Grade.objects.create(
                name=grade_data['name'],
                numeric_value=grade_data['numeric'],
                section=section,
                academic_year=current_year,
                class_teacher=class_teacher,
                room=room,
                max_students=random.randint(35, 45),
                is_active=True
            )
            grades.append(grade)
            
            # Create students for this grade
            student_count = random.randint(25, 40)
            
            # Indian first names
            first_names_boys = ['Aarav', 'Arjun', 'Aditya', 'Ansh', 'Dev', 'Dhruv', 'Ishaan', 'Kabir', 'Karan', 'Krish', 'Laksh', 'Manav', 'Naman', 'Om', 'Pranav', 'Reyansh', 'Rudra', 'Saanvi', 'Shivansh', 'Vihaan']
            first_names_girls = ['Aadhya', 'Ananya', 'Anika', 'Avni', 'Diya', 'Ishika', 'Jiya', 'Kavya', 'Kiara', 'Myra', 'Navya', 'Pari', 'Prisha', 'Riya', 'Saanvi', 'Sara', 'Shanaya', 'Siya', 'Tara', 'Zara']
            last_names = ['Sharma', 'Patel', 'Singh', 'Kumar', 'Gupta', 'Jain', 'Agarwal', 'Verma', 'Yadav', 'Mishra', 'Sinha', 'Pandey', 'Tiwari', 'Joshi', 'Saxena', 'Malhotra', 'Chopra', 'Bansal', 'Goel', 'Mittal']
            
            for i in range(student_count):
                gender = random.choice(['M', 'F'])
                first_name = random.choice(first_names_boys if gender == 'M' else first_names_girls)
                last_name = random.choice(last_names)
                
                # Generate unique admission number using global counter
                admission_year = random.randint(current_year.start_date.year - grade_data['numeric'], current_year.start_date.year)
                admission_number = f"GWS{admission_year}{admission_counter:06d}"
                admission_counter += 1
                
                student = Student.objects.create(
                    admission_number=admission_number,
                    roll_number=f"{i+1:02d}",
                    first_name=first_name,
                    last_name=last_name,
                    date_of_birth=date(
                        current_year.start_date.year - grade_data['numeric'] - 5,
                        random.randint(1, 12),
                        random.randint(1, 28)
                    ),
                    gender=gender,
                    phone=f"+91-{random.randint(7000000000, 9999999999)}" if random.choice([True, False]) else None,
                    email=f"{first_name.lower()}.{last_name.lower()}@student.greenwoodschool.edu.in" if random.choice([True, False]) else None,
                    address=f"{random.randint(1, 999)} {random.choice(['Park Street', 'Main Road', 'Gandhi Nagar', 'Nehru Colony'])}, Mumbai",
                    grade=grade,
                    admission_date=date(admission_year, random.randint(4, 6), random.randint(1, 30)),
                    parent_name=f"{random.choice(['Mr.', 'Mrs.'])} {random.choice(last_names)} {last_name}",
                    parent_phone=f"+91-{random.randint(7000000000, 9999999999)}",
                    parent_email=f"parent.{first_name.lower()}{admission_counter}@gmail.com" if random.choice([True, False]) else None,
                    emergency_contact=f"+91-{random.randint(7000000000, 9999999999)}",
                    is_active=True
                )
                students.append(student)
    
    print(f"✓ Created {len(grades)} grades and {len(students)} students")
    return grades, students

def create_fee_categories_and_structures(grades, academic_years):
    """Create fee categories and structures"""
    print("Creating fee categories and structures...")
    
    # Create fee categories
    fee_categories_data = [
        {'name': 'Tuition Fee', 'description': 'Monthly tuition fee'},
        {'name': 'Admission Fee', 'description': 'One-time admission fee'},
        {'name': 'Development Fee', 'description': 'Annual development fee'},
        {'name': 'Lab Fee', 'description': 'Laboratory usage fee'},
        {'name': 'Library Fee', 'description': 'Library access fee'},
        {'name': 'Sports Fee', 'description': 'Sports activities fee'},
        {'name': 'Transport Fee', 'description': 'School bus transportation fee'},
        {'name': 'Exam Fee', 'description': 'Examination fee'}
    ]
    
    fee_categories = []
    for cat_data in fee_categories_data:
        category = FeeCategory.objects.create(
            name=cat_data['name'],
            description=cat_data['description'],
            is_active=True
        )
        fee_categories.append(category)
    
    # Create fee structures
    current_year = [year for year in academic_years if year.is_current][0]
    fee_structures = []
    
    for grade in grades:
        for category in fee_categories:
            # Set different fee amounts based on grade and category
            base_amount = 1000 + (grade.numeric_value * 200)  # Higher grades pay more
            
            if category.name == 'Tuition Fee':
                amount = base_amount
                due_date = date(current_year.start_date.year, 4, 10)  # April 10
            elif category.name == 'Admission Fee':
                amount = 5000 + (grade.numeric_value * 500)
                due_date = date(current_year.start_date.year, 4, 1)  # April 1
            elif category.name == 'Development Fee':
                amount = 2000 + (grade.numeric_value * 200)
                due_date = date(current_year.start_date.year, 4, 15)  # April 15
            elif category.name == 'Lab Fee':
                amount = 500 + (grade.numeric_value * 100) if grade.numeric_value >= 8 else 0
                due_date = date(current_year.start_date.year, 5, 1)  # May 1
            elif category.name == 'Library Fee':
                amount = 300 + (grade.numeric_value * 50)
                due_date = date(current_year.start_date.year, 4, 20)  # April 20
            elif category.name == 'Sports Fee':
                amount = 800 + (grade.numeric_value * 100)
                due_date = date(current_year.start_date.year, 5, 15)  # May 15
            elif category.name == 'Transport Fee':
                amount = 1500 + (grade.numeric_value * 100)
                due_date = date(current_year.start_date.year, 4, 5)  # April 5
            else:  # Exam Fee
                amount = 200 + (grade.numeric_value * 50)
                due_date = date(current_year.start_date.year, 6, 1)  # June 1
            
            if amount > 0:  # Only create if amount is positive
                structure = FeeStructure.objects.create(
                    grade=grade,
                    category=category,
                    amount=Decimal(amount),
                    academic_year=current_year,
                    due_date=due_date,
                    is_active=True
                )
                fee_structures.append(structure)
    
    print(f"✓ Created {len(fee_categories)} fee categories and {len(fee_structures)} fee structures")
    return fee_categories, fee_structures

def create_fee_payments(students, fee_structures):
    """Create fee payment records"""
    print("Creating fee payments...")
    
    payments = []
    payment_methods = ['CASH', 'CARD', 'BANK_TRANSFER', 'ONLINE']
    payment_statuses = ['PAID', 'PENDING', 'PARTIAL', 'OVERDUE']
    
    for student in students:
        # Get fee structures for this student's grade
        student_fee_structures = [fs for fs in fee_structures if fs.grade == student.grade]
        
        for fee_structure in student_fee_structures:
            # 80% chance of having a payment record
            if random.random() < 0.8:
                status = random.choices(
                    payment_statuses,
                    weights=[60, 20, 10, 10],  # 60% paid, 20% pending, 10% partial, 10% overdue
                    k=1
                )[0]
                
                amount_due = fee_structure.amount
                
                if status == 'PAID':
                    amount_paid = amount_due
                    payment_date = fee_structure.due_date + timedelta(days=random.randint(-5, 30))
                    method = random.choice(payment_methods)
                    transaction_id = f"TXN{random.randint(100000, 999999)}"
                elif status == 'PARTIAL':
                    amount_paid = amount_due * Decimal(random.uniform(0.3, 0.8))
                    payment_date = fee_structure.due_date + timedelta(days=random.randint(-5, 15))
                    method = random.choice(payment_methods)
                    transaction_id = f"TXN{random.randint(100000, 999999)}"
                else:  # PENDING or OVERDUE
                    amount_paid = Decimal(0)
                    payment_date = None
                    method = None
                    transaction_id = None
                
                payment = FeePayment.objects.create(
                    student=student,
                    fee_structure=fee_structure,
                    amount_due=amount_due,
                    amount_paid=amount_paid,
                    payment_date=payment_date,
                    payment_method=method,
                    transaction_id=transaction_id,
                    status=status,
                    remarks=f"Payment for {fee_structure.category.name}" if status == 'PAID' else None
                )
                payments.append(payment)
    
    print(f"✓ Created {len(payments)} fee payment records")
    return payments

def create_exams_and_results(academic_years, subjects, students):
    """Create exams and results"""
    print("Creating exams and results...")
    
    current_year = [year for year in academic_years if year.is_current][0]
    
    # Create exams
    exams_data = [
        {'name': 'Unit Test 1', 'type': 'UNIT_TEST', 'start_month': 5, 'marks': 25},
        {'name': 'Mid Term Examination', 'type': 'MIDTERM', 'start_month': 7, 'marks': 50},
        {'name': 'Unit Test 2', 'type': 'UNIT_TEST', 'start_month': 9, 'marks': 25},
        {'name': 'Final Examination', 'type': 'FINAL', 'start_month': 12, 'marks': 100},
        {'name': 'Annual Examination', 'type': 'ANNUAL', 'start_month': 2, 'marks': 100}
    ]
    
    exams = []
    for exam_data in exams_data:
        start_month = exam_data['start_month']
        start_year = current_year.start_date.year if start_month >= 4 else current_year.end_date.year
        
        exam = Exam.objects.create(
            name=exam_data['name'],
            exam_type=exam_data['type'],
            academic_year=current_year,
            start_date=date(start_year, start_month, random.randint(1, 15)),
            end_date=date(start_year, start_month, random.randint(16, 28)),
            total_marks=exam_data['marks'],
            passing_marks=int(exam_data['marks'] * 0.35),  # 35% passing
            is_active=True
        )
        exams.append(exam)
    
    # Create exam results
    results = []
    grade_levels = {}  # Cache subjects by grade level
    
    for student in students:
        grade_level = student.grade.numeric_value
        
        # Get subjects for this grade level (simplified logic)
        if grade_level not in grade_levels:
            if grade_level <= 2:  # Nursery to UKG
                grade_subjects = [s for s in subjects if s.name in ['English Literature', 'Hindi Literature', 'Drawing', 'Physical Training']]
            elif grade_level <= 7:  # Class I to V
                grade_subjects = [s for s in subjects if s.name in ['English Literature', 'Hindi Literature', 'Algebra', 'Environmental Science', 'Drawing', 'Physical Training']]
            elif grade_level <= 10:  # Class VI to VIII
                grade_subjects = [s for s in subjects if s.name in ['English Literature', 'Hindi Literature', 'Algebra', 'Physics', 'Chemistry', 'Biology', 'History', 'Geography']]
            else:  # Class IX and X
                grade_subjects = subjects  # All subjects
            
            grade_levels[grade_level] = grade_subjects[:6]  # Limit to 6 subjects max
        
        student_subjects = grade_levels[grade_level]
        
        # Create results for completed exams (first 2-3 exams)
        completed_exams = exams[:random.randint(2, 3)]
        
        for exam in completed_exams:
            for subject in student_subjects:
                # Generate realistic marks
                if student.grade.numeric_value <= 2:  # Very young students
                    marks_percentage = random.uniform(0.7, 0.95)  # 70-95%
                else:
                    marks_percentage = random.uniform(0.4, 0.95)  # 40-95%
                
                marks_obtained = Decimal(exam.total_marks * marks_percentage)
                
                # Assign grade based on percentage
                percentage = marks_percentage * 100
                if percentage >= 90:
                    grade_letter = 'A+'
                elif percentage >= 80:
                    grade_letter = 'A'
                elif percentage >= 70:
                    grade_letter = 'B+'
                elif percentage >= 60:
                    grade_letter = 'B'
                elif percentage >= 50:
                    grade_letter = 'C+'
                elif percentage >= 40:
                    grade_letter = 'C'
                else:
                    grade_letter = 'F'
                
                result = ExamResult.objects.create(
                    student=student,
                    exam=exam,
                    subject=subject,
                    marks_obtained=marks_obtained,
                    total_marks=Decimal(exam.total_marks),
                    grade=grade_letter,
                    remarks="Good performance" if percentage >= 70 else "Needs improvement" if percentage < 50 else ""
                )
                results.append(result)
    
    print(f"✓ Created {len(exams)} exams and {len(results)} exam results")
    return exams, results

def create_attendance_records(students):
    """Create attendance records"""
    print("Creating attendance records...")
    
    attendance_records = []
    current_date = date.today()
    
    # Create attendance for last 30 days (school days only)
    for days_back in range(30):
        check_date = current_date - timedelta(days=days_back)
        
        # Skip weekends
        if check_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
            continue
        
        for student in students:
            # 90% attendance rate
            if random.random() < 0.9:
                status = random.choices(
                    ['PRESENT', 'LATE', 'ABSENT', 'EXCUSED'],
                    weights=[80, 10, 5, 5],
                    k=1
                )[0]
                
                attendance = Attendance.objects.create(
                    student=student,
                    date=check_date,
                    status=status,
                    remarks="Sick leave" if status == 'EXCUSED' else None
                )
                attendance_records.append(attendance)
    
    print(f"✓ Created {len(attendance_records)} attendance records")
    return attendance_records

def create_system_configurations():
    """Create system configuration settings"""
    print("Creating system configurations...")
    
    configs = [
        {'key': 'SCHOOL_SESSION_START_TIME', 'value': '08:00', 'type': 'STRING', 'desc': 'School session start time'},
        {'key': 'SCHOOL_SESSION_END_TIME', 'value': '15:30', 'type': 'STRING', 'desc': 'School session end time'},
        {'key': 'MAX_STUDENTS_PER_CLASS', 'value': '40', 'type': 'INTEGER', 'desc': 'Maximum students per class'},
        {'key': 'LATE_FEE_PERCENTAGE', 'value': '2.5', 'type': 'FLOAT', 'desc': 'Late fee percentage per month'},
        {'key': 'ENABLE_SMS_NOTIFICATIONS', 'value': 'true', 'type': 'BOOLEAN', 'desc': 'Enable SMS notifications'},
        {'key': 'ENABLE_EMAIL_NOTIFICATIONS', 'value': 'true', 'type': 'BOOLEAN', 'desc': 'Enable email notifications'},
        {'key': 'ACADEMIC_YEAR_START_MONTH', 'value': '4', 'type': 'INTEGER', 'desc': 'Academic year start month'},
        {'key': 'MINIMUM_ATTENDANCE_PERCENTAGE', 'value': '75', 'type': 'INTEGER', 'desc': 'Minimum attendance percentage required'},
        {'key': 'GRADING_SYSTEM', 'value': '{"A+": 90, "A": 80, "B+": 70, "B": 60, "C+": 50, "C": 40, "F": 0}', 'type': 'JSON', 'desc': 'Grading system configuration'},
        {'key': 'SCHOOL_WORKING_DAYS', 'value': '["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]', 'type': 'JSON', 'desc': 'School working days'}
    ]
    
    configurations = []
    for config in configs:
        configuration = SystemConfiguration.objects.create(
            key=config['key'],
            value=config['value'],
            data_type=config['type'],
            description=config['desc'],
            is_sensitive=False
        )
        configurations.append(configuration)
    
    print(f"✓ Created {len(configurations)} system configurations")
    return configurations

def main():
    """Main function to populate all data"""
    print("🚀 Starting School Management System Data Population")
    print("=" * 60)
    
    try:
        # Clear existing data
        clear_existing_data()
        
        # Create core data
        school = create_school_settings()
        academic_years = create_academic_years()
        campuses = create_campuses()
        departments = create_departments()
        buildings, rooms = create_buildings_and_rooms(campuses)
        subjects = create_subjects(departments)
        
        # Create users and profiles
        teachers = create_users_and_teachers(departments, subjects)
        grades, students = create_grades_and_students(academic_years, rooms, teachers)
        
        # Create fee management data
        fee_categories, fee_structures = create_fee_categories_and_structures(grades, academic_years)
        fee_payments = create_fee_payments(students, fee_structures)
        
        # Create academic data
        exams, results = create_exams_and_results(academic_years, subjects, students)
        attendance_records = create_attendance_records(students)
        
        # Create system configurations
        configurations = create_system_configurations()
        
        print("\n" + "=" * 60)
        print("✅ DATA POPULATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"📊 Summary:")
        print(f"   • School Settings: 1")
        print(f"   • Academic Years: {len(academic_years)}")
        print(f"   • Campuses: {len(campuses)}")
        print(f"   • Departments: {len(departments)}")
        print(f"   • Buildings: {len(buildings)}")
        print(f"   • Rooms: {len(rooms)}")
        print(f"   • Subjects: {len(subjects)}")
        print(f"   • Teachers: {len(teachers)}")
        print(f"   • Grades: {len(grades)}")
        print(f"   • Students: {len(students)}")
        print(f"   • Fee Categories: {len(fee_categories)}")
        print(f"   • Fee Structures: {len(fee_structures)}")
        print(f"   • Fee Payments: {len(fee_payments)}")
        print(f"   • Exams: {len(exams)}")
        print(f"   • Exam Results: {len(results)}")
        print(f"   • Attendance Records: {len(attendance_records)}")
        print(f"   • System Configurations: {len(configurations)}")
        print("\n🎓 You can now access the admin panel at: http://localhost:8000/admin/")
        print("   Username: schooladmin")
        print("   Password: admin123")
        print("\n🌐 Main dashboard: http://localhost:8000/")
        
    except Exception as e:
        print(f"\n❌ Error during data population: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 