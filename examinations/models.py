from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericRelation
from core.models import TimeStampedModel, SchoolSettings, UUIDModel, AcademicYear, Attachment
from students.models import Student, SchoolClass, Section
from hr.models import Employee
from decimal import Decimal
import uuid

class Subject(TimeStampedModel):
    """Academic subjects"""
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='exam_subjects')
    
    # Subject details
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    short_name = models.CharField(max_length=10, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    # Classification
    subject_type = models.CharField(max_length=20, choices=[
        ('CORE', 'Core Subject'),
        ('ELECTIVE', 'Elective'),
        ('OPTIONAL', 'Optional'),
        ('ACTIVITY', 'Activity/Non-Academic'),
        ('LANGUAGE', 'Language'),
        ('VOCATIONAL', 'Vocational'),
    ], default='CORE')
    
    # Academic configuration
    is_theory = models.BooleanField(default=True)
    is_practical = models.BooleanField(default=False)
    has_internal_assessment = models.BooleanField(default=True)
    
    # Grading
    max_theory_marks = models.IntegerField(default=100)
    max_practical_marks = models.IntegerField(default=0)
    max_internal_marks = models.IntegerField(default=0)
    passing_marks = models.IntegerField(default=35)
    
    # Class associations
    applicable_classes = models.ManyToManyField(SchoolClass, related_name='subjects')
    
    # Teachers
    subject_head = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='headed_subjects')
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['school', 'code']
        ordering = ['name']
    
    def __str__(self):
        return f"{self.school.name} - {self.name}"
    
    @property
    def total_marks(self):
        return self.max_theory_marks + self.max_practical_marks + self.max_internal_marks

class ExamType(TimeStampedModel):
    """Types of examinations"""
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='exam_types')
    
    # Exam type details
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    
    # Classification
    exam_category = models.CharField(max_length=20, choices=[
        ('UNIT_TEST', 'Unit Test'),
        ('MONTHLY', 'Monthly Test'),
        ('QUARTERLY', 'Quarterly Exam'),
        ('HALF_YEARLY', 'Half Yearly Exam'),
        ('ANNUAL', 'Annual Exam'),
        ('BOARD_PREP', 'Board Preparation'),
        ('ENTRANCE_PREP', 'Entrance Preparation'),
        ('SURPRISE', 'Surprise Test'),
        ('ASSIGNMENT', 'Assignment'),
        ('PROJECT', 'Project'),
        ('PRACTICAL', 'Practical Exam'),
        ('VIVA', 'Viva/Oral Exam'),
    ])
    
    # Weightage for final result
    weightage_percentage = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Configuration
    is_internal = models.BooleanField(default=True)
    is_board_exam = models.BooleanField(default=False)
    requires_hall_ticket = models.BooleanField(default=False)
    
    # Result processing
    include_in_final_result = models.BooleanField(default=True)
    show_in_report_card = models.BooleanField(default=True)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['school', 'code']
        ordering = ['exam_category', 'name']
    
    def __str__(self):
        return f"{self.school.name} - {self.name}"

class ExamSchedule(UUIDModel, TimeStampedModel):
    """Examination schedules"""
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='exam_schedules')
    exam_type = models.ForeignKey(ExamType, on_delete=models.CASCADE, related_name='schedules')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='exam_schedules')
    
    # Schedule details
    schedule_name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    # Dates
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Result processing
    result_declaration_date = models.DateField(blank=True, null=True)
    results_published = models.BooleanField(default=False)
    
    # Classes
    applicable_classes = models.ManyToManyField(SchoolClass, related_name='exam_schedules')
    
    # Status
    is_published = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Created by
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_exam_schedules')
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.schedule_name} - {self.start_date} to {self.end_date}"

