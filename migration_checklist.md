# School Database Migration Checklist

## Phase 1: Pre-Migration Assessment ✅

### **1. Data Discovery**
- [ ] **Get database access** from current school system
- [ ] **Document current database schema** (tables, relationships)
- [ ] **Export sample data** (500-1000 records) for testing
- [ ] **Identify data format**: MySQL, PostgreSQL, Excel, Access, CSV
- [ ] **Check data quality**: duplicates, missing values, inconsistencies

### **2. Data Mapping**
- [ ] **Map student fields** to Django Student model
- [ ] **Map teacher data** to Django Teacher model  
- [ ] **Map class/grade structure** to Django Grade model
- [ ] **Map subjects** to Django Subject model
- [ ] **Map fee records** to Django FeePayment model
- [ ] **Map exam/marks** to Django ExamResult model

### **3. Volume Assessment**
- [ ] **Count total students**: _______ records
- [ ] **Count total teachers**: _______ records
- [ ] **Count fee records**: _______ records
- [ ] **Count exam results**: _______ records
- [ ] **Estimate migration time**: _______ hours

## Phase 2: Data Preparation 🔧

### **4. Clean Source Data**
- [ ] **Remove duplicate students** (same name, DOB)
- [ ] **Standardize grade names** (e.g., "Class 1" → "1", "Grade I" → "1")
- [ ] **Validate phone numbers** (10-digit format)
- [ ] **Check email formats** (valid email addresses)
- [ ] **Standardize date formats** (YYYY-MM-DD)

### **5. Create Reference Data**
- [ ] **List all departments** (Math, Science, English, etc.)
- [ ] **List all subjects** with department mapping
- [ ] **List all grade levels** (1-12, Nursery, etc.)
- [ ] **List fee categories** (Tuition, Books, Transport, etc.)

## Phase 3: Migration Strategy 📊

### **6. Migration Order**
```
1. Academic Year
2. Departments  
3. Subjects
4. Teachers
5. Grades/Classes
6. Students
7. Fee Categories
8. Fee Structures  
9. Fee Payments
10. Exams
11. Exam Results
12. Attendance Records
```

### **7. Tools & Methods**

#### **Option A: CSV/Excel Files**
```python
# 1. Export current data to CSV
# 2. Clean data in Excel/Google Sheets
# 3. Use pandas to load and migrate

import pandas as pd
students_df = pd.read_csv('students.csv')
for _, row in students_df.iterrows():
    Student.objects.create(
        admission_number=row['student_id'],
        first_name=row['first_name'],
        # ... other fields
    )
```

#### **Option B: Direct Database Connection**
```python
# Connect to source database
import mysql.connector  # or psycopg2 for PostgreSQL

source_conn = mysql.connector.connect(
    host='old_school_server',
    user='username',
    password='password',
    database='school_db'
)

# Query and migrate
cursor = source_conn.cursor()
cursor.execute("SELECT * FROM students")
for row in cursor:
    Student.objects.create(...)
```

#### **Option C: Django Data Migration**
```python
# Create Django migration file
python manage.py makemigrations --empty core
# Edit migration file to include data migration logic
```

## Phase 4: Test Migration 🧪

### **8. Test Environment Setup**
- [ ] **Create test database** (copy of production)
- [ ] **Run migration on test data** (first 100 records)
- [ ] **Verify data accuracy** (spot check 10-20 records)
- [ ] **Test application functionality** with migrated data
- [ ] **Performance test** with full dataset

### **9. Validation Checks**
- [ ] **Student count matches** source vs Django
- [ ] **Teacher assignments correct** (subjects, classes)
- [ ] **Fee records accurate** (amounts, dates, status)
- [ ] **Exam results preserved** (marks, grades)
- [ ] **Parent contact info** correctly migrated

## Phase 5: Production Migration 🚀

### **10. Go-Live Preparation**
- [ ] **Schedule migration window** (preferably weekend)
- [ ] **Backup current Django database** (if any data exists)
- [ ] **Notify school staff** about temporary downtime
- [ ] **Prepare rollback plan** (in case of issues)

### **11. Migration Execution**
- [ ] **Stop current school system** (if applicable)
- [ ] **Export final data snapshot** from source
- [ ] **Run migration scripts** in order
- [ ] **Verify data integrity** 
- [ ] **Test critical functions** (enrollment, fee payment)
- [ ] **Train staff** on new system

