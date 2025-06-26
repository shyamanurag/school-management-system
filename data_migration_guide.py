#!/usr/bin/env python
"""
School Database Migration Guide
Maps common existing school database structures to Django models
"""

# Common existing school database tables and their Django model mappings
SCHOOL_DATA_MAPPING = {
    'students': {
        'existing_fields': [
            'student_id', 'first_name', 'last_name', 'date_of_birth',
            'grade_level', 'section', 'admission_date', 'parent_phone',
            'address', 'email'
        ],
        'django_model': 'Student',
        'field_mapping': {
            'student_id': 'admission_number',
            'first_name': 'first_name',
            'last_name': 'last_name',
            'date_of_birth': 'date_of_birth',
            'grade_level': 'grade.name',  # FK to Grade model
            'section': 'grade.section',
            'admission_date': 'admission_date',
            'parent_phone': 'parent_contact_number',
            'address': 'address',
            'email': 'email'
        }
    },
    
    'teachers': {
        'existing_fields': [
            'teacher_id', 'name', 'subject', 'phone', 'email',
            'hire_date', 'department'
        ],
        'django_model': 'Teacher',
        'field_mapping': {
            'teacher_id': 'employee_id',
            'name': 'full_name',
            'subject': 'subjects_taught',  # ManyToMany
            'phone': 'contact_number',
            'email': 'email',
            'hire_date': 'date_of_joining',
            'department': 'department.name'  # FK
        }
    },
    
    'classes': {
        'existing_fields': [
            'class_id', 'class_name', 'section', 'teacher_id'
        ],
        'django_model': 'Grade',
        'field_mapping': {
            'class_id': 'id',
            'class_name': 'name',
            'section': 'section',
            'teacher_id': 'class_teacher.id'  # FK
        }
    },
    
    'fees': {
        'existing_fields': [
            'student_id', 'fee_type', 'amount', 'due_date',
            'paid_date', 'status'
        ],
        'django_model': 'FeePayment',
        'field_mapping': {
            'student_id': 'student.id',
            'fee_type': 'fee_structure.category.name',
            'amount': 'amount_paid',
            'due_date': 'due_date',
            'paid_date': 'payment_date',
            'status': 'payment_status'
        }
    },
    
    'marks': {
        'existing_fields': [
            'student_id', 'subject', 'exam_type', 'marks',
            'max_marks', 'exam_date'
        ],
        'django_model': 'ExamResult',
        'field_mapping': {
            'student_id': 'student.id',
            'subject': 'subject.name',
            'exam_type': 'exam.name',
            'marks': 'marks_obtained',
            'max_marks': 'total_marks',
            'exam_date': 'exam.date'
        }
    }
}

