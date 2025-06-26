#!/usr/bin/env python
"""
Production Database Population Script
Run this on the deployed server to populate sample data
Usage: python populate_production_data.py
"""

import os
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_modernized.settings.production')
django.setup()

from core.models import *

class ProductionDataPopulator:
    def __init__(self):
        self.created_counts = {}
        
    def log_creation(self, model_name, count):
        self.created_counts[model_name] = count
        print(f"✅ Created {count} {model_name} records")
    
    def create_academic_years(self):
        """Create academic years"""
        current_year = datetime.now().year
        years_created = 0
        
        for i in range(-1, 3):  # Previous year to next 2 years
            year_start = current_year + i
            year_end = year_start + 1
            year_name = f"{year_start}-{year_end}"
            
            year, created = AcademicYear.objects.get_or_create(
                year=year_name,
                defaults={
                    'start_date': datetime(year_start, 4, 1),
                    'end_date': datetime(year_end, 3, 31),
                    'is_current': (i == 0)  # Current year
                }
            )
            if created:
                years_created += 1
        
        self.log_creation('Academic Years', years_created)
        return AcademicYear.objects.filter(is_current=True).first()
    
    def create_campuses(self):
        """Create school campuses"""
        campuses_data = [
            {'name': 'Main Campus', 'address': '123 Education Street, City Center'},
            {'name': 'Secondary Campus', 'address': '456 Learning Avenue, Education District'}
        ]
        
        campuses_created = 0
        for campus_data in campuses_data:
            campus, created = Campus.objects.get_or_create(
                name=campus_data['name'],
                defaults=campus_data
            )
            if created:
                campuses_created += 1
        
        self.log_creation('Campuses', campuses_created)
        return list(Campus.objects.all())
    
    def create_departments(self):
        """Create academic departments"""
        departments_data = [
            'Mathematics', 'Science', 'English', 'Social Studies', 'Computer Science',
            'Physical Education', 'Arts', 'Music', 'Languages', 'Commerce'
        ]
        
        departments_created = 0
        for dept_name in departments_data:
            dept, created = Department.objects.get_or_create(
                name=dept_name,
                defaults={'description': f'{dept_name} Department'}
            )
            if created:
                departments_created += 1
        
        self.log_creation('Departments', departments_created)
        return list(Department.objects.all())
    
    def create_subjects(self, departments):
        """Create subjects for each department"""
        subjects_data = {
            'Mathematics': ['Algebra', 'Geometry', 'Calculus', 'Statistics'],
            'Science': ['Physics', 'Chemistry', 'Biology', 'Environmental Science'],
            'English': ['Literature', 'Grammar', 'Creative Writing', 'Public Speaking'],
            'Social Studies': ['History', 'Geography', 'Civics', 'Economics'],
            'Computer Science': ['Programming', 'Database', 'Web Development', 'Networking'],
            'Physical Education': ['Sports', 'Fitness', 'Health Education'],
            'Arts': ['Drawing', 'Painting', 'Crafts', 'Design'],
            'Music': ['Vocal', 'Instrumental', 'Music Theory'],
            'Languages': ['Hindi', 'Sanskrit', 'French', 'Spanish'],
            'Commerce': ['Accounting', 'Business Studies', 'Entrepreneurship']
        }
        
        subjects_created = 0
        for dept in departments:
            if dept.name in subjects_data:
                for subject_name in subjects_data[dept.name]:
                    subject, created = Subject.objects.get_or_create(
                        name=subject_name,
                        department=dept,
                        defaults={
                            'code': f"{dept.name[:3].upper()}{subject_name[:3].upper()}",
                            'description': f'{subject_name} subject'
                        }
                    )
                    if created:
                        subjects_created += 1
        
        self.log_creation('Subjects', subjects_created)
        return list(Subject.objects.all())
    
    def create_teachers(self, departments, subjects):
        """Create teacher records"""
        teacher_names = [
            'Dr. Rajesh Kumar', 'Prof. Priya Sharma', 'Mr. Amit Singh', 'Ms. Sunita Patel',
            'Dr. Vikram Gupta', 'Mrs. Meera Joshi', 'Mr. Ravi Mehta', 'Ms. Kavita Rao',
            'Prof. Suresh Nair', 'Dr. Anjali Verma', 'Mr. Deepak Agarwal', 'Ms. Pooja Kapoor'
        ]
        
        teachers_created = 0
        for i, name in enumerate(teacher_names):
            dept = random.choice(departments)
            teacher, created = Teacher.objects.get_or_create(
                employee_id=f'EMP{1000 + i}',
                defaults={
                    'full_name': name,
                    'email': f'{name.lower().replace(" ", "").replace(".", "")}@school.edu',
                    'contact_number': f'98765{10000 + i}',
                    'department': dept,
                    'date_of_joining': datetime.now() - timedelta(days=random.randint(30, 1000)),
                    'address': f'{random.randint(100, 999)} Teacher Colony, Education City',
                    'qualification': random.choice(['M.Ed', 'M.A', 'M.Sc', 'Ph.D']),
                    'salary': Decimal(random.randint(25000, 75000))
                }
            )
            
            if created:
                # Assign subjects to teacher
                dept_subjects = [s for s in subjects if s.department == dept]
                if dept_subjects:
                    assigned_subjects = random.sample(dept_subjects, min(2, len(dept_subjects)))
                    teacher.subjects_taught.set(assigned_subjects)
                teachers_created += 1
        
        self.log_creation('Teachers', teachers_created)
        return list(Teacher.objects.all())
    
    def create_grades(self, academic_year, teachers):
        """Create grade/class structure"""
        grade_data = [
            ('Nursery', ['A', 'B']),
            ('LKG', ['A', 'B']),
            ('UKG', ['A', 'B']),
            ('1', ['A', 'B', 'C']),
            ('2', ['A', 'B', 'C']),
            ('3', ['A', 'B', 'C']),
            ('4', ['A', 'B', 'C']),
            ('5', ['A', 'B', 'C']),
            ('6', ['A', 'B', 'C']),
            ('7', ['A', 'B']),
            ('8', ['A', 'B']),
            ('9', ['A', 'B']),
            ('10', ['A', 'B'])
        ]
        
        grades_created = 0
        all_grades = []
        
        for grade_name, sections in grade_data:
            for section in sections:
                teacher = random.choice(teachers) if teachers else None
                grade, created = Grade.objects.get_or_create(
                    name=grade_name,
                    section=section,
                    academic_year=academic_year,
                    defaults={
                        'class_teacher': teacher,
                        'max_students': random.randint(25, 40)
                    }
                )
                if created:
                    grades_created += 1
                all_grades.append(grade)
        
        self.log_creation('Grades', grades_created)
        return all_grades
    
    def create_students(self, grades):
        """Create student records with Indian names"""
        first_names = [
            'Aarav', 'Vivaan', 'Aditya', 'Vihaan', 'Arjun', 'Sai', 'Reyansh', 'Ayaan',
            'Krishna', 'Ishaan', 'Shaurya', 'Atharv', 'Advik', 'Veer', 'Devansh',
            'Ananya', 'Fatima', 'Aadhya', 'Avni', 'Angel', 'Diya', 'Myra', 'Sara',
            'Priya', 'Kavya', 'Riya', 'Aanya', 'Tara', 'Khushi', 'Ira', 'Navya'
        ]
        
        last_names = [
            'Sharma', 'Verma', 'Gupta', 'Kumar', 'Singh', 'Patel', 'Jain', 'Agarwal',
            'Yadav', 'Mishra', 'Tiwari', 'Pandey', 'Shah', 'Joshi', 'Mehta', 'Bansal',
            'Malhotra', 'Chopra', 'Khanna', 'Kapoor', 'Arora', 'Sinha', 'Ghosh', 'Das'
        ]
        
        students_created = 0
        
        for grade in grades:
            # Create 15-35 students per grade
            num_students = random.randint(15, 35)
            
            for i in range(num_students):
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                
                # Generate admission number
                admission_num = f"2024{grade.name.replace('LKG', '0').replace('UKG', '00').replace('Nursery', '000')}{grade.section}{str(i+1).zfill(3)}"
                
                # Check if student already exists
                if Student.objects.filter(admission_number=admission_num).exists():
                    continue
                
                student = Student.objects.create(
                    admission_number=admission_num,
                    first_name=first_name,
                    last_name=last_name,
                    grade=grade,
                    date_of_birth=datetime.now().date() - timedelta(days=random.randint(2000, 4500)),
                    admission_date=datetime.now().date() - timedelta(days=random.randint(30, 365)),
                    gender=random.choice(['Male', 'Female']),
                    parent_contact_number=f'9{random.randint(100000000, 999999999)}',
                    address=f'{random.randint(1, 999)} Student Colony, {random.choice(["Sector", "Block"])} {random.randint(1, 50)}',
                    email=f'{first_name.lower()}.{last_name.lower()}@student.school.edu',
                    blood_group=random.choice(['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'])
                )
                students_created += 1
        
        self.log_creation('Students', students_created)
        return list(Student.objects.all())
    
    def create_fee_structure(self, students):
        """Create fee categories and structures"""
        fee_categories = [
            ('Tuition Fee', 5000),
            ('Books & Stationery', 1200),
            ('Uniform', 800),
            ('Transport', 1500),
            ('Activity Fee', 500),
            ('Exam Fee', 300),
            ('Library Fee', 200),
            ('Computer Fee', 400)
        ]
        
        categories_created = 0
        structures_created = 0
        payments_created = 0
        
        # Create fee categories
        for cat_name, amount in fee_categories:
            category, created = FeeCategory.objects.get_or_create(
                name=cat_name,
                defaults={'amount': Decimal(amount)}
            )
            if created:
                categories_created += 1
        
        # Create fee structures for students
        all_categories = list(FeeCategory.objects.all())
        
        for student in students[:200]:  # Limit to first 200 students
            # Create 3-5 fee structures per student
            selected_categories = random.sample(all_categories, random.randint(3, 5))
            
            for category in selected_categories:
                structure, created = FeeStructure.objects.get_or_create(
                    student=student,
                    category=category,
                    defaults={
                        'amount': category.amount,
                        'due_date': datetime.now().date() + timedelta(days=random.randint(1, 90))
                    }
                )
                if created:
                    structures_created += 1
                
                # Create payment for some structures (70% payment rate)
                if random.random() < 0.7:
                    payment, created = FeePayment.objects.get_or_create(
                        student=student,
                        fee_structure=structure,
                        defaults={
                            'amount_paid': structure.amount,
                            'payment_date': datetime.now().date() - timedelta(days=random.randint(1, 30)),
                            'payment_method': random.choice(['Cash', 'Bank Transfer', 'Online', 'Cheque']),
                            'payment_status': 'Paid',
                            'reference_number': f'TXN{random.randint(100000, 999999)}'
                        }
                    )
                    if created:
                        payments_created += 1
        
        self.log_creation('Fee Categories', categories_created)
        self.log_creation('Fee Structures', structures_created)
        self.log_creation('Fee Payments', payments_created)
    
    def create_system_settings(self):
        """Create basic system settings"""
        settings_data = {
            'school_name': 'Modern International School',
            'school_address': '123 Education Street, Knowledge City - 500001',
            'school_phone': '040-12345678',
            'school_email': 'info@modernschool.edu',
            'academic_year_start_month': '4',  # April
            'default_language': 'English',
            'currency': 'INR',
            'timezone': 'Asia/Kolkata'
        }
        
        settings_created = 0
        for key, value in settings_data.items():
            setting, created = SchoolSettings.objects.get_or_create(
                key=key,
                defaults={'value': value}
            )
            if created:
                settings_created += 1
        
        self.log_creation('School Settings', settings_created)
    
    def populate_all(self):
        """Run the complete population process"""
        print("🚀 Starting Production Database Population...")
        print("=" * 50)
        
        try:
            # Create core data
            academic_year = self.create_academic_years()
            campuses = self.create_campuses()
            departments = self.create_departments()
            subjects = self.create_subjects(departments)
            teachers = self.create_teachers(departments, subjects)
            grades = self.create_grades(academic_year, teachers)
            students = self.create_students(grades)
            
            # Create fee structure
            self.create_fee_structure(students)
            
            # Create system settings
            self.create_system_settings()
            
            print("\n" + "=" * 50)
            print("📊 POPULATION SUMMARY:")
            print("=" * 50)
            
            total_created = sum(self.created_counts.values())
            for model, count in self.created_counts.items():
                print(f"✅ {model}: {count}")
            
            print(f"\n🎉 Total Records Created: {total_created}")
            print("✅ Production database populated successfully!")
            
        except Exception as e:
            print(f"❌ Error during population: {str(e)}")
            raise

if __name__ == "__main__":
    populator = ProductionDataPopulator()
    populator.populate_all() 