### **12. Post-Migration**
- [ ] **Generate migration report** (success/error counts)
- [ ] **Create user accounts** for teachers/admin
- [ ] **Set up fee structures** for current academic year
- [ ] **Configure school settings** (logo, address, etc.)
- [ ] **Document any data gaps** or manual fixes needed

## Phase 6: User Training & Support 👥

### **13. Staff Training**
- [ ] **Admin training** (user management, reports)
- [ ] **Teacher training** (attendance, grades, student info)
- [ ] **Accountant training** (fee management, reports)
- [ ] **Create user manuals** or video tutorials

### **14. Support & Monitoring**
- [ ] **Monitor system performance** first few days
- [ ] **Address user questions** and issues
- [ ] **Fine-tune data** based on feedback
- [ ] **Plan for ongoing data updates** (new admissions)

## Common Migration Challenges & Solutions 💡

### **Challenge 1: Different Grade Systems**
**Problem**: Source uses "Class I" but Django expects "1"
**Solution**: Create mapping dictionary
```python
grade_mapping = {
    'Class I': '1', 'Class II': '2', 'Class III': '3',
    'Nursery': 'Nursery', 'KG': 'Kindergarten'
}
```

### **Challenge 2: Multiple Students Same Name**
**Problem**: "John Smith" appears 3 times
**Solution**: Use combination of name + DOB + parent contact
```python
unique_key = f"{first_name}_{last_name}_{dob}_{parent_phone}"
```

### **Challenge 3: Historical Data**
**Problem**: 5 years of student records, many graduated
**Solution**: Migrate recent data only (current + last 2 years)

### **Challenge 4: Missing Required Fields**
**Problem**: Django requires fields that don't exist in source
**Solution**: Use default values or make fields optional
```python
# Use defaults
grade = grade or Grade.objects.get(name='1', section='A')
gender = gender or 'Not Specified'
```

## Sample Migration Script Structure 📝

```python
#!/usr/bin/env python
"""
School ABC Database Migration
Date: 2025-01-XX
"""

import os
import django
import pandas as pd
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_modernized.settings')
django.setup()

from core.models import *

def migrate_students():
    """Migrate students from CSV file"""
    df = pd.read_csv('students_export.csv')
    success_count = 0
    error_count = 0
    
    for _, row in df.iterrows():
        try:
            # Data cleaning
            first_name = str(row['FirstName']).strip().title()
            last_name = str(row['LastName']).strip().title()
            
            # Get or create grade
            grade, _ = Grade.objects.get_or_create(
                name=str(row['Grade']),
                section=str(row['Section'])
            )
            
            # Create student
            student, created = Student.objects.get_or_create(
                admission_number=str(row['StudentID']),
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'grade': grade,
                    'date_of_birth': pd.to_datetime(row['DOB']).date(),
                    'parent_contact_number': str(row['ParentPhone']),
                    'address': str(row['Address'])
                }
            )
            
            if created:
                success_count += 1
                print(f"✅ Created: {first_name} {last_name}")
            else:
                print(f"⚠️  Already exists: {first_name} {last_name}")
                
        except Exception as e:
            error_count += 1
            print(f"❌ Error: {row.get('FirstName', 'Unknown')} - {str(e)}")
    
    print(f"\n📊 Migration Summary:")
    print(f"✅ Success: {success_count}")
    print(f"❌ Errors: {error_count}")

if __name__ == "__main__":
    print("Starting School Database Migration...")
    migrate_students()
    print("Migration completed!")
```

## Data Export Queries (Common Database Systems) 🗄️

### **MySQL Export**
```sql
-- Students
SELECT 
    student_id, first_name, last_name, dob, 
    class, section, admission_date, parent_phone, address
FROM students 
WHERE status = 'active';

-- Teachers  
SELECT 
    emp_id, name, department, subjects, phone, email, hire_date
FROM teachers;

-- Fee Records
SELECT 
    student_id, fee_type, amount, due_date, paid_date, status
FROM fee_payments 
WHERE academic_year = '2024-25';
```

### **Access Database Export**
```sql
-- Open Access → External Data → Export to Excel/CSV
-- Or use ODBC connection in Python:
import pyodbc
conn = pyodbc.connect(r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=school.accdb;')
```

This comprehensive guide should help you migrate any school's existing database to your Django system! 🎓 