def create_migration_script(source_db_type='mysql'):
    """
    Generate a migration script template based on source database type
    """
    
    script_template = f"""
#!/usr/bin/env python
'''
School Database Migration Script
Source: {source_db_type.upper()}
Target: Django School Management System
'''

import os
import django
import pandas as pd
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_modernized.settings.production')
django.setup()

from core.models import (
    Student, Teacher, Grade, Subject, Department,
    FeeCategory, FeeStructure, FeePayment,
    Exam, ExamResult, Attendance, AcademicYear
)

class SchoolDataMigrator:
    def __init__(self, source_connection_string):
        self.source_conn = source_connection_string
        self.migration_log = []
        
    def log_migration(self, table, success_count, error_count, errors=None):
        log_entry = {{
            'table': table,
            'timestamp': datetime.now(),
            'success_count': success_count,
            'error_count': error_count,
            'errors': errors or []
        }}
        self.migration_log.append(log_entry)
        print(f"Migrated {{table}}: {{success_count}} success, {{error_count}} errors")
    
    def migrate_academic_year(self):
        '''Create/ensure academic year exists'''
        current_year = datetime.now().year
        year, created = AcademicYear.objects.get_or_create(
            year=f"{{current_year}}-{{current_year+1}}",
            defaults={{
                'start_date': datetime(current_year, 4, 1),
                'end_date': datetime(current_year+1, 3, 31),
                'is_current': True
            }}
        )
        return year
    
    def migrate_departments(self, departments_data):
        '''Migrate departments from source data'''
        success_count = 0
        error_count = 0
        errors = []
        
        for dept_data in departments_data:
            try:
                dept, created = Department.objects.get_or_create(
                    name=dept_data['name'],
                    defaults={{
                        'description': dept_data.get('description', ''),
                        'head_of_department': dept_data.get('head', '')
                    }}
                )
                success_count += 1
            except Exception as e:
                error_count += 1
                errors.append(f"Department {{dept_data.get('name')}}: {{str(e)}}")
        
        self.log_migration('Departments', success_count, error_count, errors)
        return success_count
    
    def migrate_subjects(self, subjects_data):
        '''Migrate subjects from source data'''
        success_count = 0
        error_count = 0
        errors = []
        
        for subject_data in subjects_data:
            try:
                # Get or create department
                dept = None
                if subject_data.get('department'):
                    dept, _ = Department.objects.get_or_create(
                        name=subject_data['department']
                    )
                
                subject, created = Subject.objects.get_or_create(
                    name=subject_data['name'],
                    defaults={{
                        'code': subject_data.get('code', ''),
                        'department': dept,
                        'description': subject_data.get('description', '')
                    }}
                )
                success_count += 1
            except Exception as e:
                error_count += 1
                errors.append(f"Subject {{subject_data.get('name')}}: {{str(e)}}")
        
        self.log_migration('Subjects', success_count, error_count, errors)
        return success_count
    
    def migrate_teachers(self, teachers_data):
        '''Migrate teachers from source data'''
        success_count = 0
        error_count = 0
        errors = []
        
        for teacher_data in teachers_data:
            try:
                # Get department if specified
                dept = None
                if teacher_data.get('department'):
                    dept, _ = Department.objects.get_or_create(
                        name=teacher_data['department']
                    )
                
                teacher, created = Teacher.objects.get_or_create(
                    employee_id=teacher_data.get('employee_id', ''),
                    defaults={{
                        'full_name': teacher_data['name'],
                        'email': teacher_data.get('email', ''),
                        'contact_number': teacher_data.get('phone', ''),
                        'department': dept,
                        'date_of_joining': teacher_data.get('hire_date'),
                        'address': teacher_data.get('address', ''),
                        'qualification': teacher_data.get('qualification', '')
                    }}
                )
                
                # Add subjects taught
                if teacher_data.get('subjects'):
                    for subject_name in teacher_data['subjects']:
                        subject, _ = Subject.objects.get_or_create(name=subject_name)
                        teacher.subjects_taught.add(subject)
                
                success_count += 1
            except Exception as e:
                error_count += 1
                errors.append(f"Teacher {{teacher_data.get('name')}}: {{str(e)}}")
        
        self.log_migration('Teachers', success_count, error_count, errors)
        return success_count
    
    def migrate_grades(self, grades_data):
        '''Migrate classes/grades from source data'''
        success_count = 0
        error_count = 0
        errors = []
        
        academic_year = self.migrate_academic_year()
        
        for grade_data in grades_data:
            try:
                # Get class teacher if specified
                class_teacher = None
                if grade_data.get('teacher_id'):
                    try:
                        class_teacher = Teacher.objects.get(
                            employee_id=grade_data['teacher_id']
                        )
                    except Teacher.DoesNotExist:
                        pass
                
                grade, created = Grade.objects.get_or_create(
                    name=grade_data['class_name'],
                    section=grade_data.get('section', 'A'),
                    academic_year=academic_year,
                    defaults={{
                        'class_teacher': class_teacher,
                        'max_students': grade_data.get('max_students', 40)
                    }}
                )
                success_count += 1
            except Exception as e:
                error_count += 1
                errors.append(f"Grade {{grade_data.get('class_name')}}: {{str(e)}}")
        
        self.log_migration('Grades', success_count, error_count, errors)
        return success_count
    
    def migrate_students(self, students_data):
        '''Migrate students from source data'''
        success_count = 0
        error_count = 0
        errors = []
        
        for student_data in students_data:
            try:
                # Get grade
                grade = None
                if student_data.get('grade_level') and student_data.get('section'):
                    try:
                        grade = Grade.objects.get(
                            name=student_data['grade_level'],
                            section=student_data.get('section', 'A')
                        )
                    except Grade.DoesNotExist:
                        # Create grade if it doesn't exist
                        academic_year = AcademicYear.objects.filter(is_current=True).first()
                        grade, _ = Grade.objects.get_or_create(
                            name=student_data['grade_level'],
                            section=student_data.get('section', 'A'),
                            academic_year=academic_year
                        )
                
                student, created = Student.objects.get_or_create(
                    admission_number=student_data.get('student_id', ''),
                    defaults={{
                        'first_name': student_data['first_name'],
                        'last_name': student_data['last_name'],
                        'date_of_birth': student_data.get('date_of_birth'),
                        'grade': grade,
                        'admission_date': student_data.get('admission_date'),
                        'parent_contact_number': student_data.get('parent_phone', ''),
                        'address': student_data.get('address', ''),
                        'email': student_data.get('email', ''),
                        'gender': student_data.get('gender', 'Male'),
                        'blood_group': student_data.get('blood_group', 'O+')
                    }}
                )
                success_count += 1
            except Exception as e:
                error_count += 1
                errors.append(f"Student {{student_data.get('first_name')}} {{student_data.get('last_name')}}: {{str(e)}}")
        
        self.log_migration('Students', success_count, error_count, errors)
        return success_count
    
    def migrate_fees(self, fees_data):
        '''Migrate fee records from source data'''
        success_count = 0
        error_count = 0
        errors = []
        
        for fee_data in fees_data:
            try:
                # Get student
                student = Student.objects.get(
                    admission_number=fee_data['student_id']
                )
                
                # Get or create fee category
                fee_category, _ = FeeCategory.objects.get_or_create(
                    name=fee_data['fee_type'],
                    defaults={{'amount': fee_data['amount']}}
                )
                
                # Get or create fee structure
                fee_structure, _ = FeeStructure.objects.get_or_create(
                    student=student,
                    category=fee_category,
                    defaults={{
                        'amount': fee_data['amount'],
                        'due_date': fee_data.get('due_date')
                    }}
                )
                
                # Create fee payment if paid
                if fee_data.get('paid_date'):
                    payment, created = FeePayment.objects.get_or_create(
                        student=student,
                        fee_structure=fee_structure,
                        defaults={{
                            'amount_paid': fee_data['amount'],
                            'payment_date': fee_data['paid_date'],
                            'payment_method': fee_data.get('payment_method', 'Cash'),
                            'payment_status': 'Paid'
                        }}
                    )
                
                success_count += 1
            except Exception as e:
                error_count += 1
                errors.append(f"Fee for {{fee_data.get('student_id')}}: {{str(e)}}")
        
        self.log_migration('Fees', success_count, error_count, errors)
        return success_count
    
    def migrate_exam_results(self, results_data):
        '''Migrate exam results from source data'''
        success_count = 0
        error_count = 0
        errors = []
        
        for result_data in results_data:
            try:
                # Get student
                student = Student.objects.get(
                    admission_number=result_data['student_id']
                )
                
                # Get or create subject
                subject, _ = Subject.objects.get_or_create(
                    name=result_data['subject']
                )
                
                # Get or create exam
                exam, _ = Exam.objects.get_or_create(
                    name=result_data['exam_type'],
                    defaults={{
                        'date': result_data.get('exam_date'),
                        'total_marks': result_data.get('max_marks', 100)
                    }}
                )
                
                # Create exam result
                result, created = ExamResult.objects.get_or_create(
                    student=student,
                    exam=exam,
                    subject=subject,
                    defaults={{
                        'marks_obtained': result_data['marks'],
                        'total_marks': result_data.get('max_marks', 100),
                        'grade': self.calculate_grade(
                            result_data['marks'], 
                            result_data.get('max_marks', 100)
                        )
                    }}
                )
                
                success_count += 1
            except Exception as e:
                error_count += 1
                errors.append(f"Result for {{result_data.get('student_id')}}: {{str(e)}}")
        
        self.log_migration('Exam Results', success_count, error_count, errors)
        return success_count
    
    def calculate_grade(self, marks, total_marks):
        '''Calculate grade based on percentage'''
        percentage = (marks / total_marks) * 100
        if percentage >= 90: return 'A+'
        elif percentage >= 80: return 'A'
        elif percentage >= 70: return 'B+'
        elif percentage >= 60: return 'B'
        elif percentage >= 50: return 'C+'
        elif percentage >= 40: return 'C'
        else: return 'F'
    
    def generate_migration_report(self):
        '''Generate detailed migration report'''
        print("\\n" + "="*50)
        print("SCHOOL DATABASE MIGRATION REPORT")
        print("="*50)
        
        total_success = sum(log['success_count'] for log in self.migration_log)
        total_errors = sum(log['error_count'] for log in self.migration_log)
        
        print(f"Total Records Migrated: {{total_success}}")
        print(f"Total Errors: {{total_errors}}")
        print(f"Success Rate: {{(total_success/(total_success+total_errors))*100:.2f}}%")
        
        print("\\nDetailed Breakdown:")
        for log in self.migration_log:
            print(f"- {{log['table']}}: {{log['success_count']}} success, {{log['error_count']}} errors")
        
        # Print errors if any
        if total_errors > 0:
            print("\\nError Details:")
            for log in self.migration_log:
                if log['errors']:
                    print(f"\\n{{log['table']}} Errors:")
                    for error in log['errors'][:5]:  # Show first 5 errors
                        print(f"  - {{error}}")
                    if len(log['errors']) > 5:
                        print(f"  ... and {{len(log['errors'])-5}} more errors")

# Example usage:
if __name__ == "__main__":
    # Connection string examples:
    # MySQL: "mysql+pymysql://user:password@localhost/school_db"
    # PostgreSQL: "postgresql://user:password@localhost/school_db"
    # SQLite: "sqlite:///path/to/school.db"
    
    migrator = SchoolDataMigrator("your_source_connection_string")
    
    # Load data from source (example with pandas)
    # departments_df = pd.read_sql("SELECT * FROM departments", migrator.source_conn)
    # teachers_df = pd.read_sql("SELECT * FROM teachers", migrator.source_conn)
    # students_df = pd.read_sql("SELECT * FROM students", migrator.source_conn)
    
    # Convert to dictionaries and migrate
    # migrator.migrate_departments(departments_df.to_dict('records'))
    # migrator.migrate_teachers(teachers_df.to_dict('records'))
    # migrator.migrate_students(students_df.to_dict('records'))
    
    # Generate report
    # migrator.generate_migration_report()
    
    print("Migration script template generated!")
    """
    
    return script_template

# Data validation functions
def validate_student_data(student_record):
    """Validate student data before migration"""
    required_fields = ['first_name', 'last_name']
    errors = []
    
    for field in required_fields:
        if not student_record.get(field):
            errors.append(f"Missing required field: {field}")
    
    # Validate email format
    if student_record.get('email'):
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, student_record['email']):
            errors.append("Invalid email format")
    
    # Validate date format
    if student_record.get('date_of_birth'):
        try:
            from datetime import datetime
            datetime.strptime(student_record['date_of_birth'], '%Y-%m-%d')
        except ValueError:
            errors.append("Invalid date format (should be YYYY-MM-DD)")
    
    return errors

if __name__ == "__main__":
    print("School Database Migration Guide")
    print("==============================")
    print()
    print("This script provides templates and utilities for migrating")
    print("existing school databases to the Django School Management System.")
    print()
    print("Supported source formats:")
    print("- MySQL databases")
    print("- PostgreSQL databases") 
    print("- SQLite databases")
    print("- CSV/Excel files")
    print("- Access databases")
    print()
    print("Run with: python data_migration_guide.py") 