class Exam(UUIDModel, TimeStampedModel):
    """Individual exam sessions"""
    schedule = models.ForeignKey(ExamSchedule, on_delete=models.CASCADE, related_name='exams')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='exams')
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='exams')
    sections = models.ManyToManyField(Section, related_name='exams')
    
    # Exam details
    exam_name = models.CharField(max_length=200)
    exam_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration_minutes = models.IntegerField()
    
    # Marks configuration
    theory_marks = models.IntegerField(default=0)
    practical_marks = models.IntegerField(default=0)
    total_marks = models.IntegerField()
    passing_marks = models.IntegerField()
    
    # Exam type specific
    is_online = models.BooleanField(default=False)
    is_objective = models.BooleanField(default=False)
    is_subjective = models.BooleanField(default=True)
    
    # Instructions
    exam_instructions = models.TextField(blank=True, null=True)
    
    # Question paper
    question_paper = models.FileField(upload_to='question_papers/', blank=True, null=True)
    answer_key = models.FileField(upload_to='answer_keys/', blank=True, null=True)
    
    # Supervision
    invigilators = models.ManyToManyField(Employee, related_name='invigilated_exams')
    exam_center = models.CharField(max_length=200, blank=True, null=True)
    room_numbers = models.CharField(max_length=200, blank=True, null=True)
    
    # Status
    is_completed = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    cancellation_reason = models.TextField(blank=True, null=True)
    
    # Result processing
    results_entered = models.BooleanField(default=False)
    results_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_exams')
    verification_date = models.DateField(blank=True, null=True)
    
    class Meta:
        ordering = ['exam_date', 'start_time']
        unique_together = ['schedule', 'subject', 'school_class']
    
    def __str__(self):
        return f"{self.exam_name} - {self.subject.name} - {self.school_class.name}"

class QuestionBank(UUIDModel, TimeStampedModel):
    """Question bank for online examinations"""
    QUESTION_TYPES = [
        ('MCQ', 'Multiple Choice Question'),
        ('TRUE_FALSE', 'True/False'),
        ('FILL_BLANKS', 'Fill in the Blanks'),
        ('SHORT_ANSWER', 'Short Answer'),
        ('LONG_ANSWER', 'Long Answer'),
        ('NUMERICAL', 'Numerical Answer'),
        ('MATCH_PAIRS', 'Match the Pairs'),
        ('ORDERING', 'Ordering/Sequencing'),
        ('ESSAY', 'Essay Type'),
    ]
    
    DIFFICULTY_LEVELS = [
        ('EASY', 'Easy'),
        ('MEDIUM', 'Medium'),
        ('HARD', 'Hard'),
        ('VERY_HARD', 'Very Hard'),
    ]
    
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='question_bank')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='questions')
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='questions')
    
    # Question details
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS, default='MEDIUM')
    
    # Topic/Chapter
    chapter = models.CharField(max_length=200, blank=True, null=True)
    topic = models.CharField(max_length=200, blank=True, null=True)
    learning_objective = models.TextField(blank=True, null=True)
    
    # Marks
    marks = models.IntegerField(default=1)
    negative_marks = models.FloatField(default=0)
    
    # Multiple choice options (for MCQ)
    option_a = models.TextField(blank=True, null=True)
    option_b = models.TextField(blank=True, null=True)
    option_c = models.TextField(blank=True, null=True)
    option_d = models.TextField(blank=True, null=True)
    correct_option = models.CharField(max_length=1, choices=[
        ('A', 'Option A'), ('B', 'Option B'), ('C', 'Option C'), ('D', 'Option D')
    ], blank=True, null=True)
    
    # Answer for other types
    correct_answer = models.TextField(blank=True, null=True)
    answer_explanation = models.TextField(blank=True, null=True)
    
    # Media attachments
    question_image = models.ImageField(upload_to='question_images/', blank=True, null=True)
    question_audio = models.FileField(upload_to='question_audio/', blank=True, null=True)
    
    # Usage statistics
    times_used = models.IntegerField(default=0)
    average_score = models.FloatField(default=0)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_questions')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_questions')
    is_approved = models.BooleanField(default=False)
    
    # Tags for easy searching
    tags = models.TextField(blank=True, null=True, help_text="Comma-separated tags")
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['subject', 'chapter', 'difficulty_level']
        indexes = [
            models.Index(fields=['subject', 'school_class']),
            models.Index(fields=['question_type', 'difficulty_level']),
            models.Index(fields=['chapter', 'topic']),
        ]
    
    def __str__(self):
        return f"{self.subject.name} - {self.question_text[:50]}..."

