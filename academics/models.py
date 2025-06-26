from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericRelation
from core.models import TimeStampedModel, SchoolSettings, UUIDModel, AcademicYear, Room, Attachment, Department
from students.models import Student, SchoolClass, Section
import uuid

class Subject(TimeStampedModel):
    """Subject/Course management"""
    SUBJECT_TYPES = [
        ('CORE', 'Core Subject'),
        ('ELECTIVE', 'Elective'),
        ('OPTIONAL', 'Optional'),
        ('EXTRA_CURRICULAR', 'Extra Curricular'),
        ('VOCATIONAL', 'Vocational'),
    ]
    
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='subjects')
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    subject_type = models.CharField(max_length=20, choices=SUBJECT_TYPES, default='CORE')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='subjects')
    
    # Academic details
    credit_hours = models.IntegerField(default=1)
    theory_hours = models.IntegerField(default=0)
    practical_hours = models.IntegerField(default=0)
    
    # Assessment configuration
    max_marks = models.IntegerField(default=100)
    passing_marks = models.IntegerField(default=35)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_compulsory = models.BooleanField(default=True)
    
    # Files
    syllabus = models.FileField(upload_to='subject_syllabus/', blank=True, null=True)
    attachments = GenericRelation(Attachment)
    
    class Meta:
        unique_together = ['school', 'code']
        ordering = ['name']
    
    def __str__(self):
        return f"{self.school.name} - {self.name} ({self.code})"

class ClassSubject(TimeStampedModel):
    """Subject assignment to classes"""
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='class_subjects')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='assigned_classes')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='class_subjects')
    
    # Teaching assignment
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='teaching_subjects')
    assistant_teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assisting_subjects')
    
    # Schedule details
    periods_per_week = models.IntegerField(default=5)
    period_duration_minutes = models.IntegerField(default=45)
    
    # Assessment weights
    theory_weight = models.IntegerField(default=70, validators=[MinValueValidator(0), MaxValueValidator(100)])
    practical_weight = models.IntegerField(default=30, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Status
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['school_class', 'subject', 'academic_year']
    
    def __str__(self):
        return f"{self.school_class.name} - {self.subject.name} - {self.academic_year.name}"

class Exam(TimeStampedModel):
    """Examination management"""
    EXAM_TYPES = [
        ('UNIT_TEST', 'Unit Test'),
        ('MID_TERM', 'Mid Term'),
        ('FINAL', 'Final Exam'),
        ('QUARTERLY', 'Quarterly'),
        ('HALF_YEARLY', 'Half Yearly'),
        ('ANNUAL', 'Annual'),
        ('ENTRANCE', 'Entrance Test'),
        ('SURPRISE', 'Surprise Test'),
    ]
    
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='exams')
    name = models.CharField(max_length=200)
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPES)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='exams')
    
    # Schedule
    start_date = models.DateField()
    end_date = models.DateField()
    result_declaration_date = models.DateField(blank=True, null=True)
    
    # Configuration
    description = models.TextField(blank=True, null=True)
    instructions = models.TextField(blank=True, null=True)
    is_internal = models.BooleanField(default=True)
    is_final = models.BooleanField(default=False)
    
    # Grading
    grade_system = models.CharField(max_length=20, choices=[
        ('PERCENTAGE', 'Percentage'),
        ('GRADE', 'Grade (A, B, C)'),
        ('GPA', 'GPA (4.0 Scale)'),
        ('CGPA', 'CGPA (10.0 Scale)'),
    ], default='PERCENTAGE')
    
    # Status
    is_active = models.BooleanField(default=True)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.school.name} - {self.name} - {self.academic_year.name}"

