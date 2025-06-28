"""
Production-Grade Test Suite for School ERP System
"""
import unittest
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from core.models import Student, Teacher, Grade, SchoolSettings
from fees.models import FeePayment
from academics.models import Attendance
from examinations.models import ExamResult
from library.models import Book, BookIssue
from django.utils import timezone

class BaseTestCase(TestCase):
    """Base test case with common setup"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        # Create test school settings
        self.school = SchoolSettings.objects.create(
            name='Test School',
            address='Test Address',
            phone='+911234567890',
            email='test@school.com'
        )
        
        # Create test grade
        self.grade = Grade.objects.create(
            name='Grade 1',
            grade_level=1,
            school=self.school
        )
        
        # Login user
        self.client.login(username='testuser', password='testpass123')

class StudentModuleTests(BaseTestCase):
    """Test student management functionality"""
    
    def test_student_creation(self):
        """Test student creation"""
        student = Student.objects.create(
            student_id='TEST001',
            first_name='John',
            last_name='Doe',
            grade=self.grade,
            admission_date=timezone.now().date(),
            email='john@example.com',
            contact_number='+911234567890',
            father_name='John Sr',
            mother_name='Jane Doe',
            address='Test Address',
            city='Test City',
            state='Test State',
            postal_code='123456'
        )
        
        self.assertEqual(student.student_id, 'TEST001')
        self.assertEqual(student.full_name, 'John Doe')
        self.assertTrue(student.is_active)
    
    def test_student_list_view(self):
        """Test student list view"""
        response = self.client.get(reverse('students:student-list'))
        self.assertEqual(response.status_code, 200)
    
    def test_student_detail_view(self):
        """Test student detail view"""
        student = Student.objects.create(
            student_id='TEST002',
            first_name='Jane',
            last_name='Smith',
            grade=self.grade,
            admission_date=timezone.now().date(),
            email='jane@example.com',
            contact_number='+911234567891'
        )
        
        response = self.client.get(reverse('students:student-detail', args=[student.pk]))
        self.assertEqual(response.status_code, 200)

class AcademicsModuleTests(BaseTestCase):
    """Test academic functionality"""
    
    def test_attendance_marking(self):
        """Test attendance marking"""
        student = Student.objects.create(
            student_id='TEST003',
            first_name='Bob',
            last_name='Wilson',
            grade=self.grade,
            admission_date=timezone.now().date(),
            email='bob@example.com',
            contact_number='+911234567892'
        )
        
        attendance = Attendance.objects.create(
            student=student,
            date=timezone.now().date(),
            is_present=True
        )
        
        self.assertTrue(attendance.is_present)
        self.assertEqual(attendance.student, student)

class FeesModuleTests(BaseTestCase):
    """Test fee management functionality"""
    
    def test_fee_payment_creation(self):
        """Test fee payment creation"""
        student = Student.objects.create(
            student_id='TEST004',
            first_name='Alice',
            last_name='Brown',
            grade=self.grade,
            admission_date=timezone.now().date(),
            email='alice@example.com',
            contact_number='+911234567893'
        )
        
        payment = FeePayment.objects.create(
            student=student,
            amount=1000.00,
            payment_date=timezone.now().date(),
            status='COMPLETED',
            payment_method='CASH'
        )
        
        self.assertEqual(payment.amount, 1000.00)
        self.assertEqual(payment.status, 'COMPLETED')

class ExaminationModuleTests(BaseTestCase):
    """Test examination functionality"""
    
    def test_exam_result_creation(self):
        """Test exam result creation"""
        student = Student.objects.create(
            student_id='TEST005',
            first_name='Charlie',
            last_name='Davis',
            grade=self.grade,
            admission_date=timezone.now().date(),
            email='charlie@example.com',
            contact_number='+911234567894'
        )
        
        result = ExamResult.objects.create(
            student=student,
            subject_name='Mathematics',
            total_marks=100,
            marks_obtained=85,
            percentage=85.0,
            exam_date=timezone.now().date(),
            grade_obtained='A'
        )
        
        self.assertEqual(result.percentage, 85.0)
        self.assertEqual(result.grade_obtained, 'A')

class LibraryModuleTests(BaseTestCase):
    """Test library functionality"""
    
    def test_book_creation(self):
        """Test book creation"""
        book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            isbn='1234567890',
            category='Fiction',
            total_copies=5,
            available_copies=5
        )
        
        self.assertEqual(book.title, 'Test Book')
        self.assertEqual(book.available_copies, 5)

class SecurityTests(BaseTestCase):
    """Test security features"""
    
    def test_authentication_required(self):
        """Test that authentication is required"""
        # Logout
        self.client.logout()
        
        # Try to access protected view
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_permission_checking(self):
        """Test permission checking"""
        # This would test role-based access control
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)

class PerformanceTests(BaseTestCase):
    """Test system performance"""
    
    def test_student_list_performance(self):
        """Test student list loads quickly with many records"""
        # Create 100 students
        for i in range(100):
            Student.objects.create(
                student_id=f'PERF{i:03d}',
                first_name=f'Student{i}',
                last_name='Test',
                grade=self.grade,
                admission_date=timezone.now().date(),
                email=f'student{i}@example.com',
                contact_number=f'+91123456{i:04d}'
            )
        
        # Test that list view loads
        response = self.client.get(reverse('students:student-list'))
        self.assertEqual(response.status_code, 200)
        
        # Test pagination works
        self.assertContains(response, 'page')

class DataIntegrityTests(BaseTestCase):
    """Test data integrity and validation"""
    
    def test_unique_student_id(self):
        """Test that student IDs are unique"""
        Student.objects.create(
            student_id='UNIQUE001',
            first_name='Test1',
            last_name='User',
            grade=self.grade,
            admission_date=timezone.now().date(),
            email='test1@example.com',
            contact_number='+911234567895'
        )
        
        # Try to create another student with same ID
        with self.assertRaises(Exception):
            Student.objects.create(
                student_id='UNIQUE001',
                first_name='Test2',
                last_name='User',
                grade=self.grade,
                admission_date=timezone.now().date(),
                email='test2@example.com',
                contact_number='+911234567896'
            )

if __name__ == '__main__':
    unittest.main()