class OnlineExam(UUIDModel, TimeStampedModel):
    """Online examination configuration"""
    exam = models.OneToOneField(Exam, on_delete=models.CASCADE, related_name='online_config')
    
    # Exam configuration
    auto_submit = models.BooleanField(default=True)
    allow_review = models.BooleanField(default=True)
    show_result_immediately = models.BooleanField(default=False)
    randomize_questions = models.BooleanField(default=True)
    randomize_options = models.BooleanField(default=True)
    
    # Timing
    buffer_time_minutes = models.IntegerField(default=5)
    warning_time_minutes = models.IntegerField(default=5)
    
    # Security
    full_screen_required = models.BooleanField(default=True)
    disable_copy_paste = models.BooleanField(default=True)
    disable_right_click = models.BooleanField(default=True)
    capture_screenshots = models.BooleanField(default=False)
    monitor_tab_switching = models.BooleanField(default=True)
    max_tab_switches = models.IntegerField(default=3)
    
    # Proctoring
    enable_webcam_monitoring = models.BooleanField(default=False)
    enable_audio_monitoring = models.BooleanField(default=False)
    
    # Question selection
    total_questions = models.IntegerField()
    questions_per_section = models.JSONField(default=dict)  # {chapter: count}
    
    # Browser lockdown
    browser_lockdown = models.BooleanField(default=False)
    allowed_browsers = models.JSONField(default=list)
    
    class Meta:
        verbose_name = 'Online Exam Configuration'
    
    def __str__(self):
        return f"Online Config - {self.exam.exam_name}"