class ExamSchedule(TimeStampedModel):
    """Individual exam paper schedule"""
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='schedules')
    class_subject = models.ForeignKey(ClassSubject, on_delete=models.CASCADE, related_name='exam_schedules')
    
    # Schedule details
    exam_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration_minutes = models.IntegerField()
    
    # Venue
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    venue_details = models.CharField(max_length=200, blank=True, null=True)
    
    # Supervision
    invigilator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='invigilated_exams')
    assistant_invigilator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assisted_exams')
    
    # Paper details
    max_marks = models.IntegerField()
    passing_marks = models.IntegerField()
    question_paper = models.FileField(upload_to='question_papers/', blank=True, null=True)
    answer_key = models.FileField(upload_to='answer_keys/', blank=True, null=True)
    
    # Status
    is_completed = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    cancellation_reason = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ['exam', 'class_subject']
        ordering = ['exam_date', 'start_time']
    
    def __str__(self):
        return f"{self.exam.name} - {self.class_subject.subject.name} - {self.exam_date}"

class StudentExamResult(UUIDModel, TimeStampedModel):
    """Student exam results"""
    exam_schedule = models.ForeignKey(ExamSchedule, on_delete=models.CASCADE, related_name='student_results')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exam_results')
    
    # Marks
    marks_obtained = models.FloatField(validators=[MinValueValidator(0)])
    max_marks = models.FloatField()
    percentage = models.FloatField(blank=True, null=True)
    grade = models.CharField(max_length=5, blank=True, null=True)
    
    # Attendance
    is_present = models.BooleanField(default=True)
    is_absent = models.BooleanField(default=False)
    absence_reason = models.CharField(max_length=100, blank=True, null=True)
    
    # Status
    is_passed = models.BooleanField(default=False)
    is_improvement = models.BooleanField(default=False)  # Improvement exam
    
    # Additional details
    remarks = models.TextField(blank=True, null=True)
    checked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    checked_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        unique_together = ['exam_schedule', 'student']
        indexes = [
            models.Index(fields=['student', 'exam_schedule']),
            models.Index(fields=['marks_obtained']),
        ]
    
    def __str__(self):
        return f"{self.student.full_name} - {self.exam_schedule} - {self.marks_obtained}/{self.max_marks}"

class Grade(TimeStampedModel):
    """Grading system configuration"""
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='grades')
    name = models.CharField(max_length=10)  # A+, A, B+, etc.
    min_percentage = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    max_percentage = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    gpa_value = models.FloatField(blank=True, null=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    is_passing = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['school', 'name']
        ordering = ['-min_percentage']
    
    def __str__(self):
        return f"{self.school.name} - {self.name} ({self.min_percentage}%-{self.max_percentage}%)"

class Assignment(UUIDModel, TimeStampedModel):
    """Assignment management"""
    ASSIGNMENT_TYPES = [
        ('HOMEWORK', 'Homework'),
        ('PROJECT', 'Project'),
        ('PRESENTATION', 'Presentation'),
        ('RESEARCH', 'Research Work'),
        ('PRACTICAL', 'Practical Work'),
        ('ESSAY', 'Essay'),
        ('QUIZ', 'Quiz'),
    ]
    
    class_subject = models.ForeignKey(ClassSubject, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=300)
    description = models.TextField()
    assignment_type = models.CharField(max_length=20, choices=ASSIGNMENT_TYPES, default='HOMEWORK')
    
    # Dates
    assigned_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    submission_date = models.DateField(blank=True, null=True)
    
    # Marks
    max_marks = models.IntegerField(default=10)
    
    # Files
    attachment = models.FileField(upload_to='assignments/', blank=True, null=True)
    reference_material = models.FileField(upload_to='assignment_references/', blank=True, null=True)
    
    # Instructions
    submission_instructions = models.TextField(blank=True, null=True)
    grading_criteria = models.TextField(blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    allow_late_submission = models.BooleanField(default=False)
    late_submission_penalty = models.IntegerField(default=0, help_text="Marks deduction per day")
    
    class Meta:
        ordering = ['-assigned_date']
    
    def __str__(self):
        return f"{self.class_subject} - {self.title}"

class StudentAssignment(UUIDModel, TimeStampedModel):
    """Student assignment submissions"""
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='assignment_submissions')
    
    # Submission
    submission_file = models.FileField(upload_to='assignment_submissions/', blank=True, null=True)
    submission_text = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(blank=True, null=True)
    
    # Grading
    marks_obtained = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0)])
    feedback = models.TextField(blank=True, null=True)
    graded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    graded_at = models.DateTimeField(blank=True, null=True)
    
    # Status
    is_submitted = models.BooleanField(default=False)
    is_late = models.BooleanField(default=False)
    is_graded = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['assignment', 'student']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.assignment.title}"

