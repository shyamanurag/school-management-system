#!/usr/bin/env python
"""
CSV Data Migration Script for School Management System
Supports Excel/CSV exports from common school management systems
"""

import os
import django
import pandas as pd
import numpy as np
from datetime import datetime, date
import re

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_modernized.settings.local')
django.setup()

from core.models import (
    Student, Teacher, Grade, Subject, Department, Campus, Building,
    FeeCategory, FeeStructure, FeePayment, Exam, ExamResult,
    AcademicYear, Attendance
)
from django.contrib.auth.models import User

class CSVMigrator:
    def __init__(self):
        self.migration_log = []
        self.academic_year = self.ensure_academic_year()
        self.default_campus = self.ensure_default_campus()
        
    def log_operation(self, operation, success_count, error_count, errors=None):
        """Log migration operations"""
        log_entry = {
            'operation': operation,
            'timestamp': datetime.now(),
            'success_count': success_count,
            'error_count': error_count,
            'errors': errors or []
        }
        self.migration_log.append(log_entry)
        print(f"✅ {operation}: {success_count} success, {error_count} errors")
        
    def ensure_academic_year(self):
        """Ensure current academic year exists"""
        current_year = datetime.now().year
        year_name = f"{current_year}-{current_year+1}"
        
        year, created = AcademicYear.objects.get_or_create(
            year=year_name,
            defaults={
                'start_date': date(current_year, 4, 1),
                'end_date': date(current_year+1, 3, 31),
                'is_current': True
            }
        )
        if created:
            print(f"📅 Created academic year: {year_name}")
        return year
    
    def ensure_default_campus(self):
        """Ensure default campus exists"""
        campus, created = Campus.objects.get_or_create(
            name="Main Campus",
            defaults={
                'address': "School Address",
                'contact_number': "1234567890",
                'email': "admin@school.edu"
            }
        )
        if created:
            print(f"🏫 Created default campus: {campus.name}")
        return campus
    
    def clean_phone_number(self, phone):
        """Clean and validate phone numbers"""
        if pd.isna(phone):
            return ""
        
        # Remove all non-digits
        phone = re.sub(r'\D', '', str(phone))
        
        # Handle Indian phone numbers
        if len(phone) == 10:
            return phone
        elif len(phone) == 11 and phone.startswith('0'):
            return phone[1:]  # Remove leading 0
        elif len(phone) == 12 and phone.startswith('91'):
            return phone[2:]  # Remove country code
        elif len(phone) == 13 and phone.startswith('+91'):
            return phone[3:]  # Remove +91
        
        return phone[:10] if len(phone) > 10 else phone
    
    def clean_email(self, email):
        """Clean and validate email addresses"""
        if pd.isna(email):
            return ""
        
        email = str(email).strip().lower()
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if re.match(email_pattern, email):
            return email
        return ""
    
    def parse_date(self, date_str):
        """Parse various date formats"""
        if pd.isna(date_str):
            return None
            
        date_str = str(date_str).strip()
        
        # Common date formats
        date_formats = [
            '%Y-%m-%d',      # 2023-01-15
            '%d/%m/%Y',      # 15/01/2023
            '%m/%d/%Y',      # 01/15/2023
            '%d-%m-%Y',      # 15-01-2023
            '%Y/%m/%d',      # 2023/01/15
            '%d %b %Y',      # 15 Jan 2023
            '%d %B %Y',      # 15 January 2023
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        print(f"⚠️ Could not parse date: {date_str}")
        return None
    
    def migrate_departments(self, csv_file):
        """Migrate departments from CSV"""
        print(f"\n📂 Migrating departments from {csv_file}")
        
        try:
            df = pd.read_csv(csv_file)
            success_count = 0
            error_count = 0
            errors = []
            
            # Expected columns: name, description, head_of_department
            for _, row in df.iterrows():
                try:
                    dept, created = Department.objects.get_or_create(
                        name=str(row['name']).strip(),
                        defaults={
                            'description': str(row.get('description', '')),
                            'head_of_department': str(row.get('head_of_department', ''))
                        }
                    )
                    success_count += 1
                    if created:
                        print(f"  ➕ Created department: {dept.name}")
                        
                except Exception as e:
                    error_count += 1
                    error_msg = f"Row {_}: {str(e)}"
                    errors.append(error_msg)
                    print(f"  ❌ {error_msg}")
            
            self.log_operation('Departments', success_count, error_count, errors)
            
        except Exception as e:
            print(f"❌ Error reading {csv_file}: {str(e)}")
    
    def migrate_subjects(self, csv_file):
        """Migrate subjects from CSV"""
        print(f"\n📚 Migrating subjects from {csv_file}")
        
        try:
            df = pd.read_csv(csv_file)
            success_count = 0
            error_count = 0
            errors = []
            
            # Expected columns: name, code, department_name, description
            for _, row in df.iterrows():
                try:
                    # Get department if specified
                    department = None
                    if 'department_name' in row and not pd.isna(row['department_name']):
                        department, _ = Department.objects.get_or_create(
                            name=str(row['department_name']).strip()
                        )
                    
                    subject, created = Subject.objects.get_or_create(
                        name=str(row['name']).strip(),
                        defaults={
                            'code': str(row.get('code', '')),
                            'department': department,
                            'description': str(row.get('description', ''))
                        }
                    )
                    success_count += 1
                    if created:
                        print(f"  ➕ Created subject: {subject.name}")
                        
                except Exception as e:
                    error_count += 1
                    error_msg = f"Row {_}: {str(e)}"
                    errors.append(error_msg)
                    print(f"  ❌ {error_msg}")
            
            self.log_operation('Subjects', success_count, error_count, errors)
            
        except Exception as e:
            print(f"❌ Error reading {csv_file}: {str(e)}")
    
    def migrate_teachers(self, csv_file):
        """Migrate teachers from CSV"""
        print(f"\n👩‍🏫 Migrating teachers from {csv_file}")
        
        try:
            df = pd.read_csv(csv_file)
            success_count = 0
            error_count = 0
            errors = []
            
            # Expected columns: employee_id, full_name, email, phone, department_name, 
            # date_of_joining, address, qualification, subjects_taught (comma-separated)
            for _, row in df.iterrows():
                try:
                    # Get department
                    department = None
                    if 'department_name' in row and not pd.isna(row['department_name']):
                        department, _ = Department.objects.get_or_create(
                            name=str(row['department_name']).strip()
                        )
                    
                    # Clean data
                    email = self.clean_email(row.get('email'))
                    phone = self.clean_phone_number(row.get('phone'))
                    joining_date = self.parse_date(row.get('date_of_joining'))
                    
                    teacher, created = Teacher.objects.get_or_create(
                        employee_id=str(row.get('employee_id', '')),
                        defaults={
                            'full_name': str(row['full_name']).strip(),
                            'email': email,
                            'contact_number': phone,
                            'department': department,
                            'date_of_joining': joining_date,
                            'address': str(row.get('address', '')),
                            'qualification': str(row.get('qualification', ''))
                        }
                    )
                    
                    # Add subjects taught
                    if 'subjects_taught' in row and not pd.isna(row['subjects_taught']):
                        subjects = str(row['subjects_taught']).split(',')
                        for subject_name in subjects:
                            subject_name = subject_name.strip()
                            if subject_name:
                                subject, _ = Subject.objects.get_or_create(name=subject_name)
                                teacher.subjects_taught.add(subject)
                    
                    success_count += 1
                    if created:
                        print(f"  ➕ Created teacher: {teacher.full_name}")
                        
                except Exception as e:
                    error_count += 1
                    error_msg = f"Row {_}: {str(e)}"
                    errors.append(error_msg)
                    print(f"  ❌ {error_msg}")
            
            self.log_operation('Teachers', success_count, error_count, errors)
            
        except Exception as e:
            print(f"❌ Error reading {csv_file}: {str(e)}")
    
    def migrate_grades(self, csv_file):
        """Migrate grades/classes from CSV"""
        print(f"\n🎓 Migrating grades/classes from {csv_file}")
        
        try:
            df = pd.read_csv(csv_file)
            success_count = 0
            error_count = 0
            errors = []
            
            # Expected columns: name, section, class_teacher_id, max_students
            for _, row in df.iterrows():
                try:
                    # Get class teacher
                    class_teacher = None
                    if 'class_teacher_id' in row and not pd.isna(row['class_teacher_id']):
                        try:
                            class_teacher = Teacher.objects.get(
                                employee_id=str(row['class_teacher_id'])
                            )
                        except Teacher.DoesNotExist:
                            pass
                    
                    grade, created = Grade.objects.get_or_create(
                        name=str(row['name']).strip(),
                        section=str(row.get('section', 'A')).strip(),
                        academic_year=self.academic_year,
                        defaults={
                            'class_teacher': class_teacher,
                            'max_students': int(row.get('max_students', 40))
                        }
                    )
                    
                    success_count += 1
                    if created:
                        print(f"  ➕ Created grade: {grade.name}-{grade.section}")
                        
                except Exception as e:
                    error_count += 1
                    error_msg = f"Row {_}: {str(e)}"
                    errors.append(error_msg)
                    print(f"  ❌ {error_msg}")
            
            self.log_operation('Grades', success_count, error_count, errors)
            
        except Exception as e:
            print(f"❌ Error reading {csv_file}: {str(e)}")
    
    def migrate_students(self, csv_file):
        """Migrate students from CSV"""
        print(f"\n👨‍🎓 Migrating students from {csv_file}")
        
        try:
            df = pd.read_csv(csv_file)
            success_count = 0
            error_count = 0
            errors = []
            
            # Expected columns: admission_number, first_name, last_name, date_of_birth,
            # grade_name, section, gender, parent_contact, email, address, admission_date
            for _, row in df.iterrows():
                try:
                    # Get grade
                    grade = None
                    if 'grade_name' in row and not pd.isna(row['grade_name']):
                        grade_name = str(row['grade_name']).strip()
                        section = str(row.get('section', 'A')).strip()
                        
                        try:
                            grade = Grade.objects.get(
                                name=grade_name,
                                section=section,
                                academic_year=self.academic_year
                            )
                        except Grade.DoesNotExist:
                            # Create grade if it doesn't exist
                            grade, _ = Grade.objects.get_or_create(
                                name=grade_name,
                                section=section,
                                academic_year=self.academic_year
                            )
                    
                    # Clean data
                    dob = self.parse_date(row.get('date_of_birth'))
                    admission_date = self.parse_date(row.get('admission_date'))
                    parent_contact = self.clean_phone_number(row.get('parent_contact'))
                    email = self.clean_email(row.get('email'))
                    
                    student, created = Student.objects.get_or_create(
                        admission_number=str(row.get('admission_number', '')),
                        defaults={
                            'first_name': str(row['first_name']).strip().title(),
                            'last_name': str(row.get('last_name', '')).strip().title(),
                            'date_of_birth': dob,
                            'grade': grade,
                            'gender': str(row.get('gender', 'Male')).strip(),
                            'parent_contact_number': parent_contact,
                            'email': email,
                            'address': str(row.get('address', '')),
                            'admission_date': admission_date or datetime.now().date(),
                            'blood_group': str(row.get('blood_group', 'O+')),
                            'is_active': True
                        }
                    )
                    
                    success_count += 1
                    if created:
                        print(f"  ➕ Created student: {student.first_name} {student.last_name}")
                        
                except Exception as e:
                    error_count += 1
                    error_msg = f"Row {_}: {str(e)}"
                    errors.append(error_msg)
                    print(f"  ❌ {error_msg}")
            
            self.log_operation('Students', success_count, error_count, errors)
            
        except Exception as e:
            print(f"❌ Error reading {csv_file}: {str(e)}")
    
    def migrate_fee_payments(self, csv_file):
        """Migrate fee payment records from CSV"""
        print(f"\n💰 Migrating fee payments from {csv_file}")
        
        try:
            df = pd.read_csv(csv_file)
            success_count = 0
            error_count = 0
            errors = []
            
            # Expected columns: admission_number, fee_category, amount, due_date,
            # payment_date, payment_method, status, receipt_number
            for _, row in df.iterrows():
                try:
                    # Get student
                    student = Student.objects.get(
                        admission_number=str(row['admission_number'])
                    )
                    
                    # Get or create fee category
                    fee_category, _ = FeeCategory.objects.get_or_create(
                        name=str(row['fee_category']).strip(),
                        defaults={'amount': float(row.get('amount', 0))}
                    )
                    
                    # Get or create fee structure
                    fee_structure, _ = FeeStructure.objects.get_or_create(
                        student=student,
                        category=fee_category,
                        defaults={
                            'amount': float(row.get('amount', 0)),
                            'due_date': self.parse_date(row.get('due_date'))
                        }
                    )
                    
                    # Create fee payment if payment date exists
                    if 'payment_date' in row and not pd.isna(row['payment_date']):
                        payment_date = self.parse_date(row['payment_date'])
                        if payment_date:
                            payment, created = FeePayment.objects.get_or_create(
                                student=student,
                                fee_structure=fee_structure,
                                payment_date=payment_date,
                                defaults={
                                    'amount_paid': float(row.get('amount', 0)),
                                    'payment_method': str(row.get('payment_method', 'Cash')),
                                    'payment_status': str(row.get('status', 'Paid')),
                                    'receipt_number': str(row.get('receipt_number', ''))
                                }
                            )
                    
                    success_count += 1
                        
                except Exception as e:
                    error_count += 1
                    error_msg = f"Row {_}: {str(e)}"
                    errors.append(error_msg)
                    print(f"  ❌ {error_msg}")
            
            self.log_operation('Fee Payments', success_count, error_count, errors)
            
        except Exception as e:
            print(f"❌ Error reading {csv_file}: {str(e)}")
    
    def migrate_exam_results(self, csv_file):
        """Migrate exam results from CSV"""
        print(f"\n📝 Migrating exam results from {csv_file}")
        
        try:
            df = pd.read_csv(csv_file)
            success_count = 0
            error_count = 0
            errors = []
            
            # Expected columns: admission_number, exam_name, subject_name, 
            # marks_obtained, total_marks, exam_date, grade
            for _, row in df.iterrows():
                try:
                    # Get student
                    student = Student.objects.get(
                        admission_number=str(row['admission_number'])
                    )
                    
                    # Get or create subject
                    subject, _ = Subject.objects.get_or_create(
                        name=str(row['subject_name']).strip()
                    )
                    
                    # Get or create exam
                    exam, _ = Exam.objects.get_or_create(
                        name=str(row['exam_name']).strip(),
                        defaults={
                            'date': self.parse_date(row.get('exam_date')),
                            'total_marks': int(row.get('total_marks', 100))
                        }
                    )
                    
                    # Create exam result
                    result, created = ExamResult.objects.get_or_create(
                        student=student,
                        exam=exam,
                        subject=subject,
                        defaults={
                            'marks_obtained': float(row.get('marks_obtained', 0)),
                            'total_marks': int(row.get('total_marks', 100)),
                            'grade': str(row.get('grade', 'C')),
                            'remarks': str(row.get('remarks', ''))
                        }
                    )
                    
                    success_count += 1
                    if created:
                        print(f"  ➕ Added result: {student.first_name} - {subject.name} - {exam.name}")
                        
                except Exception as e:
                    error_count += 1
                    error_msg = f"Row {_}: {str(e)}"
                    errors.append(error_msg)
                    print(f"  ❌ {error_msg}")
            
            self.log_operation('Exam Results', success_count, error_count, errors)
            
        except Exception as e:
            print(f"❌ Error reading {csv_file}: {str(e)}")
    
    def generate_migration_report(self):
        """Generate comprehensive migration report"""
        print("\n" + "="*60)
        print("         SCHOOL DATABASE MIGRATION REPORT")
        print("="*60)
        
        total_success = sum(log['success_count'] for log in self.migration_log)
        total_errors = sum(log['error_count'] for log in self.migration_log)
        
        print(f"📊 SUMMARY")
        print(f"   Total Records Migrated: {total_success}")
        print(f"   Total Errors: {total_errors}")
        
        if total_success + total_errors > 0:
            success_rate = (total_success / (total_success + total_errors)) * 100
            print(f"   Success Rate: {success_rate:.2f}%")
        
        print(f"\n📋 DETAILED BREAKDOWN")
        for log in self.migration_log:
            print(f"   {log['operation']:<15}: {log['success_count']:<6} success, {log['error_count']:<6} errors")
        
        # Show first few errors for each operation
        print(f"\n⚠️  ERROR DETAILS")
        for log in self.migration_log:
            if log['errors']:
                print(f"\n   {log['operation']} Errors:")
                for error in log['errors'][:3]:  # Show first 3 errors
                    print(f"     • {error}")
                if len(log['errors']) > 3:
                    print(f"     ... and {len(log['errors'])-3} more errors")
        
        print(f"\n✅ Migration completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)

def main():
    """Main migration function"""
    print("🏫 School Database Migration from CSV Files")
    print("="*50)
    
    migrator = CSVMigrator()
    
    # Define CSV files to migrate (customize these paths)
    csv_files = {
        'departments': 'data/departments.csv',
        'subjects': 'data/subjects.csv', 
        'teachers': 'data/teachers.csv',
        'grades': 'data/grades.csv',
        'students': 'data/students.csv',
        'fee_payments': 'data/fee_payments.csv',
        'exam_results': 'data/exam_results.csv'
    }
    
    # Check which files exist
    existing_files = {}
    for key, filepath in csv_files.items():
        if os.path.exists(filepath):
            existing_files[key] = filepath
            print(f"✅ Found: {filepath}")
        else:
            print(f"⚠️  Not found: {filepath}")
    
    if not existing_files:
        print("\n❌ No CSV files found. Please place your CSV files in the data/ directory.")
        print("\nExpected file structure:")
        for key, filepath in csv_files.items():
            print(f"   {filepath}")
        return
    
    print(f"\n🚀 Starting migration of {len(existing_files)} file(s)...")
    
    # Migration order is important!
    migration_order = [
        ('departments', migrator.migrate_departments),
        ('subjects', migrator.migrate_subjects),
        ('teachers', migrator.migrate_teachers),
        ('grades', migrator.migrate_grades),
        ('students', migrator.migrate_students),
        ('fee_payments', migrator.migrate_fee_payments),
        ('exam_results', migrator.migrate_exam_results)
    ]
    
    for key, migrate_func in migration_order:
        if key in existing_files:
            migrate_func(existing_files[key])
    
    # Generate final report
    migrator.generate_migration_report()

if __name__ == "__main__":
    main() 