class StudentExamAttempt(UUIDModel, TimeStampedModel):
    """Student exam attempts for online exams"""
    ATTEMPT_STATUS = [
        ('NOT_STARTED', 'Not Started'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('ABANDONED', 'Abandoned'),
        ('DISQUALIFIED', 'Disqualified'),
        ('TECHNICAL_ISSUE', 'Technical Issue'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exam_attempts')
    online_exam = models.ForeignKey(OnlineExam, on_delete=models.CASCADE, related_name='attempts')
    
    # Attempt details
    attempt_number = models.IntegerField(default=1)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    actual_duration_minutes = models.IntegerField(blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=ATTEMPT_STATUS, default='NOT_STARTED')
    
    # Responses
    responses = models.JSONField(default=dict)  # {question_id: answer}
    question_sequence = models.JSONField(default=list)  # Randomized question order
    
    # Scores
    total_marks_obtained = models.FloatField(default=0)
    percentage = models.FloatField(default=0)
    
    # Security violations
    tab_switches = models.IntegerField(default=0)
    copy_paste_attempts = models.IntegerField(default=0)
    right_click_attempts = models.IntegerField(default=0)
    full_screen_exits = models.IntegerField(default=0)
    
    # Browser and device info
    browser_info = models.JSONField(default=dict)
    device_info = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    # Auto-save data
    last_saved_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        unique_together = ['student', 'online_exam', 'attempt_number']
        ordering = ['-start_time']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.online_exam.exam.exam_name} - Attempt {self.attempt_number}"

class ExamResult(UUIDModel, TimeStampedModel):
    """Student exam results"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exam_results')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='results')
    
    # Marks breakdown
    theory_marks_obtained = models.FloatField(default=0)
    practical_marks_obtained = models.FloatField(default=0)
    internal_marks_obtained = models.FloatField(default=0)
    total_marks_obtained = models.FloatField(default=0)
    
    # Calculations
    percentage = models.FloatField(default=0)
    grade = models.CharField(max_length=5, blank=True, null=True)
    grade_points = models.FloatField(default=0)
    
    # Status
    is_passed = models.BooleanField(default=False)
    is_absent = models.BooleanField(default=False)
    is_copy_case = models.BooleanField(default=False)
    is_malpractice = models.BooleanField(default=False)
    
    # Additional info
    rank_in_class = models.IntegerField(blank=True, null=True)
    rank_in_section = models.IntegerField(blank=True, null=True)
    
    # Answer sheets
    answer_sheet = models.FileField(upload_to='answer_sheets/', blank=True, null=True)
    
    # Entry and verification
    entered_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='entered_results')
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_results')
    verification_date = models.DateField(blank=True, null=True)
    
    # Remarks
    teacher_remarks = models.TextField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        # Calculate total marks and percentage
        self.total_marks_obtained = (
            self.theory_marks_obtained + 
            self.practical_marks_obtained + 
            self.internal_marks_obtained
        )
        
        if self.exam.total_marks > 0:
            self.percentage = (self.total_marks_obtained / self.exam.total_marks) * 100
        
        # Determine pass/fail
        self.is_passed = self.total_marks_obtained >= self.exam.passing_marks
        
        super().save(*args, **kwargs)
    
    class Meta:
        unique_together = ['student', 'exam']
        ordering = ['-total_marks_obtained']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.exam.exam_name} - {self.total_marks_obtained}/{self.exam.total_marks}"

class GradingScheme(TimeStampedModel):
    """Grading schemes for different classes"""
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='grading_schemes')
    name = models.CharField(max_length=100)
    applicable_classes = models.ManyToManyField(SchoolClass, related_name='grading_schemes')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='grading_schemes')
    
    # Grade definitions (stored as JSON)
    grade_definitions = models.JSONField(default=list, help_text="List of grade definitions with min/max percentages")
    
    # Configuration
    is_percentage_based = models.BooleanField(default=True)
    is_gpa_based = models.BooleanField(default=False)
    max_gpa = models.FloatField(default=10.0)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['school', 'name', 'academic_year']
    
    def __str__(self):
        return f"{self.school.name} - {self.name}"

class HallTicket(UUIDModel, TimeStampedModel):
    """Exam hall tickets"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='hall_tickets')
    exam_schedule = models.ForeignKey(ExamSchedule, on_delete=models.CASCADE, related_name='hall_tickets')
    
    # Hall ticket details
    hall_ticket_number = models.CharField(max_length=50, unique=True)
    
    # Exam center details
    exam_center = models.CharField(max_length=200)
    room_number = models.CharField(max_length=50, blank=True, null=True)
    seat_number = models.CharField(max_length=50, blank=True, null=True)
    
    # Instructions
    general_instructions = models.TextField()
    specific_instructions = models.TextField(blank=True, null=True)
    
    # Status
    is_issued = models.BooleanField(default=False)
    issued_date = models.DateField(blank=True, null=True)
    
    # Digital signature and verification
    digital_signature = models.CharField(max_length=200, blank=True, null=True)
    verification_code = models.CharField(max_length=20, blank=True, null=True)
    
    # PDF generation
    hall_ticket_pdf = models.FileField(upload_to='hall_tickets/', blank=True, null=True)
    
    class Meta:
        unique_together = ['student', 'exam_schedule']
    
    def __str__(self):
        return f"{self.hall_ticket_number} - {self.student.full_name}"

class ExamReport(UUIDModel, TimeStampedModel):
    """Examination reports and analytics"""
    REPORT_TYPES = [
        ('RESULT_ANALYSIS', 'Result Analysis'),
        ('CLASS_PERFORMANCE', 'Class Performance'),
        ('SUBJECT_ANALYSIS', 'Subject-wise Analysis'),
        ('COMPARATIVE_ANALYSIS', 'Comparative Analysis'),
        ('TOPPERS_LIST', 'Toppers List'),
        ('FAILED_STUDENTS', 'Failed Students List'),
        ('GRADE_DISTRIBUTION', 'Grade Distribution'),
        ('ABSENTEE_REPORT', 'Absentee Report'),
        ('QUESTION_ANALYSIS', 'Question Analysis'),
        ('EXAM_STATISTICS', 'Exam Statistics'),
    ]
    
    school = models.ForeignKey(SchoolSettings, on_delete=models.CASCADE, related_name='exam_reports')
    exam_schedule = models.ForeignKey(ExamSchedule, on_delete=models.CASCADE, related_name='reports')
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_exam_reports')
    
    # Report data
    report_data = models.JSONField(default=dict)
    
    # Filters
    class_filter = models.ForeignKey(SchoolClass, on_delete=models.SET_NULL, null=True, blank=True)
    subject_filter = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    section_filter = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True)
    
    # File
    report_file = models.FileField(upload_to='exam_reports/', blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.school.name} - {self.report_type} - {self.exam_schedule.schedule_name}" 