class Timetable(TimeStampedModel):
    """Class timetable management"""
    DAYS_OF_WEEK = [
        ('MONDAY', 'Monday'),
        ('TUESDAY', 'Tuesday'),
        ('WEDNESDAY', 'Wednesday'),
        ('THURSDAY', 'Thursday'),
        ('FRIDAY', 'Friday'),
        ('SATURDAY', 'Saturday'),
        ('SUNDAY', 'Sunday'),
    ]
    
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='timetables')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='timetables')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='timetables')
    
    # Period details
    day_of_week = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    period_number = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    # Subject and teacher
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='timetable_slots')
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='timetable_slots')
    
    # Venue
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, related_name='timetable_slots')
    
    # Status
    is_active = models.BooleanField(default=True)
    is_substitution = models.BooleanField(default=False)
    original_teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='substituted_classes')
    substitution_reason = models.CharField(max_length=200, blank=True, null=True)
    
    class Meta:
        unique_together = ['school_class', 'section', 'day_of_week', 'period_number', 'academic_year']
        ordering = ['day_of_week', 'period_number']
    
    def __str__(self):
        return f"{self.school_class.name}-{self.section.name} | {self.day_of_week} P{self.period_number} | {self.subject.name}"

class Attendance(TimeStampedModel):
    """Class-wise attendance tracking"""
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    
    # Class details
    topic_covered = models.CharField(max_length=500, blank=True, null=True)
    homework_given = models.TextField(blank=True, null=True)
    
    # Teacher
    taken_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    remarks = models.TextField(blank=True, null=True)
    
    # Status
    is_completed = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    cancellation_reason = models.CharField(max_length=200, blank=True, null=True)
    
    class Meta:
        unique_together = ['timetable', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.timetable} - {self.date}"

class StudentClassAttendance(TimeStampedModel):
    """Individual student attendance for specific class"""
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE, related_name='student_attendances')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='class_attendances')
    
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LATE', 'Late'),
        ('EXCUSED', 'Excused'),
    ]
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PRESENT')
    arrival_time = models.TimeField(blank=True, null=True)
    remarks = models.CharField(max_length=200, blank=True, null=True)
    
    class Meta:
        unique_together = ['attendance', 'student']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.attendance.date} - {self.status}"

class Holiday(TimeStampedModel):
    """Holiday management"""
    HOLIDAY_TYPES = [
        ('NATIONAL', 'National Holiday'),
        ('RELIGIOUS', 'Religious Holiday'),
        ('SCHOOL', 'School Holiday'),
        ('VACATION', 'Vacation'),
        ('OPTIONAL', 'Optional Holiday'),
    ]
    
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='holidays')
    name = models.CharField(max_length=200)
    date = models.DateField()
    end_date = models.DateField(blank=True, null=True)  # For multi-day holidays
    holiday_type = models.CharField(max_length=20, choices=HOLIDAY_TYPES)
    description = models.TextField(blank=True, null=True)
    
    # Applicability
    applies_to_all = models.BooleanField(default=True)
    applies_to_classes = models.ManyToManyField(SchoolClass, blank=True, related_name='holidays')
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['school', 'date', 'name']
        ordering = ['date']
    
    def __str__(self):
        return f"{self.school.name} - {self.name} - {self.date}"

# Create your models here.
